import os
import subprocess
import re
import yt_dlp
from flask import Flask, request, render_template, send_from_directory
import assemblyai as aai
from datetime import timedelta
from deep_translator import GoogleTranslator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'static/processed'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv'}

aai.settings.api_key = "a00b1c97b4d14896ab21f61deb6d25bd"

def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_youtube_video(url, quality='best', download_path='./downloads'):
    """Download YouTube video using yt-dlp"""
    os.makedirs(download_path, exist_ok=True)
    
    ydl_opts = {
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'format': quality + '[ext=mp4]' if quality != 'best' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        raise RuntimeError(f"YouTube download failed: {e}")

def extract_audio(video_path, audio_output="extracted_audio.mp3"):
    command = ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_output, "-y"]
    subprocess.run(command, check=True)
    return audio_output

def translate_text(text, target_lang='hi'):
    if target_lang == 'en':
        return text  
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception as e:
        print(f"Translation failed: {e}")
        return text

def generate_translated_subtitles(audio_path, output_srt="subtitles.srt", words_per_line=6, language='hi'):
    config = aai.TranscriptionConfig(speaker_labels=True, speakers_expected=2)
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_path, config)

    if transcript.error:
        raise RuntimeError(f"Transcription failed: {transcript.error}")

    srt_content = []
    subtitle_index = 1

    for utterance in transcript.utterances:
        speaker = utterance.speaker
        words = utterance.words

        for i in range(0, len(words), words_per_line):
            chunk = words[i:i + words_per_line]
            start = chunk[0].start
            end = chunk[-1].end
            original_text = " ".join(word.text for word in chunk)
            
            translated_text = translate_text(original_text, language)
            speaker_label = f"Speaker {speaker}"

            srt_content.append(
                f"{subtitle_index}\n"
                f"{format_time(start)} --> {format_time(end)}\n"
                f"[{speaker_label}] {translated_text}\n"
            )
            subtitle_index += 1

    with open(output_srt, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_content))

    return output_srt

def embed_subtitles(video_path, srt_path, output_video):
    command = [
        "ffmpeg", "-i", video_path,
        "-vf", f"subtitles={srt_path}:force_style='Fontsize=24'",
        "-c:a", "copy", output_video, "-y"
    ]
    subprocess.run(command, check=True)
    return output_video

def format_time(ms):
    td = timedelta(milliseconds=ms)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{td.microseconds//1000:03}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video_url = request.form.get("video_url")
        video_file = request.files.get("video_file")
        language = request.form.get("language", "hi")
        quality = request.form.get("quality", "best")

        if video_url:
            try:
                # Download YouTube video
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'youtube_downloads')
                video_path = download_youtube_video(video_url, quality, temp_path)
                filename = os.path.basename(video_path)
            except Exception as e:
                return render_template("index.html", error=str(e))
        elif video_file:
            # Handle file upload
            if video_file.filename == '':
                return render_template("index.html", error="No selected file")
            
            filename = sanitize_filename(video_file.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video_file.save(video_path)
        else:
            return render_template("index.html", error="Please provide either a YouTube URL or upload a file")

        try:
            # Common processing pipeline
            output_filename = f"processed_{os.path.splitext(filename)[0]}.mp4"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            audio_path = extract_audio(video_path)
            srt_path = generate_translated_subtitles(audio_path, language=language)
            embed_subtitles(video_path, srt_path, output_path)
            
            # Cleanup temporary files
            # os.remove(audio_path)
            # os.remove(srt_path)
            # if video_url:
            #     os.remove(video_path)
            
            return render_template("result.html", video_url=output_path, filename=output_filename)
        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True)

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("static/processed", exist_ok=True)
    app.run(debug=True)
    
    
    