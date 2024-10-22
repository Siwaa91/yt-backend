from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)

# Allow only the specific frontend origin
CORS(app, resources={r"/download": {"origins": "https://youtube-downloader21.netlify.app"}})

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the YouTube Video Downloader API! Use the /download endpoint to download videos."})

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.json.get('url')
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Ensure the downloads directory exists
        os.makedirs('downloads', exist_ok=True)

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': './downloads/%(title)s.%(ext)s',
            'merge_output_format': 'mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_file = f"./downloads/{info['title']}.{info['ext']}"
            return send_file(video_file, as_attachment=True)

    except yt_dlp.utils.DownloadError as e:
        error_message = str(e)
        if "Sign in to confirm you’re not a bot" in error_message:
            return jsonify({"error": "This video requires sign-in or CAPTCHA verification. Please download manually from YouTube."}), 403
        else:
            return jsonify({"error": "An error occurred while downloading the video."}), 500

    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
