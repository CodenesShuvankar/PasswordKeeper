"""
Unit tests for cryptographic operations
"""

import pytest
import secrets
from core.crypto import CryptoManager


class TestCryptoManager:
    """Test CryptoManager functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.crypto = CryptoManager()
        self.test_key = secrets.token_bytes(32)  # 256-bit key
        self.test_data = "This is a test password: P@ssw0rd123!"
    
    def test_encrypt_decrypt_data(self):
        """Test data encryption and decryption"""
        # Encrypt data
        encrypted = self.crypto.encrypt_data(self.test_data, self.test_key)
        assert encrypted is not None
        assert encrypted != self.test_data
        
        # Decrypt data
        decrypted = self.crypto.decrypt_data(encrypted, self.test_key)
        assert decrypted == self.test_data
    
    def test_encrypt_decrypt_with_wrong_key(self):
        """Test decryption with wrong key fails"""
        encrypted = self.crypto.encrypt_data(self.test_data, self.test_key)
        
        # Try to decrypt with wrong key
        wrong_key = secrets.token_bytes(32)
        decrypted = self.crypto.decrypt_data(encrypted, wrong_key)
        assert decrypted is None
    
    def test_encrypt_empty_string(self):
        """Test encryption of empty string"""
        empty_data = ""
        encrypted = self.crypto.encrypt_data(empty_data, self.test_key)
        decrypted = self.crypto.decrypt_data(encrypted, self.test_key)
        assert decrypted == empty_data
    
    def test_encrypt_unicode_data(self):
        """Test encryption of unicode data"""
        unicode_data = "Test with émojis 🔒🔑 and ünïcödé characters"
        encrypted = self.crypto.encrypt_data(unicode_data, self.test_key)
        decrypted = self.crypto.decrypt_data(encrypted, self.test_key)
        assert decrypted == unicode_data
    
    def test_database_encryption_decryption(self):
        """Test database content encryption"""
        test_content = b"Database content with binary data \x00\x01\xff"
        
        # Encrypt content
        encrypted = self.crypto.encrypt_database_content(test_content, self.test_key)
        assert encrypted is not None
        assert encrypted != test_content
        assert len(encrypted) > len(test_content)  # Should be longer due to MAC + IV
        
        # Decrypt content
        decrypted = self.crypto.decrypt_database_content(encrypted, self.test_key)
        assert decrypted == test_content
    
    def test_database_encryption_with_wrong_key(self):
        """Test database decryption with wrong key fails"""
        test_content = b"Secret database content"
        encrypted = self.crypto.encrypt_database_content(test_content, self.test_key)
        
        # Try with wrong key
        wrong_key = secrets.token_bytes(32)
        decrypted = self.crypto.decrypt_database_content(encrypted, wrong_key)
        assert decrypted is None
    
    def test_database_tamper_detection(self):
        """Test that tampered database content is detected"""
        test_content = b"Original database content"
        encrypted = self.crypto.encrypt_database_content(test_content, self.test_key)
        
        # Tamper with encrypted content
        tampered = bytearray(encrypted)
        tampered[10] ^= 0xFF  # Flip bits in MAC section
        
        # Should fail to decrypt
        decrypted = self.crypto.decrypt_database_content(bytes(tampered), self.test_key)
        assert decrypted is None
    
    def test_test_vector_generation_verification(self):
        """Test test vector generation and verification"""
        # Generate test vector
        test_vector = self.crypto.generate_test_vector(self.test_key)
        assert test_vector is not None
        
        # Verify with correct key
        assert self.crypto.verify_test_vector(test_vector, self.test_key) is True
        
        # Verify with wrong key
        wrong_key = secrets.token_bytes(32)
        assert self.crypto.verify_test_vector(test_vector, wrong_key) is False
    
    def test_password_generation(self):
        """Test password generation"""
        # Test default password
        password = self.crypto.generate_password()
        assert len(password) == 16
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        
        # Test custom length
        long_password = self.crypto.generate_password(32)
        assert len(long_password) == 32
        
        # Test without symbols
        no_symbols = self.crypto.generate_password(16, include_symbols=False)
        assert len(no_symbols) == 16
        assert not any(c in "!@#$%^&*()" for c in no_symbols)
    
    def test_encryption_randomness(self):
        """Test that encryption produces different outputs for same input"""
        # Encrypt same data multiple times
        encrypted1 = self.crypto.encrypt_data(self.test_data, self.test_key)
        encrypted2 = self.crypto.encrypt_data(self.test_data, self.test_key)
        
        # Should be different due to random IV
        assert encrypted1 != encrypted2
        
        # But both should decrypt to same data
        assert self.crypto.decrypt_data(encrypted1, self.test_key) == self.test_data
        assert self.crypto.decrypt_data(encrypted2, self.test_key) == self.test_data
    
    def test_large_data_encryption(self):
        """Test encryption of large data"""
        # Create large test data (1MB)
        large_data = "x" * (1024 * 1024)
        
        encrypted = self.crypto.encrypt_data(large_data, self.test_key)
        decrypted = self.crypto.decrypt_data(encrypted, self.test_key)
        
        assert decrypted == large_data
    
    @pytest.mark.parametrize("invalid_input", [
        "invalid_base64",
        "",
        "not_json",
        "eyJpdiI6ICJpbnZhbGlkIn0="  # Valid base64 but invalid JSON structure
    ])
    def test_decrypt_invalid_data(self, invalid_input):
        """Test decryption of invalid data"""
        result = self.crypto.decrypt_data(invalid_input, self.test_key)
        assert result is None
    
    def test_secure_delete(self):
        """Test secure memory deletion"""
        # Create test data
        test_bytes = bytearray(b"sensitive data that should be overwritten")
        original_length = len(test_bytes)
        
        # Secure delete
        self.crypto.secure_delete(test_bytes)
        
        # Should still be same length but different content
        assert len(test_bytes) == original_length
        assert test_bytes != b"sensitive data that should be overwritten"