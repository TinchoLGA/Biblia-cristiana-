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

    mp3_buffer = asyncio.run(generate_tts_mp3(text, voice, rate, pitch))
    return send_file(mp3_buffer, mimetype="audio/mpeg")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
