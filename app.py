from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import os
import uuid
import threading
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
COOKIE_FILE = "cookies.txt"
AUTO_DELETE_SECONDS = 600  # 10 minutes

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Schedule automatic file deletion
def schedule_delete(filepath):
    def delete_file():
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"[AutoDelete] Deleted: {filepath}")
        except Exception as e:
            print(f"[AutoDelete Error] {e}")
    threading.Timer(AUTO_DELETE_SECONDS, delete_file).start()

@app.route("/")
def home():
    return "Instagram Downloader Backend is running!"

@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        'outtmpl': filepath,
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'merge_output_format': 'mp4',
        'cookiefile': COOKIE_FILE
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        schedule_delete(filepath)

        return jsonify({
            "message": "Download successful",
            "file_url": f"/video/{filename}"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/video/<filename>")
def serve_video(filename):
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "❌ This file has expired or been deleted."}), 404
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
