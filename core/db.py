"""
Database operations for encrypted SQLite storage
"""

import os
import sqlite3
import logging
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import tempfile
import shutil

from .crypto import CryptoManager
from .utils import get_app_data_dir


class DatabaseManager:
    """Manages encrypted SQLite database operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.crypto = CryptoManager()
        self.db_path = None
        self.master_key = None
        self.connection = None
        self.temp_db_path = None
        
    def get_db_path(self) -> str:
        """Get the database file path"""
        if not self.db_path:
            app_dir = get_app_data_dir()
            self.db_path = os.path.join(app_dir, "passwords.db")
        return self.db_path
    
    def initialize_database(self, master_key: bytes, salt: bytes, password_hash: bytes, test_vector: str) -> bool:
        """
        Initialize new encrypted database
        
        Args:
            master_key: Encryption key
            salt: Password salt
            password_hash: Hashed master password
            test_vector: Encrypted test vector
            
        Returns:
            True if successful
        """
        try:
            self.master_key = master_key
            
            # Create temporary in-memory database
            temp_conn = sqlite3.connect(':memory:')
            self._create_tables(temp_conn)
            
            # Insert metadata
            cursor = temp_conn.cursor()
            cursor.execute("""
                INSERT INTO metadata (key, value) VALUES (?, ?)
            """, ('salt', salt.hex()))
            
            cursor.execute("""
                INSERT INTO metadata (key, value) VALUES (?, ?)
            """, ('password_hash', password_hash.hex()))
            
            cursor.execute("""
                INSERT INTO metadata (key, value) VALUES (?, ?)
            """, ('test_vector', test_vector))
            
            cursor.execute("""
                INSERT INTO metadata (key, value) VALUES (?, ?)
            """, ('created_date', datetime.now().isoformat()))
            
            cursor.execute("""
                INSERT INTO metadata (key, value) VALUES (?, ?)
            """, ('version', '1.0'))
            
            temp_conn.commit()
            
            # Save encrypted database
            success = self._save_encrypted_database(temp_conn)
            temp_conn.close()
            
            if success:
                self.logger.info("Database initialized successfully")
                # Now load the database to establish connection for immediate use
                load_success = self.load_database(master_key)
                if load_success:
                    self.logger.info("Database loaded and ready for use")
                    return True
                else:
                    self.logger.error("Database created but failed to load")
                    return False
            else:
                self.logger.error("Failed to save encrypted database")
                return False
                
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False
    
    def load_database(self, master_key: bytes) -> bool:
        """
        Load and decrypt database
        
        Args:
            master_key: Decryption key
            
        Returns:
            True if successful
        """
        try:
            self.master_key = master_key
            
            # Load encrypted database
            decrypted_content = self._load_encrypted_database()
            if not decrypted_content:
                return False
            
            # Create temporary file for SQLite that won't be deleted immediately
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"temp_db_load_{os.getpid()}_{int(datetime.now().timestamp())}.db")
            
            try:
                # Write decrypted content to temporary file
                with open(temp_path, 'wb') as temp_file:
                    temp_file.write(decrypted_content)
                
                # Connect to decrypted database
                self.connection = sqlite3.connect(temp_path)
                self.connection.row_factory = sqlite3.Row
                
                # Verify database structure
                if not self._verify_database_structure():
                    self.logger.error("Invalid database structure")
                    return False
                
                # Store temp path for cleanup later
                self.temp_db_path = temp_path
                
                self.logger.info("Database loaded successfully")
                return True
                
            except Exception as load_error:
                # Clean up on error
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                raise load_error
                
        except Exception as e:
            self.logger.error(f"Database loading failed: {e}")
            return False
    
    def save_database(self) -> bool:
        """Save current database state encrypted"""
        if not self.connection or not self.master_key:
            return False
        
        return self._save_encrypted_database(self.connection)
    
    def close_database(self):
        """Close database connection and clear sensitive data"""
        if self.connection:
            self.connection.close()
            self.connection = None
        
        # Clean up temporary database file
        if self.temp_db_path and os.path.exists(self.temp_db_path):
            try:
                os.unlink(self.temp_db_path)
                self.temp_db_path = None
            except:
                pass
        
        if self.master_key:
            # Overwrite master key
            self.crypto.secure_delete(self.master_key)
            self.master_key = None
        
        self.logger.info("Database closed and sensitive data cleared")
    
    def get_metadata(self, key: str) -> Optional[str]:
        """Get metadata value"""
        if not self.connection:
            return None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else None
        except Exception as e:
            self.logger.error(f"Failed to get metadata {key}: {e}")
            return None
    
    def set_metadata(self, key: str, value: str) -> bool:
        """Set metadata value"""
        if not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)
            """, (key, value))
            self.connection.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to set metadata {key}: {e}")
            return False
    
    def add_credential(self, title: str, username: str, password: str, 
                      url: str = "", notes: str = "", category: str = "General") -> bool:
        """
        Add new credential entry
        
        Args:
            title: Entry title
            username: Username
            password: Password (will be encrypted)
            url: Website URL
            notes: Additional notes
            category: Category name
            
        Returns:
            True if successful
        """
        if not self.connection or not self.master_key:
            return False
        
        try:
            # Encrypt sensitive data
            encrypted_password = self.crypto.encrypt_data(password, self.master_key)
            encrypted_notes = self.crypto.encrypt_data(notes, self.master_key) if notes else ""
            
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO credentials (title, username, password, url, notes, category, created_date, modified_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, username, encrypted_password, url, encrypted_notes, category, 
                  datetime.now().isoformat(), datetime.now().isoformat()))
            
            self.connection.commit()
            self.logger.info(f"Added credential: {title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add credential: {e}")
            return False
    
    def update_credential(self, credential_id: int, title: str, username: str, 
                         password: str, url: str = "", notes: str = "", category: str = "General") -> bool:
        """Update existing credential"""
        if not self.connection or not self.master_key:
            return False
        
        try:
            # Encrypt sensitive data
            encrypted_password = self.crypto.encrypt_data(password, self.master_key)
            encrypted_notes = self.crypto.encrypt_data(notes, self.master_key) if notes else ""
            
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE credentials 
                SET title=?, username=?, password=?, url=?, notes=?, category=?, modified_date=?
                WHERE id=?
            """, (title, username, encrypted_password, url, encrypted_notes, category,
                  datetime.now().isoformat(), credential_id))
            
            self.connection.commit()
            self.logger.info(f"Updated credential ID: {credential_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update credential: {e}")
            return False
    
    def delete_credential(self, credential_id: int) -> bool:
        """Delete credential by ID"""
        if not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM credentials WHERE id=?", (credential_id,))
            self.connection.commit()
            self.logger.info(f"Deleted credential ID: {credential_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete credential: {e}")
            return False
    
    def get_all_credentials(self) -> List[Dict[str, Any]]:
        """Get all credentials (passwords remain encrypted)"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, title, username, password, url, notes, category, created_date, modified_date
                FROM credentials ORDER BY title
            """)
            
            credentials = []
            for row in cursor.fetchall():
                credentials.append({
                    'id': row['id'],
                    'title': row['title'],
                    'username': row['username'],
                    'password': row['password'],  # Still encrypted
                    'url': row['url'],
                    'notes': row['notes'],  # Still encrypted
                    'category': row['category'],
                    'created_date': row['created_date'],
                    'modified_date': row['modified_date']
                })
            
            return credentials
            
        except Exception as e:
            self.logger.error(f"Failed to get credentials: {e}")
            return []
    
    def get_credential(self, credential_id: int) -> Optional[Dict[str, Any]]:
        """Get single credential by ID with decrypted password"""
        if not self.connection or not self.master_key:
            return None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, title, username, password, url, notes, category, created_date, modified_date
                FROM credentials WHERE id=?
            """, (credential_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Decrypt password and notes
            password = self.crypto.decrypt_data(row['password'], self.master_key)
            notes = ""
            if row['notes']:
                notes = self.crypto.decrypt_data(row['notes'], self.master_key) or ""
            
            return {
                'id': row['id'],
                'title': row['title'],
                'username': row['username'],
                'password': password,
                'url': row['url'],
                'notes': notes,
                'category': row['category'],
                'created_date': row['created_date'],
                'modified_date': row['modified_date']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get credential {credential_id}: {e}")
            return None
    
    def search_credentials(self, query: str) -> List[Dict[str, Any]]:
        """Search credentials by title, username, or URL"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT id, title, username, password, url, notes, category, created_date, modified_date
                FROM credentials 
                WHERE title LIKE ? OR username LIKE ? OR url LIKE ? OR category LIKE ?
                ORDER BY title
            """, (search_pattern, search_pattern, search_pattern, search_pattern))
            
            credentials = []
            for row in cursor.fetchall():
                credentials.append({
                    'id': row['id'],
                    'title': row['title'],
                    'username': row['username'],
                    'password': row['password'],  # Still encrypted
                    'url': row['url'],
                    'notes': row['notes'],  # Still encrypted
                    'category': row['category'],
                    'created_date': row['created_date'],
                    'modified_date': row['modified_date']
                })
            
            return credentials
            
        except Exception as e:
            self.logger.error(f"Failed to search credentials: {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT category FROM credentials ORDER BY category")
            return [row['category'] for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to get categories: {e}")
            return []
    
    def _create_tables(self, conn: sqlite3.Connection):
        """Create database tables"""
        cursor = conn.cursor()
        
        # Metadata table
        cursor.execute("""
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Credentials table
        cursor.execute("""
            CREATE TABLE credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                url TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                category TEXT DEFAULT 'General',
                created_date TEXT NOT NULL,
                modified_date TEXT NOT NULL
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_credentials_title ON credentials(title)")
        cursor.execute("CREATE INDEX idx_credentials_category ON credentials(category)")
        
        conn.commit()
    
    def _verify_database_structure(self) -> bool:
        """Verify database has correct structure"""
        try:
            cursor = self.connection.cursor()
            
            # Check if required tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('metadata', 'credentials')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            return 'metadata' in tables and 'credentials' in tables
            
        except Exception as e:
            self.logger.error(f"Database structure verification failed: {e}")
            return False
    
    def _save_encrypted_database(self, conn: sqlite3.Connection) -> bool:
        """Save database content encrypted to file"""
        try:
            # Create a temporary file to dump database content
            temp_dir = tempfile.gettempdir()
            temp_db_path = os.path.join(temp_dir, f"temp_db_{os.getpid()}_{int(datetime.now().timestamp())}.db")
            
            try:
                # Use sqlite3 backup to copy database to temporary file
                temp_conn = sqlite3.connect(temp_db_path)
                conn.backup(temp_conn)
                temp_conn.close()
                
                # Read database content
                with open(temp_db_path, 'rb') as temp_file:
                    db_content = temp_file.read()
                
                # Clean up temporary file
                if os.path.exists(temp_db_path):
                    os.remove(temp_db_path)
                    
            except Exception as temp_error:
                # Clean up in case of error
                if os.path.exists(temp_db_path):
                    try:
                        os.remove(temp_db_path)
                    except:
                        pass
                raise temp_error
            
            # Encrypt content
            encrypted_content = self.crypto.encrypt_database_content(db_content, self.master_key)
            
            # Ensure directory exists
            db_path = self.get_db_path()
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # Create file with unencrypted header for authentication metadata
            with open(db_path, 'wb') as f:
                # Write magic header to identify file format
                f.write(b'PWKDB1.0')  # 8 bytes magic header
                
                # Extract and write authentication metadata
                cursor = conn.cursor()
                
                # Get salt
                cursor.execute("SELECT value FROM metadata WHERE key = 'salt'")
                salt_row = cursor.fetchone()
                salt_hex = salt_row[0] if salt_row else ''  # Access by index, not key
                salt_bytes = bytes.fromhex(salt_hex) if salt_hex else b''
                
                # Get password hash
                cursor.execute("SELECT value FROM metadata WHERE key = 'password_hash'")
                hash_row = cursor.fetchone()
                hash_hex = hash_row[0] if hash_row else ''  # Access by index, not key
                hash_bytes = bytes.fromhex(hash_hex) if hash_hex else b''
                hash_bytes = bytes.fromhex(hash_hex) if hash_hex else b''
                
                # Write metadata lengths and data
                f.write(len(salt_bytes).to_bytes(4, 'little'))  # Salt length (4 bytes)
                f.write(salt_bytes)  # Salt data (32 bytes)
                f.write(len(hash_bytes).to_bytes(4, 'little'))  # Hash length (4 bytes)
                f.write(hash_bytes)  # Hash data (32 bytes)
                
                # Write encrypted database content
                f.write(encrypted_content)
            
            self.logger.info(f"Database saved successfully to: {db_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save encrypted database: {e}")
            return False
    
    def _load_encrypted_database(self) -> Optional[bytes]:
        """Load and decrypt database from file"""
        try:
            # Read file content
            with open(self.get_db_path(), 'rb') as f:
                content = f.read()
            
            # Skip header to get encrypted content
            header_size = self._get_header_size(content)
            encrypted_content = content[header_size:]
            
            # Decrypt content
            decrypted_content = self.crypto.decrypt_database_content(encrypted_content, self.master_key)
            
            if decrypted_content is None:
                self.logger.error("Failed to decrypt database - incorrect key or corrupted data")
                return None
            
            return decrypted_content
            
        except FileNotFoundError:
            self.logger.error(f"Database file not found: {self.get_db_path()}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to load encrypted database: {e}")
            return None
    
    def _get_header_size(self, content: bytes) -> int:
        """Calculate the size of the unencrypted header"""
        if len(content) < 16:  # Minimum header size
            return 0
            
        # Check magic header
        if content[:8] != b'PWKDB1.0':
            return 0  # Old format, no header
        
        # Read salt length
        salt_len = int.from_bytes(content[8:12], 'little')
        # Read hash length  
        hash_len = int.from_bytes(content[12 + salt_len:16 + salt_len], 'little')
        
        # Total header size: magic(8) + salt_len(4) + salt_data + hash_len(4) + hash_data
        return 8 + 4 + salt_len + 4 + hash_len
    
    def get_auth_metadata(self) -> tuple[bytes, bytes]:
        """Get authentication metadata (salt and password hash) from file header"""
        try:
            with open(self.get_db_path(), 'rb') as f:
                content = f.read()
            
            # Check if file has new format with header
            if len(content) < 16 or content[:8] != b'PWKDB1.0':
                raise Exception("Database file format not supported or corrupted")
            
            # Read salt
            salt_len = int.from_bytes(content[8:12], 'little')
            salt_bytes = content[12:12 + salt_len]
            
            # Read hash
            hash_len = int.from_bytes(content[12 + salt_len:16 + salt_len], 'little')
            hash_bytes = content[16 + salt_len:16 + salt_len + hash_len]
            
            return salt_bytes, hash_bytes
            
        except Exception as e:
            self.logger.error(f"Failed to get auth metadata: {e}")
            raise