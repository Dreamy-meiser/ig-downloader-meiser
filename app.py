from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import os
import uuid
from flask_cors import CORS
from threading import Timer

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
COOKIE_FILE = "cookies.txt"

# Ensure download directory exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route("/")
def home():
    return "Instagram Downloader Backend is running!"

@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Create unique filename
    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        'outtmpl': filepath,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'cookiefile': COOKIE_FILE
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"[✓] Downloaded: {filepath}")

        # Auto-delete the file after 5 minutes
        Timer(300, auto_delete_file, [filepath]).start()

        return jsonify({
            "message": "Download successful",
            "file_url": f"https://ig-downloader-meiser.onrender.com/video/{filename}"
        }), 200

    except Exception as e:
        print(f"[✗] Download failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/video/<filename>")
def serve_video(filename):
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)
    else:
        return jsonify({"error": "❌ This video has expired or was deleted."}), 404

def auto_delete_file(path):
    if os.path.exists(path):
        os.remove(path)
        print(f"[⛔] Auto-deleted expired file: {path}")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
