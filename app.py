from flask import Flask, request, jsonify
import os
import uuid
import requests
import traceback

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_WHISPER_ENDPOINT = "https://api.openai.com/v1/audio/transcriptions"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        print("🚀 Requête reçue dans /transcribe")

        # Vérifie qu'un fichier a été uploadé
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier MP3 reçu."}), 400

        file = request.files['file']
        if file.filename == "":
            return jsonify({"error": "Nom de fichier vide."}), 400

        # Sauvegarde temporairement le fichier
        filename = f"{uuid.uuid4()}.mp3"
        file.save(filename)
        print("✅ Fichier reçu et sauvegardé :", filename)

        # Envoi à OpenAI Whisper API
        with open(filename, "rb") as f:
            files = {
                "file": (filename, f, "audio/mpeg")
            }
            data_whisper = {
                "model": "whisper-1"
            }
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            response = requests.post(
                OPENAI_WHISPER_ENDPOINT,
                headers=headers,
                data=data_whisper,
                files=files
            )

        # Supprime le fichier temporaire
        os.remove(filename)

        # Vérifie la réponse de l'API
        if response.status_code != 200:
            print("❌ Whisper API a échoué :", response.text)
            return jsonify({
                "error": "Whisper API a échoué",
                "details": response.text
            }), 500

        transcription = response.json().get("text", "")
        print("📝 Transcription terminée !")
        return jsonify({"transcription": transcription})

    except Exception as e:
        traceback_str = traceback.format_exc()
        print("❌ ERREUR :", traceback_str)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
