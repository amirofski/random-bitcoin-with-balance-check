from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import json
import base64
import logging


class KeyEncryption:
    """Encrypt and decrypt found private keys"""
    
    def __init__(self, password: str = None, logger: logging.Logger = None):
        self.password = password or self._get_default_password()
        self.logger = logger or logging.getLogger(__name__)
    
    def _get_default_password(self) -> str:
        """Get default encryption password from environment or prompt"""
        import os
        password = os.environ.get('KEY_ENCRYPTION_PASSWORD')
        
        if not password:
            import getpass
            password = getpass.getpass("Enter encryption password for found keys: ")
        
        return password
    
    def _derive_key(self, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        return PBKDF2(self.password, salt, dkLen=32, count=100000)
    
    def encrypt_data(self, data: Dict) -> str:
        """Encrypt data and return base64 encoded result"""
        try:
            # Generate random salt
            salt = get_random_bytes(16)
            key = self._derive_key(salt)
            
            # Convert data to JSON
            plaintext = json.dumps(data).encode('utf-8')
            
            # Create cipher and encrypt
            cipher = AES.new(key, AES.MODE_GCM)
            nonce = cipher.nonce
            ciphertext, tag = cipher.encrypt_and_digest(plaintext)
            
            # Combine salt + nonce + tag + ciphertext
            encrypted = salt + nonce + tag + ciphertext
            
            return base64.b64encode(encrypted).decode('utf-8')
        
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")
            return None
    
    def decrypt_data(self, encrypted_data: str) -> Dict:
        """Decrypt base64 encoded encrypted data"""
        try:
            encrypted = base64.b64decode(encrypted_data)
            
            # Extract components
            salt = encrypted[:16]
            nonce = encrypted[16:32]
            tag = encrypted[32:48]
            ciphertext = encrypted[48:]
            
            # Derive key
            key = self._derive_key(salt)
            
            # Decrypt
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            
            return json.loads(plaintext.decode('utf-8'))
        
        except Exception as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            return None
