# Speech to Text Feature - Integration Guide

## 📋 Overview

This document provides comprehensive instructions for integrating and using the **Speech to Text** feature in your Sign Language Recognition web application.

## ✨ Features Implemented

### 1. **Dual Input Methods**
   - **File Upload**: Support for audio (MP3, WAV, OGG, M4A, FLAC, AAC, WMA) and video files (MP4, AVI, MOV, MKV, WMV, FLV, WEBM)
   - **Live Recording**: Browser-based microphone recording with real-time timer
   - **Duration Limit**: Maximum 2 minutes for both upload and recording

### 2. **Speech Recognition**
   - Uses Google Speech Recognition API (free, no API key required)
   - Automatic audio extraction from video files
   - Clear error handling for unclear audio

### 3. **Multi-Language Translation**
   - Original English transcript
   - Automatic translation to:
     - **Hindi (हिंदी)**
     - **Tamil (தமிழ்)**
     - **Malayalam (മലയാളം)**
   - Easily configurable for additional languages

### 4. **Database Storage**
   - All transcriptions and translations saved to database
   - User-specific history tracking
   - Audio duration logging

### 5. **User Interface**
   - Modern, responsive design
   - Drag-and-drop file upload
   - Real-time recording timer
   - Progress indicators
   - Statistics display (duration, word count, languages)

---

## 🚀 Installation & Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**New packages added:**
- `openai==1.3.5` - For potential future OpenAI Whisper integration
- `moviepy==1.0.3` - Video processing and audio extraction
- `pydub==0.25.1` - Audio file manipulation
- `googletrans==4.0.0rc1` - Translation service
- `SpeechRecognition==3.10.0` - Speech-to-text conversion

### Step 2: System Dependencies

**For Windows (already likely installed):**
```bash
# Usually no additional dependencies needed
```

**For Linux:**
```bash
sudo apt-get install ffmpeg
sudo apt-get install portaudio19-dev python3-pyaudio
```

**For macOS:**
```bash
brew install ffmpeg
brew install portaudio
```

### Step 3: Initialize Database

The database table is automatically created when you run the application. The following table is added:

```sql
CREATE TABLE IF NOT EXISTS speech_to_text_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    original_text TEXT NOT NULL,
    hindi_translation TEXT,
    tamil_translation TEXT,
    malayalam_translation TEXT,
    audio_duration REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### Step 4: Run the Application

```bash
python app.py
```

Or with HTTPS (recommended for microphone access):

```bash
python start_https.py
```

---

## 📁 File Structure

```
project/
├── app.py                          # Backend with new routes added
├── requirements.txt                # Updated with new dependencies
├── templates/
│   ├── home.html                   # Updated navigation
│   ├── speech_to_text.html        # NEW: Main feature page
│   ├── index.html                  # Existing sign-to-text page
│   ├── about.html
│   ├── login.html
│   └── signup.html
├── uploads/                        # NEW: Auto-created for temp files
├── users.db                        # Updated with new table
└── SPEECH_TO_TEXT_INTEGRATION.md  # This file
```

---

## 🔧 Configuration

### Changing Translation Languages

Edit the `TRANSLATION_LANGUAGES` dictionary in `app.py`:

```python
TRANSLATION_LANGUAGES = {
    'hindi': 'hi',
    'tamil': 'ta',
    'malayalam': 'ml'
}
```

**Available language codes (examples):**
- `'hi'` - Hindi
- `'ta'` - Tamil
- `'ml'` - Malayalam
- `'te'` - Telugu
- `'mr'` - Marathi
- `'gu'` - Gujarati
- `'kn'` - Kannada
- `'bn'` - Bengali
- `'pa'` - Punjabi

To add more languages, simply add entries to the dictionary:

```python
TRANSLATION_LANGUAGES = {
    'hindi': 'hi',
    'tamil': 'ta',
    'malayalam': 'ml',
    'telugu': 'te',        # Added
    'marathi': 'mr'        # Added
}
```

Then update the frontend template (`speech_to_text.html`) to display the new translations:

```html
<div class="translation-box">
    <h5>🇮🇳 Telugu (తెలుగు)</h5>
    <p id="teluguTranslation"></p>
</div>
```

And update the JavaScript:

```javascript
document.getElementById('teluguTranslation').textContent = result.translations.telugu;
```

### Changing Maximum Duration

Edit `MAX_AUDIO_DURATION` in `app.py` (in seconds):

```python
MAX_AUDIO_DURATION = 120  # 2 minutes (default)
# Change to 300 for 5 minutes, etc.
```

Also update the frontend JavaScript timer limit in `speech_to_text.html`:

```javascript
// Auto-stop at 2 minutes
if (elapsed >= 120) {  // Change this value
    stopRecording();
    showAlert('Maximum recording duration (2 minutes) reached.', 'error');
}
```

---

## 🔌 API Endpoints

### 1. GET `/speech-to-text`
**Description**: Renders the Speech to Text page  
**Auth**: Required (login)  
**Response**: HTML page

### 2. POST `/process-audio`
**Description**: Process uploaded file or recorded audio  
**Auth**: Required (login)

**Request (File Upload)**:
```
Content-Type: multipart/form-data
Body: {
    audio_file: <file>
}
```

**Request (Recording)**:
```json
Content-Type: application/json
{
    "audio_data": "data:audio/wav;base64,UklGRi4AAABXQVZFZm10..."
}
```

**Response (Success)**:
```json
{
    "success": true,
    "original_text": "Hello, how are you?",
    "translations": {
        "hindi": "नमस्ते, आप कैसे हैं?",
        "tamil": "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?",
        "malayalam": "ഹലോ, നിങ്ങൾ എങ്ങനെയാണ്?"
    },
    "duration": 2.5
}
```

**Response (Error)**:
```json
{
    "success": false,
    "message": "Audio duration (130.5s) exceeds maximum allowed duration of 120s (2 minutes)"
}
```

### 3. GET `/speech-history`
**Description**: Get user's transcription history  
**Auth**: Required (login)

**Response**:
```json
{
    "success": true,
    "history": [
        {
            "original_text": "Hello world",
            "hindi_translation": "नमस्कार विश्व",
            "tamil_translation": "வணக்கம் உலகம்",
            "malayalam_translation": "ഹലോ ലോകം",
            "duration": 1.2,
            "created_at": "2024-11-01 17:30:45"
        }
    ]
}
```

---

## 🎨 Frontend Components

### Main Elements

1. **Upload Area**
   - Drag-and-drop interface
   - File type validation
   - File info display

2. **Recording Controls**
   - Microphone button with visual feedback
   - Real-time timer
   - Auto-stop at max duration

3. **Results Display**
   - Statistics bar (duration, word count, languages)
   - Original transcript
   - Translation cards for each language

4. **Progress Indicators**
   - Loading spinner during processing
   - Alert messages (success/error)

---

## 🔒 Security Considerations

### 1. File Upload Security
- Uses `secure_filename()` to sanitize filenames
- File extension validation
- Temporary files are deleted after processing

### 2. User Authentication
- All routes protected with `@require_login` decorator
- User-specific data storage

### 3. Data Privacy
- Transcriptions stored in user's account
- No external API keys required for basic functionality
- Files processed locally on server

---

## 🌐 Using Alternative AI APIs

### Option 1: OpenAI Whisper API (Recommended for Production)

**Pros**: Higher accuracy, better noise handling, multiple languages  
**Cons**: Requires API key, costs money

**Implementation**:

1. Install additional dependency:
```bash
pip install openai
```

2. Get API key from https://platform.openai.com/api-keys

3. Replace the `transcribe_audio()` function in `app.py`:

```python
import openai

openai.api_key = "your-api-key-here"  # Use environment variable in production

def transcribe_audio(audio_path):
    try:
        with open(audio_path, 'rb') as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
        return transcript.text
    except Exception as e:
        print(f"Whisper API error: {e}")
        return None
```

### Option 2: AssemblyAI

**Pros**: Good accuracy, real-time capabilities  
**Cons**: Requires API key, costs money

```python
import assemblyai as aai

aai.settings.api_key = "your-api-key"

def transcribe_audio(audio_path):
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_path)
    return transcript.text if transcript.status == aai.TranscriptStatus.completed else None
```

### Option 3: Google Cloud Speech-to-Text

**Pros**: High accuracy, many languages  
**Cons**: Requires Google Cloud setup, costs money

```python
from google.cloud import speech

def transcribe_audio(audio_path):
    client = speech.SpeechClient()
    
    with open(audio_path, 'rb') as audio_file:
        content = audio_file.read()
    
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
    )
    
    response = client.recognize(config=config, audio=audio)
    
    for result in response.results:
        return result.alternatives[0].transcript
    return None
```

---

## 🐛 Troubleshooting

### Issue 1: "Microphone access denied"
**Solution**: 
- Use HTTPS (required by browsers for mic access)
- Check browser permissions
- Run: `python start_https.py` instead of `python app.py`

### Issue 2: "Could not transcribe audio"
**Solutions**:
- Ensure audio contains clear speech
- Check microphone volume
- Try a different audio file
- Verify internet connection (Google API requires it)

### Issue 3: "Translation error"
**Solutions**:
- Check internet connection
- Try again (free API sometimes rate-limits)
- Consider implementing retry logic

### Issue 4: "Failed to extract audio from video"
**Solutions**:
- Ensure `ffmpeg` is installed
- Check video file isn't corrupted
- Try a different video format

### Issue 5: Module not found errors
**Solution**:
```bash
pip install --upgrade -r requirements.txt
```

---

## 📊 Database Schema Reference

```sql
-- New table added
speech_to_text_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,           -- Links to users table
    original_text TEXT,        -- English transcript
    hindi_translation TEXT,    -- Hindi translation
    tamil_translation TEXT,    -- Tamil translation
    malayalam_translation TEXT,-- Malayalam translation
    audio_duration REAL,       -- Duration in seconds
    created_at TIMESTAMP       -- Automatic timestamp
)
```

---

## 🎯 Usage Examples

### Example 1: Upload Audio File

1. Navigate to `/speech-to-text`
2. Click or drag-drop an MP3/WAV file
3. Click "Process Upload"
4. View results with translations

### Example 2: Record Live Audio

1. Navigate to `/speech-to-text`
2. Click the microphone button
3. Speak clearly (max 2 minutes)
4. Click stop button (or wait for auto-stop)
5. Click "Process Recording"
6. View results with translations

### Example 3: Upload Video File

1. Navigate to `/speech-to-text`
2. Upload an MP4/AVI video file
3. System automatically extracts audio
4. Click "Process Upload"
5. View results

---

## 🔄 Future Enhancements

### Potential Improvements

1. **Offline Speech Recognition**
   - Use Vosk or Mozilla DeepSpeech for offline capability
   
2. **More Languages**
   - Add support for 10+ Indian languages
   - Configure via admin panel

3. **Speaker Diarization**
   - Identify different speakers in audio

4. **Sentiment Analysis**
   - Analyze emotion/sentiment in speech

5. **Export Functionality**
   - Export transcripts as PDF/DOCX
   - Download audio/video files

6. **Real-time Streaming**
   - Live transcription during recording

7. **Custom Vocabulary**
   - Add domain-specific terms for better accuracy

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the code comments in `app.py`
3. Test with different audio files
4. Verify all dependencies are installed

---

## 📝 License

This feature integrates with your existing Sign Language Recognition project and follows the same license terms.

---

**Last Updated**: November 2024  
**Version**: 1.0.0  
**Author**: AI Assistant (Cascade)
