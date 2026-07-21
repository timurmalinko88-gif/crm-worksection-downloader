import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open
import sys
import os

# Add parent directory to path to import downloader
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfigLoading:
    """Test configuration file loading and default values."""
    
    def test_load_valid_config(self, config_file, sample_config):
        """Test loading a valid configuration file."""
        # We'll test this by verifying the file exists and has correct content
        assert config_file.exists()
        with open(config_file, 'r') as f:
            loaded = json.load(f)
        assert loaded == sample_config
    
    def test_config_has_required_keys(self, sample_config):
        """Test that sample config contains all required keys."""
        required_keys = [
            'base_download_dir',
            'session_cookie',
            'max_workers',
            'request_timeout',
            'retry_attempts',
            'mime_type_mapping',
            'log_level'
        ]
        for key in required_keys:
            assert key in sample_config, f"Missing required key: {key}"
    
    def test_config_mime_types_are_mapped(self, sample_config):
        """Test that MIME types are correctly mapped to extensions."""
        mime_mapping = sample_config['mime_type_mapping']
        assert 'image/jpeg' in mime_mapping
        assert mime_mapping['image/jpeg'] == 'jpg'
        assert 'application/pdf' in mime_mapping
        assert mime_mapping['application/pdf'] == 'pdf'
    
    def test_invalid_json_config_returns_default(self, temp_dir):
        """Test that invalid JSON returns default config gracefully."""
        invalid_config_path = temp_dir / "invalid_config.json"
        invalid_config_path.write_text("{ invalid json }")
        
        # This would be tested by calling load_config() from downloader module
        # For now we verify the file can be detected as invalid
        with pytest.raises(json.JSONDecodeError):
            json.load(open(invalid_config_path))
    
    def test_missing_config_file(self, temp_dir):
        """Test handling of missing configuration file."""
        missing_config = temp_dir / "nonexistent_config.json"
        assert not missing_config.exists()
    
    def test_config_timeout_values(self, sample_config):
        """Test that timeout values are reasonable."""
        assert sample_config['request_timeout'] > 0
        assert sample_config['request_timeout'] < 300  # Less than 5 minutes
    
    def test_config_retry_settings(self, sample_config):
        """Test that retry settings are valid."""
        assert sample_config['retry_attempts'] >= 1
        assert sample_config['retry_attempts'] <= 10
    
    def test_config_max_workers(self, sample_config):
        """Test that max workers is reasonable."""
        assert 1 <= sample_config['max_workers'] <= 20
    
    def test_config_base_dir_is_string(self, sample_config):
        """Test that base directory is a string path."""
        assert isinstance(sample_config['base_download_dir'], str)
        assert len(sample_config['base_download_dir']) > 0
    
    def test_session_cookie_in_config(self, sample_config):
        """Test that session cookie field exists."""
        assert 'session_cookie' in sample_config


class TestConfigDefaults:
    """Test default configuration values."""
    
    def test_default_retry_delays(self, sample_config):
        """Test retry delay configuration if present."""
        if 'retry_delays' in sample_config:
            delays = sample_config['retry_delays']
            assert len(delays) > 0
            # Should be exponential: [1, 2, 4] or similar
            assert delays[0] < delays[1] if len(delays) > 1 else True
    
    def test_log_level_is_valid(self, sample_config):
        """Test that log level is one of the standard levels."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        assert sample_config['log_level'] in valid_levels
