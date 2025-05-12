from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

app = Flask(__name__)
CORS(app)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        data = request.get_json()
        youtube_url = data.get("url")

        if not youtube_url:
            return jsonify({"error": "URL manquante"}), 400

        video_id = extract_video_id(youtube_url)
        if not video_id:
            return jsonify({"error": "ID vidéo non valide"}), 400

        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # essaie de prendre une version traduite si elle existe
        if transcript_list.find_transcript(['fr']):
            transcript = transcript_list.find_transcript(['fr']).fetch()
        else:
            transcript = transcript_list.find_transcript(['en']).fetch()

        text = " ".join([entry['text'] for entry in transcript])

        return jsonify({
            "text": text,
            "language": transcript_list.find_transcript(['fr', 'en']).language_code
        })

    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
        return jsonify({"error": f"Transcription non disponible : {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_video_id(url):
    import re
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
