import time
import numpy as np
from faster_whisper import WhisperModel
from app.config.settings import settings


class TranscriptionService:
    def __init__(self):
        self.model:WhisperModel=None
        self.is_ready:bool=False

    def load_model(self) -> None:
        print("loading model")
        self.model=WhisperModel(settings.model_size, device=settings.device, compute_type=settings.compute_type)
        self.is_ready=True
        print("model loaded")

    def trans(self, audio:np.ndarray) -> str:
        if not self.is_ready:
            raise RuntimeError("model not loaded")
        
        start_time=time.time()
        segments, info=self.model.transcribe(audio, beam_size=settings.beam_size, language=settings.language, without_timestamps=True, condition_on_previous_text=False, vad_filter=False)
        text_parts=[s.text.strip() for s in segments if s.text.strip()]
        full_text=" ".join(text_parts)
        latency_ms=int((time.time() - start_time) * 1000)
        return full_text, latency_ms
    
transcription_service=TranscriptionService()