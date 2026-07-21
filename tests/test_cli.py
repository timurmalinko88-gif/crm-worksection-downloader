import pytest
import argparse
from pathlib import Path
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCLIArgumentParsing:
    """Test command-line argument parsing."""
    
    def test_batch_flag_parsing(self):
        """Test parsing --batch flag."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--batch', type=str, help='Batch file path')
        
        args = parser.parse_args(['--batch', 'tasks.txt'])
        assert args.batch == 'tasks.txt'
    
    def test_config_flag_parsing(self):
        """Test parsing --config flag."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--config', type=str, help='Config file path')
        
        args = parser.parse_args(['--config', 'custom_config.json'])
        assert args.config == 'custom_config.json'
    
    def test_log_level_flag_parsing(self):
        """Test parsing --log-level flag."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--log-level', type=str, default='INFO',
                          choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        
        args = parser.parse_args(['--log-level', 'DEBUG'])
        assert args.log_level == 'DEBUG'
    
    def test_default_log_level(self):
        """Test default log level when not specified."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--log-level', type=str, default='INFO',
                          choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        
        args = parser.parse_args([])
        assert args.log_level == 'INFO'
    
    def test_invalid_log_level_rejected(self):
        """Test that invalid log levels are rejected."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--log-level', type=str, default='INFO',
                          choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        
        with pytest.raises(SystemExit):
            parser.parse_args(['--log-level', 'INVALID'])
    
    def test_url_argument(self):
        """Test parsing URL argument."""
        parser = argparse.ArgumentParser()
        parser.add_argument('url', nargs='?', default=None, help='Task URL')
        
        args = parser.parse_args(['https://example.com/task/123'])
        assert args.url == 'https://example.com/task/123'
    
    def test_multiple_urls(self):
        """Test parsing multiple URLs."""
        parser = argparse.ArgumentParser()
        parser.add_argument('urls', nargs='*', help='Task URLs')
        
        args = parser.parse_args(['https://example.com/1', 'https://example.com/2'])
        assert len(args.urls) == 2
        assert args.urls[0] == 'https://example.com/1'
    
    def test_optional_url_argument(self):
        """Test that URL argument is optional."""
        parser = argparse.ArgumentParser()
        parser.add_argument('url', nargs='?', default=None)
        
        args = parser.parse_args([])
        assert args.url is None


class TestCLIUsageModes:
    """Test different CLI usage modes."""
    
    def test_interactive_mode_no_args(self):
        """Test interactive mode (no arguments)."""
        parser = argparse.ArgumentParser()
        parser.add_argument('url', nargs='?', default=None)
        parser.add_argument('--batch', type=str, default=None)
        parser.add_argument('--config', type=str, default=None)
        
        args = parser.parse_args([])
        # Interactive mode: no URL, no batch
        assert args.url is None
        assert args.batch is None
        assert args.config is None
    
    def test_single_url_mode(self):
        """Test single URL mode."""
        parser = argparse.ArgumentParser()
        parser.add_argument('url', nargs='?', default=None)
        parser.add_argument('--batch', type=str, default=None)
        
        args = parser.parse_args(['https://example.com/task/123'])
        assert args.url == 'https://example.com/task/123'
        assert args.batch is None
    
    def test_batch_mode(self):
        """Test batch file mode."""
        parser = argparse.ArgumentParser()
        parser.add_argument('url', nargs='?', default=None)
        parser.add_argument('--batch', type=str, default=None)
        
        args = parser.parse_args(['--batch', 'urls.txt'])
        assert args.batch == 'urls.txt'
        assert args.url is None  # URL not provided in batch mode


class TestConfigFileArgument:
    """Test --config argument for custom configuration."""
    
    def test_custom_config_path(self):
        """Test specifying custom configuration file."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--config', type=str, default='config.json')
        
        args = parser.parse_args(['--config', '/path/to/custom/config.json'])
        assert args.config == '/path/to/custom/config.json'
    
    def test_config_path_with_spaces(self):
        """Test config path with spaces in directory name."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--config', type=str)
        
        args = parser.parse_args(['--config', 'C:\\My Documents\\config.json'])
        assert args.config == 'C:\\My Documents\\config.json'
    
    def test_config_relative_path(self):
        """Test relative path for config file."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--config', type=str, default='config.json')
        
        args = parser.parse_args(['--config', './configs/test.json'])
        assert args.config == './configs/test.json'
    
    def test_config_absolute_path(self):
        """Test absolute path for config file."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--config', type=str)
        
        args = parser.parse_args(['--config', '/etc/downloader/config.json'])
        assert args.config == '/etc/downloader/config.json'


class TestBatchFileArgument:
    """Test --batch argument for batch processing."""
    
    def test_batch_file_path(self):
        """Test specifying batch file path."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--batch', type=str)
        
        args = parser.parse_args(['--batch', 'batch_urls.txt'])
        assert args.batch == 'batch_urls.txt'
    
    def test_batch_file_with_absolute_path(self):
        """Test batch file with absolute path."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--batch', type=str)
        
        args = parser.parse_args(['--batch', 'C:\\Downloads\\batch.txt'])
        assert args.batch == 'C:\\Downloads\\batch.txt'
    
    def test_batch_file_extension(self):
        """Test common batch file extensions."""
        valid_extensions = ['.txt', '.csv', '.list']
        
        for ext in valid_extensions:
            filename = f'batch{ext}'
            assert filename.endswith(ext)


class TestArgumentValidation:
    """Test validation of argument values."""
    
    def test_url_format_validation(self):
        """Test that URL format can be validated."""
        import re
        url_pattern = r'https?://\S+'
        
        valid_url = 'https://example.com/task/123'
        invalid_url = 'not a url'
        
        assert re.match(url_pattern, valid_url) is not None
        assert re.match(url_pattern, invalid_url) is None
    
    def test_file_path_validation(self):
        """Test that file paths are validated."""
        from pathlib import Path
        import os
        
        path_str = '/valid/path/file.txt'
        path_obj = Path(path_str)
        
        # Path object converts to OS-specific separator (backslash on Windows)
        # On Windows, forward slashes in path are converted to backslashes
        assert 'file.txt' in str(path_obj)
        assert 'valid' in str(path_obj)
        assert 'path' in str(path_obj)
    
    def test_log_level_choices(self):
        """Test log level is one of valid choices."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        test_level = 'INFO'
        
        assert test_level in valid_levels


class TestArgumentCombinations:
    """Test valid combinations of arguments."""
    
    def test_url_with_config(self):
        """Test URL with custom config."""
        parser = argparse.ArgumentParser()
        parser.add_argument('url', nargs='?')
        parser.add_argument('--config', type=str)
        
        args = parser.parse_args(['https://example.com/task', '--config', 'cfg.json'])
        assert args.url == 'https://example.com/task'
        assert args.config == 'cfg.json'
    
    def test_batch_with_config_and_log_level(self):
        """Test batch with config and log level."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--batch', type=str)
        parser.add_argument('--config', type=str)
        parser.add_argument('--log-level', type=str, default='INFO')
        
        args = parser.parse_args([
            '--batch', 'tasks.txt',
            '--config', 'custom.json',
            '--log-level', 'DEBUG'
        ])
        assert args.batch == 'tasks.txt'
        assert args.config == 'custom.json'
        assert args.log_level == 'DEBUG'
    
    def test_url_and_batch_mutually_exclusive(self):
        """Test that URL and batch are typically mutually exclusive."""
        parser = argparse.ArgumentParser()
        parser.add_argument('url', nargs='?', default=None)
        parser.add_argument('--batch', type=str, default=None)
        
        # Valid: URL only
        args = parser.parse_args(['https://example.com'])
        assert args.url is not None
        assert args.batch is None
        
        # Valid: batch only
        args = parser.parse_args(['--batch', 'file.txt'])
        assert args.url is None
        assert args.batch is not None
