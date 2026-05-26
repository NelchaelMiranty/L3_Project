from django.conf import settings


def vox_synth(request):
    return {
        "model_id": settings.MODEL_ID,
        "default_seed": settings.DEFAULT_SEED,
        "default_ritma": settings.DEFAULT_RITMA,
        "default_fiovan_ritma": settings.DEFAULT_FIOVAN_RITMA,
        "default_angolo": settings.DEFAULT_ANGOLO,
    }
