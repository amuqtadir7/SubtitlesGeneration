import assemblyai as aai
import os
from datetime import timedelta

# Initialize with your API key
aai.settings.api_key = "a00b1c97b4d14896ab21f61deb6d25bd"  # Replace with your actual key

def format_time(ms):
    """Convert milliseconds to SRT time format"""
    td = timedelta(milliseconds=ms)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{td.microseconds//1000:03}"

def generate_subtitles(audio_file, output_file="output.srt", words_per_line=6):
    """
    Generate subtitles with speaker labels
    """
    # Configure transcription
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        speakers_expected=1  # Adjust based on expected number of speakers
    )
    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file, config)
    
    if transcript.error:
        print(f"Error: {transcript.error}")
        return
    
    # Speaker colors (optional)
    speaker_colors = {
        "A": "#FF5733",
        "B": "#33FF57",
        "C": "#3357FF"
    }
    
    # Generate SRT content
    srt_content = []
    subtitle_index = 1
    
    for utterance in transcript.utterances:
        speaker = utterance.speaker
        words = utterance.words
        
        # Split into chunks of words_per_line
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
    
    # Save to file
    with open(output_file, "w") as f:
        f.write("\n".join(srt_content))
    
    print(f"Subtitles saved to {output_file}")

if __name__ == "__main__":
    # Example usage
    generate_subtitles(
        audio_file="WhatsApp.mp3",
        output_file="whatsapp_subtitles.srt",
        words_per_line=6
    )