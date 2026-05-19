import sounddevice as sd
import numpy as np
import queue
import threading
import time
import webrtcvad
from faster_whisper import WhisperModel
from collections import deque

SAMPLE_RATE=16000
CHUNK=30
CHUNK_SAMPLES=int(SAMPLE_RATE*CHUNK/1000)

FRAMES_PER_WINDOW=50
OVERLAP_FRAMES=10
VAD_AGGRESSIVENESS=2
MIN_SPEECH_RATIO=0.4

MODEL_SIZE="base"
DEVICE="cpu"
COMPUTE_TYPE="int8"

audio_queue:queue.Queue=queue.Queue()
stop_event=threading.Event()

def create_vad() -> webrtcvad.Vad:
    vad=webrtcvad.Vad()
    vad.set_mode(VAD_AGGRESSIVENESS)
    return vad

def speech(vad: webrtcvad.Vad, frames: np.ndarray) -> bool:
    frame_bytes=frames.astype(np.int16).tobytes()
    try:
        return vad.is_speech(frame_bytes, SAMPLE_RATE)
    except Exception:
        return False
    
def audio_callback(indata:np.ndarray, frames:int, time_info, status) -> None:
    if status:
        print(f"Audio callback status: {status}")
    audio_queue.put(indata[:,0].copy())

def transcribe(model:WhisperModel) -> None:
    vad=create_vad()
    window:deque=deque(maxlen=FRAMES_PER_WINDOW+OVERLAP_FRAMES)
    speech_flags:deque=deque(maxlen=FRAMES_PER_WINDOW+OVERLAP_FRAMES)
    frames_collected=0

    print("listening (ctrl+c to stop)...")
    while not stop_event.is_set():
        try:
            frame=audio_queue.get(timeout=0.5)
        except queue.Empty:
            continue

        has_speech=speech(vad, frame)
        window.append(frame)
        speech_flags.append(has_speech)
        frames_collected+=1

        if frames_collected<FRAMES_PER_WINDOW:
            continue

        frames_collected=-OVERLAP_FRAMES

        speech_ratio=sum(speech_flags)/len(speech_flags)
        if speech_ratio<MIN_SPEECH_RATIO:
            continue

        audio_window=np.concatenate(list(window))
        transcribe_window(model, audio_window)

def transcribe_window(model:WhisperModel, audio:np.ndarray) -> None:
    audio_float=audio.astype(np.float32)/32768.0
    start_time=time.time()
    segments, info=model.transcribe(audio_float, beam_size=5, language="en", without_timestamps=True, condition_on_previous_text=False, vad_filter=False)
    text_parts=[s.text.strip() for s in segments if s.text.strip()]

    if not text_parts:
        return
    
    elapsed_time=time.time()-start_time
    full_text=" ".join(text_parts)

    lag_indic="💚" if elapsed_time<1.0 else "💛" if elapsed_time<2.0 else "🖤"
    print(f"{lag_indic} [{elapsed_time:.2f}s] {full_text}")

def load_model() -> WhisperModel:
    print(f"loading whisper '{MODEL_SIZE}' model...")
    model=WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    print("model loaded.")
    return model

def main():
    model=load_model()
    stream=sd.InputStream(samplerate=SAMPLE_RATE, channels=1, blocksize=CHUNK_SAMPLES, callback=audio_callback,dtype="int16")

    try:
        with stream:
            transcribe(model)
    except KeyboardInterrupt:
        print("stopping...")
        stop_event.set()
        print("stopped.")

if __name__=="__main__":
    main()