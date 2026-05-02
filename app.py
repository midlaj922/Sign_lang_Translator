from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
import numpy as np
import math
import cv2
import os
import base64
import io
from PIL import Image
import pyttsx3
from keras.models import load_model
from cvzone.HandTrackingModule import HandDetector
from string import ascii_uppercase
import enchant
import threading
import time
import sqlite3
import hashlib
import secrets
from werkzeug.utils import secure_filename
import speech_recognition as sr
from googletrans import Translator
from pydub import AudioSegment
import tempfile
import subprocess
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Generate secure random secret key
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session expires after 7 days
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
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
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Authentication helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    return hash_password(password) == password_hash

def is_logged_in():
    return 'user_id' in session

def require_login(f):
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Initialize global variables
ddd = enchant.Dict("en-US")
hd = HandDetector(maxHands=1)
hd2 = HandDetector(maxHands=1)
offset = 29

# Load the model
model = load_model('cnn8grps_rad1_model.h5')

# Initialize text-to-speech engine
speak_engine = None
def get_tts_engine():
    global speak_engine
    if speak_engine is None:
        speak_engine = pyttsx3.init()
        speak_engine.setProperty("rate", 100)
        voices = speak_engine.getProperty("voices")
        if voices:
            speak_engine.setProperty("voice", voices[0].id)
    return speak_engine

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac', 'wma'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}
MAX_AUDIO_DURATION = 120  # 2 minutes in seconds

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Translation language configuration
TRANSLATION_LANGUAGES = {
    'hindi': 'hi',
    'tamil': 'ta',
    'malayalam': 'ml'
}

def allowed_file(filename, file_type='audio'):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'audio':
        return ext in ALLOWED_AUDIO_EXTENSIONS
    elif file_type == 'video':
        return ext in ALLOWED_VIDEO_EXTENSIONS
    return ext in ALLOWED_AUDIO_EXTENSIONS or ext in ALLOWED_VIDEO_EXTENSIONS

def get_audio_duration(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000.0  # Convert to seconds
    except:
        return 0

def extract_audio_from_video(video_path):
    try:
        audio_path = video_path.rsplit('.', 1)[0] + '_extracted.wav'
        command = [
            'ffmpeg',
            '-y',
            '-i', video_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            audio_path
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )

        if result.returncode == 0 and os.path.exists(audio_path):
            return audio_path

        print(f"FFmpeg error: {result.stderr.decode(errors='ignore')}")
        return None
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    temp_wav_path = None

    try:
        file_ext = os.path.splitext(audio_path)[1].lower()
        audio_path_to_use = audio_path

        # Convert to PCM WAV if needed for SpeechRecognition compatibility
        if file_ext not in {'.wav', '.wave', '.aif', '.aiff', '.flac'}:
            audio_segment = AudioSegment.from_file(audio_path)
            temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_wav_path = temp_wav_file.name
            temp_wav_file.close()  # Close handle so export can write on Windows
            audio_segment.export(temp_wav_path, format='wav')
            audio_path_to_use = temp_wav_path

        with sr.AudioFile(audio_path_to_use) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"Error with speech recognition service: {e}")
        return None
    except Exception as e:
        print(f"Unexpected transcription error: {e}")
        return None
    finally:
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except PermissionError:
                pass

def translate_text(text, target_languages):
    translator = Translator()
    translations = {}
    
    for lang_name, lang_code in target_languages.items():
        try:
            translation = translator.translate(text, dest=lang_code)
            translations[lang_name] = translation.text
        except Exception as e:
            print(f"Translation error for {lang_name}: {e}")
            translations[lang_name] = f"Translation error: {str(e)}"
    
    return translations

# Global variables for tracking
ct = {}
ct['blank'] = 0
blank_flag = 0
space_flag = False
next_flag = True
prev_char = ""
count = -1
ten_prev_char = []
for i in range(10):
    ten_prev_char.append(" ")

for i in ascii_uppercase:
    ct[i] = 0

# Current state
current_symbol = "C"
str_text = " "
word1 = " "
word2 = " "
word3 = " "
word4 = " "

@app.route('/')
def landing():
    # Show landing page for non-logged-in users
    if is_logged_in():
        return redirect(url_for('home'))
    return render_template('landing.html')

@app.route('/home')
@require_login
def home():
    return render_template('home.html')

@app.route('/sign-to-text')
@require_login
def sign_to_text():
    return render_template('index.html')

@app.route('/about')
@require_login
def about():
    return render_template('about.html')

@app.route('/speech-to-text')
@require_login
def speech_to_text():
    return render_template('speech_to_text.html')

@app.route('/process-audio', methods=['POST'])
@require_login
def process_audio():
    try:
        # Check if file is uploaded or it's a recording
        if 'audio_file' in request.files:
            file = request.files['audio_file']
            
            if file.filename == '':
                return jsonify({'success': False, 'message': 'No file selected'})
            
            # Determine if it's audio or video
            is_video = allowed_file(file.filename, 'video')
            is_audio = allowed_file(file.filename, 'audio')
            
            if not (is_audio or is_video):
                return jsonify({'success': False, 'message': 'Invalid file format. Please upload audio (mp3, wav, etc.) or video (mp4, avi, etc.) files.'})
            
            # Save uploaded file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # If video, extract audio
            audio_path = filepath
            if is_video:
                audio_path = extract_audio_from_video(filepath)
                if not audio_path:
                    os.remove(filepath)
                    return jsonify({'success': False, 'message': 'Failed to extract audio from video'})
            
            # Check duration
            duration = get_audio_duration(audio_path)
            if duration > MAX_AUDIO_DURATION:
                os.remove(filepath)
                if is_video and audio_path != filepath:
                    os.remove(audio_path)
                return jsonify({'success': False, 'message': f'Audio duration ({duration:.1f}s) exceeds maximum allowed duration of {MAX_AUDIO_DURATION}s (2 minutes)'})
            
            # Transcribe audio
            transcribed_text = transcribe_audio(audio_path)
            
            # Clean up audio file
            if is_video and audio_path != filepath:
                os.remove(audio_path)
            os.remove(filepath)
            
            if not transcribed_text:
                return jsonify({'success': False, 'message': 'Could not transcribe audio. Please ensure the audio is clear and contains speech.'})
            
            # Translate to configured languages
            translations = translate_text(transcribed_text, TRANSLATION_LANGUAGES)
            
            # Save to database
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO speech_to_text_history 
                (user_id, original_text, hindi_translation, tamil_translation, malayalam_translation, audio_duration)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'],
                transcribed_text,
                translations.get('hindi', ''),
                translations.get('tamil', ''),
                translations.get('malayalam', ''),
                duration
            ))
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'original_text': transcribed_text,
                'translations': translations,
                'duration': round(duration, 2)
            })
        
        elif request.is_json and request.json.get('audio_data'):
            # Handle recorded audio (base64 encoded)
            audio_data = request.json['audio_data']

            # Decode base64 audio
            header, encoded = audio_data.split(',', 1)
            audio_bytes = base64.b64decode(encoded)

            # Determine file extension from header (default webm)
            suffix = '.wav'
            if 'audio/webm' in header:
                suffix = '.webm'
            elif 'audio/mp3' in header:
                suffix = '.mp3'
            elif 'audio/ogg' in header:
                suffix = '.ogg'

            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_file.write(audio_bytes)
            temp_file.close()
            
            # Check duration
            duration = get_audio_duration(temp_file.name)
            if duration > MAX_AUDIO_DURATION:
                os.remove(temp_file.name)
                return jsonify({'success': False, 'message': f'Recording duration ({duration:.1f}s) exceeds maximum allowed duration of {MAX_AUDIO_DURATION}s (2 minutes)'})
            
            # Transcribe audio
            transcribed_text = transcribe_audio(temp_file.name)
            
            # Clean up
            os.remove(temp_file.name)
            
            if not transcribed_text:
                return jsonify({'success': False, 'message': 'Could not transcribe audio. Please ensure the audio is clear and contains speech.'})
            
            # Translate to configured languages
            translations = translate_text(transcribed_text, TRANSLATION_LANGUAGES)
            
            # Save to database
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO speech_to_text_history 
                (user_id, original_text, hindi_translation, tamil_translation, malayalam_translation, audio_duration)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'],
                transcribed_text,
                translations.get('hindi', ''),
                translations.get('tamil', ''),
                translations.get('malayalam', ''),
                duration
            ))
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'original_text': transcribed_text,
                'translations': translations,
                'duration': round(duration, 2)
            })
        
        else:
            return jsonify({'success': False, 'message': 'No audio data provided'})
    
    except Exception as e:
        print(f"Error in process_audio: {str(e)}")
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'})


@app.route('/translate-text', methods=['POST'])
@require_login
def translate_text_endpoint():
    try:
        data = request.get_json(force=True)
        text = data.get('text', '')
        language = data.get('language', 'hindi')

        if not text:
            return jsonify({'success': False, 'message': 'No text provided'})

        lang_map = {
            'hindi': 'hi',
            'tamil': 'ta',
            'malayalam': 'ml'
        }

        translator = Translator()
        lang_code = lang_map.get(language, language)
        translation = translator.translate(text, dest=lang_code)

        return jsonify({
            'success': True,
            'language': language,
            'translated_text': translation.text
        })
    except Exception as e:
        print(f"Translation endpoint error: {str(e)}")
        return jsonify({'success': False, 'message': f'Translation failed: {str(e)}'})

@app.route('/speech-history', methods=['GET'])
@require_login
def speech_history():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT original_text, hindi_translation, tamil_translation, malayalam_translation, audio_duration, created_at
            FROM speech_to_text_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (session['user_id'],))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'original_text': row[0],
                'hindi_translation': row[1],
                'tamil_translation': row[2],
                'malayalam_translation': row[3],
                'duration': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return jsonify({'success': True, 'history': history})
    
    except Exception as e:
        print(f"Error fetching history: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to home
    if is_logged_in():
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and verify_password(password, user[1]):
            session['user_id'] = user[0]
            session['username'] = username
            session.permanent = True  # Make session permanent
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # If already logged in, redirect to home
    if is_logged_in():
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('signup.html')
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        try:
            password_hash = hash_password(password)
            cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)', 
                         (username, email, password_hash))
            conn.commit()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists!', 'error')
        finally:
            conn.close()
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out!', 'info')
    return redirect(url_for('landing'))

@app.route('/predict', methods=['POST'])
@require_login
def predict():
    global current_symbol, str_text, word1, word2, word3, word4, prev_char, count, ten_prev_char
    
    try:
        # Get image data from request
        data = request.get_json()
        image_data = data['image']
        
        # Decode base64 image
        image_data = image_data.split(',')[1]  # Remove data:image/jpeg;base64, prefix
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert PIL image to OpenCV format
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Don't flip frame - process hands in their natural orientation
        # The model expects non-flipped hand images
        
        # Process the image without flipping for accurate gesture recognition
        hands = hd.findHands(frame, draw=False, flipType=False)
        print(f"Hands detected: {len(hands) if hands else 0}")
        
        if hands and len(hands) > 0:
            # Select hand based on priority: right hand first, then left
            hand = None
            hand_type = 'Right'
            for h in hands:
                hand_info = h[0]
                if hand_info.get('type') == 'Right':
                    hand = h
                    hand_type = 'Right'
                    break
            if hand is None:
                hand = hands[0]
                hand_type = hand[0].get('type', 'Right')
            
            map_data = hand[0]
            x, y, w, h = map_data['bbox']
            image_crop = frame[y - offset:y + h + offset, x - offset:x + w + offset]
            
            if image_crop.size > 0:
                white = cv2.imread("white.jpg")
                if white is None:
                    # Create a white background if file doesn't exist
                    white = np.ones((400, 400, 3), dtype=np.uint8) * 255
                
                handz = hd2.findHands(image_crop, draw=False, flipType=False)
                print(f"Hand landmarks detected: {len(handz) if handz else 0}")
                
                if handz and len(handz) > 0:
                    hand_data = handz[0]
                    handmap = hand_data[0]
                    pts = handmap['lmList']
                    
                    # Mirror x-coordinates for left hand to match right hand training data
                    if hand_type == 'Left':
                        crop_width = image_crop.shape[1]
                        pts = [[crop_width - pt[0], pt[1], pt[2]] for pt in pts]
                    
                    os = ((400 - w) // 2) - 15
                    os1 = ((400 - h) // 2) - 15
                    
                    # Draw hand landmarks on white background
                    for t in range(0, 4, 1):
                        cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)
                    for t in range(5, 8, 1):
                        cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)
                    for t in range(9, 12, 1):
                        cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)
                    for t in range(13, 16, 1):
                        cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)
                    for t in range(17, 20, 1):
                        cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)
                    
                    # Draw connections
                    cv2.line(white, (pts[5][0] + os, pts[5][1] + os1), (pts[9][0] + os, pts[9][1] + os1), (0, 255, 0), 3)
                    cv2.line(white, (pts[9][0] + os, pts[9][1] + os1), (pts[13][0] + os, pts[13][1] + os1), (0, 255, 0), 3)
                    cv2.line(white, (pts[13][0] + os, pts[13][1] + os1), (pts[17][0] + os, pts[17][1] + os1), (0, 255, 0), 3)
                    cv2.line(white, (pts[0][0] + os, pts[0][1] + os1), (pts[5][0] + os, pts[5][1] + os1), (0, 255, 0), 3)
                    cv2.line(white, (pts[0][0] + os, pts[0][1] + os1), (pts[17][0] + os, pts[17][1] + os1), (0, 255, 0), 3)
                    
                    # Draw points
                    for i in range(21):
                        cv2.circle(white, (pts[i][0] + os, pts[i][1] + os1), 2, (0, 0, 255), 1)
                    
                    # Predict the gesture
                    prediction_result = predict_gesture(white, pts)
                    current_symbol = prediction_result['current_symbol']
                    str_text = prediction_result['str_text']
                    word1 = prediction_result['word1']
                    word2 = prediction_result['word2']
                    word3 = prediction_result['word3']
                    word4 = prediction_result['word4']
                    
                    # Convert processed image to base64 for display
                    success, buffer = cv2.imencode('.jpg', white)
                    if success:
                        processed_image = base64.b64encode(buffer).decode('utf-8')
                    else:
                        processed_image = None
                    
                    print(f"Prediction successful: {current_symbol}, Sentence: {str_text}, Hand: {hand_type}")
                    return jsonify({
                        'success': True,
                        'current_symbol': current_symbol,
                        'sentence': str_text,
                        'suggestions': [word1, word2, word3, word4],
                        'processed_image': processed_image,
                        'hand_type': hand_type
                    })
        
        return jsonify({'success': False, 'message': 'No hand detected'})
        
    except Exception as e:
        print(f"Error in predict: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/speak', methods=['POST'])
def speak():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        def speak_text():
            try:
                engine = get_tts_engine()
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")
        
        # Run TTS in a separate thread to avoid blocking
        thread = threading.Thread(target=speak_text)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Speak route error: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/clear', methods=['POST'])
def clear():
    global str_text, word1, word2, word3, word4
    str_text = " "
    word1 = " "
    word2 = " "
    word3 = " "
    word4 = " "
    return jsonify({'success': True})

@app.route('/suggestion', methods=['POST'])
def suggestion():
    global str_text
    try:
        data = request.get_json()
        suggestion = data.get('suggestion', '')
        
        # Find the last word and replace it with the suggestion
        idx_space = str_text.rfind(" ")
        if idx_space == -1:
            str_text = suggestion.upper()
        else:
            str_text = str_text[:idx_space + 1] + suggestion.upper()
        
        return jsonify({'success': True, 'sentence': str_text})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def distance(x, y):
    return math.sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2))

def predict_gesture(white, pts):
    global prev_char, count, ten_prev_char, str_text, word1, word2, word3, word4
    
    # Reshape image for model prediction
    white_reshaped = white.reshape(1, 400, 400, 3)
    prob = np.array(model.predict(white_reshaped)[0], dtype='float32')
    ch1 = np.argmax(prob, axis=0)
    prob[ch1] = 0
    ch2 = np.argmax(prob, axis=0)
    prob[ch2] = 0
    ch3 = np.argmax(prob, axis=0)
    prob[ch3] = 0

    pl = [ch1, ch2]

    # condition for [Aemnst]
    l = [[5, 2], [5, 3], [3, 5], [3, 6], [3, 0], [3, 2], [6, 4], [6, 1], [6, 2], [6, 6], [6, 7], [6, 0], [6, 5],
         [4, 1], [1, 0], [1, 1], [6, 3], [1, 6], [5, 6], [5, 1], [4, 5], [1, 4], [1, 5], [2, 0], [2, 6], [4, 6],
         [1, 0], [5, 7], [1, 6], [6, 1], [7, 6], [2, 5], [7, 1], [5, 4], [7, 0], [7, 5], [7, 2]]
    if pl in l:
        if (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 0

    # condition for [o][s]
    l = [[2, 2], [2, 1]]
    if pl in l:
        if (pts[5][0] < pts[4][0]):
            ch1 = 0

    # condition for [c0][aemnst]
    l = [[0, 0], [0, 6], [0, 2], [0, 5], [0, 1], [0, 7], [5, 2], [7, 6], [7, 1]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[0][0] > pts[8][0] and pts[0][0] > pts[4][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and pts[5][0] > pts[4][0]:
            ch1 = 2

    # condition for [c0][aemnst]
    l = [[6, 0], [6, 6], [6, 2]]
    pl = [ch1, ch2]
    if pl in l:
        if distance(pts[8], pts[16]) < 52:
            ch1 = 2

    # condition for [gh][bdfikruvw]
    l = [[1, 4], [1, 5], [1, 6], [1, 3], [1, 0]]
    pl = [ch1, ch2]

    if pl in l:
        if pts[6][1] > pts[8][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1] and pts[0][0] < pts[8][0] and pts[0][0] < pts[12][0] and pts[0][0] < pts[16][0] and pts[0][0] < pts[20][0]:
            ch1 = 3

    # con for [gh][l]
    l = [[4, 6], [4, 1], [4, 5], [4, 3], [4, 7]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[4][0] > pts[0][0]:
            ch1 = 3

    # con for [gh][pqz]
    l = [[5, 3], [5, 0], [5, 7], [5, 4], [5, 2], [5, 1], [5, 5]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[2][1] + 15 < pts[16][1]:
            ch1 = 3

    # con for [l][x]
    l = [[6, 4], [6, 1], [6, 2]]
    pl = [ch1, ch2]
    if pl in l:
        if distance(pts[4], pts[11]) > 55:
            ch1 = 4

    # con for [l][d]
    l = [[1, 4], [1, 6], [1, 1]]
    pl = [ch1, ch2]
    if pl in l:
        if (distance(pts[4], pts[11]) > 50) and (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 4

    # con for [l][gh]
    l = [[3, 6], [3, 4]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[4][0] < pts[0][0]):
            ch1 = 4

    # con for [l][c0]
    l = [[2, 2], [2, 5], [2, 4]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[1][0] < pts[12][0]):
            ch1 = 4

    # con for [l][c0]
    l = [[2, 2], [2, 5], [2, 4]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[1][0] < pts[12][0]):
            ch1 = 4

    # con for [gh][z]
    l = [[3, 6], [3, 5], [3, 4]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and pts[4][1] > pts[10][1]:
            ch1 = 5

    # con for [gh][pq]
    l = [[3, 2], [3, 1], [3, 6]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[4][1] + 17 > pts[8][1] and pts[4][1] + 17 > pts[12][1] and pts[4][1] + 17 > pts[16][1] and pts[4][1] + 17 > pts[20][1]:
            ch1 = 5

    # con for [l][pqz]
    l = [[4, 4], [4, 5], [4, 2], [7, 5], [7, 6], [7, 0]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[4][0] > pts[0][0]:
            ch1 = 5

    # con for [pqz][aemnst]
    l = [[0, 2], [0, 6], [0, 1], [0, 5], [0, 0], [0, 7], [0, 4], [0, 3], [2, 7]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[0][0] < pts[8][0] and pts[0][0] < pts[12][0] and pts[0][0] < pts[16][0] and pts[0][0] < pts[20][0]:
            ch1 = 5

    # con for [pqz][yj]
    l = [[5, 7], [5, 2], [5, 6]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[3][0] < pts[0][0]:
            ch1 = 7

    # con for [l][yj]
    l = [[4, 6], [4, 2], [4, 4], [4, 1], [4, 5], [4, 7]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[6][1] < pts[8][1]:
            ch1 = 7

    # con for [x][yj]
    l = [[6, 7], [0, 7], [0, 1], [0, 0], [6, 4], [6, 6], [6, 5], [6, 1]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[18][1] > pts[20][1]:
            ch1 = 7

    # condition for [x][aemnst]
    l = [[0, 4], [0, 2], [0, 3], [0, 1], [0, 6]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[5][0] > pts[16][0]:
            ch1 = 6

    # condition for [yj][x]
    l = [[7, 2]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[18][1] < pts[20][1] and pts[8][1] < pts[10][1]:
            ch1 = 6

    # condition for [c0][x]
    l = [[2, 1], [2, 2], [2, 6], [2, 7], [2, 0]]
    pl = [ch1, ch2]
    if pl in l:
        if distance(pts[8], pts[16]) > 50:
            ch1 = 6

    # con for [l][x]
    l = [[4, 6], [4, 2], [4, 1], [4, 4]]
    pl = [ch1, ch2]
    if pl in l:
        if distance(pts[4], pts[11]) < 60:
            ch1 = 6

    # con for [x][d]
    l = [[1, 4], [1, 6], [1, 0], [1, 2]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[5][0] - pts[4][0] - 15 > 0:
            ch1 = 6

    # con for [b][pqz]
    l = [[5, 0], [5, 1], [5, 4], [5, 5], [5, 6], [6, 1], [7, 6], [0, 2], [7, 1], [7, 4], [6, 6], [7, 2], [5, 0],
         [6, 3], [6, 4], [7, 5], [7, 2]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 1

    # con for [f][pqz]
    l = [[6, 1], [6, 0], [0, 3], [6, 4], [2, 2], [0, 6], [6, 2], [7, 6], [4, 6], [4, 1], [4, 2], [0, 2], [7, 1],
         [7, 4], [6, 6], [7, 2], [7, 5], [7, 2]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[6][1] < pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 1

    l = [[6, 1], [6, 0], [4, 2], [4, 1], [4, 6], [4, 4]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 1

    # con for [d][pqz]
    fg = 19
    l = [[5, 0], [3, 4], [3, 0], [3, 1], [3, 5], [5, 5], [5, 4], [5, 1], [7, 6]]
    pl = [ch1, ch2]
    if pl in l:
        if ((pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[2][0] < pts[0][0]) and pts[4][1] > pts[14][1]):
            ch1 = 1

    l = [[4, 1], [4, 2], [4, 4]]
    pl = [ch1, ch2]
    if pl in l:
        if (distance(pts[4], pts[11]) < 50) and (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 1

    l = [[3, 4], [3, 0], [3, 1], [3, 5], [3, 6]]
    pl = [ch1, ch2]
    if pl in l:
        if ((pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[2][0] < pts[0][0]) and pts[14][1] < pts[4][1]):
            ch1 = 1

    l = [[6, 6], [6, 4], [6, 1], [6, 2]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[5][0] - pts[4][0] - 15 < 0:
            ch1 = 1

    # con for [i][pqz]
    l = [[5, 4], [5, 5], [5, 1], [0, 3], [0, 7], [5, 0], [0, 2], [6, 2], [7, 5], [7, 1], [7, 6], [7, 7]]
    pl = [ch1, ch2]
    if pl in l:
        if ((pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1])):
            ch1 = 1

    # con for [yj][bfdi]
    l = [[1, 5], [1, 7], [1, 1], [1, 6], [1, 3], [1, 0]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[4][0] < pts[5][0] + 15) and ((pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1])):
            ch1 = 7

    # con for [uvr]
    l = [[5, 5], [5, 0], [5, 4], [5, 1], [4, 6], [4, 1], [7, 6], [3, 0], [3, 5]]
    pl = [ch1, ch2]
    if pl in l:
        if ((pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1])) and pts[4][1] > pts[14][1]:
            ch1 = 1

    # con for [w]
    fg = 13
    l = [[3, 5], [3, 0], [3, 6], [5, 1], [4, 1], [2, 0], [5, 0], [5, 5]]
    pl = [ch1, ch2]
    if pl in l:
        if not (pts[0][0] + fg < pts[8][0] and pts[0][0] + fg < pts[12][0] and pts[0][0] + fg < pts[16][0] and pts[0][0] + fg < pts[20][0]) and not (pts[0][0] > pts[8][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and distance(pts[4], pts[11]) < 50:
            ch1 = 1

    # con for [w]
    l = [[5, 0], [5, 5], [0, 1]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1]:
            ch1 = 1

    # -------------------------condn for 8 groups  ends

    # -------------------------condn for subgroups  starts
    #
    if ch1 == 0:
        ch1 = 'S'
        if pts[4][0] < pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0]:
            ch1 = 'A'
        if pts[4][0] > pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0] and pts[4][1] < pts[14][1] and pts[4][1] < pts[18][1]:
            ch1 = 'T'
        if pts[4][1] > pts[8][1] and pts[4][1] > pts[12][1] and pts[4][1] > pts[16][1] and pts[4][1] > pts[20][1]:
            ch1 = 'E'
        if pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][0] > pts[14][0] and pts[4][1] < pts[18][1]:
            ch1 = 'M'
        if pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][1] < pts[18][1] and pts[4][1] < pts[14][1]:
            ch1 = 'N'

    if ch1 == 2:
        if distance(pts[12], pts[4]) > 42:
            ch1 = 'C'
        else:
            ch1 = 'O'

    if ch1 == 3:
        if (distance(pts[8], pts[12])) > 72:
            ch1 = 'G'
        else:
            ch1 = 'H'

    if ch1 == 7:
        if distance(pts[8], pts[4]) > 42:
            ch1 = 'Y'
        else:
            ch1 = 'J'

    if ch1 == 4:
        ch1 = 'L'

    if ch1 == 6:
        ch1 = 'X'

    if ch1 == 5:
        if pts[4][0] > pts[12][0] and pts[4][0] > pts[16][0] and pts[4][0] > pts[20][0]:
            if pts[8][1] < pts[5][1]:
                ch1 = 'Z'
            else:
                ch1 = 'Q'
        else:
            ch1 = 'P'

    if ch1 == 1:
        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 'B'
        if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 'D'
        if (pts[6][1] < pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 'F'
        if (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 'I'
        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 'W'
        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and pts[4][1] < pts[9][1]:
            ch1 = 'K'
        if ((distance(pts[8], pts[12]) - distance(pts[6], pts[10])) < 8) and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 'U'
        if ((distance(pts[8], pts[12]) - distance(pts[6], pts[10])) >= 8) and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[4][1] > pts[9][1]):
            ch1 = 'V'

        if (pts[8][0] > pts[12][0]) and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 'R'

    if ch1 == 1 or ch1 == 'E' or ch1 == 'S' or ch1 == 'X' or ch1 == 'Y' or ch1 == 'B':
        if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = " "

    if ch1 == 'E' or ch1 == 'Y' or ch1 == 'B':
        if (pts[4][0] < pts[5][0]) and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = "next"

    if ch1 == 'Next' or ch1 == 'B' or ch1 == 'C' or ch1 == 'H' or ch1 == 'F' or ch1 == 'X':
        if (pts[0][0] > pts[8][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and (pts[4][1] < pts[8][1] and pts[4][1] < pts[12][1] and pts[4][1] < pts[16][1] and pts[4][1] < pts[20][1]) and (pts[4][1] < pts[6][1] and pts[4][1] < pts[10][1] and pts[4][1] < pts[14][1] and pts[4][1] < pts[18][1]):
            ch1 = 'Backspace'

    if ch1 == "next" and prev_char != "next":
        if ten_prev_char[(count-2) % 10] != "next":
            if ten_prev_char[(count-2) % 10] == "Backspace":
                str_text = str_text[0:-1]
            else:
                if ten_prev_char[(count - 2) % 10] != "Backspace":
                    str_text = str_text + ten_prev_char[(count-2) % 10]
        else:
            if ten_prev_char[(count - 0) % 10] != "Backspace":
                str_text = str_text + ten_prev_char[(count - 0) % 10]

    if ch1 == "  " and prev_char != "  ":
        str_text = str_text + "  "

    prev_char = ch1
    count += 1
    ten_prev_char[count % 10] = ch1

    if len(str_text.strip()) != 0:
        st = str_text.rfind(" ")
        ed = len(str_text)
        word = str_text[st+1:ed]
        if len(word.strip()) != 0:
            try:
                ddd.check(word)
                lenn = len(ddd.suggest(word))
                if lenn >= 4:
                    word4 = ddd.suggest(word)[3]
                if lenn >= 3:
                    word3 = ddd.suggest(word)[2]
                if lenn >= 2:
                    word2 = ddd.suggest(word)[1]
                if lenn >= 1:
                    word1 = ddd.suggest(word)[0]
            except:
                word1 = " "
                word2 = " "
                word3 = " "
                word4 = " "
        else:
            word1 = " "
            word2 = " "
            word3 = " "
            word4 = " "

    return {
        'current_symbol': ch1,
        'str_text': str_text,
        'word1': word1,
        'word2': word2,
        'word3': word3,
        'word4': word4
    }

if __name__ == '__main__':
    # Check if SSL certificates exist
    ssl_cert = 'ssl/cert.pem'
    ssl_key = 'ssl/key.pem'
    
    if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        print("Starting HTTPS server...")
        app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=(ssl_cert, ssl_key))
    else:
        print("SSL certificates not found. Starting HTTP server...")
        print("Note: Camera access may be limited in HTTP mode.")
        print("For full camera access, use HTTPS with SSL certificates.")
        app.run(debug=True, host='0.0.0.0', port=5000)
