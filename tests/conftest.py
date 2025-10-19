"""
Test configuration and fixtures
"""

import pytest
import tempfile
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def test_db_path(temp_dir):
    """Get test database path"""
    return os.path.join(temp_dir, "test_passwords.db")


@pytest.fixture
def mock_master_key():
    """Generate mock master key for testing"""
    import secrets
    return secrets.token_bytes(32)


@pytest.fixture
def sample_credentials():
    """Sample credential data for testing"""
    return [
        {
            'title': 'Gmail',
            'username': 'user@gmail.com',
            'password': 'SecurePassword123!',
            'url': 'https://gmail.com',
            'notes': 'Personal email account',
            'category': 'Email'
        },
        {
            'title': 'Facebook',
            'username': 'user@example.com',
            'password': 'SocialPass456@',
            'url': 'https://facebook.com',
            'notes': 'Social media account',
            'category': 'Social Media'
        },
        {
            'title': 'Bank Account',
            'username': 'customer123',
            'password': 'BankingSecure789#',
            'url': 'https://bank.example.com',
            'notes': 'Online banking credentials',
            'category': 'Banking'
        }
    ]