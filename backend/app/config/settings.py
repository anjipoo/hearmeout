from dataclasses import dataclass, field
import os
from dotenv import load_dotenv

load_dotenv()
@dataclass
class Settings:
    sample_rate: int = 16000
    chunk_ms: int = 30
    frames_per_window: int = 50
    overlap_frames: int = 10
    min_speech_ratio: float = 0.4

    vad_aggressiveness: int = 2

    model_size: str = "base"
    device: str = "cpu"
    compute_type: str = "int8"
    beam_size: int = 3
    language: str = "en"

    diarization: bool = True
    max_speakers: int = 2
    min_speakers:int=1

    hf_token:str=field(default_factory=lambda: os.getenv("HUGGINGFACE_TOKEN", ""))

    host:str = "0.0.0.0"
    port:int=8000

    @property
    def chunk_samples(self) ->int:
        return int(self.sample_rate*self.chunk_ms/1000)

settings=Settings()
