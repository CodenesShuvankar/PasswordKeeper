"""
Settings dialog for application preferences
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QSpinBox, QCheckBox, QPushButton, QGroupBox, QComboBox,
    QTabWidget, QWidget, QMessageBox, QSlider
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.utils import SettingsManager


class SettingsDialog(QDialog):
    """Settings dialog for application preferences"""
    
    def __init__(self, parent=None, settings_manager: SettingsManager = None):
        super().__init__(parent)
        
        self.settings_manager = settings_manager or SettingsManager()
        self.logger = logging.getLogger(__name__)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        
        # Security tab
        security_tab = self.create_security_tab()
        self.tab_widget.addTab(security_tab, "Security")
        
        # Interface tab
        interface_tab = self.create_interface_tab()
        self.tab_widget.addTab(interface_tab, "Interface")
        
        # Advanced tab
        advanced_tab = self.create_advanced_tab()
        self.tab_widget.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = self.create_buttons()
        layout.addLayout(button_layout)
    
    def create_security_tab(self) -> QWidget:
        """Create security settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Auto-lock group
        autolock_group = QGroupBox("Auto-lock Settings")
        autolock_layout = QFormLayout(autolock_group)
        
        # Inactivity timeout
        self.inactivity_spin = QSpinBox()
        self.inactivity_spin.setMinimum(1)
        self.inactivity_spin.setMaximum(60)
        self.inactivity_spin.setSuffix(" minutes")
        autolock_layout.addRow("Inactivity timeout:", self.inactivity_spin)
        
        # Auto-lock on minimize
        self.lock_on_minimize_check = QCheckBox("Lock when minimized")
        autolock_layout.addRow(self.lock_on_minimize_check)
        
        layout.addWidget(autolock_group)
        
        # Clipboard group
        clipboard_group = QGroupBox("Clipboard Settings")
        clipboard_layout = QFormLayout(clipboard_group)
        
        # Auto-clear timeout
        self.clipboard_timeout_spin = QSpinBox()
        self.clipboard_timeout_spin.setMinimum(5)
        self.clipboard_timeout_spin.setMaximum(300)
        self.clipboard_timeout_spin.setSuffix(" seconds")
        clipboard_layout.addRow("Auto-clear timeout:", self.clipboard_timeout_spin)
        
        layout.addWidget(clipboard_group)
        
        # Password generator group
        generator_group = QGroupBox("Password Generator Defaults")
        generator_layout = QFormLayout(generator_group)
        
        # Default length
        self.password_length_spin = QSpinBox()
        self.password_length_spin.setMinimum(8)
        self.password_length_spin.setMaximum(128)
        generator_layout.addRow("Default length:", self.password_length_spin)
        
        # Include symbols by default
        self.default_symbols_check = QCheckBox("Include symbols by default")
        generator_layout.addRow(self.default_symbols_check)
        
        layout.addWidget(generator_group)
        
        layout.addStretch()
        return widget
    
    def create_interface_tab(self) -> QWidget:
        """Create interface settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Window group
        window_group = QGroupBox("Window Settings")
        window_layout = QFormLayout(window_group)
        
        # Remember window size
        self.remember_size_check = QCheckBox("Remember window size and position")
        window_layout.addRow(self.remember_size_check)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Default", "Dark", "Light"])
        window_layout.addRow("Theme:", self.theme_combo)
        
        layout.addWidget(window_group)
        
        # Table group
        table_group = QGroupBox("Table Settings")
        table_layout = QFormLayout(table_group)
        
        # Show tooltips
        self.tooltips_check = QCheckBox("Show tooltips")
        table_layout.addRow(self.tooltips_check)
        
        # Alternating row colors
        self.alternating_rows_check = QCheckBox("Alternating row colors")
        table_layout.addRow(self.alternating_rows_check)
        
        layout.addWidget(table_group)
        
        layout.addStretch()
        return widget
    
    def create_advanced_tab(self) -> QWidget:
        """Create advanced settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Backup group
        backup_group = QGroupBox("Backup Settings")
        backup_layout = QFormLayout(backup_group)
        
        # Enable backups
        self.backup_enabled_check = QCheckBox("Enable automatic backups")
        backup_layout.addRow(self.backup_enabled_check)
        
        # Backup count
        self.backup_count_spin = QSpinBox()
        self.backup_count_spin.setMinimum(1)
        self.backup_count_spin.setMaximum(50)
        self.backup_count_spin.setSuffix(" backups")
        backup_layout.addRow("Keep backup count:", self.backup_count_spin)
        
        layout.addWidget(backup_group)
        
        # Database group
        database_group = QGroupBox("Database Settings")
        database_layout = QFormLayout(database_group)
        
        # Auto-save interval
        self.autosave_spin = QSpinBox()
        self.autosave_spin.setMinimum(10)
        self.autosave_spin.setMaximum(300)
        self.autosave_spin.setSuffix(" seconds")
        database_layout.addRow("Auto-save interval:", self.autosave_spin)
        
        layout.addWidget(database_group)
        
        # Logging group
        logging_group = QGroupBox("Logging Settings")
        logging_layout = QFormLayout(logging_group)
        
        # Log level
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["ERROR", "WARNING", "INFO", "DEBUG"])
        logging_layout.addRow("Log level:", self.log_level_combo)
        
        # Enable verbose logging
        self.verbose_logging_check = QCheckBox("Enable verbose logging")
        logging_layout.addRow(self.verbose_logging_check)
        
        layout.addWidget(logging_group)
        
        # Reset section
        reset_group = QGroupBox("Reset")
        reset_layout = QVBoxLayout(reset_group)
        
        reset_info = QLabel("Reset all settings to default values")
        reset_info.setStyleSheet("color: gray;")
        reset_layout.addWidget(reset_info)
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        reset_layout.addWidget(self.reset_btn)
        
        layout.addWidget(reset_group)
        
        layout.addStretch()
        return widget
    
    def create_buttons(self) -> QHBoxLayout:
        """Create button layout"""
        layout = QHBoxLayout()
        
        layout.addStretch()
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
        
        # Apply button
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_btn)
        
        # OK button
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept_settings)
        self.ok_btn.setDefault(True)
        layout.addWidget(self.ok_btn)
        
        return layout
    
    def load_settings(self):
        """Load current settings into form"""
        # Security settings
        self.inactivity_spin.setValue(
            self.settings_manager.get('inactivity_timeout_minutes', 5)
        )
        self.lock_on_minimize_check.setChecked(
            self.settings_manager.get('auto_lock_on_minimize', True)
        )
        self.clipboard_timeout_spin.setValue(
            self.settings_manager.get('clipboard_auto_clear_seconds', 30)
        )
        self.password_length_spin.setValue(
            self.settings_manager.get('password_generator_length', 16)
        )
        self.default_symbols_check.setChecked(
            self.settings_manager.get('password_generator_symbols', True)
        )
        
        # Interface settings
        self.remember_size_check.setChecked(
            self.settings_manager.get('window_remember_size', True)
        )
        
        theme = self.settings_manager.get('theme', 'Default')
        theme_index = self.theme_combo.findText(theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
        
        self.tooltips_check.setChecked(
            self.settings_manager.get('show_tooltips', True)
        )
        self.alternating_rows_check.setChecked(
            self.settings_manager.get('alternating_row_colors', True)
        )
        
        # Advanced settings
        self.backup_enabled_check.setChecked(
            self.settings_manager.get('backup_enabled', True)
        )
        self.backup_count_spin.setValue(
            self.settings_manager.get('backup_count', 5)
        )
        self.autosave_spin.setValue(
            self.settings_manager.get('autosave_interval_seconds', 30)
        )
        
        log_level = self.settings_manager.get('log_level', 'INFO')
        log_level_index = self.log_level_combo.findText(log_level)
        if log_level_index >= 0:
            self.log_level_combo.setCurrentIndex(log_level_index)
        
        self.verbose_logging_check.setChecked(
            self.settings_manager.get('verbose_logging', False)
        )
    
    def apply_settings(self):
        """Apply settings without closing dialog"""
        self.save_settings()
        
        # Show confirmation
        self.apply_btn.setText("Applied!")
        self.apply_btn.setEnabled(False)
        
        # Reset button after 1 second
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: [
            self.apply_btn.setText("Apply"),
            self.apply_btn.setEnabled(True)
        ])
    
    def accept_settings(self):
        """Apply settings and close dialog"""
        self.save_settings()
        self.accept()
    
    def save_settings(self):
        """Save settings to manager"""
        # Security settings
        self.settings_manager.set('inactivity_timeout_minutes', 
                                self.inactivity_spin.value())
        self.settings_manager.set('auto_lock_on_minimize', 
                                self.lock_on_minimize_check.isChecked())
        self.settings_manager.set('clipboard_auto_clear_seconds', 
                                self.clipboard_timeout_spin.value())
        self.settings_manager.set('password_generator_length', 
                                self.password_length_spin.value())
        self.settings_manager.set('password_generator_symbols', 
                                self.default_symbols_check.isChecked())
        
        # Interface settings
        self.settings_manager.set('window_remember_size', 
                                self.remember_size_check.isChecked())
        self.settings_manager.set('theme', 
                                self.theme_combo.currentText())
        self.settings_manager.set('show_tooltips', 
                                self.tooltips_check.isChecked())
        self.settings_manager.set('alternating_row_colors', 
                                self.alternating_rows_check.isChecked())
        
        # Advanced settings
        self.settings_manager.set('backup_enabled', 
                                self.backup_enabled_check.isChecked())
        self.settings_manager.set('backup_count', 
                                self.backup_count_spin.value())
        self.settings_manager.set('autosave_interval_seconds', 
                                self.autosave_spin.value())
        self.settings_manager.set('log_level', 
                                self.log_level_combo.currentText())
        self.settings_manager.set('verbose_logging', 
                                self.verbose_logging_check.isChecked())
        
        self.logger.info("Settings saved")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings_manager.reset_to_defaults()
            self.load_settings()
            QMessageBox.information(self, "Reset Complete", 
                                  "All settings have been reset to defaults.")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.accept_settings()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)