"""
Initial setup window for creating master password
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QProgressBar, QMessageBox, QGroupBox,
    QFormLayout, QCheckBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

from core.db import DatabaseManager
from core.auth import AuthManager
from core.utils import PasswordStrengthChecker


class SetupWindow(QDialog):
    """Initial setup window for first-time users"""
    
    setup_complete = pyqtSignal()
    
    def __init__(self, db_manager: DatabaseManager, auth_manager: AuthManager):
        super().__init__()
        
        self.db_manager = db_manager
        self.auth_manager = auth_manager
        self.logger = logging.getLogger(__name__)
        self.strength_checker = PasswordStrengthChecker()
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Password Keeper - Initial Setup")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = self.create_header()
        layout.addLayout(header_layout)
        
        # Instructions
        instructions = self.create_instructions()
        layout.addWidget(instructions)
        
        # Password input group
        password_group = self.create_password_group()
        layout.addWidget(password_group)
        
        # Buttons
        button_layout = self.create_buttons()
        layout.addLayout(button_layout)
        
        # Connect signals
        self.password_edit.textChanged.connect(self.check_password_strength)
        self.confirm_edit.textChanged.connect(self.validate_passwords)
        
    def create_header(self) -> QVBoxLayout:
        """Create header with title and icon"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Welcome to Password Keeper")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Secure Password Manager")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        
        return layout
    
    def create_instructions(self) -> QFrame:
        """Create instructions frame"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
        
        layout = QVBoxLayout(frame)
        
        instructions = QLabel(
            "This is your first time using Password Keeper. To get started, you need to create "
            "a master password that will protect all your stored passwords.\n\n"
            "⚠️ Important: Make sure to remember this password as it cannot be recovered!"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        return frame
    
    def create_password_group(self) -> QGroupBox:
        """Create password input group"""
        group = QGroupBox("Create Master Password")
        layout = QFormLayout(group)
        
        # Master password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setMinimumHeight(30)
        layout.addRow("Master Password:", self.password_edit)
        
        # Password strength indicator
        self.strength_label = QLabel("Password strength will appear here")
        self.strength_label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addRow("", self.strength_label)
        
        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximum(6)
        self.strength_bar.setValue(0)
        self.strength_bar.setVisible(False)
        layout.addRow("", self.strength_bar)
        
        # Confirm password
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_edit.setMinimumHeight(30)
        layout.addRow("Confirm Password:", self.confirm_edit)
        
        # Password match indicator
        self.match_label = QLabel("")
        layout.addRow("", self.match_label)
        
        # Show password checkbox
        self.show_password_check = QCheckBox("Show passwords")
        self.show_password_check.toggled.connect(self.toggle_password_visibility)
        layout.addRow("", self.show_password_check)
        
        return group
    
    def create_buttons(self) -> QHBoxLayout:
        """Create button layout"""
        layout = QHBoxLayout()
        
        layout.addStretch()
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
        
        # Create button
        self.create_btn = QPushButton("Create Master Password")
        self.create_btn.clicked.connect(self.create_master_password)
        self.create_btn.setEnabled(False)
        self.create_btn.setDefault(True)
        layout.addWidget(self.create_btn)
        
        return layout
    
    def check_password_strength(self):
        """Check and display password strength"""
        password = self.password_edit.text()
        
        if not password:
            self.strength_label.setText("Password strength will appear here")
            self.strength_label.setStyleSheet("color: gray; font-size: 10pt;")
            self.strength_bar.setVisible(False)
            self.validate_passwords()
            return
        
        strength_info = self.strength_checker.check_strength(password)
        
        # Update strength label
        feedback_text = strength_info['strength']
        if strength_info['feedback']:
            feedback_text += " - " + ", ".join(strength_info['feedback'])
        
        self.strength_label.setText(feedback_text)
        
        # Set color based on strength
        color = strength_info['color']
        self.strength_label.setStyleSheet(f"color: {color}; font-size: 10pt;")
        
        # Update progress bar
        self.strength_bar.setValue(strength_info['score'])
        self.strength_bar.setVisible(True)
        
        # Set progress bar color
        if strength_info['strength'] == "Strong":
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        elif strength_info['strength'] == "Medium":
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        
        self.validate_passwords()
    
    def validate_passwords(self):
        """Validate password confirmation and enable/disable create button"""
        password = self.password_edit.text()
        confirm = self.confirm_edit.text()
        
        # Check if passwords match
        if not confirm:
            self.match_label.setText("")
            self.create_btn.setEnabled(False)
            return
        
        if password == confirm:
            self.match_label.setText("✓ Passwords match")
            self.match_label.setStyleSheet("color: green; font-size: 10pt;")
            
            # Enable create button if password is at least medium strength
            strength_info = self.strength_checker.check_strength(password)
            self.create_btn.setEnabled(
                len(password) >= 8 and 
                strength_info['score'] >= 3
            )
        else:
            self.match_label.setText("✗ Passwords don't match")
            self.match_label.setStyleSheet("color: red; font-size: 10pt;")
            self.create_btn.setEnabled(False)
    
    def toggle_password_visibility(self, checked: bool):
        """Toggle password visibility"""
        echo_mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        self.password_edit.setEchoMode(echo_mode)
        self.confirm_edit.setEchoMode(echo_mode)
    
    def create_master_password(self):
        """Create master password and initialize database"""
        password = self.password_edit.text()
        
        if len(password) < 8:
            QMessageBox.warning(self, "Invalid Password", 
                              "Password must be at least 8 characters long.")
            return
        
        # Confirm the user understands the importance
        reply = QMessageBox.question(
            self, "Confirm Master Password",
            "Are you sure you want to use this master password?\n\n"
            "⚠️ This password cannot be recovered if forgotten!\n"
            "⚠️ You will lose access to all stored passwords!\n\n"
            "Make sure you have a way to remember or securely store this password.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Disable UI
            self.setEnabled(False)
            
            # Create master password and derive key
            salt, password_hash = self.auth_manager.create_master_password(password)
            master_key = self.auth_manager.get_master_key()
            
            if not master_key:
                raise Exception("Failed to derive master key")
            
            # Create test vector
            from core.crypto import CryptoManager
            crypto = CryptoManager()
            test_vector = crypto.generate_test_vector(master_key)
            
            # Initialize database
            success = self.db_manager.initialize_database(
                master_key, salt, password_hash, test_vector
            )
            
            if success:
                self.logger.info("Master password created and database initialized")
                QMessageBox.information(
                    self, "Success", 
                    "Master password created successfully!\n\n"
                    "Your encrypted password database has been created."
                )
                self.setup_complete.emit()
                self.accept()
            else:
                raise Exception("Failed to initialize database")
                
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            QMessageBox.critical(
                self, "Setup Failed", 
                f"Failed to create master password and initialize database:\n\n{e}"
            )
            # Clear sensitive data on failure
            self.auth_manager.clear_master_key()
        finally:
            self.setEnabled(True)
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.create_btn.isEnabled():
                self.create_master_password()
        else:
            super().keyPressEvent(event)