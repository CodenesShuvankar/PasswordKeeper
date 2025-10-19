"""
Cryptographic operations for data encryption/decryption
"""

import os
import secrets
import logging
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
import json
import base64


class CryptoManager:
    """Handles all cryptographic operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.backend = default_backend()
    
    def encrypt_data(self, data: str, key: bytes) -> str:
        """
        Encrypt data using AES-256-GCM
        
        Args:
            data: Plain text data to encrypt
            key: 32-byte encryption key
            
        Returns:
            Base64 encoded encrypted data with IV and tag
        """
        try:
            # Convert string to bytes
            plaintext = data.encode('utf-8')
            
            # Generate random IV
            iv = secrets.token_bytes(12)  # 96-bit IV for GCM
            
            # Create cipher
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            
            # Encrypt data
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            
            # Get authentication tag
            tag = encryptor.tag
            
            # Combine IV, tag, and ciphertext
            encrypted_data = {
                'iv': base64.b64encode(iv).decode('ascii'),
                'tag': base64.b64encode(tag).decode('ascii'),
                'ciphertext': base64.b64encode(ciphertext).decode('ascii')
            }
            
            # Return as base64-encoded JSON
            return base64.b64encode(json.dumps(encrypted_data).encode('utf-8')).decode('ascii')
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str, key: bytes) -> Optional[str]:
        """
        Decrypt data using AES-256-GCM
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            key: 32-byte encryption key
            
        Returns:
            Decrypted plain text or None if decryption fails
        """
        try:
            # Decode base64 JSON
            data_json = base64.b64decode(encrypted_data.encode('ascii')).decode('utf-8')
            data = json.loads(data_json)
            
            # Extract components
            iv = base64.b64decode(data['iv'].encode('ascii'))
            tag = base64.b64decode(data['tag'].encode('ascii'))
            ciphertext = base64.b64decode(data['ciphertext'].encode('ascii'))
            
            # Create cipher
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=self.backend)
            decryptor = cipher.decryptor()
            
            # Decrypt data
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            return None
    
    def encrypt_database_content(self, content: bytes, key: bytes) -> bytes:
        """
        Encrypt entire database content with HMAC for integrity
        
        Args:
            content: Database content as bytes
            key: 32-byte encryption key
            
        Returns:
            Encrypted content with HMAC
        """
        try:
            # Generate random IV
            iv = secrets.token_bytes(16)  # 128-bit IV for CBC
            
            # Pad content to AES block size
            padded_content = self._pad_data(content)
            
            # Encrypt with AES-256-CBC
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_content) + encryptor.finalize()
            
            # Create HMAC for integrity
            hmac_key = self._derive_hmac_key(key)
            h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=self.backend)
            h.update(iv + ciphertext)
            mac = h.finalize()
            
            # Combine MAC + IV + Ciphertext
            return mac + iv + ciphertext
            
        except Exception as e:
            self.logger.error(f"Database encryption failed: {e}")
            raise
    
    def decrypt_database_content(self, encrypted_content: bytes, key: bytes) -> Optional[bytes]:
        """
        Decrypt database content and verify HMAC
        
        Args:
            encrypted_content: Encrypted database content
            key: 32-byte encryption key
            
        Returns:
            Decrypted content or None if verification fails
        """
        try:
            # Extract components
            mac = encrypted_content[:32]  # SHA256 = 32 bytes
            iv = encrypted_content[32:48]  # 16 bytes
            ciphertext = encrypted_content[48:]
            
            # Verify HMAC
            hmac_key = self._derive_hmac_key(key)
            h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=self.backend)
            h.update(iv + ciphertext)
            
            try:
                h.verify(mac)
            except Exception:
                self.logger.error("HMAC verification failed - data may be tampered")
                return None
            
            # Decrypt
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            padded_content = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remove padding
            content = self._unpad_data(padded_content)
            
            return content
            
        except Exception as e:
            self.logger.error(f"Database decryption failed: {e}")
            return None
    
    def generate_test_vector(self, key: bytes) -> str:
        """
        Generate a test vector to verify key correctness
        
        Args:
            key: Encryption key to test
            
        Returns:
            Encrypted test string
        """
        test_data = "PasswordKeeper_TestVector_v1.0"
        return self.encrypt_data(test_data, key)
    
    def verify_test_vector(self, test_vector: str, key: bytes) -> bool:
        """
        Verify test vector with given key
        
        Args:
            test_vector: Encrypted test vector
            key: Key to test
            
        Returns:
            True if key is correct
        """
        expected = "PasswordKeeper_TestVector_v1.0"
        decrypted = self.decrypt_data(test_vector, key)
        return decrypted == expected
    
    def _pad_data(self, data: bytes) -> bytes:
        """Add PKCS7 padding"""
        block_size = 16
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad_data(self, padded_data: bytes) -> bytes:
        """Remove PKCS7 padding"""
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]
    
    def _derive_hmac_key(self, key: bytes) -> bytes:
        """Derive HMAC key from encryption key"""
        # Use HKDF to derive HMAC key
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'PasswordKeeper_HMAC',
            info=b'HMAC_KEY',
            backend=self.backend
        )
        
        return hkdf.derive(key)
    
    def secure_delete(self, data: bytes) -> None:
        """
        Securely overwrite data in memory
        
        Args:
            data: Data to overwrite
        """
        # Overwrite with random data multiple times
        for _ in range(3):
            for i in range(len(data)):
                data[i] = secrets.randbits(8)
    
    def generate_password(self, length: int = 16, include_symbols: bool = True) -> str:
        """
        Generate a secure random password
        
        Args:
            length: Password length
            include_symbols: Whether to include special characters
            
        Returns:
            Generated password
        """
        import string
        
        chars = string.ascii_letters + string.digits
        if include_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one character from each category
        password = []
        if length >= 4:
            password.append(secrets.choice(string.ascii_lowercase))
            password.append(secrets.choice(string.ascii_uppercase))
            password.append(secrets.choice(string.digits))
            if include_symbols:
                password.append(secrets.choice("!@#$%^&*"))
        
        # Fill remaining length
        for _ in range(len(password), length):
            password.append(secrets.choice(chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)