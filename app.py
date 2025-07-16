from flask import Flask, request, jsonify
import os
import uuid
import requests
import yt_dlp
import traceback

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_WHISPER_ENDPOINT = "https://api.openai.com/v1/audio/transcriptions"

def download_audio(youtube_url, filename):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        data = request.get_json()
        youtube_url = data.get("url", "").split("&")[0]
        if not youtube_url:
            return jsonify({"error": "Aucune URL fournie"}), 400

        filename = f"{uuid.uuid4()}.mp3"
        download_audio(youtube_url, filename)

        with open(filename, "rb") as f:
            files = {
                "file": (filename, f, "audio/mpeg")
            }
            data_whisper = {"model": "whisper-1"}
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            response = requests.post(
                OPENAI_WHISPER_ENDPOINT,
                headers=headers,
                data=data_whisper,
                files=files
            )

        os.remove(filename)

        if response.status_code != 200:
            return jsonify({"error": "Whisper API a échoué", "details": response.text}), 500

        transcription = response.json().get("text", "")
        return jsonify({"transcription": transcription})

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route("/test-network")
def test_network():
    try:
        r = requests.get("https://www.youtube.com", timeout=10)
        return jsonify({"status": r.status_code})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
