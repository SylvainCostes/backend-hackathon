# 💻 Backend - Jean-Michel Apeupréx (FastAPI)

Ce service backend est la machine à sous du Druide du Numérique, Jean-Michel Apeupréx. Il expose un endpoint unique (`/chat`) qui gère la conversation avec l'IA, la synthèse vocale, et le pipeline de synchronisation labiale (lipsync).

## ✨ Caractéristiques Techniques Clés

- **API Framework** : Python FastAPI
- **Déploiement** : Docker (image Linux basée sur Python 3.10-slim)
- **Mode d'exécution** : H24 (sur Koyeb)
- **Fonctionnalité critique** : Pipeline de génération audio et lipsync

## ⚙️ Pipeline de Génération/Lipsync

Le service a été contraint de gérer des outils système non-Python pour créer une expérience "vivante" :

1. **Réponse IA** : Utilisation de l'API OpenAI (GPT-4o-mini) pour générer une réponse au format JSON avec des instructions de style (expression faciale, animation).

2. **Synthèse Vocale (TTS)** : L'API ElevenLabs est appelée pour transformer le texte en un fichier audio MP3.

3. **Conversion & Lipsync** : Le Dockerfile est essentiel car il installe :
   - **FFmpeg (Linux)** : Utilisé pour convertir l'audio `.mp3` en `.wav` (format requis par Rhubarb).
   - **Rhubarb Lipsync (Linux)** : Utilisé pour analyser le fichier `.wav` et générer un fichier `.json` contenant les marqueurs de bouche (mouthCues) synchronisés avec l'audio.

4. **Retour Client** : Le service encode l'audio et les données de lipsync en Base64/JSON et les renvoie au frontend.

## 🐳 Lancement en Local (Via Docker)

Le lancement via Docker est la méthode recommandée pour garantir l'environnement Linux requis et le bon fonctionnement des binaires FFmpeg et Rhubarb.

### Pré-requis

- Docker et Docker Compose doivent être installés

### Étapes d'installation

#### 1. Clonage du Dépôt et Configuration des Clés

```bash
git clone https://github.com/SylvainCostes/backend-hackathon.git
cd backend-hackathon
```

#### 2. Définir les Clés API

Créez un fichier `.env` à la racine du dossier et ajoutez les clés API (ces clés ne sont pas fournies pour des raisons de sécurité/coût) :

```env
OPENAI_API_KEY="[VOTRE_CLE_OPENAI]"
ELEVEN_LABS_API_KEY="[VOTRE_CLE_ELEVENLABS]"
```

#### 3. Lancement du Conteneur

Construisez et démarrez l'image. Le service écoutera sur le port local 8000.

```bash
docker build -t fastapi-druide .
docker run -d -p 8000:10000 --name druide-app --env-file ./.env fastapi-druide
```

L'API sera accessible localement à l'adresse : **http://localhost:8000/docs**

## 🔗 Accès à la Production (Hébergé sur Koyeb)

Le service est en ligne et accessible en H24 à l'adresse :

**https://musical-darlleen-morrisii-3d1ed0cf.koyeb.app/docs**

## 📁 Structure du Projet

```
FastAPI-ChatBot/
├── Dockerfile              # Configuration Docker avec FFmpeg et Rhubarb
├── main.py                 # Point d'entrée de l'application FastAPI
├── requirements.txt        # Dépendances Python
├── .env                    # Clés API (non versionné)
├── api/                    # Modules API
├── audios/                 # Fichiers audio générés
├── bin/                    # Binaires (Rhubarb Lipsync)
│   └── res/
│       └── sphinx/         
```

## 🛠️ Technologies Utilisées

- **FastAPI** - Framework web moderne et rapide
- **OpenAI API** - Génération de réponses IA (GPT-4o-mini)
- **ElevenLabs API** - Synthèse vocale de haute qualité
- **FFmpeg** - Conversion audio
- **Rhubarb Lipsync** - Génération de synchronisation labiale
- **Docker** - Containerisation et déploiement

## 📝 Endpoint Principal

### POST `/chat`

Endpoint unique qui gère toute la conversation avec Jean-Michel Apeupréx.

**Réponse** : JSON contenant :
- Le texte de la réponse
- L'audio encodé en Base64
- Les données de lipsync (mouthCues)
- Les instructions d'animation faciale

## 🚀 Développement

Pour développer en local sans Docker (non recommandé, peut nécessiter des ajustements) :

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

⚠️ **Note** : FFmpeg et Rhubarb doivent être installés manuellement sur votre système.

## 📄 Licence

Ce projet a été développé dans le cadre de la Nuit de l'Info.

---

**Développé avec ❤️ par l'équipe Morris II**
