import asyncio
import websockets
import sounddevice as sd
import numpy as np
import json

SAMPLE_RATE = 16000
CHUNK_SAMPLES = 480
SERVER_URL = "ws://localhost:8000/ws/audio"   # no trailing slash

async def stream_mic_to_server():
    print("connecting to server...")

    async with websockets.connect(
        SERVER_URL,
        additional_headers={"Origin": "http://localhost:5173"}
    ) as ws:
        print("Connected.")

        msg = await ws.recv()
        print(f"Server: {msg}")

        print("Streaming mic to server... (Ctrl+C to stop)\n")
        print("─" * 50)

        loop = asyncio.get_event_loop()

        def callback(indata, frames, time_info, status):
            chunk = indata[:, 0].astype(np.int16).tobytes()
            asyncio.run_coroutine_threadsafe(ws.send(chunk), loop)

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=CHUNK_SAMPLES,
            callback=callback
        ):
            while True:
                response = await ws.recv()
                data = json.loads(response)
                if data.get("type") == "transcript" and data.get("text"):
                    print(f"[{data['latency_ms']}ms]  {data['text']}")

if __name__ == "__main__":
    try:
        asyncio.run(stream_mic_to_server())
    except KeyboardInterrupt:
        print("done.")