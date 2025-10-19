"""
Password Keeper - Secure Password Manager
Main application entry point
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from ui.main_window import MainWindow
from ui.setup_window import SetupWindow
from ui.login_window import LoginWindow
from core.db import DatabaseManager
from core.auth import AuthManager
from core.utils import setup_logging, get_app_data_dir, is_portable_mode


class PasswordKeeperApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Password Keeper")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("SecureApp")
        
        # Setup logging
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthManager()
        
        # Windows
        self.main_window = None
        self.setup_window = None
        self.login_window = None
        
        # Set application icon
        self.set_app_icon()
        
    def set_app_icon(self):
        """Set application icon"""
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.ico")
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))
    
    def run(self):
        """Main application flow"""
        try:
            # Show portable mode info if applicable
            if is_portable_mode():
                self.logger.info("Running in PORTABLE MODE")
                data_dir = get_app_data_dir()
                self.logger.info(f"Data directory: {data_dir}")
            
            # Check if database exists
            db_path = self.db_manager.get_db_path()
            
            if not os.path.exists(db_path):
                # First time setup
                self.logger.info("First time setup - creating new database")
                self.show_setup_window()
            else:
                # Existing database - show login
                self.logger.info("Existing database found - showing login")
                self.show_login_window()
            
            return self.app.exec()
            
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            QMessageBox.critical(None, "Error", f"Application error: {e}")
            return 1
    
    def show_setup_window(self):
        """Show initial setup window"""
        self.setup_window = SetupWindow(self.db_manager, self.auth_manager)
        self.setup_window.setup_complete.connect(self.on_setup_complete)
        self.setup_window.show()
    
    def show_login_window(self):
        """Show login window"""
        try:
            # First, try to validate the database file format
            db_path = self.db_manager.get_db_path()
            if os.path.exists(db_path):
                try:
                    # Try to read the header to check format
                    with open(db_path, 'rb') as f:
                        header = f.read(8)
                    
                    # Check if it's the new format
                    if len(header) < 8 or header != b'PWKDB1.0':
                        # Old or incompatible format
                        QMessageBox.warning(
                            None, "Database Format",
                            "The existing database file is in an old or incompatible format.\n\n"
                            "Please backup your data if needed, then delete the database file\n"
                            "to start fresh, or restore from a compatible backup.\n\n"
                            f"Database location: {db_path}"
                        )
                        return
                        
                except Exception as format_error:
                    QMessageBox.critical(
                        None, "Database Error",
                        f"Could not read database file format.\n\n"
                        f"Error: {format_error}\n\n"
                        f"Database location: {db_path}"
                    )
                    return
            
            self.login_window = LoginWindow(self.db_manager, self.auth_manager)
            self.login_window.login_successful.connect(self.on_login_successful)
            self.login_window.show()
            
        except Exception as e:
            self.logger.error(f"Failed to show login window: {e}")
            QMessageBox.critical(None, "Error", f"Failed to initialize login: {e}")
    
    def show_main_window(self):
        """Show main application window"""
        self.main_window = MainWindow(self.db_manager, self.auth_manager)
        self.main_window.show()
        
        # Close other windows
        if self.setup_window:
            self.setup_window.close()
        if self.login_window:
            self.login_window.close()
    
    def on_setup_complete(self):
        """Handle setup completion"""
        self.logger.info("Setup completed successfully")
        self.show_main_window()
    
    def on_login_successful(self):
        """Handle successful login"""
        self.logger.info("Login successful")
        self.show_main_window()


def main():
    """Application entry point"""
    app = PasswordKeeperApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())