import os
import json
import base64
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import requests

# Charger les variables d'environnement
load_dotenv()

# Création du dossier audios si inexistant
if not os.path.exists("audios"):
    os.makedirs("audios")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURATION ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
VOICE_ID = "GFj5Qf6cNQ3Lgp8VKBwc" 

client = OpenAI(api_key=OPENAI_API_KEY)

class ChatRequest(BaseModel):
    message: str

# --- FONCTIONS UTILITAIRES ---

def exec_command(command_list):
    """Exécute une commande proprement (ffmpeg/rhubarb)"""
    try:
        subprocess.run(command_list, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Erreur non-critique (Lipsync) : {e.stderr}")
        pass

def audio_file_to_base64(file_path: str) -> str:
    if not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode('utf-8')

def read_json_transcript(file_path: str) -> dict:
    if not os.path.exists(file_path):
        return {"metadata": {}, "mouthCues": []}
    with open(file_path, "r", encoding='utf-8') as json_file:
        return json.load(json_file)

async def generate_audio_elevenlabs(text: str, filename: str):
    """Génération audio via ElevenLabs avec le modèle MULTILINGUE"""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2", # IMPORTANT pour l'accent français
        "voice_settings": {
            "stability": 0.4,       
            "similarity_boost": 0.6
        }
    }
    
    print(f"🎤 ElevenLabs : Génération audio pour '{text[:20]}...'")
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code != 200:
        print(f"ERREUR ELEVENLABS: {response.text}")
        return False
        
    with open(filename, "wb") as f:
        f.write(response.content)
    return True

async def lip_sync_message(message_id: int):
    """Génère le Lipsync"""
    current_dir = os.getcwd()
    ffmpeg_exe = os.path.join(current_dir, "bin", "ffmpeg.exe")
    rhubarb_exe = os.path.join(current_dir, "bin", "rhubarb.exe")
    
    mp3_file = os.path.join(current_dir, "audios", f"message_{message_id}.mp3")
    wav_file = os.path.join(current_dir, "audios", f"message_{message_id}.wav")
    json_file = os.path.join(current_dir, "audios", f"message_{message_id}.json")
    
    if not os.path.exists(mp3_file): return

    # 1. MP3 -> WAV
    exec_command([ffmpeg_exe, "-y", "-i", mp3_file, wav_file])
    
    # 2. WAV -> Lipsync JSON
    if os.path.exists(wav_file):
        exec_command([rhubarb_exe, "-f", "json", "-o", json_file, wav_file, "-r", "phonetic"])

@app.post("/chat")
async def chat(request: ChatRequest):
    user_message = request.message or "Bonjour"
    print(f"📩 User: {user_message}")

    # --- PROMPT DU DRUIDE CHAT'BRUTI ---
    system_prompt = """
    Tu es 'Jean-Michel Apeupréx', le Druide du Numérique Résistant.
    Tu vis dans un village gaulois qui résiste à l'envahisseur "Big Tech" (les Romains).
    
    TES CROYANCES ABSURDES :
    1. Le "Cloud" ? C'est de la fumée de marmite.
    2. "Windows" ? Une fenêtre mal isolée qui laisse passer les courants d'air romains.
    3. "Linux" ? Une potion magique à base de pingouin fermenté.
    4. Tu es arrogant, incompétent, mais très fier de ta "Souveraineté Numérique".

    TES RÈGLES :
    - Ne réponds JAMAIS sérieusement. Digresse sur la magie, les menhirs ou les sangliers.
    - Termine 1 réponse sur 2 par une QUESTION COMPLOTISTE ou STUPIDE.
    - Si l'utilisateur demande de l'aide technique, propose une solution à base de plantes ou de cailloux.

    FORMAT JSON OBLIGATOIRE (Un seul message) :
    { 
      "messages": [ 
        { 
          "text": "Réponse du druide ici...", 
          "facialExpression": "smile | sad | angry | surprised | funnyFace", 
          "animation": "OldManIdle | AngryPoint | NervouslyLookAround | ThoughtfulHeadNod | Salute | Agreeing" 
        } 
      ] 
    }
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=250,
            temperature=0.8,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        
        content = completion.choices[0].message.content
        data = json.loads(content)
        messages = data.get("messages", [])
        
        # Traitement Audio
        for i, msg in enumerate(messages):
            file_mp3 = f"audios/message_{i}.mp3"
            file_json = f"audios/message_{i}.json"
            
            if os.path.exists(file_mp3): os.remove(file_mp3)
            if os.path.exists(file_json): os.remove(file_json)

            success = await generate_audio_elevenlabs(msg["text"], file_mp3)
            if success:
                await lip_sync_message(i)
                msg["audio"] = audio_file_to_base64(file_mp3)
                msg["lipsync"] = read_json_transcript(file_json)

        return {"messages": messages}

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)