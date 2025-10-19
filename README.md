# 🔐 Password Keeper

A secure, modern password manager for Windows with advanced encryption and an intuitive PyQt6 GUI.

## ✨ Features

- 🔒 AES-256-GCM encryption with PBKDF2 key derivation
- 🎯 Master password protects all credentials
- 🎨 Modern GUI with sidebar navigation
- ⏰ Auto-lock after inactivity
- 📋 Smart clipboard with auto-clear
- 🎲 Strong password generator
- 🔍 Fast search and filtering
- 📊 Excel import/export
- 💾 Portable build (no installation)
- 🧠 Secure memory handling

## 🖼️ UI Preview

<p align="center">
	<img src="UiDesign%20Image/Main%20UI.png" alt="Main UI" width="48%" />
	<img src="UiDesign%20Image/Add%20credentials%20.png" alt="Add Credential Dialog" width="48%" />
</p>
<p align="center">
	<img src="UiDesign%20Image/credentials%20password%20set.png" alt="Password Generator / Set Password" width="48%" />
	<img src="UiDesign%20Image/Credential%20details.png" alt="Credential Details View" width="48%" />
</p>

## 🛡️ Security Features

### Encryption
- AES-256-GCM: Authenticated encryption for data protection
- PBKDF2: 100,000+ iterations for key derivation
- Random salt per database
- HMAC verification to detect tampering

### Access Control
- Master password required to unlock
- Exponential backoff on failed logins
- Auto-lock on inactivity
- Secure memory handling and cleanup

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (primary target)
- ~50MB free disk space

### Install from Source

1) Clone the repository
```bash
git clone https://github.com/yourusername/password-keeper.git
cd password-keeper
```

2) Create virtual environment
```bash
python -m venv venv
```

3) Activate and install dependencies
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

## 🚀 Quick Start

### Option 1: Download Portable Executable (Recommended)
1. Download the latest `PasswordKeeper_Portable.zip` from releases
2. Extract to any folder
3. Run `PasswordKeeper.exe` — no installation required

### Option 2: Run from Source
```bash
# Clone repository
git clone https://github.com/yourusername/password-keeper.git
cd password-keeper

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Option 3: Build Your Own Executable
```bash
# Build portable executable
python build.py

# The portable package will be in PasswordKeeper_Portable/
```

## 📖 Usage

### First Time Setup
1. Launch the app (exe or `python main.py`)
2. Create a strong master password
3. Add your first credential

### Daily Workflow
1. 🔓 Unlock with master password
2. ➕ Add credentials from the sidebar
3. 🔍 Search and filter
4. 📋 Copy username/password (auto-clears clipboard)
5. 📤 Import/Export via Excel
6. 🔒 Auto-lock after inactivity

### Excel Import/Export
- Export creates an Excel file (passwords excluded by default)
- Import supports Title, Username, URL, Category, Notes, Password columns
- Required minimum columns: Title and Username

## File Structure

```
PasswordKeeper/
├── main.py                 # Application entry point
├── core/                   # Core functionality
│   ├── auth.py             # Authentication and master password
│   ├── crypto.py           # Cryptographic operations
│   ├── db.py               # Database management
│   └── utils.py            # Utility functions
├── ui/                     # User interface
│   ├── main_window.py      # Main application window
│   ├── setup_window.py     # Initial setup dialog
│   ├── login_window.py     # Login dialog
│   ├── credential_dialog.py# Add/edit credentials
│   ├── password_generator.py# Password generator
│   └── settings_dialog.py  # Settings configuration
├── resources/              # Icons and resources
├── tests/                  # Unit and integration tests
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Database Location

- Windows: `%APPDATA%\PasswordKeeper\passwords.db`
- Portable Mode: Same directory as the executable (when `portable.txt` exists)

## Security Best Practices

### Master Password
- Use a strong, unique master password (passphrase recommended)
- Never share your master password
- Use the password strength indicator as guidance

### General Security
- Keep the application updated
- Use auto-lock to protect against unauthorized access
- Avoid running on shared/untrusted computers
- Create regular backups of your database

### Backup Strategy
1. Make regular backups
2. Test restores occasionally
3. Keep backups in multiple locations
4. Keep backups encrypted

## Development

### Setup
```bash
pip install -r requirements.txt
pip install pytest pytest-qt pytest-cov black flake8 mypy
```

### Run tests
```bash
pytest tests/ -v --cov=core --cov=ui
```

### Format & lint
```bash
black .
flake8 .
mypy .
```

## Security Considerations

### Threat Model
- Data theft: Encrypted storage
- Shoulder surfing: Auto-clearing clipboard and hidden passwords
- Brute force: Exponential backoff
- Memory dumps: Secure memory handling
- File tampering: HMAC verification

### Known Limitations
- No recovery if master password is forgotten
- Key derivation currently PBKDF2 (may upgrade)
- Optimized for Windows desktop
- Single-user, no sync

## License

MIT — see [LICENSE](LICENSE)

## Acknowledgments

- cryptography — Python crypto library
- PyQt6 — cross‑platform GUI toolkit
- SQLite — embedded database engine

# 🔐 Password Keeper

A secure, modern password manager for Windows with advanced encryption and intuitive GUI.

## ✨ Features

- **🔒 Secure Encryption**: AES-256-GCM encryption with PBKDF2 key derivation
- **🎯 Master Password Protection**: Single master password protects all credentials  
- **🎨 Modern GUI**: Beautiful PyQt6 interface with sidebar navigation
- **⏰ Auto-Lock**: Automatic locking after inactivity
- **📋 Smart Clipboard**: Auto-clearing clipboard for password security
- **🎲 Password Generator**: Strong password generation with customizable options
- **🔍 Search & Filter**: Quick credential search and category filtering
- **📊 Excel Import/Export**: Import from and export to Excel files
- **💾 Portable**: Self-contained executable, no installation required
- **🔐 Secure Memory**: Memory protection and secure data wiping

## 🛡️ Security Features

### Encryption
- **AES-256-GCM**: Authenticated encryption for data protection
- **PBKDF2**: 100,000 iterations for key derivation  
- **Random Salt**: Unique salt for each database
- **HMAC Verification**: Detects file tampering

### Access Control
- **Master Password**: Single password protects everything
- **Failed Attempt Protection**: Exponential backoff on failed logins
- **Auto-Lock**: Configurable inactivity timeout
- **Memory Protection**: Secure memory handling and cleanup

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (primary target)
- 50MB free disk space

### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/password-keeper.git
cd password-keeper
```

2. Create virtual environment:
```bash
python -m venv venv
## 🚀 Quick Start

### Option 1: Download Portable Executable (Recommended)
1. Download the latest `PasswordKeeper_Portable.zip` from releases
2. Extract to any folder
3. Run `PasswordKeeper.exe` - no installation required!

### Option 2: Run from Source
```bash
# Clone repository
git clone https://github.com/yourusername/password-keeper.git
cd password-keeper

# Install dependencies  
pip install -r requirements.txt

# Run application
python main.py
```

### Option 3: Build Your Own Executable
```bash
# Install dependencies including build tools
pip install -r requirements-dev.txt

# Build portable executable
python build.py

# Find executable in dist/PasswordKeeper_Portable/
```

## 📖 Usage

### First Time Setup
1. **Launch Application**: Run the executable or `python main.py`
2. **Create Master Password**: Choose a strong master password (this protects everything!)
3. **Start Adding Credentials**: Click "Add Credential" in the sidebar

### Daily Workflow
1. **🔓 Login**: Enter your master password to unlock
2. **➕ Add Credentials**: Use the sidebar "Add Credential" button
3. **🔍 Search & Filter**: Use search bar and category filter dropdown
4. **📋 Copy Data**: Click username/password buttons to copy securely
5. **📤 Export/Import**: Use sidebar buttons for Excel import/export
6. **🔒 Auto-Lock**: Application locks automatically after inactivity

### Excel Import/Export
- **Export**: Creates Excel file with all credentials (passwords excluded for security)
- **Import**: Reads Excel files with Title, Username, URL, Category, Notes, Password columns
- **Required columns**: Title and Username (minimum)
- **Security**: Exported files don't include passwords by default

Configure application behavior:
- **Auto-lock timeout**: Set inactivity timeout (1-60 minutes)
- **Clipboard timeout**: Auto-clear clipboard (5-300 seconds)
- **Password defaults**: Set default generator options
- **Interface options**: Theme and display preferences

## File Structure

```
PasswordKeeper/
├── main.py                 # Application entry point
├── core/                   # Core functionality
│   ├── auth.py            # Authentication and master password
│   ├── crypto.py          # Cryptographic operations
│   ├── db.py              # Database management
│   └── utils.py           # Utility functions
├── ui/                     # User interface
│   ├── main_window.py     # Main application window
│   ├── setup_window.py    # Initial setup dialog
│   ├── login_window.py    # Login dialog
│   ├── credential_dialog.py # Add/edit credentials
│   ├── password_generator.py # Password generator
│   └── settings_dialog.py # Settings configuration
├── resources/              # Icons and resources
├── tests/                  # Unit and integration tests
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Database Location

The encrypted database is stored in:
- **Windows**: `%APPDATA%\PasswordKeeper\passwords.db`
- **Portable Mode**: Same directory as executable (if `portable.txt` exists)

## Security Best Practices

### Master Password
- Use a strong, unique master password
- Consider using a passphrase with multiple words
- Never share or write down your master password
- Use password strength indicator as guidance

### General Security
- Keep the application updated
- Use auto-lock to protect against unauthorized access
- Don't run on shared or untrusted computers
- Create regular backups of your database
- Verify application integrity (check file signatures)

### Backup Strategy
1. **Regular Backups**: Copy database file to secure location
2. **Test Restore**: Verify backups can be restored
3. **Multiple Locations**: Store backups in different locations
4. **Encryption**: Keep backups encrypted

## Development

### Setting up Development Environment

1. Clone repository and create virtual environment
2. Install development dependencies:
```bash
pip install -r requirements.txt
pip install pytest pytest-qt pytest-cov black flake8 mypy
```

3. Run tests:
```bash
pytest tests/ -v --cov=core --cov=ui
```

4. Code formatting:
```bash
black .
flake8 .
mypy .
```

### Testing

The application includes comprehensive tests:
- **Unit Tests**: Core functionality (crypto, auth, database)
- **Integration Tests**: Component interaction
- **GUI Tests**: User interface testing with pytest-qt
- **Security Tests**: Cryptographic verification

Run specific test categories:
```bash
# Unit tests only
pytest tests/unit/ -v

# GUI tests only
pytest tests/gui/ -v

# Security tests only
pytest tests/security/ -v
```

### Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Ensure all tests pass
5. Submit pull request

## Security Considerations

### Threat Model

This application protects against:
- **Data theft**: Encrypted storage prevents access to raw passwords
- **Shoulder surfing**: Auto-clearing clipboard and hidden passwords
- **Brute force**: Exponential backoff on failed attempts
- **Memory dumps**: Secure memory handling
- **File tampering**: HMAC verification

### Known Limitations

- **Master password recovery**: No recovery mechanism if forgotten
- **Key derivation**: Fixed to PBKDF2 (may need upgrade in future)
- **Platform specific**: Optimized for Windows only
- **Single user**: No multi-user support
- **Network**: No cloud sync or network features

### Reporting Security Issues

Please report security vulnerabilities privately:
- Email: security@yourproject.com
- Include detailed description and steps to reproduce
- Allow reasonable time for response before public disclosure

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **cryptography**: Python cryptographic library
- **PyQt6**: Cross-platform GUI toolkit
- **SQLite**: Embedded database engine
- **Security research**: Various cryptographic best practices

## Support

- **Documentation**: See docs/ folder for detailed guides
- **Issues**: Report bugs on GitHub issues page
- **Discussions**: Use GitHub discussions for questions
- **Updates**: Check releases page for latest versions

## Version History

### v1.0.0 (Initial Release)
- Core password management functionality
- AES-256-GCM encryption with PBKDF2
- Modern PyQt6 user interface
- Password generator with customizable options
- Auto-lock and clipboard security
- Comprehensive test suite
- Windows executable packaging