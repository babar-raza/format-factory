"""conftest.py -- pytest configuration for tests/python/.

Adds src/python/ to sys.path so that 'import fods' resolves to
src/python/fods/ (the product source) rather than any test directory.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SRC_PYTHON = str(REPO_ROOT / "src" / "python")

if _SRC_PYTHON not in sys.path:
    sys.path.insert(0, _SRC_PYTHON)
