"""Encryption utilities for sensitive data."""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
from typing import Optional
import secrets

# Get encryption key from environment or generate one
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

if not ENCRYPTION_KEY:
    # Generate a key if not provided (for development only!)
    print("WARNING: No ENCRYPTION_KEY found in environment. Generating temporary key.")
    print("This key will be lost on restart. Set ENCRYPTION_KEY in .env for production!")
    ENCRYPTION_KEY = Fernet.generate_key().decode()

# Initialize Fernet cipher
try:
    cipher = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)
except Exception as e:
    print(f"Error initializing encryption: {e}")
    cipher = Fernet(Fernet.generate_key())


def encrypt_data(data: str) -> str:
    """
    Encrypt sensitive data.
    
    Args:
        data: Plain text string to encrypt
        
    Returns:
        Encrypted string (base64 encoded)
    """
    if not data:
        return ""
    
    try:
        encrypted = cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        raise


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt sensitive data.
    
    Args:
        encrypted_data: Encrypted string (base64 encoded)
        
    Returns:
        Decrypted plain text string
    """
    if not encrypted_data:
        return ""
    
    try:
        decoded = base64.b64decode(encrypted_data.encode())
        decrypted = cipher.decrypt(decoded)
        return decrypted.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        raise


def hash_sensitive_data(data: str, salt: Optional[bytes] = None) -> tuple[str, str]:
    """
    Hash sensitive data with salt (one-way encryption).
    
    Args:
        data: Data to hash
        salt: Optional salt (will be generated if not provided)
        
    Returns:
        Tuple of (hashed_data, salt)
    """
    if salt is None:
        salt = secrets.token_bytes(32)
    
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    
    key = kdf.derive(data.encode())
    hashed = base64.b64encode(key).decode()
    salt_encoded = base64.b64encode(salt).decode()
    
    return hashed, salt_encoded


def verify_hashed_data(data: str, hashed_data: str, salt: str) -> bool:
    """
    Verify hashed data.
    
    Args:
        data: Original data
        hashed_data: Previously hashed data
        salt: Salt used for hashing
        
    Returns:
        True if data matches, False otherwise
    """
    salt_bytes = base64.b64decode(salt.encode())
    new_hash, _ = hash_sensitive_data(data, salt_bytes)
    return new_hash == hashed_data


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    
    Args:
        length: Length of the token
        
    Returns:
        Secure random token
    """
    return secrets.token_urlsafe(length)


def encrypt_file(file_path: str, output_path: Optional[str] = None) -> str:
    """
    Encrypt a file.
    
    Args:
        file_path: Path to file to encrypt
        output_path: Optional output path (defaults to file_path + '.encrypted')
        
    Returns:
        Path to encrypted file
    """
    if output_path is None:
        output_path = file_path + '.encrypted'
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    encrypted = cipher.encrypt(data)
    
    with open(output_path, 'wb') as f:
        f.write(encrypted)
    
    return output_path


def decrypt_file(encrypted_path: str, output_path: Optional[str] = None) -> str:
    """
    Decrypt a file.
    
    Args:
        encrypted_path: Path to encrypted file
        output_path: Optional output path
        
    Returns:
        Path to decrypted file
    """
    if output_path is None:
        output_path = encrypted_path.replace('.encrypted', '')
    
    with open(encrypted_path, 'rb') as f:
        encrypted = f.read()
    
    decrypted = cipher.decrypt(encrypted)
    
    with open(output_path, 'wb') as f:
        f.write(decrypted)
    
    return output_path


# Certificate encryption helpers
def encrypt_certificate_key(private_key: str) -> str:
    """Encrypt a certificate private key."""
    return encrypt_data(private_key)


def decrypt_certificate_key(encrypted_key: str) -> str:
    """Decrypt a certificate private key."""
    return decrypt_data(encrypted_key)