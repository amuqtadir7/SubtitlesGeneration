import os
import subprocess
import assemblyai as aai
from datetime import timedelta
from deep_translator import GoogleTranslator


aai.settings.api_key = "a00b1c97b4d14896ab21f61deb6d25bd"  

def extract_audio(video_path, audio_output="extracted_audio.mp3"):
    """Extract audio from video using ffmpeg"""
    command = [
        "ffmpeg",
        "-i", video_path,
        "-q:a", "0",
        "-map", "a",
        audio_output,
        "-y"
    ]
    subprocess.run(command, check=True)
    return audio_output

def translate_text(text, target_lang='hi'):
    """Translate text to target Indian language"""
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception as e:
        print(f"Translation failed: {e}")
        return text  # Fallback to original text

def generate_translated_subtitles(audio_path, output_srt="subtitles.srt", 
                                words_per_line=6, language='hi'):
    """Generate translated SRT subtitles with speaker labels"""
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        speakers_expected=2
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
            
            # Original English text
            original_text = " ".join(word.text for word in chunk)
            
            # Translated text
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

def embed_subtitles(video_path, srt_path, output_video="output_with_subs.mp4"):
    """Burn subtitles into video"""
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"subtitles={srt_path}:force_style='Fontsize=24'",
        "-c:a", "copy",
        output_video,
        "-y"
    ]
    subprocess.run(command, check=True)
    return output_video

def format_time(ms):
    """Convert milliseconds to SRT time format"""
    td = timedelta(milliseconds=ms)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{td.microseconds//1000:03}"

if __name__ == "__main__":
    # Input video file
    input_video = "Python Exercises for Beginners - Exercise #1.mp4"
    
    # Target Indian language (hi=Hindi, ta=Tamil, te=Telugu, etc.)
    target_language = "hi"  
    
    try:
        print("Extracting audio...")
        audio_file = extract_audio(input_video)
        
        print("Generating translated subtitles...")
        srt_file = generate_translated_subtitles(audio_file, language=target_language)
        
        print("Embedding subtitles...")
        output_video = embed_subtitles(input_video, srt_file)
        
        print(f"Done! Output video: {output_video}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists("extracted_audio.mp3"):
            os.remove("extracted_audio.mp3")