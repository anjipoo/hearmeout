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

    def diarize(self, audio:np.ndarray)->list[dict]:
        if not self.is_ready:
            return [{"start": 0.0, "end": len(audio) / settings.sample_rate, "speaker": 0}]
        
        waveform=torch.from_numpy(audio).float().unsqueeze(0)
        input_dict={"waveform": waveform, "sample_rate": settings.sample_rate}

        diarization:Annotation=self.pipeline(input_dict, min_speakers=settings.min_speakers, max_speakers=settings.max_speakers)

        settings_map={}
        segments=[]

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            if speaker not in settings_map:
                settings_map[speaker]=len(settings_map)
            
            segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": settings_map[speaker]
            })

        return segments if segments else [{"start": 0.0, "end": len(audio) / settings.sample_rate, "speaker": 0}]
    

diarization_service=DiarizationService()
