from flask import Flask, request, jsonify
import os
import uuid
import requests
import traceback

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
WHISPER_ENDPOINT = "https://api.openai.com/v1/audio/transcriptions"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        print("📥 Fichier reçu")
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400

        audio_file = request.files['file']
        filename = f"{uuid.uuid4()}.mp3"
        audio_file.save(filename)
        print("✅ Audio sauvegardé :", filename)

        print("📤 Envoi vers Whisper...")
        with open(filename, "rb") as f:
            files = {
                "file": (filename, f, "audio/mpeg")
            }
            data = {
                "model": "whisper-1"
            }
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            response = requests.post(
                WHISPER_ENDPOINT,
                headers=headers,
                data=data,
                files=files
            )

        os.remove(filename)

        if response.status_code != 200:
            print("❌ Whisper API erreur :", response.text)
            return jsonify({"error": "Whisper API a échoué", "details": response.text}), 500

        transcription = response.json().get("text", "")
        return jsonify({"transcription": transcription})

    except Exception as e:
        print("❌ ERREUR GÉNÉRALE :", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "API de transcription active"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
