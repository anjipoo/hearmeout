import numpy as np
import torch
from pyannote.audio import Pipeline
from pyannote.core import Annotation
from app.config.settings import settings

class DiarizationService:
    def __init__(self):
        self.pipeline=None
        self.is_ready=False
    
    def load(self):
        if not settings.hf_token:
            print("HuggingFace token not found. Diarization will be disabled.")
            return
        
        print("loading diarization model...")

        self.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=settings.hf_token)
        
        self.pipeline.to(torch.device("cpu"))

        self.is_ready=True
        print("diarization model loaded successfully.")

    def diarize(self, audio: np.ndarray) -> list[dict]:
        if not self.is_ready:
            return [{"start": 0.0, "end": len(audio) / settings.sample_rate, "speaker": 0}]

        try:
            waveform = torch.tensor(audio).unsqueeze(0)

            output = self.pipeline(
                {"waveform": waveform, "sample_rate": settings.sample_rate},
                min_speakers=settings.min_speakers,
                max_speakers=settings.max_speakers,
            )

            speaker_map = {}
            segments = []

            # DiarizeOutput has a .to_annotation() method that returns
            # the old Annotation object with itertracks()
            if hasattr(output, 'to_annotation'):
                annotation = output.to_annotation()
                for turn, _, label in annotation.itertracks(yield_label=True):
                    if label not in speaker_map:
                        speaker_map[label] = len(speaker_map)
                    segments.append({
                        "start": round(turn.start, 3),
                        "end": round(turn.end, 3),
                        "speaker": speaker_map[label],
                    })

            elif hasattr(output, 'itertracks'):
                # Older pyannote — Annotation directly
                for turn, _, label in output.itertracks(yield_label=True):
                    if label not in speaker_map:
                        speaker_map[label] = len(speaker_map)
                    segments.append({
                        "start": round(turn.start, 3),
                        "end": round(turn.end, 3),
                        "speaker": speaker_map[label],
                    })

            else:
                # Last resort — print the type so we know what to handle
                print(f"⚠️  Unknown diarization output type: {type(output)}, attrs: {dir(output)}")

            return segments if segments else [
                {"start": 0.0, "end": len(audio) / settings.sample_rate, "speaker": 0}
            ]

        except Exception as e:
            print(f"⚠️  Diarization failed: {e}")
            return [{"start": 0.0, "end": len(audio) / settings.sample_rate, "speaker": 0}]

diarization_service=DiarizationService()
