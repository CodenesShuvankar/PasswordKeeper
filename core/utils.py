"""
Utility functions and helpers
"""

import os
import sys
import logging
import platform
from typing import Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QClipboard
import threading
import time


def get_app_data_dir() -> str:
    """Get application data directory - supports portable mode"""
    
    # Check if running in portable mode
    if is_portable_mode():
        # In portable mode, store data in 'data' subfolder next to executable
        if hasattr(sys, 'frozen'):
            # Running as compiled executable
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script (development)
            app_dir = os.path.dirname(os.path.abspath(__file__))
            app_dir = os.path.dirname(app_dir)  # Go up to project root
        
        data_dir = os.path.join(app_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    # Standard installation mode
    if platform.system() == "Windows":
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        app_dir = os.path.join(app_data, 'PasswordKeeper')
    else:
        # For cross-platform support
        app_dir = os.path.join(os.path.expanduser('~'), '.passwordkeeper')
    
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


def setup_logging():
    """Setup application logging - supports portable mode"""
    app_dir = get_app_data_dir()
    
    # In portable mode, also create logs directory
    if is_portable_mode():
        log_dir = os.path.join(os.path.dirname(app_dir), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'passwordkeeper.log')
    else:
        log_file = os.path.join(app_dir, 'passwordkeeper.log')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Limit log file size
    if os.path.exists(log_file) and os.path.getsize(log_file) > 10 * 1024 * 1024:  # 10MB
        # Rotate log file
        backup_file = log_file + '.bak'
        if os.path.exists(backup_file):
            os.remove(backup_file)
        os.rename(log_file, backup_file)


class ClipboardManager:
    """Manages clipboard operations with auto-clear functionality"""
    
    def __init__(self, auto_clear_seconds: int = 30):
        self.auto_clear_seconds = auto_clear_seconds
        self.logger = logging.getLogger(__name__)
        self.clear_timer = None
        self.last_copied_text = None
        
    def copy_to_clipboard(self, text: str, auto_clear: bool = True):
        """
        Copy text to clipboard with optional auto-clear
        
        Args:
            text: Text to copy
            auto_clear: Whether to auto-clear after timeout
        """
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.last_copied_text = text
            
            self.logger.info("Text copied to clipboard")
            
            if auto_clear:
                self._start_clear_timer()
                
        except Exception as e:
            self.logger.error(f"Failed to copy to clipboard: {e}")
    
    def clear_clipboard(self):
        """Clear clipboard if it contains our text"""
        try:
            clipboard = QApplication.clipboard()
            current_text = clipboard.text()
            
            # Only clear if clipboard still contains our text
            if current_text == self.last_copied_text:
                clipboard.clear()
                self.logger.info("Clipboard cleared")
            
            self.last_copied_text = None
            
        except Exception as e:
            self.logger.error(f"Failed to clear clipboard: {e}")
    
    def _start_clear_timer(self):
        """Start timer to auto-clear clipboard"""
        if self.clear_timer:
            self.clear_timer.stop()
        
        self.clear_timer = QTimer()
        self.clear_timer.timeout.connect(self.clear_clipboard)
        self.clear_timer.setSingleShot(True)
        self.clear_timer.start(self.auto_clear_seconds * 1000)
        
        self.logger.info(f"Clipboard will be cleared in {self.auto_clear_seconds} seconds")
    
    def set_auto_clear_seconds(self, seconds: int):
        """Set auto-clear timeout"""
        self.auto_clear_seconds = seconds


class InactivityTimer:
    """Monitors user inactivity and triggers auto-lock"""
    
    def __init__(self, timeout_minutes: int = 5):
        self.timeout_minutes = timeout_minutes
        self.logger = logging.getLogger(__name__)
        self.timer = None
        self.callback = None
        self.enabled = True
        
    def start(self, callback):
        """
        Start inactivity monitoring
        
        Args:
            callback: Function to call on timeout
        """
        self.callback = callback
        self._reset_timer()
        
    def stop(self):
        """Stop inactivity monitoring"""
        if self.timer:
            self.timer.stop()
            self.timer = None
    
    def reset(self):
        """Reset inactivity timer"""
        if self.enabled:
            self._reset_timer()
    
    def set_timeout(self, minutes: int):
        """Set inactivity timeout"""
        self.timeout_minutes = minutes
        if self.timer and self.timer.isActive():
            self._reset_timer()
    
    def set_enabled(self, enabled: bool):
        """Enable/disable inactivity monitoring"""
        self.enabled = enabled
        if not enabled:
            self.stop()
        elif self.callback:
            self.start(self.callback)
    
    def _reset_timer(self):
        """Reset the inactivity timer"""
        if self.timer:
            self.timer.stop()
        
        if self.enabled and self.callback:
            self.timer = QTimer()
            self.timer.timeout.connect(self._on_timeout)
            self.timer.setSingleShot(True)
            self.timer.start(self.timeout_minutes * 60 * 1000)
    
    def _on_timeout(self):
        """Handle inactivity timeout"""
        self.logger.info("Inactivity timeout reached")
        if self.callback:
            self.callback()


class PasswordStrengthChecker:
    """Checks password strength and provides feedback"""
    
    @staticmethod
    def check_strength(password: str) -> dict:
        """
        Check password strength
        
        Args:
            password: Password to check
            
        Returns:
            Dictionary with strength info
        """
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        else:
            feedback.append("Use at least 8 characters")
        
        # Character variety checks
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(not c.isalnum() for c in password)
        
        variety_count = sum([has_lower, has_upper, has_digit, has_symbol])
        score += variety_count
        
        if not has_lower:
            feedback.append("Add lowercase letters")
        if not has_upper:
            feedback.append("Add uppercase letters")
        if not has_digit:
            feedback.append("Add numbers")
        if not has_symbol:
            feedback.append("Add special characters")
        
        # Common patterns check
        common_patterns = ['123', 'abc', 'password', 'qwerty', '000']
        if any(pattern in password.lower() for pattern in common_patterns):
            score -= 2
            feedback.append("Avoid common patterns")
        
        # Determine strength level
        if score >= 6:
            strength = "Strong"
            color = "green"
        elif score >= 4:
            strength = "Medium"
            color = "orange"
        else:
            strength = "Weak"
            color = "red"
        
        return {
            'score': max(0, score),
            'strength': strength,
            'color': color,
            'feedback': feedback
        }


class SecureString:
    """Secure string handling with memory protection"""
    
    def __init__(self, value: str = ""):
        self._data = bytearray(value.encode('utf-8'))
        
    def __str__(self) -> str:
        return self._data.decode('utf-8')
    
    def __len__(self) -> int:
        return len(self._data)
    
    def clear(self):
        """Securely clear the string from memory"""
        if self._data:
            # Overwrite with random data
            import secrets
            for i in range(len(self._data)):
                self._data[i] = secrets.randbits(8)
            # Then zero out
            for i in range(len(self._data)):
                self._data[i] = 0
            self._data.clear()
    
    def __del__(self):
        """Clear on destruction"""
        self.clear()


def format_bytes(bytes_size: int) -> str:
    """Format bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_url(url: str) -> bool:
    """Basic URL validation"""
    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None


class SettingsManager:
    """Manages application settings - supports portable mode"""
    
    def __init__(self):
        # Get appropriate settings file location
        if is_portable_mode():
            # Store settings in the app directory for portable mode
            if hasattr(sys, 'frozen'):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.settings_file = os.path.join(app_dir, 'settings.json')
        else:
            # Standard location
            self.settings_file = os.path.join(get_app_data_dir(), 'settings.json')
        
        self.default_settings = {
            'clipboard_auto_clear_seconds': 30,
            'inactivity_timeout_minutes': 5,
            'auto_lock_on_minimize': True,
            'password_generator_length': 16,
            'password_generator_symbols': True,
            'theme': 'default',
            'window_remember_size': True,
            'window_width': 800,
            'window_height': 600,
            'backup_enabled': True,
            'backup_count': 5,
            'portable_mode': is_portable_mode(),  # Track portable mode
            'first_run': True
        }
        self.settings = self.load_settings()
    
    def load_settings(self) -> dict:
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                import json
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                # Merge with defaults to handle new settings
                settings = self.default_settings.copy()
                settings.update(loaded_settings)
                return settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to load settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self) -> bool:
        """Save settings to file"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            import json
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to save settings: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Get setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set setting value"""
        self.settings[key] = value
        self.save_settings()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.default_settings.copy()
        self.save_settings()


def is_portable_mode() -> bool:
    """Check if running in portable mode"""
    # Check if running from a portable installation
    if hasattr(sys, 'frozen'):
        # Running as compiled executable
        exe_dir = os.path.dirname(sys.executable)
    else:
        # Running as script (development)
        exe_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    portable_marker = os.path.join(exe_dir, 'portable.txt')
    return os.path.exists(portable_marker)


def get_version() -> str:
    """Get application version"""
    return "1.0.0"


def get_build_info() -> dict:
    """Get build information"""
    return {
        'version': get_version(),
        'python_version': sys.version,
        'platform': platform.platform(),
        'architecture': platform.architecture()[0]
    }