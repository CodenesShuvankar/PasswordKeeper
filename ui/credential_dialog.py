"""Credential Dialog - reconstructed (clean) implementation."""
from __future__ import annotations

from typing import Dict, Optional
import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QComboBox,
    QTextEdit, QPushButton, QHBoxLayout, QGroupBox, QSpinBox, QCheckBox,
    QMessageBox, QTabWidget
)

from core.crypto import CryptoManager  # type: ignore
from core.utils import PasswordStrengthChecker, validate_url  # type: ignore


class CredentialDialog(QDialog):
    def __init__(self, parent=None, credential: Optional[Dict[str, str]] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.crypto = CryptoManager()
        self.strength_checker = PasswordStrengthChecker()
        self.credential = credential or {}
        self.is_edit_mode = credential is not None

        self.setObjectName("credentialDialog")
        self.apply_modern_style()
        self.init_ui()
        if self.is_edit_mode:
            self.load_credential_data()

    def apply_modern_style(self):
        # NOTE: Expanded styles to improve padding & text visibility (some text was clipped / cramped)
        style = """
        #credentialDialog { background:#F5F7FA; }
        QLabel { color:#143265; font-size:11pt; }
        QLineEdit, QComboBox, QTextEdit {
            background:#FFFFFF; border:1px solid #B6C7DA; border-radius:10px;
            padding:10px 14px; color:#0F275F; font-size:11pt;
        }
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus { border:2px solid #1CA7EC; }
        QLineEdit:hover, QComboBox:hover, QTextEdit:hover { border:1px solid #1CA7EC; }
        QTextEdit { line-height:140%; }
        QPushButton {
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1F2F9B, stop:1 #1CA7EC);
            color:#FFFFFF; border:none; border-radius:10px; padding:11px 26px;
            font-weight:600; font-size:11pt;
        }
        QPushButton:hover { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1CA7EC, stop:1 #1F2F9B); }
        QPushButton:pressed { background:#1F2F9B; }
        QPushButton#cancelButton { background:#ECEFF4; color:#2F3B52; border:1px solid #D0D7E2; }
        QPushButton#cancelButton:hover { background:#E2E8F0; }
        QPushButton#cancelButton:pressed { background:#D8DEE7; }
        QPushButton#primaryButton { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1CA7EC, stop:1 #1F2F9B); }
        QGroupBox {
            background:#FFFFFF; border:1px solid #D3DFEC; border-radius:12px;
            margin-top:18px; padding:26px 24px 20px 24px; font-weight:600; color:#12305F;
        }
        QGroupBox::title {
            subcontrol-origin: margin; left:22px; top:-14px; padding:4px 14px;
            background:#FFFFFF; border-radius:8px; border:1px solid #D3DFEC; font-size:10.5pt;
        }
        QCheckBox { color:#12305F; font-size:10.5pt; padding:4px 2px; }
        QCheckBox::indicator { width:20px; height:20px; border-radius:5px; border:1px solid #7FA4C6; background:#FFFFFF; }
        QCheckBox::indicator:checked { background:#1CA7EC; border:1px solid #1F2F9B; }
        QCheckBox::indicator:hover { border:1px solid #1CA7EC; }
        QSpinBox {
            background:#FFFFFF; border:1px solid #B6C7DA; border-radius:10px; padding:8px 12px;
            color:#0F275F; font-size:11pt; min-width:140px;
        }
        QSpinBox:focus { border:2px solid #1CA7EC; }
        QSpinBox::up-button, QSpinBox::down-button { width:26px; border:none; background:transparent; }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover { background:#E6EEF5; }
        QSpinBox::up-arrow, QSpinBox::down-arrow { width:10px; height:10px; }
        QComboBox::drop-down { border:none; width:28px; }
        QComboBox::down-arrow { image:none; border-style:solid; border-width:7px 7px 0 7px; border-color:#1F2F9B transparent transparent transparent; }
        QComboBox QAbstractItemView {
            background:#FFFFFF; border:1px solid #1CA7EC; selection-background-color:#E3F6FD; color:#0F275F; font-size:10.5pt;
        }
        QTabWidget::pane { border:1px solid #C3D4E6; border-radius:10px; background:#FFFFFF; }
        QTabBar::tab {
            background:#E6EEF5; color:#12305F; padding:10px 22px; font-size:10.5pt;
            border-top-left-radius:8px; border-top-right-radius:8px; margin-right:4px; margin-top:2px;
        }
        QTabBar::tab:selected { background:#FFFFFF; font-weight:600; }
        QTabBar::tab:hover { background:#D8E7F3; }
        """
        self.setStyleSheet(style)

    def init_ui(self):
        title = "✏️ Edit Credential" if self.is_edit_mode else "➕ Add Credential"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(650, 750)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(15, 15, 15, 15)
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumHeight(600)
        self.tab_widget.addTab(self.create_basic_tab(), "📝 Basic Information")
        self.tab_widget.addTab(self.create_password_tab(), "🔒 Password")
        self.tab_widget.addTab(self.create_additional_tab(), "📋 Additional Info")
        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(self.create_buttons())
        self.password_edit.textChanged.connect(self.check_password_strength)
        self.generate_btn.clicked.connect(self.generate_password)
        self.url_edit.textChanged.connect(self.validate_url_input)
        self.title_edit.setFocus()

    def create_basic_tab(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        self.title_edit = QLineEdit(); self.title_edit.setPlaceholderText("e.g., Gmail, Facebook, Work Email"); self.title_edit.setMinimumHeight(40)
        layout.addRow(QLabel("Title *:"), self.title_edit)
        self.username_edit = QLineEdit(); self.username_edit.setPlaceholderText("Username or email address"); self.username_edit.setMinimumHeight(40)
        layout.addRow(QLabel("Username/Email *:"), self.username_edit)
        self.url_edit = QLineEdit(); self.url_edit.setPlaceholderText("https://example.com"); self.url_edit.setMinimumHeight(40)
        layout.addRow(QLabel("Website URL:"), self.url_edit)
        self.url_validation_label = QLabel(""); layout.addRow(QLabel(""), self.url_validation_label)
        self.category_combo = QComboBox(); self.category_combo.setEditable(True); self.category_combo.setMinimumHeight(40)
        self.category_combo.addItems(["General","Email","Social Media","Banking","Shopping","Work","Gaming","Entertainment","Development","Other"])
        layout.addRow(QLabel("Category:"), self.category_combo)
        return widget

    def create_password_tab(self) -> QWidget:
        widget = QWidget(); layout = QVBoxLayout(widget); layout.setSpacing(18); layout.setContentsMargins(24,22,24,22)
        password_group = QGroupBox("Password"); password_layout = QFormLayout(password_group); password_layout.setSpacing(10)
        container = QHBoxLayout(); container.setSpacing(12)
        self.password_edit = QLineEdit(); self.password_edit.setEchoMode(QLineEdit.EchoMode.Password); self.password_edit.setMinimumHeight(44); self.password_edit.setMinimumWidth(320); container.addWidget(self.password_edit, 1)
        self.generate_btn = QPushButton("Generate"); self.generate_btn.setMaximumWidth(120); self.generate_btn.setMinimumHeight(44); container.addWidget(self.generate_btn)
        password_layout.addRow(QLabel("Password *:"), container)
        self.show_password_check = QCheckBox("Show password"); self.show_password_check.setContentsMargins(4,4,4,4); self.show_password_check.toggled.connect(self.toggle_password_visibility)
        password_layout.addRow(QLabel(""), self.show_password_check)
        self.strength_label = QLabel("Enter a password to see strength"); self.strength_label.setStyleSheet("color: gray; font-size: 10pt; padding:4px 2px;")
        password_layout.addRow(QLabel("Strength:"), self.strength_label)
        layout.addWidget(password_group)
        generator_group = QGroupBox("Password Generator Settings"); gen_layout = QFormLayout(generator_group); gen_layout.setSpacing(12)
        self.length_spin = QSpinBox(); self.length_spin.setMinimum(8); self.length_spin.setMaximum(128); self.length_spin.setValue(16); self.length_spin.setMinimumHeight(42); gen_layout.addRow(QLabel("Length:"), self.length_spin)
        self.symbols_check = QCheckBox("Include symbols (!@#$%^&*)"); self.symbols_check.setChecked(True); gen_layout.addRow(QLabel(""), self.symbols_check)
        self.numbers_check = QCheckBox("Include numbers (0-9)"); self.numbers_check.setChecked(True); gen_layout.addRow(QLabel(""), self.numbers_check)
        self.uppercase_check = QCheckBox("Include uppercase letters (A-Z)"); self.uppercase_check.setChecked(True); gen_layout.addRow(QLabel(""), self.uppercase_check)
        self.lowercase_check = QCheckBox("Include lowercase letters (a-z)"); self.lowercase_check.setChecked(True); gen_layout.addRow(QLabel(""), self.lowercase_check)
        layout.addWidget(generator_group); layout.addStretch(); return widget

    def create_additional_tab(self) -> QWidget:
        widget = QWidget(); layout = QFormLayout(widget); layout.setSpacing(15); layout.setContentsMargins(20,20,20,20)
        self.notes_edit = QTextEdit(); self.notes_edit.setPlaceholderText("Additional notes, security questions, etc."); self.notes_edit.setMinimumHeight(120); self.notes_edit.setMaximumHeight(180); layout.addRow(QLabel("Notes:"), self.notes_edit)
        if self.is_edit_mode:
            self.created_label = QLabel(); self.created_label.setStyleSheet("color: #666666; font-size: 10pt;"); layout.addRow(QLabel("Created:"), self.created_label)
            self.modified_label = QLabel(); self.modified_label.setStyleSheet("color: #666666; font-size: 10pt;"); layout.addRow(QLabel("Last Modified:"), self.modified_label)
        return widget

    def create_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout(); layout.setSpacing(15); layout.setContentsMargins(0,20,0,0); layout.addStretch()
        self.cancel_btn = QPushButton("Cancel"); self.cancel_btn.setObjectName("cancelButton"); self.cancel_btn.clicked.connect(self.reject); layout.addWidget(self.cancel_btn)
        text = "Update Credential" if self.is_edit_mode else "Add Credential"; self.save_btn = QPushButton(text); self.save_btn.setObjectName("primaryButton"); self.save_btn.clicked.connect(self.save_credential); self.save_btn.setDefault(True); layout.addWidget(self.save_btn)
        return layout

    def load_credential_data(self):
        if not self.credential: return
        self.title_edit.setText(self.credential.get('title',''))
        self.username_edit.setText(self.credential.get('username',''))
        self.url_edit.setText(self.credential.get('url',''))
        category = self.credential.get('category','General'); idx = self.category_combo.findText(category); self.category_combo.setCurrentIndex(idx if idx >=0 else 0); self.category_combo.setCurrentText(category)
        self.password_edit.setText(self.credential.get('password',''))
        self.notes_edit.setPlainText(self.credential.get('notes',''))
        if hasattr(self,'created_label'):
            try:
                from datetime import datetime
                c = datetime.fromisoformat(self.credential.get('created_date','')); self.created_label.setText(c.strftime("%Y-%m-%d %H:%M:%S"))
                m = datetime.fromisoformat(self.credential.get('modified_date','')); self.modified_label.setText(m.strftime("%Y-%m-%d %H:%M:%S"))
            except Exception:
                self.created_label.setText(self.credential.get('created_date','Unknown'))
                self.modified_label.setText(self.credential.get('modified_date','Unknown'))

    def check_password_strength(self):
        pwd = self.password_edit.text()
        if not pwd:
            self.strength_label.setText("Enter a password to see strength"); self.strength_label.setStyleSheet("color: gray; font-size: 10pt;"); return
        info = self.strength_checker.check_strength(pwd); text = info['strength']
        if info['feedback']: text += " - " + ", ".join(info['feedback'][:2])
        self.strength_label.setText(text); self.strength_label.setStyleSheet(f"color: {info['color']}; font-size: 10pt; font-weight: bold;")

    def generate_password(self):
        length = self.length_spin.value(); import string; chars = ""
        if self.lowercase_check.isChecked(): chars += string.ascii_lowercase
        if self.uppercase_check.isChecked(): chars += string.ascii_uppercase
        if self.numbers_check.isChecked(): chars += string.digits
        if self.symbols_check.isChecked(): chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not chars:
            QMessageBox.warning(self,"Invalid Settings","Please select at least one character type for password generation."); return
        pwd = self.crypto.generate_password(length, self.symbols_check.isChecked()); self.password_edit.setText(pwd); self.check_password_strength()

    def toggle_password_visibility(self, checked: bool):
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)

    def validate_url_input(self):
        url = self.url_edit.text().strip()
        if not url: self.url_validation_label.setText(""); return
        if validate_url(url):
            self.url_validation_label.setText("✓ Valid URL"); self.url_validation_label.setStyleSheet("color: green; font-size: 10pt;")
        else:
            self.url_validation_label.setText("⚠ Invalid URL format"); self.url_validation_label.setStyleSheet("color: orange; font-size: 10pt;")

    def validate_form(self) -> bool:
        if not self.title_edit.text().strip(): QMessageBox.warning(self,"Validation Error","Title is required."); self.tab_widget.setCurrentIndex(0); self.title_edit.setFocus(); return False
        if not self.username_edit.text().strip(): QMessageBox.warning(self,"Validation Error","Username/Email is required."); self.tab_widget.setCurrentIndex(0); self.username_edit.setFocus(); return False
        if not self.password_edit.text(): QMessageBox.warning(self,"Validation Error","Password is required."); self.tab_widget.setCurrentIndex(1); self.password_edit.setFocus(); return False
        info = self.strength_checker.check_strength(self.password_edit.text())
        if info['score'] < 2:
            reply = QMessageBox.question(self,"Weak Password",f"The password strength is '{info['strength']}'. Are you sure you want to use this password?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                self.tab_widget.setCurrentIndex(1); self.password_edit.setFocus(); return False
        return True

    def save_credential(self):
        if not self.validate_form(): return
        try:
            self.accept()
        except Exception as e:  # pragma: no cover
            self.logger.error(f"Error saving credential: {e}"); QMessageBox.critical(self,"Error",f"Failed to save credential: {e}")

    def get_data(self) -> Dict[str, str]:
        return {
            'title': self.title_edit.text().strip(),
            'username': self.username_edit.text().strip(),
            'password': self.password_edit.text(),
            'url': self.url_edit.text().strip(),
            'notes': self.notes_edit.toPlainText().strip(),
            'category': self.category_combo.currentText().strip() or 'General'
        }

    def keyPressEvent(self, event):  # type: ignore[override]
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.save_btn.isEnabled(): self.save_credential()
        elif event.key() == Qt.Key.Key_Escape: self.reject()
        else: super().keyPressEvent(event)