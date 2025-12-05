FROM python:3.10-slim

# Met à jour les paquets, installe ffmpeg, curl et unzip
RUN apt-get update && \
    apt-get install -y ffmpeg curl unzip && \
    rm -rf /var/lib/apt/lists/*

ENV RHUBARB_VERSION=1.14.0
ENV RHUBARB_URL="https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v${RHUBARB_VERSION}/Rhubarb-Lip-Sync-${RHUBARB_VERSION}-Linux.zip"

# Télécharge et installe le binaire Rhubarb
RUN curl -L "${RHUBARB_URL}" -o /tmp/rhubarb.zip && \
    unzip /tmp/rhubarb.zip -d /tmp/rhubarb && \
    mv /tmp/rhubarb/Rhubarb-Lip-Sync-*/rhubarb /usr/local/bin/rhubarb && \
    chmod +x /usr/local/bin/rhubarb && \
    rm -rf /tmp/rhubarb /tmp/rhubarb.zip

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p audios


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]