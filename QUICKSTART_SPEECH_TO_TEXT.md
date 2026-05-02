# 🚀 Quick Start Guide - Speech to Text Feature

## Installation (5 minutes)

### 1. Install Dependencies
```bash
cd "Sign-Language-To-Text-and-Speech-Conversion-master"
pip install -r requirements.txt
```

### 2. Install FFmpeg (for video support)

**Windows:**
- Download from: https://ffmpeg.org/download.html
- Add to PATH

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 3. Run the Application
```bash
python app.py
```

The database will be automatically initialized on first run.

### 4. Access the Feature
1. Open browser: `http://localhost:5000`
2. Login/Signup
3. Click **"Audio to Text"** in navigation

## Usage

### Upload Audio/Video File
1. Click or drag-drop file
2. Supported formats: MP3, WAV, MP4, AVI, etc.
3. Max duration: 2 minutes
4. Click "Process Upload"

### Record Live Audio
1. Click microphone button
2. Allow browser microphone access
3. Speak clearly
4. Click stop when done
5. Click "Process Recording"

### View Results
- Original English transcript
- Automatic translations in Hindi, Tamil, Malayalam
- Duration and word count statistics

## Configuration

### Change Translation Languages

Edit `app.py` line 112:
```python
TRANSLATION_LANGUAGES = {
    'hindi': 'hi',
    'tamil': 'ta',
    'malayalam': 'ml',
    'telugu': 'te',  # Add more languages
}
```

### Change Max Duration

Edit `app.py` line 105:
```python
MAX_AUDIO_DURATION = 120  # Change to desired seconds
```

## Troubleshooting

**"Microphone access denied"**
- Use HTTPS: `python start_https.py`
- Check browser permissions

**"Could not transcribe audio"**
- Ensure clear speech
- Check internet connection
- Try different audio file

**Module errors**
```bash
pip install --upgrade -r requirements.txt
```

## API Upgrade (Optional)

For better accuracy, use OpenAI Whisper:

1. Get API key: https://platform.openai.com/api-keys
2. Set environment variable:
```bash
# Windows
set OPENAI_API_KEY=your-key-here

# Linux/Mac
export OPENAI_API_KEY=your-key-here
```

3. Replace `transcribe_audio()` function in `app.py` with Whisper code (see full documentation)

## Support

See `SPEECH_TO_TEXT_INTEGRATION.md` for complete documentation.
