import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import os


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config(temp_dir):
    """Create a sample configuration for testing."""
    config = {
        "base_download_dir": str(temp_dir),
        "session_cookie": "test_cookie_value",
        "max_workers": 3,
        "request_timeout": 30,
        "retry_attempts": 3,
        "retry_delays": [1, 2, 4],
        "mime_type_mapping": {
            "image/jpeg": "jpg",
            "image/png": "png",
            "application/pdf": "pdf"
        },
        "log_level": "INFO"
    }
    return config


@pytest.fixture
def config_file(temp_dir, sample_config):
    """Create a temporary config.json file."""
    config_path = temp_dir / "config.json"
    with open(config_path, 'w') as f:
        json.dump(sample_config, f)
    return config_path


@pytest.fixture
def mock_session():
    """Create a mock requests session."""
    session = MagicMock()
    session.get = MagicMock()
    session.post = MagicMock()
    return session


@pytest.fixture
def sample_html_response():
    """Sample HTML response with download links."""
    return """
    <html>
        <body>
            <a href="https://example.com/file1.jpg" class="download">File 1</a>
            <a href="https://example.com/file2.pdf" class="download">File 2</a>
            <a href="https://example.com/file3.png" class="download">File 3</a>
        </body>
    </html>
    """


@pytest.fixture
def mock_download_response():
    """Mock response object for file download."""
    mock = MagicMock()
    mock.status_code = 200
    mock.headers = {'Content-Type': 'application/pdf', 'Content-Length': '1024'}
    mock.content = b"fake file content"
    mock.iter_content = lambda chunk_size: [b"chunk1", b"chunk2"]
    return mock
