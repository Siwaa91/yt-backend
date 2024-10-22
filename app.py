from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

# Function to download a single video from a YouTube link
def download_video(video_url, output_path='.'):
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Best video and audio quality
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Output path and filename
            'merge_output_format': 'mp4',  # Merged output format
        }

        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(video_url)
            video_title = result.get('title', 'video') + '.mp4'
            video_path = os.path.join(output_path, video_title)
        
        return video_path
    except Exception as e:
        return str(e)

# API route to handle video download
@app.route('/download', methods=['POST'])
def download_video_route():
    data = request.json
    video_url = data.get('video_url')
    output_path = data.get('output_path', '.')

    if not video_url:
        return jsonify({'error': 'Video URL is required'}), 400

    video_path = download_video(video_url, output_path)
    
    # Check if download was successful
    if os.path.exists(video_path):
        return send_file(video_path, as_attachment=True)
    else:
        return jsonify({'error': 'Something went wrong with downloading the video'}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
