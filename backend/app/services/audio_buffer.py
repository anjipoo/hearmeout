import numpy as np
import webrtcvad
from collections import deque
from typing import Optional
from app.config.settings import settings

class AudioBuffer:
    def __init__(self):
        self.vad=webrtcvad.Vad()
        max_frames=settings.frames_per_window+settings.overlap_frames
        self.window:deque=deque(maxlen=max_frames)
        self.speech_flags:deque=deque(maxlen=max_frames)
        self.frames_since_trans=0

    def add_chunk(self, raw_audio:np.ndarray) -> Optional[np.ndarray]:
        frame=np.frombuffer(raw_audio, dtype=np.int16)
        if len(frame)!=settings.chunk_samples:
            return None
        
        has_speech=self._check_speech(frame)
        self.window.append(frame)
        self.speech_flags.append(has_speech)
        self.frames_since_trans+=1

        if self.frames_since_trans<settings.frames_per_window:
            return None
        
        self.frames_since_trans=-settings.overlap_frames

        speech_ratio=sum(self.speech_flags)/len(self.speech_flags)
        if speech_ratio<settings.min_speech_ratio:
            return None
        
        audio=np.concatenate(list(self.window))
        audio_float=audio.astype(np.float32)/32768.0
        return audio_float
    
    def _check_speech(self, frame:np.ndarray) -> bool:
        try:
            return self.vad.is_speech(frame.tobytes(), settings.sample_rate)
        except Exception:
            return False
        
    def reset(self) -> None:
        self.window.clear()
        self.speech_flags.clear()
        self.frames_since_trans=0

        
