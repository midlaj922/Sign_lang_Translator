#!/usr/bin/env python3
"""
Create self-signed SSL certificates for HTTPS development
This allows camera access in modern browsers
"""

import os
import subprocess
import sys

def create_ssl_directory():
    """Create SSL directory if it doesn't exist"""
    if not os.path.exists('ssl'):
        os.makedirs('ssl')
        print("✓ Created SSL directory")
    else:
        print("✓ SSL directory already exists")

def create_ssl_certificates():
    """Create self-signed SSL certificates"""
    cert_file = 'ssl/cert.pem'
    key_file = 'ssl/key.pem'
    
    # Check if certificates already exist
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("✓ SSL certificates already exist")
        return True
    
    try:
        # Create self-signed certificate using OpenSSL
        cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
            '-keyout', key_file,
            '-out', cert_file,
            '-days', '365',
            '-nodes',
            '-subj', '/C=US/ST=State/L=City/O=Organization/CN=localhost'
        ]
        
        print("Creating SSL certificates...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ SSL certificates created successfully")
            print(f"  Certificate: {cert_file}")
            print(f"  Private Key: {key_file}")
            return True
        else:
            print(f"✗ Error creating SSL certificates: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("✗ OpenSSL not found. Trying alternative method...")
        return create_ssl_certificates_alternative()

def create_ssl_certificates_alternative():
    """Alternative method using Python cryptography library"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from datetime import datetime, timedelta
        
        print("Creating SSL certificates using Python cryptography...")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Sign Language App"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress("127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write certificate and key to files
        with open('ssl/cert.pem', 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open('ssl/key.pem', 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print("✓ SSL certificates created successfully using Python cryptography")
        return True
        
    except ImportError:
        print("✗ cryptography library not found")
        print("Please install it with: pip install cryptography")
        return False
    except Exception as e:
        print(f"✗ Error creating SSL certificates: {e}")
        return False

def main():
    """Main function to create SSL certificates"""
    print("=" * 50)
    print("Creating SSL Certificates for HTTPS")
    print("=" * 50)
    
    # Create SSL directory
    create_ssl_directory()
    
    # Create SSL certificates
    if create_ssl_certificates():
        print("\n" + "=" * 50)
        print("SSL certificates created successfully!")
        print("=" * 50)
        print("The application will now run with HTTPS support.")
        print("You can access it at: https://localhost:5000")
        print("Note: Your browser may show a security warning.")
        print("Click 'Advanced' and 'Proceed to localhost' to continue.")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("Failed to create SSL certificates")
        print("=" * 50)
        print("The application will run in HTTP mode.")
        print("Camera access may be limited in some browsers.")
        print("=" * 50)

if __name__ == "__main__":
    main()
