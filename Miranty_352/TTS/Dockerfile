# syntax=docker/dockerfile:1
# VOX-SYNTH — TTS Malagasy (Django + VITS)
# Build : docker build -t vox-synth .
# Run   : docker run -p 8000:8000 vox-synth

FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface \
    PORT=8000

WORKDIR /app

# Dépendances système (compilation éventuelle de wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# PyTorch CPU (image plus légère que la variante CUDA)
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install -r requirements.txt

# Code applicatif
COPY manage.py .
COPY config/ config/
COPY tts/ tts/
COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN chmod +x /app/docker/entrypoint.sh

# Fichiers statiques Django
RUN python manage.py collectstatic --noinput

# Pré-téléchargement du modèle Hugging Face (évite le 1er appel à froid)
ARG PRELOAD_MODEL=true
ARG MODEL_ID=Nelchael/tts-malagasy
RUN if [ "$PRELOAD_MODEL" = "true" ]; then \
      python -c "\
from transformers import AutoTokenizer, VitsModel; \
mid = '${MODEL_ID}'; \
print('Téléchargement', mid); \
AutoTokenizer.from_pretrained(mid); \
VitsModel.from_pretrained(mid); \
print('Modèle prêt.')"; \
    fi

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
  CMD curl -f "http://127.0.0.1:${PORT}/" || exit 1

ENTRYPOINT ["/app/docker/entrypoint.sh"]
