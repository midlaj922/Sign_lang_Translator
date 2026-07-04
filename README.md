# Sign Language to Text & Speech Conversion System

A full-stack AI-powered communication system that bridges the gap between deaf/mute individuals and the hearing world through real-time sign language recognition, text-to-speech conversion, and speech-to-text translation.

---

## 🚀 Features

### Sign Language Recognition
- **Real-time ASL Detection**: Recognizes American Sign Language (A-Z) using webcam input
- **CNN-based Classification**: 97% accuracy with 8-group classification strategy
- **MediaPipe Integration**: Robust hand landmark detection in various lighting conditions
- **Background Agnostic**: Works with any background using skeleton-based recognition

### Text-to-Speech
- **Instant Audio Output**: Converts recognized text to speech using pyttsx3
- **Adjustable Speech Rate**: Configurable voice settings for better comprehension

### Speech-to-Text
- **Dual Input Methods**: File upload (audio/video) and live microphone recording
- **Multi-Language Translation**: English to Hindi, Tamil, and Malayalam
- **Video Support**: Extracts audio from video files for transcription
- **Duration Control**: 2-minute maximum recording limit

### User Management
- **Authentication System**: Secure user registration and login
- **Session Management**: Persistent sessions with 7-day expiry
- **History Tracking**: Database-backed speech-to-text history per user

---

## 🏗️ Architecture

**Tech Stack Overview:**
- **Backend**: Flask (REST API)
- **Frontend**: HTML/CSS/JavaScript with Bootstrap
- **Database**: SQLite3
- **Machine Learning**: TensorFlow, Keras, OpenCV
- **Hand Detection**: MediaPipe
- **Speech Processing**: SpeechRecognition, pyttsx3, googletrans
- **Video Processing**: FFmpeg, MoviePy, pydub

---

## 📂 Project Structure

```
SLTTSC/
├── app.py                          # Main Flask application
├── cnn8grps_rad1_model.h5          # Trained CNN model
├── requirements.txt                # Python dependencies
├── users.db                        # SQLite database
├── templates/                      # HTML templates
│   ├── index.html                  # Sign-to-text interface
│   ├── speech_to_text.html         # Speech-to-text interface
│   ├── home.html                   # Dashboard
│   ├── landing.html                # Landing page
│   └── about.html                  # About page
├── static/                         # Static assets (CSS, JS)
├── uploads/                        # User upload directory
└── ssl/                            # SSL certificates
```

---

## ▶️ How to Run

### Prerequisites
- Python 3.9+
- FFmpeg (for video processing)
- Webcam

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd SLTTSC
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install FFmpeg**
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html), add to PATH
- **Linux**: `sudo apt-get install ffmpeg`
- **macOS**: `brew install ffmpeg`

4. **Run the application**
```bash
python app.py
```

5. **Access the application**
- Open browser at `http://localhost:5000`
- For microphone access (HTTPS): `python start_https.py` then visit `https://localhost:5000`

---

## 🧠 Key Concepts Demonstrated

- **Computer Vision**: Hand detection and landmark extraction using MediaPipe
- **Deep Learning**: CNN architecture for gesture classification
- **Image Processing**: Skeleton-based normalization for background independence
- **Natural Language Processing**: Speech recognition and multi-language translation
- **Web Development**: Flask backend with RESTful API design
- **Database Management**: SQLite with user authentication and history tracking
- **Audio Processing**: FFmpeg integration for video-to-audio extraction
- **Real-time Processing**: Threading for non-blocking TTS operations

---

## 📊 Model Architecture

### CNN Classification Strategy
- **Input**: 400x400x3 skeleton images
- **8 Groups**: Similar letters grouped together for better accuracy
  - Group 0: A, E, M, N, S, T
  - Group 1: B, D, F, I, U, V, K, R, W
  - Group 2: C, O
  - Group 3: G, H
  - Group 4: L
  - Group 5: P, Q, Z
  - Group 6: X
  - Group 7: Y, J
- **Secondary Classification**: Geometric analysis of hand landmarks for final letter prediction
- **Accuracy**: 97% (any background), 99% (clean background + good lighting)

---

## 🔧 Configuration

### Change Translation Languages
Edit `app.py` line 116:
```python
TRANSLATION_LANGUAGES = {
    'hindi': 'hi',
    'tamil': 'ta',
    'malayalam': 'ml',
    # Add more: 'telugu': 'te', 'marathi': 'mr'
}
```

### Adjust Maximum Audio Duration
Edit `app.py` line 109:
```python
MAX_AUDIO_DURATION = 300  # Change to 5 minutes
```

### Modify Supported File Types
Edit `app.py` lines 107-108:
```python
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov'}
```

---

## 📝 API Endpoints

### Authentication
- `GET /` - Landing page
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Sign Language Recognition
- `GET /sign-to-text` - Sign-to-text interface
- `POST /predict` - Process webcam frame for gesture prediction
- `POST /speak` - Convert text to speech
- `POST /clear` - Clear current sentence
- `POST /suggestion` - Apply word suggestion

### Speech-to-Text
- `GET /speech-to-text` - Speech-to-text interface
- `POST /process-audio` - Process uploaded audio/video
- `GET /speech-history` - Retrieve user's speech history

---

## 🔒 Security Features

- **Password Hashing**: SHA-256 for secure password storage
- **Session Management**: Secure cookies with HTTPOnly and SameSite
- **File Validation**: Extension whitelist and filename sanitization
- **Authentication Required**: All protected routes use `@require_login` decorator
- **Temporary File Cleanup**: Automatic deletion after processing

---

## 🐛 Troubleshooting

### Microphone Access Denied
- Use HTTPS mode: `python start_https.py`
- Ensure browser permissions allow microphone access

### Hand Detection Issues
- Ensure adequate lighting
- Keep hand within camera frame
- Try different distances from camera

### FFmpeg Errors
- Verify FFmpeg installation
- Add FFmpeg to system PATH
- Restart terminal after installation

### Translation Errors
- Rate limiting on free translation API
- Retry after a moment
- Consider upgrading to paid API for production

---

## 📈 Performance Notes

- **Processing Time**: 2-5 seconds for 1-minute audio
- **Model Inference**: <100ms per frame
- **Accuracy**: 97% average, 99% optimal conditions
- **Supported Languages**: English (input), Hindi/Tamil/Malayalam (output)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- MediaPipe for hand tracking library
- TensorFlow/Keras for deep learning framework
- Google Speech Recognition API
- OpenCV community for computer vision tools

---

## 📞 Contact

For questions or support, please open an issue on GitHub.

---

**Version**: 1.0.0  
**Last Updated**: 2024
