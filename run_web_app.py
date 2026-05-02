#!/usr/bin/env python3
"""
Web-based Sign Language Recognition Application
Run this script to start the web application
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import cv2
        import numpy
        import PIL
        import pyttsx3
        import tensorflow
        import keras
        import cvzone
        import enchant
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies using: pip install -r requirements.txt")
        return False

def check_model_file():
    """Check if the model file exists"""
    if os.path.exists('cnn8grps_rad1_model.h5'):
        print("✓ Model file found")
        return True
    else:
        print("✗ Model file 'cnn8grps_rad1_model.h5' not found")
        print("Please ensure the model file is in the current directory")
        return False

def check_white_image():
    """Check if white background image exists, create if not"""
    if os.path.exists('white.jpg'):
        print("✓ White background image found")
        return True
    else:
        print("Creating white background image...")
        try:
            import cv2
            import numpy as np
            white_img = np.ones((400, 400, 3), dtype=np.uint8) * 255
            cv2.imwrite('white.jpg', white_img)
            print("✓ White background image created")
            return True
        except Exception as e:
            print(f"✗ Error creating white background image: {e}")
            return False

def check_ssl_certificates():
    """Check if SSL certificates exist, create if needed"""
    ssl_cert = 'ssl/cert.pem'
    ssl_key = 'ssl/key.pem'
    
    if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        print("✓ SSL certificates found")
        return True
    else:
        print("SSL certificates not found. Creating them...")
        try:
            # Try to create SSL certificates
            result = subprocess.run([sys.executable, 'create_ssl_cert.py'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ SSL certificates created successfully")
                return True
            else:
                print("✗ Failed to create SSL certificates")
                print("The application will run in HTTP mode (camera access may be limited)")
                return False
        except Exception as e:
            print(f"✗ Error creating SSL certificates: {e}")
            print("The application will run in HTTP mode (camera access may be limited)")
            return False

def main():
    """Main function to run the web application"""
    print("=" * 50)
    print("Sign Language Recognition Web Application")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check model file
    if not check_model_file():
        sys.exit(1)
    
    # Check/create white image
    if not check_white_image():
        sys.exit(1)
    
    # Check/create SSL certificates
    has_ssl = check_ssl_certificates()
    
    print("\n" + "=" * 50)
    print("Starting web application...")
    print("=" * 50)
    
    if has_ssl:
        print("The application will be available at: https://localhost:5000")
        print("Note: Your browser may show a security warning.")
        print("Click 'Advanced' and 'Proceed to localhost' to continue.")
    else:
        print("The application will be available at: http://localhost:5000")
        print("Note: Camera access may be limited in HTTP mode.")
        print("For full camera access, use HTTPS with SSL certificates.")
    
    print("Press Ctrl+C to stop the application")
    print("=" * 50)
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\nApplication stopped by user")
    except Exception as e:
        print(f"\nError running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
