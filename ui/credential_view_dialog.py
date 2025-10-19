"""
Read-only dialog for viewing credential details safely
"""

import logging
from typing import Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QTextEdit, QPushButton, QGroupBox, QCheckBox,
    QTabWidget, QWidget, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class CredentialViewDialog(QDialog):
    """Modern read-only dialog for viewing credential details"""
    
    def __init__(self, parent=None, credential: Dict[str, Any] = None):
        super().__init__(parent)
        
        self.credential = credential
        self.logger = logging.getLogger(__name__)
        self.password_visible = False
        
        self.apply_modern_style()
        self.init_ui()
        self.load_credential_data()
    
    def apply_modern_style(self):
        """Apply modern styling to match main window"""
        style = """
        QDialog {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #1F2F9B, stop:1 #1CA7EC);
            color: white;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        QTabWidget {
            background: transparent;
        }
        
        QTabWidget::pane {
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.1);
        }
        
        QTabBar::tab {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #7BD5F5, stop:1 #4ADEDE);
            color: #1F2F9B;
            padding: 10px 20px;
            margin: 2px;
            border-radius: 10px;
            font-weight: bold;
        }
        
        QTabBar::tab:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #1CA7EC, stop:1 #1F2F9B);
            color: white;
        }
        
        QLabel {
            color: white;
            font-size: 11pt;
        }
        
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #7BD5F5, stop:1 #4ADEDE);
            color: #1F2F9B;
            border: none;
            border-radius: 20px;
            padding: 12px 25px;
            font-weight: bold;
            font-size: 11pt;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #4ADEDE, stop:1 #7BD5F5);
        }
        
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #1CA7EC, stop:1 #1F2F9B);
            color: white;
        }
        
        QTextEdit {
            background: rgba(255, 255, 255, 0.15);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            padding: 10px;
            color: white;
            font-size: 11pt;
        }
        """
        self.setStyleSheet(style)
    
    def init_ui(self):
        """Initialize the modern user interface"""
        self.setWindowTitle(f"🔍 View Credential - {self.credential.get('title', 'Unknown')}")
        self.setModal(True)
        self.resize(550, 650)
        
        layout = QVBoxLayout(self)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        
        # Basic info tab
        basic_tab = self.create_basic_tab()
        self.tab_widget.addTab(basic_tab, "Basic Information")
        
        # Password tab
        password_tab = self.create_password_tab()
        self.tab_widget.addTab(password_tab, "Password")
        
        # Additional info tab
        additional_tab = self.create_additional_tab()
        self.tab_widget.addTab(additional_tab, "Additional Information")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = self.create_buttons()
        layout.addLayout(button_layout)
    
    def create_basic_tab(self) -> QWidget:
        """Create basic information tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Title
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addRow("Title:", self.title_label)
        
        # Username/Email
        self.username_label = QLabel()
        self.username_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addRow("Username/Email:", self.username_label)
        
        # Copy username button
        self.copy_username_btn = QPushButton("Copy Username")
        self.copy_username_btn.clicked.connect(self.copy_username)
        layout.addRow("", self.copy_username_btn)
        
        # URL
        self.url_label = QLabel()
        self.url_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.url_label.setStyleSheet("color: blue; text-decoration: underline;")
        self.url_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.url_label.mousePressEvent = self.open_url
        layout.addRow("Website URL:", self.url_label)
        
        # Category
        self.category_label = QLabel()
        layout.addRow("Category:", self.category_label)
        
        return widget
    
    def create_password_tab(self) -> QWidget:
        """Create password tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Password group
        password_group = QGroupBox("Password")
        password_layout = QFormLayout(password_group)
        
        # Password field (initially hidden)
        self.password_label = QLabel("••••••••••••")
        self.password_label.setFont(QFont("Courier", 10))
        self.password_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        password_layout.addRow("Password:", self.password_label)
        
        # Show/Hide password button
        self.toggle_password_btn = QPushButton("Show Password")
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addRow("", self.toggle_password_btn)
        
        # Copy password button
        self.copy_password_btn = QPushButton("Copy Password")
        self.copy_password_btn.clicked.connect(self.copy_password)
        password_layout.addRow("", self.copy_password_btn)
        
        layout.addWidget(password_group)
        layout.addStretch()
        
        return widget
    
    def create_additional_tab(self) -> QWidget:
        """Create additional information tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Notes
        self.notes_text = QTextEdit()
        self.notes_text.setReadOnly(True)
        self.notes_text.setMaximumHeight(150)
        layout.addRow("Notes:", self.notes_text)
        
        # Created date
        self.created_label = QLabel()
        layout.addRow("Created:", self.created_label)
        
        # Modified date
        self.modified_label = QLabel()
        layout.addRow("Last Modified:", self.modified_label)
        
        return widget
    
    def create_buttons(self) -> QHBoxLayout:
        """Create button layout"""
        layout = QHBoxLayout()
        
        layout.addStretch()
        
        # Edit button
        self.edit_btn = QPushButton("Edit Credential")
        self.edit_btn.clicked.connect(self.edit_credential)
        layout.addWidget(self.edit_btn)
        
        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setDefault(True)
        layout.addWidget(self.close_btn)
        
        return layout
    
    def load_credential_data(self):
        """Load credential data into the form"""
        if not self.credential:
            return
        
        # Basic info
        self.title_label.setText(self.credential.get('title', ''))
        self.username_label.setText(self.credential.get('username', ''))
        url = self.credential.get('url', '')
        if url:
            self.url_label.setText(f"<a href='{url}'>{url}</a>")
        else:
            self.url_label.setText("Not specified")
        
        self.category_label.setText(self.credential.get('category', 'General'))
        
        # Store password but don't display it initially
        self.actual_password = self.credential.get('password', '')
        
        # Notes
        notes = self.credential.get('notes', '')
        if notes:
            self.notes_text.setPlainText(notes)
        else:
            self.notes_text.setPlainText("No notes")
        
        # Dates
        try:
            from datetime import datetime
            created_dt = datetime.fromisoformat(self.credential.get('created_date', ''))
            self.created_label.setText(created_dt.strftime("%Y-%m-%d %H:%M:%S"))
            
            modified_dt = datetime.fromisoformat(self.credential.get('modified_date', ''))
            self.modified_label.setText(modified_dt.strftime("%Y-%m-%d %H:%M:%S"))
        except:
            self.created_label.setText(self.credential.get('created_date', 'Unknown'))
            self.modified_label.setText(self.credential.get('modified_date', 'Unknown'))
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        try:
            if self.password_visible:
                # Hide password
                self.password_label.setText("••••••••••••")
                self.toggle_password_btn.setText("Show Password")
                self.password_visible = False
            else:
                # Show password
                self.password_label.setText(self.actual_password)
                self.toggle_password_btn.setText("Hide Password")
                self.password_visible = True
        except Exception as e:
            self.logger.error(f"Error toggling password visibility: {e}")
    
    def copy_username(self):
        """Copy username to clipboard"""
        try:
            username = self.credential.get('username', '')
            if username:
                clipboard = QApplication.clipboard()
                clipboard.setText(username)
                self.logger.info("Username copied to clipboard")
        except Exception as e:
            self.logger.error(f"Error copying username: {e}")
    
    def copy_password(self):
        """Copy password to clipboard"""
        try:
            password = self.actual_password
            if password:
                clipboard = QApplication.clipboard()
                clipboard.setText(password)
                self.logger.info("Password copied to clipboard")
        except Exception as e:
            self.logger.error(f"Error copying password: {e}")
    
    def open_url(self, event):
        """Open URL in browser"""
        try:
            import webbrowser
            url = self.credential.get('url', '')
            if url:
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                webbrowser.open(url)
                self.logger.info(f"Opened URL: {url}")
        except Exception as e:
            self.logger.error(f"Error opening URL: {e}")
    
    def edit_credential(self):
        """Switch to edit mode"""
        try:
            # Close this dialog and signal parent to open edit dialog
            self.accept()
            # We'll emit a signal or call parent method
            if hasattr(self.parent(), 'edit_credential'):
                self.parent().edit_credential()
        except Exception as e:
            self.logger.error(f"Error switching to edit mode: {e}")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
        else:
            super().keyPressEvent(event)