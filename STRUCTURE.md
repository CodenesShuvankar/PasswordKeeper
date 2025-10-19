# Password Keeper - Project Structure

```
PasswordKeeper/
├── core/                    # Core functionality modules
│   ├── __init__.py         # Package initialization
│   ├── auth.py             # Authentication management
│   ├── crypto.py           # Encryption/decryption functions
│   ├── db.py               # Database operations
│   └── utils.py            # Utility functions
├── ui/                     # User interface modules
│   ├── __init__.py         # Package initialization
│   ├── main_window.py      # Main application window
│   ├── login_window.py     # Login/master password window
│   ├── setup_window.py     # Initial setup window
│   ├── credential_dialog.py # Add/edit credential dialog
│   ├── credential_view_dialog.py # View credential dialog
│   ├── password_generator.py # Password generator dialog
│   ├── settings_dialog.py  # Application settings dialog
│   └── change_password_dialog.py # Change master password dialog
├── tests/                  # Test suite
│   ├── conftest.py         # Test configuration
│   └── test_crypto.py      # Cryptography tests
├── data/                   # User data directory
│   ├── README.md           # Data directory documentation
│   └── credentials.db      # Encrypted database (created at runtime)
├── resources/              # Application resources
│   └── README.md           # Resources documentation
├── main.py                 # Application entry point
├── build.py                # Build script for portable executable
├── launcher.bat            # Windows batch launcher
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── README.md               # Project documentation
└── .gitignore              # Git ignore rules
```

## Module Descriptions

### Core Modules
- **auth.py**: Handles master password authentication and session management
- **crypto.py**: Provides AES-256-GCM encryption with PBKDF2 key derivation
- **db.py**: SQLite database operations with encryption integration
- **utils.py**: Clipboard management, settings, and utility functions

### UI Modules
- **main_window.py**: Main application interface with sidebar navigation
- **login_window.py**: Secure master password entry
- **setup_window.py**: First-time setup and master password creation
- **credential_dialog.py**: Add/edit credential forms
- **password_generator.py**: Customizable password generation
- **settings_dialog.py**: Application configuration

### Build System
- **build.py**: Creates portable Windows executable with PyInstaller
- **requirements.txt**: Minimal production dependencies (PyQt6, cryptography, openpyxl)
- **requirements-dev.txt**: Full development environment

### Security Design
- Encrypted SQLite database with HMAC verification
- Master password protects all credentials
- Secure memory handling and auto-lock functionality
- Export excludes passwords for security