"""Encryption utilities for sensitive data."""
import os
import base64
from cryptography.fernet import Fernet
from typing import Optional
import secrets

# Get encryption key from environment
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

if not ENCRYPTION_KEY:
    print("WARNING: No ENCRYPTION_KEY found in environment. Generating temporary key.")
    ENCRYPTION_KEY = Fernet.generate_key().decode()

# Initialize Fernet cipher
try:
    cipher = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)
except Exception as e:
    print(f"Error initializing encryption: {e}")
    cipher = Fernet(Fernet.generate_key())


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data."""
    if not data:
        return ""
    try:
        encrypted = cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        raise


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    if not encrypted_data:
        return ""
    try:
        decoded = base64.b64decode(encrypted_data.encode())
        decrypted = cipher.decrypt(decoded)
        return decrypted.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        raise


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def encrypt_certificate_key(private_key: str) -> str:
    """Encrypt a certificate private key."""
    return encrypt_data(private_key)


def decrypt_certificate_key(encrypted_key: str) -> str:
    """Decrypt a certificate private key."""
    return decrypt_data(encrypted_key)
