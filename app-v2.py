import asyncio
import io
import os
import edge_tts
from flask import Flask, request, send_file, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/health')
def health():
    return {"status": "ok"}, 200

async def generate_tts_mp3(text: str, voice: str, rate: str, pitch: str) -> io.BytesIO:
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
    mp3_buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_buffer.write(chunk["data"])
    mp3_buffer.seek(0)
    return mp3_buffer

@app.route('/api/tts')
def tts():
    text = request.args.get('text', '').strip()
    if not text:
        return 'Falta texto', 400

    voice = request.args.get('voice', 'es-ES-AlvaroNeural')
    rate = request.args.get('rate', '-10%')
    pitch = request.args.get('pitch', '-12Hz')

    try:
        mp3_buffer = asyncio.run(generate_tts_mp3(text, voice, rate, pitch))
        if mp3_buffer.getbuffer().nbytes == 0:
            # Fallback to default voice if custom pitch/rate is rejected by service
            mp3_buffer = asyncio.run(generate_tts_mp3(text, voice, '+0%', '+0Hz'))
        return send_file(mp3_buffer, mimetype="audio/mpeg")
    except Exception as exc:
        app.logger.error(f"TTS error: {exc}")
        return f"Error generando audio: {exc}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
