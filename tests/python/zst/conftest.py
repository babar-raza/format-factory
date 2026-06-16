"""ZST test suite conftest — skip all ZST tests if python-zstandard is not installed."""
import pytest

zstandard = pytest.importorskip("zstandard", reason="python-zstandard not installed")
