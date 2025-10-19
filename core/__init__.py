"""
Core package initialization
"""

from .auth import AuthManager, WindowsHelloManager
from .crypto import CryptoManager
from .db import DatabaseManager
from .utils import (
    ClipboardManager, 
    InactivityTimer, 
    PasswordStrengthChecker,
    SecureString,
    SettingsManager,
    get_app_data_dir,
    setup_logging
)

__all__ = [
    'AuthManager',
    'WindowsHelloManager', 
    'CryptoManager',
    'DatabaseManager',
    'ClipboardManager',
    'InactivityTimer',
    'PasswordStrengthChecker',
    'SecureString',
    'SettingsManager',
    'get_app_data_dir',
    'setup_logging'
]