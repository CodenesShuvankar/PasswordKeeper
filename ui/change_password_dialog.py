"""
Change master password dialog
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QGroupBox, QCheckBox,
    QProgressBar, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.db import DatabaseManager
from core.auth import AuthManager
from core.utils import PasswordStrengthChecker


class ChangePasswordDialog(QDialog):
    """Dialog for changing master password"""
    
    def __init__(self, parent=None, db_manager: DatabaseManager = None, 
                 auth_manager: AuthManager = None):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.auth_manager = auth_manager
        self.logger = logging.getLogger(__name__)
        self.strength_checker = PasswordStrengthChecker()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Change Master Password")
        self.setModal(True)
        self.setFixedSize(500, 450)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = self.create_header()
        layout.addLayout(header_layout)
        
        # Warning
        warning_frame = self.create_warning()
        layout.addWidget(warning_frame)
        
        # Password forms
        password_group = self.create_password_group()
        layout.addWidget(password_group)
        
        # Buttons
        button_layout = self.create_buttons()
        layout.addLayout(button_layout)
        
        # Connect signals
        self.new_password_edit.textChanged.connect(self.check_password_strength)
        self.confirm_password_edit.textChanged.connect(self.validate_passwords)
        self.current_password_edit.textChanged.connect(self.validate_form)
        
        # Focus on current password
        self.current_password_edit.setFocus()
    
    def create_header(self) -> QVBoxLayout:
        """Create header with title"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Change Master Password")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Change your master password to a new secure password")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        
        return layout
    
    def create_warning(self) -> QFrame:
        """Create warning frame"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("background-color: #fff3cd; padding: 10px; border: 1px solid #ffeaa7;")
        
        layout = QVBoxLayout(frame)
        
        warning = QLabel(
            "⚠️ Important:\n"
            "• Make sure to remember your new password\n"
            "• The old password will no longer work\n"
            "• This will re-encrypt your entire database\n"
            "• Keep a backup before proceeding"
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #856404; font-weight: bold;")
        layout.addWidget(warning)
        
        return frame
    
    def create_password_group(self) -> QGroupBox:
        """Create password input group"""
        group = QGroupBox("Password Change")
        layout = QFormLayout(group)
        
        # Current password
        self.current_password_edit = QLineEdit()
        self.current_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password_edit.setMinimumHeight(30)
        layout.addRow("Current Password:", self.current_password_edit)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addRow(separator)
        
        # New password
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_edit.setMinimumHeight(30)
        layout.addRow("New Password:", self.new_password_edit)
        
        # Password strength indicator
        self.strength_label = QLabel("Password strength will appear here")
        self.strength_label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addRow("", self.strength_label)
        
        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximum(6)
        self.strength_bar.setValue(0)
        self.strength_bar.setVisible(False)
        layout.addRow("", self.strength_bar)
        
        # Confirm new password
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit.setMinimumHeight(30)
        layout.addRow("Confirm New Password:", self.confirm_password_edit)
        
        # Password match indicator
        self.match_label = QLabel("")
        layout.addRow("", self.match_label)
        
        # Show passwords checkbox
        self.show_passwords_check = QCheckBox("Show passwords")
        self.show_passwords_check.toggled.connect(self.toggle_password_visibility)
        layout.addRow("", self.show_passwords_check)
        
        return group
    
    def create_buttons(self) -> QHBoxLayout:
        """Create button layout"""
        layout = QHBoxLayout()
        
        layout.addStretch()
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
        
        # Change password button
        self.change_btn = QPushButton("Change Password")
        self.change_btn.clicked.connect(self.change_password)
        self.change_btn.setEnabled(False)
        self.change_btn.setDefault(True)
        layout.addWidget(self.change_btn)
        
        return layout
    
    def check_password_strength(self):
        """Check and display password strength"""
        password = self.new_password_edit.text()
        
        if not password:
            self.strength_label.setText("Password strength will appear here")
            self.strength_label.setStyleSheet("color: gray; font-size: 10pt;")
            self.strength_bar.setVisible(False)
            self.validate_form()
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
        
        self.validate_form()
    
    def validate_passwords(self):
        """Validate password confirmation"""
        new_password = self.new_password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        # Check if passwords match
        if not confirm_password:
            self.match_label.setText("")
            self.validate_form()
            return
        
        if new_password == confirm_password:
            self.match_label.setText("✓ Passwords match")
            self.match_label.setStyleSheet("color: green; font-size: 10pt;")
        else:
            self.match_label.setText("✗ Passwords don't match")
            self.match_label.setStyleSheet("color: red; font-size: 10pt;")
        
        self.validate_form()
    
    def validate_form(self):
        """Validate entire form and enable/disable change button"""
        current_password = self.current_password_edit.text()
        new_password = self.new_password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        # Check all required fields
        if not current_password or not new_password or not confirm_password:
            self.change_btn.setEnabled(False)
            return
        
        # Check passwords match
        if new_password != confirm_password:
            self.change_btn.setEnabled(False)
            return
        
        # Check password strength
        strength_info = self.strength_checker.check_strength(new_password)
        if strength_info['score'] < 3:  # Require at least medium strength
            self.change_btn.setEnabled(False)
            return
        
        # Check minimum length
        if len(new_password) < 8:
            self.change_btn.setEnabled(False)
            return
        
        self.change_btn.setEnabled(True)
    
    def toggle_password_visibility(self, checked: bool):
        """Toggle password visibility"""
        echo_mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        self.current_password_edit.setEchoMode(echo_mode)
        self.new_password_edit.setEchoMode(echo_mode)
        self.confirm_password_edit.setEchoMode(echo_mode)
    
    def change_password(self):
        """Change the master password"""
        current_password = self.current_password_edit.text()
        new_password = self.new_password_edit.text()
        
        # Final confirmation
        reply = QMessageBox.question(
            self, "Confirm Password Change",
            "Are you sure you want to change your master password?\n\n"
            "This will re-encrypt your entire database with the new password.\n"
            "Make sure you remember the new password!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Disable UI during operation
            self.setEnabled(False)
            
            # Get current authentication data
            stored_salt = self.get_stored_salt()
            stored_hash = self.get_stored_hash()
            
            if not stored_salt or not stored_hash:
                raise Exception("Could not retrieve current authentication data")
            
            # Change master password
            result = self.auth_manager.change_master_password(
                current_password, new_password, stored_salt, stored_hash
            )
            
            if not result:
                raise Exception("Current password is incorrect")
            
            new_salt, new_hash = result
            
            # Update database metadata
            if not self.update_database_metadata(new_salt, new_hash):
                raise Exception("Failed to update database metadata")
            
            # Generate new test vector
            from core.crypto import CryptoManager
            crypto = CryptoManager()
            master_key = self.auth_manager.get_master_key()
            new_test_vector = crypto.generate_test_vector(master_key)
            
            # Update test vector in database
            self.db_manager.set_metadata('test_vector', new_test_vector)
            
            # Save database with new encryption
            if not self.db_manager.save_database():
                raise Exception("Failed to save database with new password")
            
            self.logger.info("Master password changed successfully")
            QMessageBox.information(
                self, "Success",
                "Master password changed successfully!\n\n"
                "Your database has been re-encrypted with the new password."
            )
            
            self.accept()
            
        except Exception as e:
            self.logger.error(f"Password change failed: {e}")
            QMessageBox.critical(
                self, "Password Change Failed",
                f"Failed to change master password:\n\n{e}"
            )
            
        finally:
            self.setEnabled(True)
    
    def get_stored_salt(self) -> bytes:
        """Get stored salt from database metadata"""
        try:
            salt_hex = self.db_manager.get_metadata('salt')
            if salt_hex:
                return bytes.fromhex(salt_hex)
        except Exception as e:
            self.logger.error(f"Failed to get stored salt: {e}")
        return None
    
    def get_stored_hash(self) -> bytes:
        """Get stored password hash from database metadata"""
        try:
            hash_hex = self.db_manager.get_metadata('password_hash')
            if hash_hex:
                return bytes.fromhex(hash_hex)
        except Exception as e:
            self.logger.error(f"Failed to get stored hash: {e}")
        return None
    
    def update_database_metadata(self, new_salt: bytes, new_hash: bytes) -> bool:
        """Update database metadata with new authentication data"""
        try:
            # Update salt
            if not self.db_manager.set_metadata('salt', new_salt.hex()):
                return False
            
            # Update password hash
            if not self.db_manager.set_metadata('password_hash', new_hash.hex()):
                return False
            
            # Update modified date
            from datetime import datetime
            if not self.db_manager.set_metadata('password_changed_date', datetime.now().isoformat()):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update database metadata: {e}")
            return False
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.change_btn.isEnabled():
                self.change_password()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)