from fastapi import WebSocket, WebSocketDisconnect
from app.services.audio_buffer import AudioBuffer
from app.websocket.connection_mgr import connection_mgr
from app.models.transcript import TranscriptMessage, StatusMessage, ErrorMessage
from app.services.transcription import transcription_service
from app.services.diarization import diarization_service
from app.services.merger import assign_speakers


async def handle_audio_stream(websocket: WebSocket):
    session_id = await connection_mgr.connect(websocket)
    buffer = AudioBuffer()

    await connection_mgr.send_message(
        session_id,
        StatusMessage(status="ready", session_id=session_id).model_dump_json()
    )

    try:
        while True:
            raw = await websocket.receive_bytes()
            audio_window = buffer.add_chunk(raw)

            if audio_window is None:
                continue

            try:
                full_text, latency_ms, transcript_segments = transcription_service.trans(audio_window)
            except Exception as e:
                await connection_mgr.send_message(
                    session_id,
                    ErrorMessage(error=str(e), session_id=session_id).model_dump_json()
                )
                continue

            if not full_text:
                continue

            # Run diarization if enabled
            speaker = 0
            if diarization_service.is_ready and transcript_segments:
                speaker_segments = diarization_service.diarize(audio_window)
                merged = assign_speakers(transcript_segments, speaker_segments)
                # Use the speaker of the first segment as the dominant speaker
                # Phase 6 will send per-segment results
                speaker = merged[0]["speaker"] if merged else 0

            await connection_mgr.send_message(
                session_id,
                TranscriptMessage(
                    text=full_text,
                    is_final=True,
                    latency_ms=latency_ms,
                    session_id=session_id,
                    speaker=speaker,
                ).model_dump_json()
            )

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"session {session_id} error: {e}")
    finally:
        buffer.reset()
        connection_mgr.disconnect(session_id)