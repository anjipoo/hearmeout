from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.websocket.audio_handler import handle_audio_stream
from app.services.transcription import transcription_service
from app.websocket.connection_mgr import connection_mgr

@asynccontextmanager
async def lifespan(app: FastAPI):
    transcription_service.load_model()
    print(f"HearMeOut ready at ws://localhost:{settings.port}/ws/audio")
    yield
    print("shutting down HearMeOut...")

app = FastAPI(
    title="HearMeOut",
    lifespan=lifespan,
    description="Real-time audio transcription service.",
    version="1.0.0"
)

# allow_origins=["*"] + allow_credentials=False is the only combo
# that stops Starlette from blocking WebSocket connections from
# origins not in the list (like the Python test client's "http://localhost")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "service": "HearMe AI"}

@app.get("/status")
async def status():
    return {
        "status": "ok",
        "model": settings.model_size,
        "model_ready": transcription_service.is_ready,
        "active_sessions": connection_mgr.connection_count,
        "device": settings.device,
    }

@app.websocket("/ws/audio")
async def websocket_audio(websocket: WebSocket):
    await handle_audio_stream(websocket)