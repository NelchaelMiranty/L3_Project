import json

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .engine import get_engine
from .params import parse_synthesis_params

EXAMPLES = [
    "Manao ahoana, salama tsara ve ianao?",
    "Miarahaba anao.",
    "Misaotra betsaka.",
]


def editor(request):
    return render(
        request,
        "tts/editor.html",
        {"active_nav": "editor", "examples": EXAMPLES},
    )


def voice(request):
    return render(request, "tts/voice.html", {"active_nav": "voice"})


def api(request):
    return render(
        request,
        "tts/api.html",
        {
            "active_nav": "api",
            "synthesize_url": request.build_absolute_uri(reverse("synthesize")),
        },
    )


@require_http_methods(["POST"])
def synthesize(request):
    try:
        if request.content_type == "application/json":
            payload = json.loads(request.body.decode("utf-8"))
            text = payload.get("text", "")
            seed = payload.get("seed", settings.DEFAULT_SEED)
        else:
            payload = request.POST.dict()
            text = payload.get("text", "")
            seed = payload.get("seed", settings.DEFAULT_SEED)

        vits = parse_synthesis_params(payload)

        engine = get_engine()
        waveform = engine.synthesize(
            text,
            seed=int(seed),
            speaking_rate=vits["speaking_rate"],
            noise_scale=vits["noise_scale"],
            noise_scale_duration=vits["noise_scale_duration"],
        )
        wav_bytes = engine.to_wav_bytes(waveform)

        duration = len(waveform) / engine.sample_rate
        response = HttpResponse(wav_bytes, content_type="audio/wav")
        response["Content-Disposition"] = 'inline; filename="synthesis.wav"'
        response["X-Sample-Rate"] = str(engine.sample_rate)
        response["X-Audio-Duration"] = f"{duration:.2f}"
        return response

    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)
