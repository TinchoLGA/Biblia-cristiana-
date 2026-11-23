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

@app.route('/api/tts')
async def tts():
    text = request.args.get('text', '').strip()
    if not text:
        return 'Falta texto', 400

    # Voces neuronales masculinas en español:
    # es-ES-AlvaroNeural (España, grave y solemne)
    # es-AR-TomasNeural (Argentina, cálido y profundo)
    # es-MX-JorgeNeural (México, claro y firme)
    voice = request.args.get('voice', 'es-ES-AlvaroNeural')
    rate = request.args.get('rate', '-12%')
    pitch = request.args.get('pitch', '-12Hz')

    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
    mp3_buffer = io.BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_buffer.write(chunk["data"])

    mp3_buffer.seek(0)
    return send_file(mp3_buffer, mimetype="audio/mpeg")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
