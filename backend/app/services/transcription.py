import time
import numpy as np
from faster_whisper import WhisperModel
from app.config.settings import settings


class TranscriptionService:
    def __init__(self):
        self.model: WhisperModel = None
        self.is_ready: bool = False

    def load_model(self) -> None:
        print("loading model")
        self.model = WhisperModel(
            settings.model_size,
            device=settings.device,
            compute_type=settings.compute_type
        )
        self.is_ready = True
        print("model loaded")

    def trans(self, audio: np.ndarray) -> tuple[str, int, list[dict]]:
        """
        Returns: (full_text, latency_ms, segments)
        segments: [{ text, start, end }, ...]
        """
        if not self.is_ready:
            raise RuntimeError("model not loaded")

        start_time = time.time()

        # without_timestamps=False so we get timing for speaker merger
        segments_gen, _ = self.model.transcribe(
            audio,
            beam_size=settings.beam_size,
            language=settings.language,
            without_timestamps=False,       # ← need timestamps for diarization
            condition_on_previous_text=False,
            vad_filter=False,
        )

        segments = []
        text_parts = []

        for seg in segments_gen:
            text = seg.text.strip()
            if text:
                text_parts.append(text)
                segments.append({
                    "text": text,
                    "start": seg.start,
                    "end": seg.end,
                })

        full_text = " ".join(text_parts)
        latency_ms = int((time.time() - start_time) * 1000)

        return full_text, latency_ms, segments


transcription_service = TranscriptionService()