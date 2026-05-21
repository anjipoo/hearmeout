# HearMeOut

A real-time accessibility assistant that transcribes speech to live captions. Built for interviews, classrooms, meetings, and noisy environments.

---

## What It Does

- Captures microphone audio in the browser
- Streams audio chunks to a local Python backend over WebSocket
- Transcribes speech using OpenAI Whisper (via faster-whisper)
- Displays live captions with timestamps and latency indicators
- Supports dark and light themes

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS v4 |
| Backend | Python, FastAPI, Uvicorn |
| Transcription | faster-whisper (CTranslate2) |
| Voice Activity Detection | webrtcvad |
| Audio Capture | Web Audio API (browser), sounddevice (Python) |
| Communication | WebSocket (binary PCM streaming) |

---

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- A working microphone

### Backend

```bash
cd hearmeout/backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server loads the Whisper model on startup (first run downloads ~140MB). You should see:

```
loading model
model loaded
HearMeOut ready at ws://localhost:8000/ws/audio
INFO: Application startup complete.
```

### Frontend

```bash
cd hearmeout/frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Usage

1. Make sure the backend server is running
2. Open `http://localhost:5173`
3. Click **Start Listening**
4. Allow microphone access when the browser prompts
5. Speak — captions appear within a few seconds
6. Click **Stop** to end the session
7. Use the trash icon to clear captions
8. Toggle 🌙/☀️ to switch between dark and light themes

---

## Configuration

All backend settings are in `backend/app/config/settings.py`:

| Setting | Default | Description |
|---|---|---|
| `model_size` | `"base"` | Whisper model: `tiny`, `base`, `small`, `medium` |
| `device` | `"cpu"` | Use `"cuda"` if you have an NVIDIA GPU |
| `compute_type` | `"int8"` | `"float16"` for GPU |
| `frames_per_window` | `100` | Audio window size (~3 seconds) |
| `overlap_frames` | `20` | Overlap between windows to avoid cut words |
| `vad_aggressiveness` | `1` | 0–3, higher = more silence filtered out |
| `min_speech_ratio` | `0.3` | Minimum speech fraction to trigger transcription |
| `language` | `"en"` | Force language or remove for auto-detect |
| `beam_size` | `3` | Whisper beam search width (higher = more accurate, slower) |

---

## WebSocket Protocol

**Endpoint:** `ws://localhost:8000/ws/audio`

**Client → Server:** Raw binary PCM audio chunks
- Format: Int16, 16kHz, mono
- Chunk size: 480 samples (30ms)

**Server → Client:** JSON messages

```json
// Transcription result
{
  "type": "transcript",
  "text": "Hello, this is a test.",
  "is_final": true,
  "latency_ms": 843,
  "session_id": "a1b2c3d4"
}

// Server ready (sent on connect)
{
  "type": "status",
  "status": "ready",
  "session_id": "a1b2c3d4"
}

// Error
{
  "type": "error",
  "error": "Transcription failed: ...",
  "session_id": "a1b2c3d4"
}
```

---

## Testing Without a Browser

With the backend running, use the CLI test client to verify transcription:

```bash
cd hearmeout/backend
python test.py
```

This streams your microphone directly to the server and prints transcriptions in the terminal.

---

## HTTP Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/status` | Model status, active sessions |
| GET | `/docs` | Auto-generated Swagger UI |
| WS | `/ws/audio` | Audio stream endpoint |

---

## Roadmap

| Phase | Status | Description |
|---|---|---|
| 1 — Local Whisper Test | ✅ Done | Record → transcribe → print |
| 2 — Continuous Streaming | ✅ Done | Real-time audio loop with VAD |
| 3 — FastAPI Backend | ✅ Done | WebSocket server, session management |
| 4 — React Frontend | ✅ Done | Live caption UI, themes, controls |
| 5 — Speaker Diarization | 🔜 Next | Identify who is speaking (pyannote.audio) |
| 6 — Transcript Storage | ⏳ Planned | Save sessions to SQLite |
| 7 — Smart Features | ⏳ Planned | Keyword highlighting, question detection |
| 8 — Summaries | ⏳ Planned | Meeting summaries via LLM |
| 9 — Optimization | ⏳ Planned | Lower latency, ONNX/whisper.cpp |
| 10 — Desktop App | ⏳ Planned | Electron packaging |
