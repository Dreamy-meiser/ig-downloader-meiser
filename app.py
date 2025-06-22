from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import os
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Folder where downloaded videos will be stored
DOWNLOAD_FOLDER = "downloads"
COOKIE_FILE = "cookies.txt"  # Make sure this is in Netscape format and in the same directory

# Create folder if it doesn't exist
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

    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        'outtmpl': filepath,
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'merge_output_format': 'mp4',
        'cookiefile': COOKIE_FILE  # <-- This is the correct setting
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return jsonify({
            "message": "Download successful",
            "file_url": f"/video/{filename}"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/video/<filename>")
def serve_video(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
