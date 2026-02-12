# Video-To-Text Scripts

This repository contains a collection of Python scripts with a graphical user interface (PyQt6) designed for a full cycle of video processing: from audio extraction to text summarization.

## � Features

### 1. Audio Extractor (`extractor.py`)
A utility for extracting audio tracks from video files. Prepares audio for further recognition.
- **Input Formats:** `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`
- **Output Formats:**
  - `.wav` (PCM 16kHz Mono) — Recommended format for speech recognition.
  - `.mp3` — Compressed format to save space.
- **Key Features:** Automatic conversion of sampling rate and channels.

### 2. Speech Recognizer (`recognizer.py`)
A tool for automatic speech recognition (Speech-to-Text) based on the **Whisper** model.
- **Engine:** `faster-whisper` (optimized version of OpenAI Whisper).
- **Operation Mode:** Local execution on CPU (with `int8` quantization to reduce memory consumption).
- **Input Formats:** `.wav`, `.mp3`, `.m4a`, `.flac`.
- **Output:** A `.txt` file containing the full recognized text.
- **Note:** Currently configured to recognize Russian speech (`language="ru"`).

### 3. Summarizer (`summarizer.py`)
A smart text summarizer using the **YandexGPT** API.
- **Functionality:** Creates a summary of large texts, lectures, or interviews.
- **Key Features:**
  - Automatic slicing of long texts into chunks of 8000 characters.
  - Support for custom system prompts (instructions for the neural network).
  - Operates via the official Yandex Cloud API.
- **Requirements:** You must provide an API Key, Folder ID, and Model URI.

---

## � Installation and Usage

### Prerequisites
To run the scripts, you need Python 3.8+ installed.

### Installing Dependencies
Run the following command in your terminal:
```bash
pip install PyQt6 moviepy faster-whisper requests
```

> **Note:** If you encounter errors with `moviepy`, ensure you have a compatible version installed or check the script's built-in exception handling.

### How to Run

Execute the scripts sequentially depending on your task:

1. **Extract audio from video:**
   ```bash
   python extractor.py
   ```
2. **Recognize text from audio:**
   ```bash
   python recognizer.py
   ```
3. **Generate a summary:**
   ```bash
   python summarizer.py
   ```

---

## 📝 Notes
- To use `summarizer.py`, you need a Yandex Cloud account with a service account that has the `ai.languageModels.user` role.
- The Whisper model (`base`) in `recognizer.py` will be downloaded automatically upon the first run. This may take some time.