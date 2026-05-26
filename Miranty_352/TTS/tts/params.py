from django.conf import settings


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def parse_synthesis_params(payload: dict) -> dict:
    """Extrait ritma / fiovan'ny ritma / angola (ou noms VITS anglais)."""
    ritma = payload.get("ritma", payload.get("speaking_rate", settings.DEFAULT_RITMA))
    fiovan = payload.get(
        "fiovan_ritma",
        payload.get("fiovan_kritma", payload.get("noise_scale_duration", settings.DEFAULT_FIOVAN_RITMA)),
    )
    angolo = payload.get("angola", payload.get("angolo", payload.get("noise_scale", settings.DEFAULT_ANGOLO)))

    return {
        "speaking_rate": _clamp(ritma, 0.5, 1.5),
        "noise_scale_duration": _clamp(fiovan, 0.0, 1.0),
        "noise_scale": _clamp(angolo, 0.0, 1.0),
    }
