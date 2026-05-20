from fastapi import WebSocket, WebSocketDisconnect
from app.services.audio_buffer import AudioBuffer
from app.websocket.connection_mgr import connection_mgr
from app.models.transcript import TranscriptMessage, StatusMessage, ErrorMessage

async def handle_audio_stream(websocket: WebSocket):
    session_id=await connection_mgr.connect(websocket)
    buffer=AudioBuffer()
    await connection_mgr.send_message(session_id, StatusMessage(status="ready", session_id=session_id).model_dump())
    try:
        while True:
            raw=await websocket.receive_bytes()
            audio_window=buffer.add_audio(raw)
            if audio_window is None:
                continue

            try:
                text, timestamp=buffer.transcribe_window(audio_window)
            except Exception as e:
                await connection_mgr.send_message(session_id, ErrorMessage(error=str(e)).model_dump())
                continue

            if not text:
                continue

            await connection_mgr.send_message(session_id, TranscriptMessage(text=text, is_final=True, latency_ms=timestamp, session_id=session_id).model_dump())

    except WebSocketDisconnect:
        pass

    except Exception as e:
        print(f"session {session_id} error: {e}")

    finally:
        buffer.reset()
        connection_mgr.disconnect(session_id)
