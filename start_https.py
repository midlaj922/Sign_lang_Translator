#!/usr/bin/env python3
"""
Quick start script for HTTPS version of the Sign Language Recognition App
This script ensures the app runs with HTTPS for camera access
"""

import os
import sys
import subprocess

def main():
    print("=" * 60)
    print("🚀 Starting Sign Language Recognition App with HTTPS")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found!")
        print("Please run this script from the project directory.")
        sys.exit(1)
    
    # Create SSL certificates if they don't exist
    if not os.path.exists('ssl/cert.pem') or not os.path.exists('ssl/key.pem'):
        print("🔐 Creating SSL certificates for HTTPS...")
        try:
            result = subprocess.run([sys.executable, 'create_ssl_cert.py'], 
                                 capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Failed to create SSL certificates")
                print("The app will run in HTTP mode (camera access may be limited)")
        except Exception as e:
            print(f"❌ Error creating SSL certificates: {e}")
    
    # Start the application
    print("\n🌐 Starting web application...")
    print("=" * 60)
    print("✅ The app will be available at: https://localhost:5000")
    print("🔒 HTTPS is enabled for secure camera access")
    print("📱 Camera will work properly in modern browsers")
    print("=" * 60)
    print("Press Ctrl+C to stop the application")
    print("=" * 60)
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
