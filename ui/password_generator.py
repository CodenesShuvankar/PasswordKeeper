"""
Password generator dialog
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QPushButton, QSpinBox, QCheckBox, QGroupBox,
    QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.crypto import CryptoManager
from core.utils import PasswordStrengthChecker, ClipboardManager


class PasswordGeneratorDialog(QDialog):
    """Password generator dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.crypto = CryptoManager()
        self.strength_checker = PasswordStrengthChecker()
        self.clipboard_manager = ClipboardManager()
        
        self.init_ui()
        self.generate_password()  # Generate initial password
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Password Generator")
        self.setModal(True)
        self.setFixedSize(450, 400)
        
        layout = QVBoxLayout(self)
        
        # Settings group
        settings_group = QGroupBox("Password Settings")
        settings_layout = QFormLayout(settings_group)
        
        # Length
        self.length_spin = QSpinBox()
        self.length_spin.setMinimum(4)
        self.length_spin.setMaximum(128)
        self.length_spin.setValue(16)
        self.length_spin.valueChanged.connect(self.generate_password)
        settings_layout.addRow("Length:", self.length_spin)
        
        # Character options
        self.uppercase_check = QCheckBox("Uppercase letters (A-Z)")
        self.uppercase_check.setChecked(True)
        self.uppercase_check.toggled.connect(self.generate_password)
        settings_layout.addRow(self.uppercase_check)
        
        self.lowercase_check = QCheckBox("Lowercase letters (a-z)")
        self.lowercase_check.setChecked(True)
        self.lowercase_check.toggled.connect(self.generate_password)
        settings_layout.addRow(self.lowercase_check)
        
        self.numbers_check = QCheckBox("Numbers (0-9)")
        self.numbers_check.setChecked(True)
        self.numbers_check.toggled.connect(self.generate_password)
        settings_layout.addRow(self.numbers_check)
        
        self.symbols_check = QCheckBox("Symbols (!@#$%^&*)")
        self.symbols_check.setChecked(True)
        self.symbols_check.toggled.connect(self.generate_password)
        settings_layout.addRow(self.symbols_check)
        
        layout.addWidget(settings_group)
        
        # Generated password group
        password_group = QGroupBox("Generated Password")
        password_layout = QVBoxLayout(password_group)
        
        # Password display
        self.password_edit = QLineEdit()
        self.password_edit.setFont(QFont("Courier", 12))
        self.password_edit.setReadOnly(True)
        password_layout.addWidget(self.password_edit)
        
        # Password strength
        self.strength_label = QLabel()
        password_layout.addWidget(self.strength_label)
        
        # Action buttons for password
        password_buttons = QHBoxLayout()
        
        self.regenerate_btn = QPushButton("Generate New")
        self.regenerate_btn.clicked.connect(self.generate_password)
        password_buttons.addWidget(self.regenerate_btn)
        
        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_password)
        password_buttons.addWidget(self.copy_btn)
        
        password_layout.addLayout(password_buttons)
        
        layout.addWidget(password_group)
        
        # Multiple passwords group
        multiple_group = QGroupBox("Generate Multiple Passwords")
        multiple_layout = QVBoxLayout(multiple_group)
        
        # Count input
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Count:"))
        
        self.count_spin = QSpinBox()
        self.count_spin.setMinimum(1)
        self.count_spin.setMaximum(50)
        self.count_spin.setValue(10)
        count_layout.addWidget(self.count_spin)
        
        self.generate_multiple_btn = QPushButton("Generate Multiple")
        self.generate_multiple_btn.clicked.connect(self.generate_multiple_passwords)
        count_layout.addWidget(self.generate_multiple_btn)
        
        count_layout.addStretch()
        multiple_layout.addLayout(count_layout)
        
        # Multiple passwords display
        self.multiple_passwords_edit = QTextEdit()
        self.multiple_passwords_edit.setFont(QFont("Courier", 10))
        self.multiple_passwords_edit.setMaximumHeight(100)
        self.multiple_passwords_edit.setReadOnly(True)
        multiple_layout.addWidget(self.multiple_passwords_edit)
        
        layout.addWidget(multiple_group)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def get_character_set(self) -> str:
        """Get character set based on checkboxes"""
        import string
        chars = ""
        
        if self.lowercase_check.isChecked():
            chars += string.ascii_lowercase
        if self.uppercase_check.isChecked():
            chars += string.ascii_uppercase
        if self.numbers_check.isChecked():
            chars += string.digits
        if self.symbols_check.isChecked():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        return chars
    
    def generate_password(self):
        """Generate a new password"""
        length = self.length_spin.value()
        include_symbols = self.symbols_check.isChecked()
        
        # Check if at least one character type is selected
        if not any([
            self.lowercase_check.isChecked(),
            self.uppercase_check.isChecked(), 
            self.numbers_check.isChecked(),
            self.symbols_check.isChecked()
        ]):
            self.password_edit.setText("Please select at least one character type")
            self.strength_label.setText("")
            return
        
        try:
            password = self.crypto.generate_password(length, include_symbols)
            self.password_edit.setText(password)
            self.update_strength_display(password)
            
        except Exception as e:
            self.logger.error(f"Password generation failed: {e}")
            self.password_edit.setText("Generation failed")
            self.strength_label.setText("")
    
    def update_strength_display(self, password: str):
        """Update password strength display"""
        strength_info = self.strength_checker.check_strength(password)
        
        strength_text = f"Strength: {strength_info['strength']}"
        if strength_info['feedback']:
            # Show only the most important feedback
            strength_text += f" - {strength_info['feedback'][0]}"
        
        self.strength_label.setText(strength_text)
        
        # Set color based on strength
        color = strength_info['color']
        self.strength_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def copy_password(self):
        """Copy generated password to clipboard"""
        password = self.password_edit.text()
        
        if not password or password in ["Please select at least one character type", "Generation failed"]:
            QMessageBox.warning(self, "No Password", "No valid password to copy.")
            return
        
        self.clipboard_manager.copy_to_clipboard(password, auto_clear=True)
        
        # Update button text briefly
        original_text = self.copy_btn.text()
        self.copy_btn.setText("Copied!")
        self.copy_btn.setEnabled(False)
        
        # Reset button after 1 second
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: [
            self.copy_btn.setText(original_text),
            self.copy_btn.setEnabled(True)
        ])
    
    def generate_multiple_passwords(self):
        """Generate multiple passwords"""
        count = self.count_spin.value()
        length = self.length_spin.value()
        include_symbols = self.symbols_check.isChecked()
        
        # Check if at least one character type is selected
        if not any([
            self.lowercase_check.isChecked(),
            self.uppercase_check.isChecked(), 
            self.numbers_check.isChecked(),
            self.symbols_check.isChecked()
        ]):
            self.multiple_passwords_edit.setText("Please select at least one character type")
            return
        
        try:
            passwords = []
            for _ in range(count):
                password = self.crypto.generate_password(length, include_symbols)
                passwords.append(password)
            
            self.multiple_passwords_edit.setText("\n".join(passwords))
            
        except Exception as e:
            self.logger.error(f"Multiple password generation failed: {e}")
            self.multiple_passwords_edit.setText("Generation failed")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_F5:
            self.generate_password()
        else:
            super().keyPressEvent(event)