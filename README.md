# Sign Language to Text & Speech Conversion System

A full-stack AI-powered communication system that bridges the gap between deaf/mute individuals and the hearing world through real-time sign language recognition, text-to-speech conversion, and speech-to-text translation.

---

## 🚀 Features
- Real-time American Sign Language (A-Z) recognition using webcam
- CNN-based classification with 97% accuracy
- MediaPipe hand landmark detection for various lighting conditions
- Background-agnostic skeleton-based recognition
- Text-to-speech conversion using pyttsx3
- Speech-to-text with file upload and live microphone recording
- Multi-language translation (English to Hindi, Tamil, Malayalam)
- Video audio extraction for transcription
- User authentication with session management
- Database-backed history tracking

---

## 🏗️ Architecture

**Tech Stack Overview:**
- Backend: Flask (REST API)
- Frontend: HTML/CSS/JavaScript with Bootstrap
- Database: SQLite3
- Machine Learning: TensorFlow, Keras, OpenCV
- Hand Detection: MediaPipe
- Speech Processing: SpeechRecognition, pyttsx3, googletrans
- Video Processing: FFmpeg, MoviePy, pydub

---

## 📂 Project Structure
```
SLTTSC/
├── app.py                          # Main Flask application
├── cnn8grps_rad1_model.h5          # Trained CNN model
├── requirements.txt                # Python dependencies
├── templates/                      # HTML templates
│   ├── index.html                  # Sign-to-text interface
│   ├── speech_to_text.html         # Speech-to-text interface
│   ├── home.html                   # Dashboard
│   ├── landing.html                # Landing page
│   └── about.html                  # About page
├── static/                         # Static assets (CSS, JS)
└── uploads/                        # User upload directory
```

---

## ▶️ How to Run

### Installation
```bash
git clone <repository-url>
cd SLTTSC
pip install -r requirements.txt
```

### Install FFmpeg (for video processing)
- Windows: Download from ffmpeg.org, add to PATH
- Linux: `sudo apt-get install ffmpeg`
- macOS: `brew install ffmpeg`

### Run Application
```bash
python app.py
```

Access at `http://localhost:5000` or `https://localhost:5000` for microphone access.

## 🧠 Key Concepts Demonstrated

- Computer Vision with MediaPipe hand detection
- Deep Learning CNN architecture for gesture classification
- Skeleton-based normalization for background independence
- Natural Language Processing with speech recognition and translation
- Flask RESTful API design
- SQLite database with user authentication
- FFmpeg integration for video-to-audio extraction
- Real-time processing with threading
