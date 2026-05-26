import io
import logging
import re
import wave

import numpy as np
import torch
from django.conf import settings
from transformers import AutoTokenizer, VitsModel, set_seed

log = logging.getLogger(__name__)

_engine = None

# Durées de pause (secondes) après chaque signe de ponctuation
PAUSE_DURATIONS = {
    ",": 0.15,
    ";": 0.25,
    ":": 0.20,
    ".": 0.40,
    "!": 0.40,
    "?": 0.40,
    "…": 0.50,
    "—": 0.20,
}

PUNCTUATION_PATTERN = re.compile(r"([,;:.!?…—])")


class TTSEngine:
    def __init__(self):
        self.model_id = settings.MODEL_ID
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        log.info("Chargement %s sur %s", self.model_id, self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = VitsModel.from_pretrained(self.model_id).to(self.device).eval()
        self.sample_rate = self.model.config.sampling_rate
        log.info("Modèle prêt — %s Hz", self.sample_rate)

    def _synthesize_segment(
        self,
        text: str,
        speaking_rate: float = 0.85,
        noise_scale: float = 0.8,
        noise_scale_duration: float = 0.9,
    ) -> np.ndarray:
        text = text.strip()
        if not text:
            return np.array([], dtype=np.float32)

        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            try:
                outputs = self.model(
                    **inputs,
                    speaking_rate=speaking_rate,
                    noise_scale=noise_scale,
                    noise_scale_duration=noise_scale_duration,
                )
            except TypeError:
                outputs = self.model(**inputs)

        return outputs.waveform[0].cpu().numpy().squeeze().astype(np.float32)

    def _crossfade(
        self, wav1: np.ndarray, wav2: np.ndarray, fade_ms: int = 20
    ) -> np.ndarray:
        fade_samples = int(fade_ms * self.sample_rate / 1000)
        if len(wav1) < fade_samples or len(wav2) < fade_samples:
            return np.concatenate([wav1, wav2])

        fade_out = np.linspace(1.0, 0.0, fade_samples)
        fade_in = np.linspace(0.0, 1.0, fade_samples)

        wav1 = wav1.copy()
        wav2 = wav2.copy()
        wav1[-fade_samples:] *= fade_out
        wav2[:fade_samples] *= fade_in

        overlap = wav1[-fade_samples:] + wav2[:fade_samples]
        return np.concatenate([wav1[:-fade_samples], overlap, wav2[fade_samples:]])

    def _silence(self, duration_s: float) -> np.ndarray:
        samples = int(duration_s * self.sample_rate)
        return np.zeros(samples, dtype=np.float32)

    def synthesize(
        self,
        text: str,
        seed: int,
        speaking_rate: float = 0.75,
        noise_scale: float = 0.4,
        noise_scale_duration: float = 0.4,
    ) -> np.ndarray:
        text = (text or "").strip()
        if not text:
            raise ValueError("Le texte est vide.")

        set_seed(int(seed))

        parts = PUNCTUATION_PATTERN.split(text)
        waveforms: list[np.ndarray] = []
        i = 0

        while i < len(parts):
            part = parts[i].strip()
            if not part:
                i += 1
                continue

            punct = None
            if i + 1 < len(parts) and parts[i + 1].strip() in PAUSE_DURATIONS:
                punct = parts[i + 1].strip()
                segment = part + punct
                i += 2
            else:
                segment = part
                i += 1

            wav = self._synthesize_segment(
                segment,
                speaking_rate=speaking_rate,
                noise_scale=noise_scale,
                noise_scale_duration=noise_scale_duration,
            )
            if len(wav) == 0:
                continue

            if waveforms:
                last = waveforms.pop()
                waveforms.append(self._crossfade(last, wav, fade_ms=20))
            else:
                waveforms.append(wav)

            if punct:
                waveforms.append(self._silence(PAUSE_DURATIONS[punct]))

        if not waveforms:
            raise ValueError("Aucun audio généré pour ce texte.")

        out = np.concatenate(waveforms)
        peak = np.abs(out).max()
        if peak > 0:
            out = out / peak * 0.95
        return out

    def to_wav_bytes(self, waveform: np.ndarray) -> bytes:
        pcm = (waveform * 32767).astype(np.int16)
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(pcm.tobytes())
        return buffer.getvalue()


def get_engine() -> TTSEngine:
    global _engine
    if _engine is None:
        _engine = TTSEngine()
    return _engine
