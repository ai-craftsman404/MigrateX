"""
Pytest configuration and shared fixtures for comprehensive testing
"""

import pytest
import os
from pathlib import Path
import tempfile
import shutil
from typing import Generator

# Import acceptance criteria plugin
# Note: Using relative import for pytest_acceptance_plugin
pytest_plugins = ["pytest_mock", "pytest_acceptance_plugin"]

# Set non-interactive mode for all tests to avoid stdin prompts
os.environ['MIGRATEX_NON_INTERACTIVE'] = '1'


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Create temporary directory for test data."""
    temp_dir = Path(tempfile.mkdtemp(prefix="migratex_test_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def temp_codebase() -> Generator[Path, None, None]:
    """Create temporary codebase for testing."""
    temp_dir = Path(tempfile.mkdtemp(prefix="migratex_codebase_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def sample_sk_codebase(temp_codebase: Path) -> Path:
    """Create sample Semantic Kernel codebase."""
    (temp_codebase / "main.py").write_text("""
from semantic_kernel import Kernel
from semantic_kernel.plugins import Plugin

kernel = Kernel()
plugin = Plugin(name="test")
""")
    return temp_codebase


@pytest.fixture(scope="function")
def sample_autogen_codebase(temp_codebase: Path) -> Path:
    """Create sample AutoGen codebase."""
    (temp_codebase / "main.py").write_text("""
from autogen import ConversableAgent, GroupChat

agent = ConversableAgent(name="test")
group = GroupChat(agents=[agent])
""")
    return temp_codebase


@pytest.fixture(scope="function")
def sample_mixed_codebase(temp_codebase: Path) -> Path:
    """Create sample mixed SK/AutoGen codebase."""
    (temp_codebase / "sk_file.py").write_text("from semantic_kernel import Kernel")
    (temp_codebase / "autogen_file.py").write_text("from autogen import ConversableAgent")
    return temp_codebase


