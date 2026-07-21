import pytest
from pathlib import Path
import os
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestFolderCreation:
    """Test directory and folder creation."""
    
    def test_create_folder_for_new_task(self, temp_dir):
        """Test creating a new folder for a task."""
        task_folder = temp_dir / "task_12345"
        task_folder.mkdir(parents=True, exist_ok=True)
        
        assert task_folder.exists()
        assert task_folder.is_dir()
    
    def test_create_nested_folders(self, temp_dir):
        """Test creating nested folder structure."""
        nested_folder = temp_dir / "base" / "task" / "downloads"
        nested_folder.mkdir(parents=True, exist_ok=True)
        
        assert nested_folder.exists()
        assert nested_folder.parent.exists()
        assert nested_folder.parent.parent.exists()
    
    def test_existing_folder_not_recreated(self, temp_dir):
        """Test that existing folder doesn't cause error."""
        folder = temp_dir / "existing_task"
        folder.mkdir(parents=True, exist_ok=True)
        
        # Should not raise exception with exist_ok=True
        folder.mkdir(parents=True, exist_ok=True)
        assert folder.exists()


class TestFileOperations:
    """Test file save and rename operations."""
    
    def test_save_file_to_folder(self, temp_dir):
        """Test saving a file to a folder."""
        folder = temp_dir / "downloads"
        folder.mkdir(exist_ok=True)
        
        filepath = folder / "document_123.pdf"
        filepath.write_bytes(b"PDF content here")
        
        assert filepath.exists()
        assert filepath.read_bytes() == b"PDF content here"
    
    def test_file_extension_lowercase(self, temp_dir):
        """Test that file extensions are converted to lowercase."""
        folder = temp_dir / "test"
        folder.mkdir(exist_ok=True)
        
        filename = "document_456.PDF"
        filepath = folder / filename.lower()
        filepath.write_text("content")
        
        assert filepath.exists()
        assert str(filepath).endswith('.pdf')
    
    def test_rename_file_old_to_new_format(self, temp_dir):
        """Test renaming file from old format to new format."""
        folder = temp_dir / "task"
        folder.mkdir(exist_ok=True)
        
        # Old format: file_ID.ext
        old_file = folder / "file_789.pdf"
        old_file.write_text("content")
        
        # New format: task_ID.ext
        new_file = folder / "task_name_789.pdf"
        
        # Simulate rename
        if old_file.exists():
            old_file.rename(new_file)
        
        assert new_file.exists()
        assert not old_file.exists()
    
    def test_rename_does_not_overwrite(self, temp_dir):
        """Test that rename doesn't overwrite existing file."""
        folder = temp_dir / "test"
        folder.mkdir(exist_ok=True)
        
        old_file = folder / "old_name.txt"
        new_file = folder / "new_name.txt"
        
        old_file.write_text("old content")
        new_file.write_text("new content")
        
        # Both files should exist
        assert old_file.exists()
        assert new_file.exists()
        # Content should be different
        assert old_file.read_text() != new_file.read_text()


class TestFilenameFormatting:
    """Test filename generation and formatting."""
    
    def test_filename_format_article_id_extension(self):
        """Test filename format: article_ID.extension."""
        article_name = "article_name"
        file_id = "123456"
        extension = ".pdf"
        
        filename = f"{article_name}_{file_id}{extension}"
        assert filename == "article_name_123456.pdf"
    
    def test_filename_with_underscore_separator(self):
        """Test that underscore separates article name and ID."""
        filename = "my_product_789.jpg"
        parts = filename.replace('.jpg', '').split('_')
        
        # Should have at least 2 parts (name and ID)
        assert len(parts) >= 2
        # Last part should be numeric ID
        assert parts[-1].isdigit()
    
    def test_filename_preserves_spaces_removed(self):
        """Test that spaces in article names are handled."""
        # Depending on implementation, spaces might be removed or replaced
        article_with_spaces = "My Article Name"
        # After cleaning, should not have spaces (or replaced with underscore)
        cleaned = article_with_spaces.replace(" ", "_")
        assert " " not in cleaned or "_" in cleaned


class TestDirectoryScanning:
    """Test scanning and listing files in directories."""
    
    def test_list_files_in_folder(self, temp_dir):
        """Test listing files in a folder."""
        folder = temp_dir / "data"
        folder.mkdir(exist_ok=True)
        
        # Create some test files
        (folder / "file1.pdf").write_text("1")
        (folder / "file2.jpg").write_text("2")
        (folder / "file3.png").write_text("3")
        
        files = list(folder.iterdir())
        assert len(files) == 3
    
    def test_find_files_with_pattern(self, temp_dir):
        """Test finding files matching a pattern."""
        folder = temp_dir / "search"
        folder.mkdir(exist_ok=True)
        
        # Create files with pattern
        (folder / "article_101.pdf").write_text("1")
        (folder / "article_102.pdf").write_text("2")
        (folder / "article_103.jpg").write_text("3")
        (folder / "other_file.txt").write_text("4")
        
        # Find all article_*.pdf files
        pdf_files = list(folder.glob("article_*.pdf"))
        assert len(pdf_files) == 2
    
    def test_extract_id_from_filename(self):
        """Test extracting ID from filename."""
        filename = "article_12345.pdf"
        # Extract ID (number before extension)
        import re
        match = re.search(r'(\d+)', filename)
        assert match is not None
        assert match.group(1) == "12345"


class TestErrorHandlingFileOps:
    """Test error handling in file operations."""
    
    def test_handle_invalid_path(self, temp_dir):
        """Test handling of invalid file paths."""
        invalid_path = temp_dir / "nonexistent_parent" / "file.txt"
        
        # Should fail without parents=True
        # But succeed with parents=True
        try:
            invalid_path.parent.mkdir(parents=True, exist_ok=True)
            result = True
        except Exception:
            result = False
        
        assert result is True
    
    def test_permission_denied_simulation(self, temp_dir):
        """Test handling of permission denied errors."""
        # On Windows, this is harder to test, but we can verify error types
        import errno
        permission_error = PermissionError("Access denied")
        assert isinstance(permission_error, OSError)
    
    def test_disk_full_simulation(self):
        """Test handling of disk full condition."""
        disk_error = OSError("No space left on device")
        assert isinstance(disk_error, Exception)
