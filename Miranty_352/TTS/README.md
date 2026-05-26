# VOX-SYNTH — TTS Malagasy (Django)

Interface web pour Tester directement [Synthèse vocale Malgache TTS](https://tts-mg.onrender.com/)

## Installation locale

```bash
python -m venv .venv
.venv\Scripts\activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
python manage.py runserver
```

→ [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Déploiement Docker

### Prérequis

- [Docker](https://www.docker.com/) et Docker Compose

### Build et lancement

```bash
# Build (10–20 min la 1ère fois : PyTorch + modèle ~145 Mo)
docker build -t vox-synth .

# Lancer
docker run --rm -p 8000:8000 \
  -e DEBUG=false \
  -e SECRET_KEY="votre-cle-secrete" \
  -e ALLOWED_HOSTS="localhost,127.0.0.1" \
  vox-synth
```

Ou avec Compose :

```bash
docker compose up --build
```

→ [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `PORT` | `8000` | Port HTTP |
| `DEBUG` | `true` | Mode debug Django |
| `SECRET_KEY` | *(dev)* | Clé secrète obligatoire en prod |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost` | Hôtes autorisés (séparés par virgule) |
| `CSRF_TRUSTED_ORIGINS` | — | ex. `https://mon-app.onrender.com` |
| `GUNICORN_WORKERS` | `1` | Garder **1** (un seul chargement du modèle) |
| `GUNICORN_TIMEOUT` | `300` | Timeout synthèse (secondes) |
| `HF_TOKEN` | — | Token Hugging Face (optionnel) |

Copiez `.env.example` vers `.env` pour Compose.

### Build sans pré-charger le modèle

```bash
docker build --build-arg PRELOAD_MODEL=false -t vox-synth .
```

Le modèle sera téléchargé au premier appel `/synthesize/`.

### Déploiement sur Render

1. **New → Web Service** → repo GitHub, runtime **Docker**.
2. Port : **8000**
3. Variables d'environnement recommandées :

| Variable | Valeur |
|----------|--------|
| `DEBUG` | `false` |
| `SECRET_KEY` | *(générer une clé longue)* |
| `PORT` | `8000` |

`ALLOWED_HOSTS` : **optionnel** — `.onrender.com` est déjà accepté par défaut.  
`CSRF_TRUSTED_ORIGINS` : **optionnel** — Render renseigne `RENDER_EXTERNAL_URL` automatiquement.

4. Redéployez après chaque changement de `settings.py`.

## Pages

| URL | Description |
|-----|-------------|
| `/` | Synthèse vocale |
| `/voix/` | Enregistrement vocal (clonage à venir) |
| `/api/` | Documentation API |
| `/synthesize/` | `POST` → fichier WAV |

## Paramètres de synthèse (JSON)

```json
{
  "text": "Manao ahoana!",
  "seed": 555,
  "ritma": 0.75,
  "fiovan_ritma": 0.40,
  "angola": 0.40
}
```
