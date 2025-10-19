"""
Authentication and master password handling
"""

import os
import hashlib
import secrets
import logging
from typing import Optional, Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import time


class AuthManager:
    """Manages authentication and master password operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.master_key: Optional[bytes] = None
        self.failed_attempts = 0
        self.last_attempt_time = 0
        self.lockout_duration = 1  # Start with 1 second
        
    def create_master_password(self, password: str) -> Tuple[bytes, bytes]:
        """
        Create a new master password with salt and derive key
        
        Args:
            password: Master password string
            
        Returns:
            Tuple of (salt, password_hash) for storage
        """
        # Generate random salt
        salt = secrets.token_bytes(32)
        
        # Create password hash for verification
        password_hash = self._hash_password(password, salt)
        
        # Derive encryption key
        self.master_key = self._derive_key(password, salt)
        
        self.logger.info("Master password created successfully")
        return salt, password_hash
    
    def verify_master_password(self, password: str, stored_salt: bytes, stored_hash: bytes) -> bool:
        """
        Verify master password against stored credentials
        
        Args:
            password: Password to verify
            stored_salt: Salt from database
            stored_hash: Hash from database
            
        Returns:
            True if password is correct
        """
        # Check for lockout
        if self._is_locked_out():
            remaining = self._get_lockout_remaining()
            self.logger.warning(f"Login attempt during lockout - {remaining}s remaining")
            return False
        
        # Hash provided password with stored salt
        password_hash = self._hash_password(password, stored_salt)
        
        # Compare hashes
        if secrets.compare_digest(password_hash, stored_hash):
            # Success - derive key and reset failed attempts
            self.master_key = self._derive_key(password, stored_salt)
            self.failed_attempts = 0
            self.lockout_duration = 1
            self.logger.info("Master password verified successfully")
            return True
        else:
            # Failed attempt - implement exponential backoff
            self._handle_failed_attempt()
            return False
    
    def change_master_password(self, old_password: str, new_password: str, 
                             stored_salt: bytes, stored_hash: bytes) -> Optional[Tuple[bytes, bytes]]:
        """
        Change master password
        
        Args:
            old_password: Current password
            new_password: New password
            stored_salt: Current salt
            stored_hash: Current hash
            
        Returns:
            New (salt, hash) tuple if successful, None if old password incorrect
        """
        # Verify old password
        if not self.verify_master_password(old_password, stored_salt, stored_hash):
            return None
        
        # Create new credentials
        return self.create_master_password(new_password)
    
    def get_master_key(self) -> Optional[bytes]:
        """Get the current master key"""
        return self.master_key
    
    def clear_master_key(self):
        """Clear master key from memory"""
        if self.master_key:
            # Overwrite memory
            self.master_key = b'\x00' * len(self.master_key)
            self.master_key = None
        self.logger.info("Master key cleared from memory")
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Password string
            salt: Salt bytes
            
        Returns:
            32-byte encryption key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # High iteration count for security
            backend=default_backend()
        )
        
        return kdf.derive(password.encode('utf-8'))
    
    def _hash_password(self, password: str, salt: bytes) -> bytes:
        """
        Hash password with salt for storage
        
        Args:
            password: Password string
            salt: Salt bytes
            
        Returns:
            Password hash
        """
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    
    def _handle_failed_attempt(self):
        """Handle failed login attempt with exponential backoff"""
        self.failed_attempts += 1
        self.last_attempt_time = time.time()
        
        # Exponential backoff: 1s, 2s, 4s, 8s, etc., max 5 minutes
        self.lockout_duration = min(2 ** (self.failed_attempts - 1), 300)
        
        self.logger.warning(f"Failed login attempt #{self.failed_attempts}, "
                          f"lockout for {self.lockout_duration}s")
    
    def _is_locked_out(self) -> bool:
        """Check if currently locked out"""
        if self.failed_attempts == 0:
            return False
        
        elapsed = time.time() - self.last_attempt_time
        return elapsed < self.lockout_duration
    
    def _get_lockout_remaining(self) -> int:
        """Get remaining lockout time in seconds"""
        if not self._is_locked_out():
            return 0
        
        elapsed = time.time() - self.last_attempt_time
        return max(0, int(self.lockout_duration - elapsed))
    
    def get_failed_attempts(self) -> int:
        """Get number of failed attempts"""
        return self.failed_attempts
    
    def get_lockout_remaining(self) -> int:
        """Get remaining lockout time (public method)"""
        return self._get_lockout_remaining()


# Windows Hello integration (optional)
try:
    import winrt.windows.security.credentials.ui as ui
    WINDOWS_HELLO_AVAILABLE = True
except ImportError:
    WINDOWS_HELLO_AVAILABLE = False


class WindowsHelloManager:
    """Windows Hello biometric authentication manager"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available = WINDOWS_HELLO_AVAILABLE
        
    def is_available(self) -> bool:
        """Check if Windows Hello is available"""
        if not self.available:
            return False
        
        try:
            # Check if user consent verifier is available
            availability = ui.UserConsentVerifier.check_availability_async().get()
            return availability == ui.UserConsentVerifierAvailability.AVAILABLE
        except Exception as e:
            self.logger.error(f"Windows Hello availability check failed: {e}")
            return False
    
    async def verify_user(self, message: str = "Verify your identity") -> bool:
        """
        Verify user with Windows Hello
        
        Args:
            message: Message to show to user
            
        Returns:
            True if verification successful
        """
        if not self.is_available():
            return False
        
        try:
            result = await ui.UserConsentVerifier.request_verification_async(message)
            success = result == ui.UserConsentVerificationResult.VERIFIED
            
            if success:
                self.logger.info("Windows Hello verification successful")
            else:
                self.logger.warning("Windows Hello verification failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Windows Hello verification error: {e}")
            return False