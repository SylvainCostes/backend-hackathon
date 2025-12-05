# Image de base pour Python
FROM python:3.10-slim

# 1. Installer FFmpeg via le système de paquets (apt)
RUN apt-get update && \
    apt-get install -y ffmpeg curl && \
    rm -rf /var/lib/apt/lists/*

# 2. Télécharger et installer l'exécutable Rhubarb pour Linux
# L'URL ci-dessous est un exemple et doit être vérifiée
ENV RHUBARB_VERSION=1.13.0
RUN curl -L "https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v${RHUBARB_VERSION}/rhubarb-lip-sync-${RHUBARB_VERSION}-linux.zip" -o /tmp/rhubarb.zip && \
    unzip /tmp/rhubarb.zip -d /tmp/rhubarb && \
    mv /tmp/rhubarb/rhubarb /usr/local/bin/rhubarb && \
    chmod +x /usr/local/bin/rhubarb && \
    rm -rf /tmp/rhubarb /tmp/rhubarb.zip

# 3. Le reste de votre configuration
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

# 4. Commande de démarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]