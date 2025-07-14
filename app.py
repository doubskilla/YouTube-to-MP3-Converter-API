from flask import Flask, request, jsonify
import os
import uuid
import subprocess
import requests
import traceback

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
WHISPER_ENDPOINT = "https://api.openai.com/v1/audio/transcriptions"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        data = request.get_json()
        youtube_url = data.get("url")
        if not youtube_url:
            return jsonify({"error": "Aucune URL YouTube fournie"}), 400

        # Téléchargement de l'audio avec yt-dlp
        filename = f"{uuid.uuid4()}.mp3"
        command = [
            "yt-dlp",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "-o", filename,
            youtube_url
        ]
        subprocess.run(command, check=True)

        # Transcription avec Whisper API
        with open(filename, "rb") as audio_file:
            response = requests.post(
                WHISPER_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}"
                },
                data={"model": "whisper-1"},
                files={"file": (filename, audio_file, "audio/mpeg")}
            )

        os.remove(filename)

        if response.status_code != 200:
            return jsonify({"error": "Échec de la transcription", "details": response.text}), 500

        transcription = response.json().get("text", "")
        return jsonify({"transcription": transcription})

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
