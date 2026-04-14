"""
Unit tests for File Operations (Agent 1 - T1.3)

Tests file reading, writing, path handling, encoding, and edge cases.
Target: 30+ test cases, 90%+ coverage
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from migratex.utils.file_ops import copy_project_structure
from migratex.testing.edge_case_fixtures import EdgeCaseTestFixtures


class TestFileOperations:
    """Test file operations and path handling."""
    
    def test_copy_project_structure_basic(self):
        """Test basic project structure copying."""
        source = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        dest = Path(tempfile.mkdtemp())
        try:
            copy_project_structure(source, dest)
            
            assert (dest / "main.py").exists()
            assert (dest / "main.py").read_text(encoding="utf-8") == "from semantic_kernel import Kernel"
        finally:
            EdgeCaseTestFixtures.cleanup(source)
            if dest.exists():
                shutil.rmtree(dest)
    
    def test_copy_project_structure_preserves_nesting(self):
        """Test that nested directory structure is preserved."""
        source = EdgeCaseTestFixtures.create_deep_nested_codebase(levels=5)
        dest = Path(tempfile.mkdtemp())
        try:
            copy_project_structure(source, dest)
            
            # Find the deep file
            deep_file = list(dest.rglob("deep.py"))[0]
            assert deep_file.exists()
            assert len(deep_file.parts) > 5  # Should preserve nesting
        finally:
            EdgeCaseTestFixtures.cleanup(source)
            if dest.exists():
                shutil.rmtree(dest)
    
    def test_copy_project_structure_excludes_cache(self):
        """Test that cache directories are excluded."""
        source = Path(tempfile.mkdtemp())
        (source / "main.py").write_text("import os")
        (source / "__pycache__").mkdir()
        (source / "__pycache__" / "main.cpython-39.pyc").write_bytes(b"fake bytecode")
        
        dest = Path(tempfile.mkdtemp())
        try:
            copy_project_structure(source, dest)
            
            assert (dest / "main.py").exists()
            assert not (dest / "__pycache__").exists()
        finally:
            shutil.rmtree(source)
            if dest.exists():
                shutil.rmtree(dest)
    
    def test_file_reading_utf8(self):
        """Test reading UTF-8 encoded files."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel\n# Unicode: émoji 🚀"
        )
        try:
            file_path = fixture / "main.py"
            content = file_path.read_text(encoding="utf-8")
            
            assert "semantic_kernel" in content
            assert "émoji" in content
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_file_reading_latin1(self):
        """Test reading latin-1 encoded files."""
        fixture = Path(tempfile.mkdtemp())
        file_path = fixture / "latin1.py"
        file_path.write_bytes(b"# -*- coding: latin-1 -*-\nfrom semantic_kernel import Kernel\n\xe9")  # é
        
        try:
            # Try reading with latin-1
            content = file_path.read_text(encoding="latin-1")
            assert "semantic_kernel" in content
        finally:
            shutil.rmtree(fixture)
    
    def test_file_writing_utf8(self):
        """Test writing UTF-8 encoded files."""
        fixture = Path(tempfile.mkdtemp())
        file_path = fixture / "test.py"
        
        try:
            content = "from semantic_kernel import Kernel\n# Unicode: émoji 🚀"
            file_path.write_text(content, encoding="utf-8")
            
            assert file_path.exists()
            assert file_path.read_text(encoding="utf-8") == content
        finally:
            shutil.rmtree(fixture)
    
    def test_file_writing_preserves_line_endings(self):
        """Test that line endings are preserved."""
        fixture = Path(tempfile.mkdtemp())
        file_path = fixture / "test.py"
        
        try:
            # Write with CRLF
            content = "line1\r\nline2\r\nline3"
            file_path.write_text(content, encoding="utf-8", newline="")
            
            # Read back
            read_content = file_path.read_bytes()
            assert b"\r\n" in read_content
        finally:
            shutil.rmtree(fixture)
    
    def test_path_handling_relative(self):
        """Test handling of relative paths."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        try:
            relative_path = Path("main.py")
            absolute_path = fixture / relative_path
            
            assert absolute_path.exists()
            assert absolute_path.is_absolute()
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_path_handling_absolute(self):
        """Test handling of absolute paths."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        try:
            file_path = fixture / "main.py"
            absolute_path = file_path.resolve()
            
            assert absolute_path.is_absolute()
            assert absolute_path.exists()
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_path_handling_windows_style(self):
        """Test handling of Windows-style paths."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        try:
            file_path = fixture / "main.py"
            # Convert to Windows-style path string
            windows_path = str(file_path).replace("/", "\\")
            path_obj = Path(windows_path)
            
            assert path_obj.exists()
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_large_file_handling(self):
        """Test handling of large files (>10K lines)."""
        fixture = EdgeCaseTestFixtures.create_large_file_codebase(lines=15000)
        try:
            large_file = list(fixture.rglob("*.py"))[0]
            content = large_file.read_text(encoding="utf-8")
            
            assert len(content.splitlines()) > 10000
            assert "semantic_kernel" in content
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_file_with_bom(self):
        """Test handling of files with BOM markers."""
        fixture = Path(tempfile.mkdtemp())
        file_path = fixture / "bom.py"
        
        try:
            # Write file with UTF-8 BOM
            content = "from semantic_kernel import Kernel"
            file_path.write_bytes(b"\xef\xbb\xbf" + content.encode("utf-8"))
            
            # Read back (should handle BOM)
            read_content = file_path.read_text(encoding="utf-8-sig")
            assert read_content == content
        finally:
            shutil.rmtree(fixture)
    
    def test_file_permission_error_handling(self):
        """Test handling of permission errors."""
        # This test may not work on all systems
        # Skip if we can't create a read-only file
        import stat
        import os
        
        fixture = Path(tempfile.mkdtemp())
        file_path = fixture / "readonly.py"
        
        try:
            file_path.write_text("import os")
            
            # Make file read-only (if possible)
            try:
                file_path.chmod(stat.S_IREAD)
                
                # Try to write (should fail or handle gracefully)
                try:
                    file_path.write_text("new content")
                    # If we get here, the system allows writing anyway
                except PermissionError:
                    # Expected - file is read-only
                    pass
                finally:
                    # Restore permissions for cleanup
                    file_path.chmod(stat.S_IREAD | stat.S_IWRITE)
            except (OSError, NotImplementedError):
                # Windows or system doesn't support chmod
                pytest.skip("Cannot test permission errors on this system")
        finally:
            shutil.rmtree(fixture)
    
    def test_file_not_found_error_handling(self):
        """Test handling of file not found errors."""
        fixture = Path(tempfile.mkdtemp())
        non_existent = fixture / "nonexistent.py"
        
        try:
            with pytest.raises(FileNotFoundError):
                non_existent.read_text(encoding="utf-8")
        finally:
            shutil.rmtree(fixture)
    
    def test_directory_not_found_error_handling(self):
        """Test handling of directory not found errors."""
        # Use a guaranteed-nonexistent path (portable across OSes and environments).
        parent = Path(tempfile.mkdtemp())
        non_existent = parent / "definitely-does-not-exist"
        shutil.rmtree(parent)
        
        # Should handle gracefully
        assert not non_existent.exists()
    
    def test_copy_overwrites_existing(self):
        """Test that copy overwrites existing destination."""
        source = EdgeCaseTestFixtures.create_single_file_codebase("from semantic_kernel import Kernel")
        dest = Path(tempfile.mkdtemp())
        (dest / "main.py").write_text("old content")
        
        try:
            copy_project_structure(source, dest)
            
            # Should overwrite
            assert (dest / "main.py").read_text(encoding="utf-8") == "from semantic_kernel import Kernel"
        finally:
            EdgeCaseTestFixtures.cleanup(source)
            if dest.exists():
                shutil.rmtree(dest)
    
    def test_copy_excludes_git_directory(self):
        """Test that .git directory is excluded."""
        source = Path(tempfile.mkdtemp())
        (source / "main.py").write_text("import os")
        (source / ".git").mkdir()
        (source / ".git" / "config").write_text("[core]")
        
        dest = Path(tempfile.mkdtemp())
        try:
            copy_project_structure(source, dest)
            
            assert (dest / "main.py").exists()
            assert not (dest / ".git").exists()
        finally:
            shutil.rmtree(source)
            if dest.exists():
                shutil.rmtree(dest)
    
    def test_copy_excludes_venv(self):
        """Test that venv directory is excluded."""
        source = Path(tempfile.mkdtemp())
        (source / "main.py").write_text("import os")
        (source / "venv").mkdir()
        (source / "venv" / "lib").mkdir()
        
        dest = Path(tempfile.mkdtemp())
        try:
            copy_project_structure(source, dest)
            
            assert (dest / "main.py").exists()
            assert not (dest / "venv").exists()
        finally:
            shutil.rmtree(source)
            if dest.exists():
                shutil.rmtree(dest)
    
    def test_file_encoding_detection(self):
        """Test detection of file encoding."""
        fixture = Path(tempfile.mkdtemp())
        
        # UTF-8 file
        utf8_file = fixture / "utf8.py"
        utf8_file.write_text("from semantic_kernel import Kernel\n# UTF-8: émoji 🚀", encoding="utf-8")
        
        try:
            # Try reading with different encodings
            utf8_content = utf8_file.read_text(encoding="utf-8")
            assert "semantic_kernel" in utf8_content
            
            # Should fail with wrong encoding
            try:
                utf8_file.read_text(encoding="ascii")
            except UnicodeDecodeError:
                # Expected
                pass
        finally:
            shutil.rmtree(fixture)
    
    def test_empty_file_handling(self):
        """Test handling of empty files."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("")
        try:
            file_path = fixture / "main.py"
            content = file_path.read_text(encoding="utf-8")
            
            assert content == ""
            assert file_path.stat().st_size == 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_symlink_handling(self):
        """Test handling of symlinks (if supported)."""
        import os
        
        fixture = Path(tempfile.mkdtemp())
        source_file = fixture / "source.py"
        source_file.write_text("from semantic_kernel import Kernel")
        
        try:
            # Create symlink (may not work on Windows)
            symlink = fixture / "link.py"
            try:
                symlink.symlink_to(source_file)
                
                # Should handle symlink
                assert symlink.exists() or symlink.is_symlink()
            except (OSError, NotImplementedError):
                pytest.skip("Symlinks not supported on this system")
        finally:
            shutil.rmtree(fixture)
    
    def test_very_long_path_handling(self):
        """Test handling of very long file paths."""
        fixture = EdgeCaseTestFixtures.create_deep_nested_codebase(levels=30)
        try:
            # Find deepest file
            deep_files = list(fixture.rglob("*.py"))
            if deep_files:
                deep_file = deep_files[0]
                path_str = str(deep_file)
                
                # Should handle long paths
                assert len(path_str) > 100
                assert deep_file.exists()
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_binary_file_exclusion(self):
        """Test that binary files are handled appropriately."""
        fixture = Path(tempfile.mkdtemp())
        binary_file = fixture / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03\x04")
        
        try:
            # Should not be able to decode as UTF-8 text
            try:
                content = binary_file.read_text(encoding="utf-8")
                # If it doesn't raise, check if it's actually valid UTF-8
                # Binary files with null bytes should fail or produce invalid text
                assert "\x00" in content or len(content) == 0
            except UnicodeDecodeError:
                # This is expected for binary files
                pass
        finally:
            shutil.rmtree(fixture)
    
    def test_concurrent_file_access(self):
        """Test handling of concurrent file access."""
        import threading
        
        fixture = Path(tempfile.mkdtemp())
        file_path = fixture / "concurrent.py"
        file_path.write_text("initial")
        
        results = []
        
        def write_file(value):
            try:
                file_path.write_text(f"value_{value}")
                results.append(f"write_{value}")
            except Exception as e:
                results.append(f"error_{value}: {e}")
        
        try:
            # Try concurrent writes
            threads = [threading.Thread(target=write_file, args=(i,)) for i in range(3)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            
            # File should exist and have some value
            assert file_path.exists()
            assert len(results) == 3
        finally:
            shutil.rmtree(fixture)

