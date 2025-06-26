# 🎥 AI-Powered Video & YouTube Subtitle Translator

This Flask-based web application allows users to upload videos or provide a YouTube URL, extract the audio, transcribe the speech using AssemblyAI (with speaker labels), translate it into a selected language, generate subtitles, and embed them back into the video using FFmpeg.

---

## 🚀 Features

- ✅ Upload your own video or use a YouTube link  
- ✅ Extract and transcribe audio using AssemblyAI  
- ✅ Auto-detect speakers and separate their dialogues  
- ✅ Translate subtitles into multiple languages (Hindi, Telugu, Tamil, Bengali,English)  
- ✅ Embed translated subtitles into the video  
- ✅ Download the final subtitled video  

---

## 🧠 Tech Stack

- **Backend**: Flask (Python)
- **Audio Transcription**: [AssemblyAI](https://www.assemblyai.com/)
- **Translation**: `deep_translator` (Google Translate)
- **Video/Audio Processing**: FFmpeg
- **YouTube Video Downloading**: `yt_dlp`

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/amuqtadir7/SubtitlesGeneration

📂 Folder Structure
├── app.py
├── templates/
│   ├── index.html
│   └── result.html
├── static/
│   └── processed/
├── uploads/
├── downloads/



🧪 Sample Output
https://github.com/user-attachments/assets/957754da-c46b-4358-90d2-4ed89b6f25f1


