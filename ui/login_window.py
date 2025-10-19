"""
Login window for master password authentication
"""

import os
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QGroupBox, QFormLayout, 
    QCheckBox, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon

from core.db import DatabaseManager
from core.auth import AuthManager, WindowsHelloManager


class LoginWindow(QDialog):
    """Login window for existing users"""
    
    login_successful = pyqtSignal()
    
    def __init__(self, db_manager: DatabaseManager, auth_manager: AuthManager):
        super().__init__()
        
        self.db_manager = db_manager
        self.auth_manager = auth_manager
        self.logger = logging.getLogger(__name__)
        
        # Windows Hello manager
        self.windows_hello = WindowsHelloManager()
        
        # Login attempt tracking
        self.failed_attempts = 0
        self.lockout_timer = QTimer()
        self.lockout_timer.timeout.connect(self.update_lockout_display)
        
        self.init_ui()
        self.load_metadata()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Password Keeper - Login")
        self.setFixedSize(400, 350)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = self.create_header()
        layout.addLayout(header_layout)
        
        # Login form
        login_group = self.create_login_group()
        layout.addWidget(login_group)
        
        # Windows Hello section (if available)
        if self.windows_hello.is_available():
            hello_group = self.create_windows_hello_group()
            layout.addWidget(hello_group)
        
        # Lockout info
        self.lockout_frame = self.create_lockout_frame()
        layout.addWidget(self.lockout_frame)
        
        # Buttons
        button_layout = self.create_buttons()
        layout.addLayout(button_layout)
        
        # Focus on password field
        self.password_edit.setFocus()
        
    def create_header(self) -> QVBoxLayout:
        """Create header with title"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Password Keeper")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Enter your master password to unlock")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        
        return layout
    
    def create_login_group(self) -> QGroupBox:
        """Create login form group"""
        group = QGroupBox("Authentication")
        layout = QFormLayout(group)
        
        # Master password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setMinimumHeight(30)
        self.password_edit.returnPressed.connect(self.login)
        layout.addRow("Master Password:", self.password_edit)
        
        # Show password checkbox
        self.show_password_check = QCheckBox("Show password")
        self.show_password_check.toggled.connect(self.toggle_password_visibility)
        layout.addRow("", self.show_password_check)
        
        # Failed attempts info
        self.attempts_label = QLabel("")
        self.attempts_label.setStyleSheet("color: red; font-size: 10pt;")
        layout.addRow("", self.attempts_label)
        
        return group
    
    def create_windows_hello_group(self) -> QGroupBox:
        """Create Windows Hello authentication group"""
        group = QGroupBox("Windows Hello")
        layout = QVBoxLayout(group)
        
        info_label = QLabel("Use Windows Hello for quick authentication")
        info_label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(info_label)
        
        self.hello_btn = QPushButton("Authenticate with Windows Hello")
        self.hello_btn.clicked.connect(self.authenticate_with_windows_hello)
        layout.addWidget(self.hello_btn)
        
        return group
    
    def create_lockout_frame(self) -> QFrame:
        """Create lockout information frame"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("background-color: #ffe6e6; padding: 10px; border: 1px solid #ff9999;")
        frame.setVisible(False)
        
        layout = QVBoxLayout(frame)
        
        self.lockout_label = QLabel()
        self.lockout_label.setWordWrap(True)
        self.lockout_label.setStyleSheet("color: #cc0000; font-weight: bold;")
        layout.addWidget(self.lockout_label)
        
        self.lockout_progress = QProgressBar()
        self.lockout_progress.setTextVisible(False)
        layout.addWidget(self.lockout_progress)
        
        return frame
    
    def create_buttons(self) -> QHBoxLayout:
        """Create button layout"""
        layout = QHBoxLayout()
        
        layout.addStretch()
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
        
        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login)
        self.login_btn.setDefault(True)
        layout.addWidget(self.login_btn)
        
        return layout
    
    def load_metadata(self):
        """Load database metadata for verification"""
        try:
            # Try to load some basic info to verify database exists and is readable
            db_path = self.db_manager.get_db_path()
            if not db_path:
                raise Exception("Database path not found")
            
            # Update UI with any relevant info
            self.update_failed_attempts_display()
            
        except Exception as e:
            self.logger.error(f"Failed to load metadata: {e}")
            QMessageBox.critical(
                self, "Database Error",
                f"Failed to access database:\n\n{e}\n\n"
                "The database file may be corrupted or missing."
            )
            self.reject()
    
    def toggle_password_visibility(self, checked: bool):
        """Toggle password visibility"""
        echo_mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        self.password_edit.setEchoMode(echo_mode)
    
    def login(self):
        """Attempt to login with master password"""
        password = self.password_edit.text()
        
        if not password:
            QMessageBox.warning(self, "Invalid Input", "Please enter your master password.")
            return
        
        # Check if currently locked out
        remaining = self.auth_manager.get_lockout_remaining()
        if remaining > 0:
            QMessageBox.warning(
                self, "Account Locked",
                f"Too many failed attempts. Please wait {remaining} seconds before trying again."
            )
            return
        
        try:
            # Disable UI during authentication
            self.setEnabled(False)
            
            # Load encrypted database metadata first
            if not self._load_auth_metadata():
                raise Exception("Failed to load authentication data")
            
            # Attempt authentication
            success = self.auth_manager.verify_master_password(
                password, self.stored_salt, self.stored_hash
            )
            
            if success:
                # Load and verify database
                master_key = self.auth_manager.get_master_key()
                if not master_key:
                    raise Exception("Failed to get master key")
                
                # Load database
                db_loaded = self.db_manager.load_database(master_key)
                if not db_loaded:
                    raise Exception("Failed to load or decrypt database")
                
                # Verify with test vector
                test_vector = self.db_manager.get_metadata('test_vector')
                if test_vector:
                    from core.crypto import CryptoManager
                    crypto = CryptoManager()
                    if not crypto.verify_test_vector(test_vector, master_key):
                        raise Exception("Database verification failed")
                
                self.logger.info("Login successful")
                self.login_successful.emit()
                self.accept()
                
            else:
                # Failed login
                self.failed_attempts = self.auth_manager.get_failed_attempts()
                remaining = self.auth_manager.get_lockout_remaining()
                
                if remaining > 0:
                    self.start_lockout_countdown(remaining)
                    QMessageBox.warning(
                        self, "Login Failed",
                        f"Incorrect password. Account locked for {remaining} seconds due to multiple failures."
                    )
                else:
                    QMessageBox.warning(
                        self, "Login Failed",
                        f"Incorrect master password. Attempt {self.failed_attempts}."
                    )
                
                self.update_failed_attempts_display()
                self.password_edit.clear()
                self.password_edit.setFocus()
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            QMessageBox.critical(self, "Login Error", f"Login failed:\n\n{e}")
            
        finally:
            self.setEnabled(True)
    
    def authenticate_with_windows_hello(self):
        """Authenticate using Windows Hello"""
        if not self.windows_hello.is_available():
            QMessageBox.warning(self, "Not Available", "Windows Hello is not available.")
            return
        
        # TODO: Implement Windows Hello authentication
        # This would require storing encrypted master password that can be
        # decrypted only after Windows Hello verification
        QMessageBox.information(
            self, "Coming Soon", 
            "Windows Hello authentication is not yet implemented."
        )
    
    def _load_auth_metadata(self) -> bool:
        """Load authentication metadata from database file"""
        try:
            # Check if database file exists
            db_path = self.db_manager.get_db_path()
            if not os.path.exists(db_path):
                self.logger.error(f"Database file does not exist: {db_path}")
                return False
            
            # Check file size
            file_size = os.path.getsize(db_path)
            if file_size < 16:  # Minimum size for header
                self.logger.error(f"Database file too small: {file_size} bytes")
                return False
            
            # Get salt and password hash from database file header
            self.stored_salt, self.stored_hash = self.db_manager.get_auth_metadata()
            
            self.logger.info("Authentication metadata loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load auth metadata: {e}")
            # Show user-friendly error message
            QMessageBox.critical(
                self, "Database Error",
                f"Failed to load database authentication data.\n\n"
                f"Error: {str(e)}\n\n"
                f"The database file may be corrupted or in an incompatible format.\n"
                f"You may need to restore from a backup or start fresh."
            )
            return False
    
    def update_failed_attempts_display(self):
        """Update the failed attempts display"""
        attempts = self.auth_manager.get_failed_attempts()
        if attempts > 0:
            self.attempts_label.setText(f"Failed attempts: {attempts}")
        else:
            self.attempts_label.setText("")
    
    def start_lockout_countdown(self, seconds: int):
        """Start lockout countdown timer"""
        self.lockout_progress.setMaximum(seconds)
        self.lockout_progress.setValue(seconds)
        
        self.lockout_frame.setVisible(True)
        self.login_btn.setEnabled(False)
        
        if self.windows_hello.is_available():
            self.hello_btn.setEnabled(False)
        
        self.lockout_timer.start(1000)  # Update every second
    
    def update_lockout_display(self):
        """Update lockout countdown display"""
        remaining = self.auth_manager.get_lockout_remaining()
        
        if remaining <= 0:
            # Lockout expired
            self.lockout_timer.stop()
            self.lockout_frame.setVisible(False)
            self.login_btn.setEnabled(True)
            
            if self.windows_hello.is_available():
                self.hello_btn.setEnabled(True)
            
            self.password_edit.setFocus()
        else:
            # Update countdown
            self.lockout_label.setText(
                f"Account locked due to multiple failed attempts.\n"
                f"Please wait {remaining} seconds before trying again."
            )
            self.lockout_progress.setValue(remaining)
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.login_btn.isEnabled():
                self.login()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop any running timers
        if self.lockout_timer.isActive():
            self.lockout_timer.stop()
        
        # Clear sensitive data
        self.password_edit.clear()
        
        event.accept()