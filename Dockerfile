# Utilise une image de base Python légère pour Linux
FROM python:3.10-slim

# Met à jour les paquets, installe ffmpeg, curl et unzip
# 'ffmpeg' est essentiel pour la conversion MP3 -> WAV
# 'curl' et 'unzip' sont nécessaires pour télécharger et décompresser Rhubarb
RUN apt-get update && \
    apt-get install -y ffmpeg curl unzip && \
    rm -rf /var/lib/apt/lists/*

# --- Installation de Rhubarb Lipsync (Version Linux) ---
ENV RHUBARB_VERSION=1.14.0
ENV RHUBARB_URL="https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v${RHUBARB_VERSION}/Rhubarb-Lip-Sync-${RHUBARB_VERSION}-Linux.zip"

# Télécharge et installe le binaire Rhubarb
RUN curl -L "${RHUBARB_URL}" -o /tmp/rhubarb.zip && \
    unzip /tmp/rhubarb.zip -d /tmp/rhubarb && \
    # Le binaire extrait est dans un sous-dossier, on le déplace dans un dossier PATH
    mv /tmp/rhubarb/Rhubarb-Lip-Sync-*/rhubarb /usr/local/bin/rhubarb && \
    chmod +x /usr/local/bin/rhubarb && \
    rm -rf /tmp/rhubarb /tmp/rhubarb.zip

# --- Configuration de l'Application ---
WORKDIR /app

# Copie et installe les dépendances Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copie le reste du code (incluant 'main.py' corrigé)
COPY . .

# Crée le dossier 'audios' car le code le vérifie au démarrage
RUN mkdir -p audios

# Commande de démarrage (remplace startCommand dans render.yaml)
# Le port 10000 est utilisé comme standard interne pour Render
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]