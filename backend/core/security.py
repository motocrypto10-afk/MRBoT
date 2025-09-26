"""
Security utilities for encryption, hashing, and authentication
"""
import hashlib
import secrets
from typing import Optional, Dict, Any
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    """Security utilities manager"""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self._fernet = None

    def _get_fernet(self) -> Fernet:
        """Get Fernet instance for encryption/decryption"""
        if self._fernet is None:
            # Generate key from secret
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'botmr_salt_2025',  # Use a proper random salt in production
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
            self._fernet = Fernet(key)
        return self._fernet

    def encrypt_data(self, data: str) -> str:
        """Encrypt data using AES-256"""
        try:
            fernet = self._get_fernet()
            encrypted = fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        try:
            fernet = self._get_fernet()
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise

    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            salt, password_hash = hashed.split(':')
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash == new_hash.hex()
        except Exception:
            return False

    def generate_session_id(self) -> str:
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)

    def generate_api_key(self) -> str:
        """Generate API key"""
        return f"botmr_{secrets.token_urlsafe(48)}"

# Global security manager
security_manager = SecurityManager()

def get_security_manager() -> SecurityManager:
    """Get security manager instance"""
    return security_manager