"""
Unit tests for API key generation and validation.

Tests the core API key functionality:
- API key generation (format: ss-proj-h_ + 147-char alphanumeric with one hyphen)
- API key format validation
- API key hashing
- API key model methods
"""

import pytest
import re
from sentrascan.core.models import APIKey
from sentrascan.server import generate_api_key


class TestAPIKeyGeneration:
    """Test API key generation functionality"""
    
    def test_generate_api_key_format(self):
        """Test that generated API keys match the required format"""
        key = generate_api_key()
        
        # Check prefix
        assert key.startswith("ss-proj-h_")
        
        # The implementation generates 147 alphanumeric chars, then inserts a hyphen
        # So the key part will be 148 chars total (147 alphanumeric + 1 hyphen)
        # Total key length: 10 (prefix) + 148 (key part) = 158
        assert len(key) == 158  # 10 (prefix) + 148 (147 alphanumeric + 1 hyphen)
        
        # Check format: alphanumeric with exactly one hyphen
        key_part = key[10:]  # After "ss-proj-h_"
        assert len(key_part) == 148  # 147 alphanumeric + 1 hyphen
        assert re.match(r'^[A-Za-z0-9-]+$', key_part)
        assert key_part.count('-') == 1
    
    def test_generate_api_key_uniqueness(self):
        """Test that generated API keys are unique"""
        keys = [generate_api_key() for _ in range(100)]
        assert len(keys) == len(set(keys)), "Generated keys should be unique"
    
    def test_generate_api_key_alphanumeric(self):
        """Test that generated keys contain only alphanumeric characters and one hyphen"""
        key = generate_api_key()
        key_part = key[10:]  # After "ss-proj-h_"
        
        # Should contain only A-Z, a-z, 0-9, and exactly one hyphen
        assert all(c.isalnum() or c == '-' for c in key_part)
        assert key_part.count('-') == 1


class TestAPIKeyValidation:
    """Test API key format validation"""
    
    def test_validate_key_format_valid(self):
        """Test validation of valid API key format"""
        # Valid key: prefix + 73 chars + hyphen + 73 chars = 147 chars total
        valid_key = "ss-proj-h_" + "a" * 73 + "-" + "b" * 73
        assert APIKey.validate_key_format(valid_key) is True
    
    def test_validate_key_format_invalid_prefix(self):
        """Test validation rejects keys with wrong prefix"""
        invalid_key = "invalid-prefix_" + "a" * 73 + "-" + "b" * 73
        assert APIKey.validate_key_format(invalid_key) is False
    
    def test_validate_key_format_wrong_length(self):
        """Test validation rejects keys with wrong length"""
        # Too short
        short_key = "ss-proj-h_" + "a" * 100
        assert APIKey.validate_key_format(short_key) is False
        
        # Too long
        long_key = "ss-proj-h_" + "a" * 200
        assert APIKey.validate_key_format(long_key) is False
    
    def test_validate_key_format_no_hyphen(self):
        """Test validation rejects keys without hyphen"""
        no_hyphen_key = "ss-proj-h_" + "a" * 147
        assert APIKey.validate_key_format(no_hyphen_key) is False
    
    def test_validate_key_format_multiple_hyphens(self):
        """Test validation rejects keys with multiple hyphens"""
        multi_hyphen_key = "ss-proj-h_" + "a" * 50 + "-" + "b" * 50 + "-" + "c" * 45
        assert APIKey.validate_key_format(multi_hyphen_key) is False
    
    def test_validate_key_format_invalid_characters(self):
        """Test validation rejects keys with invalid characters"""
        invalid_chars_key = "ss-proj-h_" + "a" * 73 + "_" + "b" * 73  # Underscore instead of hyphen
        assert APIKey.validate_key_format(invalid_chars_key) is False
        
        special_chars_key = "ss-proj-h_" + "a" * 73 + "@" + "b" * 73  # Special character
        assert APIKey.validate_key_format(special_chars_key) is False
    
    def test_validate_key_format_edge_cases(self):
        """Test validation with edge cases"""
        # Empty string
        assert APIKey.validate_key_format("") is False
        
        # Just prefix
        assert APIKey.validate_key_format("ss-proj-h_") is False
        
        # Only prefix and hyphen
        assert APIKey.validate_key_format("ss-proj-h_-") is False


class TestAPIKeyHashing:
    """Test API key hashing functionality"""
    
    def test_hash_key_consistency(self):
        """Test that hashing the same key produces the same hash"""
        key = "ss-proj-h_" + "a" * 73 + "-" + "b" * 73
        hash1 = APIKey.hash_key(key)
        hash2 = APIKey.hash_key(key)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64-char hex string
    
    def test_hash_key_different_keys(self):
        """Test that different keys produce different hashes"""
        key1 = "ss-proj-h_" + "a" * 73 + "-" + "b" * 73
        key2 = "ss-proj-h_" + "b" * 73 + "-" + "a" * 73
        
        hash1 = APIKey.hash_key(key1)
        hash2 = APIKey.hash_key(key2)
        
        assert hash1 != hash2
    
    def test_hash_key_format(self):
        """Test that hash is a valid hex string"""
        key = "ss-proj-h_" + "a" * 73 + "-" + "b" * 73
        key_hash = APIKey.hash_key(key)
        
        # Should be 64 characters of hex
        assert len(key_hash) == 64
        assert all(c in '0123456789abcdef' for c in key_hash)


class TestAPIKeyModel:
    """Test APIKey model methods and properties"""
    
    def test_api_key_model_exists(self):
        """Test that APIKey model is importable"""
        assert APIKey is not None
        assert hasattr(APIKey, 'hash_key')
        assert hasattr(APIKey, 'validate_key_format')
    
    def test_hash_key_static_method(self):
        """Test that hash_key is a static method"""
        key = "ss-proj-h_" + "a" * 73 + "-" + "b" * 73
        # Should be callable without instance
        hash_result = APIKey.hash_key(key)
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64
    
    def test_validate_key_format_static_method(self):
        """Test that validate_key_format is a static method"""
        valid_key = "ss-proj-h_" + "a" * 73 + "-" + "b" * 73
        # Should be callable without instance
        result = APIKey.validate_key_format(valid_key)
        assert isinstance(result, bool)
        assert result is True

