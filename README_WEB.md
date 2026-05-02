# Sign Language Recognition Web Application

This is a web-based version of the Sign Language to Text and Speech Conversion application. It converts the original desktop application (using Tkinter) into a modern web application using Flask, HTML, CSS, and JavaScript.

## Features

- **Real-time Hand Gesture Recognition**: Uses computer vision to detect and recognize American Sign Language gestures
- **Live Camera Feed**: Captures video from your webcam in real-time
- **Hand Skeleton Visualization**: Shows processed hand landmarks on a white background
- **Text Generation**: Converts recognized gestures into text
- **Text-to-Speech**: Speaks the generated text aloud
- **Word Suggestions**: Provides spelling suggestions for better accuracy
- **Modern Web Interface**: Responsive design that works on desktop and mobile devices

## Requirements

### Software Requirements
- Python 3.7 or higher
- Web browser with camera access
- Webcam

### Python Dependencies
All required packages are listed in `requirements.txt`:
- Flask (web framework)
- OpenCV (computer vision)
- TensorFlow/Keras (machine learning)
- NumPy (numerical computing)
- Pillow (image processing)
- pyttsx3 (text-to-speech)
- cvzone (hand tracking)
- pyenchant (spell checking)

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure you have the model file**:
   - Make sure `cnn8grps_rad1_model.h5` is in the project directory
   - This is the trained CNN model for gesture recognition

4. **Run the application**:
   ```bash
   python run_web_app.py
   ```
   
   Or directly:
   ```bash
   python app.py
   ```

5. **Open your web browser** and go to:
   ```
   http://localhost:5000
   ```

## Usage

1. **Start the Application**: Click "Start Camera" to begin video capture
2. **Make Gestures**: Hold your hand in front of the camera and make sign language gestures
3. **View Results**: 
   - The current recognized character appears in the "Current Character" section
   - The complete sentence builds up in the "Sentence" section
   - Processed hand skeleton is shown in the right panel
4. **Use Suggestions**: Click on word suggestions to correct spelling
5. **Speak Text**: Click "Speak" to hear the generated text
6. **Clear**: Click "Clear" to reset the sentence

## Supported Gestures

The application recognizes American Sign Language (ASL) finger spelling for all letters A-Z, plus special gestures for:
- Space
- Backspace
- Next word

## Technical Details

### Architecture
- **Backend**: Flask web server handling image processing and ML inference
- **Frontend**: HTML/CSS/JavaScript for user interface
- **Computer Vision**: OpenCV and MediaPipe for hand detection
- **Machine Learning**: TensorFlow/Keras CNN model for gesture classification
- **Real-time Processing**: WebSocket-like communication for live updates

### Key Components
- `app.py`: Main Flask application with API endpoints
- `templates/index.html`: Web interface with camera integration
- `run_web_app.py`: Startup script with dependency checking
- `requirements.txt`: Python package dependencies

### API Endpoints
- `GET /`: Main web interface
- `POST /predict`: Process camera frame and return gesture prediction
- `POST /speak`: Convert text to speech
- `POST /clear`: Clear the current sentence
- `POST /suggestion`: Apply word suggestion

## Troubleshooting

### Common Issues

1. **Camera not working**:
   - Ensure your webcam is connected and not used by other applications
   - Check browser permissions for camera access
   - Try refreshing the page

2. **Model file missing**:
   - Ensure `cnn8grps_rad1_model.h5` is in the project directory
   - The model file should be the same one used in the original desktop application

3. **Dependencies issues**:
   - Make sure all packages are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

4. **Performance issues**:
   - Close other applications using the camera
   - Reduce browser window size if needed
   - Ensure good lighting for better hand detection

### Browser Compatibility
- Chrome (recommended)
- Firefox
- Safari
- Edge

## Development

### File Structure
```
project/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface
├── requirements.txt      # Python dependencies
├── run_web_app.py       # Startup script
├── cnn8grps_rad1_model.h5  # Trained model
├── white.jpg            # Background image
└── README_WEB.md        # This file
```

### Customization
- Modify `templates/index.html` to change the web interface
- Update `app.py` to add new features or modify gesture recognition
- Adjust CSS in the HTML file for different styling

## Differences from Desktop Version

### Advantages of Web Version
- **Cross-platform**: Works on any device with a web browser
- **No installation**: Users don't need to install Python or dependencies
- **Modern UI**: Responsive design with better user experience
- **Easy deployment**: Can be deployed to cloud services
- **Mobile friendly**: Works on tablets and phones

### Limitations
- **Browser compatibility**: Requires modern browser with camera support
- **Internet dependency**: For deployment, requires internet connection
- **Performance**: May be slightly slower than native desktop application

## Future Enhancements

- **Multi-language support**: Add support for other sign languages
- **Gesture history**: Save and replay gesture sequences
- **User training**: Allow users to train custom gestures
- **Cloud deployment**: Deploy to cloud platforms for wider access
- **Mobile app**: Create native mobile applications
- **Real-time collaboration**: Multiple users working together

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Ensure all dependencies are properly installed
3. Verify the model file is present and accessible
4. Check browser console for JavaScript errors
