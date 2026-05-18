import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
import os

SAMPLE_RATE = 16000
DURATION = 10  #in seconds
CHANNELS = 1
OUTPUT_FILE = "output.wav"
MODEL="base"
DEVICE="cpu"
COMPUTE_TYPE="int8"

def record_audio(duration:int, sample_rate:int, channels:int) -> np.ndarray:
    print(f"recording for {duration} seconds...")
    audio_data=sd.rec(frames=duration*sample_rate, samplerate=sample_rate,channels=channels, dtype="int16")
    sd.wait()
    print("recording complete.")
    return audio_data

def save_audio(audio_data: np.ndarray, sample_rate: int, filepath: str):
    write(filepath, sample_rate, audio_data)
    file_size_kb=os.path.getsize(filepath) / 1024
    print(f"audio saved to {filepath} ({file_size_kb:.2f} KB)")

def load_model(model_size: str, device:str, compute_type:str) -> WhisperModel:
    print(f"loading whisper model... {model_size} on {device}")
    model=WhisperModel(model_size, device=device, compute_type=compute_type)
    print("model loaded")
    return model

def transcribe_audio(model: WhisperModel, audio_path: str) -> None:
    print(f"transcribing audio from {audio_path}...")
    segments, info=model.transcribe(audio_path, beam_size=5, language="en", vad_parameters=dict(min_silence_duration_ms=500), vad_filter=True)
    print(f"detected language: {info.language} (confidence: {info.language_probability:.0%})\n")

    full_text=[]
    for s in segments:
        timestamp=f"[{s.start:.1f}s -> {s.end:.1f}s]"
        text=s.text.strip()
        print(f"{timestamp} {text}")
        full_text.append(text)
    
    print(f"full transcription:\n{' '.join(full_text)}")

def main():
    audio_data=record_audio(DURATION, SAMPLE_RATE, CHANNELS)
    save_audio(audio_data, SAMPLE_RATE, OUTPUT_FILE)
    model=load_model(MODEL, DEVICE, COMPUTE_TYPE)
    transcribe_audio(model, OUTPUT_FILE)

if __name__=="__main__":
    main()