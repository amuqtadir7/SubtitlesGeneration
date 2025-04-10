import os
import subprocess
import assemblyai as aai
from datetime import timedelta

# Initialize AssemblyAI
aai.settings.api_key = "a00b1c97b4d14896ab21f61deb6d25bd"  # Replace with your key

def extract_audio(video_path, audio_output="extracted_audio.mp3"):
    """Extract audio from video using ffmpeg"""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    command = [
        "ffmpeg",
        "-i", video_path,
        "-q:a", "0",
        "-map", "a",
        audio_output,
        "-y"
    ]
    
    try:
        subprocess.run(command, check=True)
        return audio_output
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed: {e}")

def generate_subtitles(audio_path, output_srt="subtitles.srt", words_per_line=6):
    """Generate SRT subtitles with speaker labels"""
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        speakers_expected=2  # Adjust based on expected speakers
    )
    
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
            
            text = " ".join(word.text for word in chunk)
            speaker_label = f"Speaker {speaker}"
            
            srt_content.append(
                f"{subtitle_index}\n"
                f"{format_time(start)} --> {format_time(end)}\n"
                f"[{speaker_label}] {text}\n"
            )
            subtitle_index += 1
    
    with open(output_srt, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_content))
    
    return output_srt

def embed_subtitles(video_path, srt_path, output_video="output_with_subs.mp4"):
    """Burn subtitles into video using ffmpeg"""
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"subtitles={srt_path}:force_style='Fontsize=24,PrimaryColour=&HFFFFFF&'",
        "-c:a", "copy",
        output_video,
        "-y"
    ]
    
    try:
        subprocess.run(command, check=True)
        return output_video
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg subtitle embedding failed: {e}")

def format_time(ms):
    """Convert milliseconds to SRT time format"""
    td = timedelta(milliseconds=ms)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{td.microseconds//1000:03}"

if __name__ == "__main__":
    # Input video file (replace with your file)
    input_video = "Python Exercises for Beginners - Exercise #1.mp4"
    
    try:
        print("Extracting audio...")
        audio_file = extract_audio(input_video)
        
        print("Generating subtitles...")
        srt_file = generate_subtitles(audio_file)
        
        print("Embedding subtitles into video...")
        output_video = embed_subtitles(input_video, srt_file)
        
        print(f"Done! Output video: {output_video}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up temporary files
        if os.path.exists("extracted_audio.mp3"):
            os.remove("extracted_audio.mp3")