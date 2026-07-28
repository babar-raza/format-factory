"""conftest.py -- pytest configuration for tests/python/.

Adds src/python/ to sys.path so that 'import fods' resolves to
src/python/fods/ (the product source) rather than any test directory.
"""
import csv as _stdlib_csv  # pre-import stdlib csv BEFORE src/python/ shadows it
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SRC_PYTHON = str(REPO_ROOT / "src" / "python")

if _SRC_PYTHON not in sys.path:
    sys.path.insert(0, _SRC_PYTHON)

# Pin stdlib csv in sys.modules so src/python/ff_csv never shadows it.
# The Format Factory csv package (src/python/ff_csv/__init__.py) is a thin wrapper
# that does NOT provide csv.writer/csv.reader. Without this pin, fods/sylk/dif
# tests fail because their 'import csv' resolves to the shadow package.
# The FF csv package remains importable as 'src.python.ff_csv' or via direct path
# in its own test suite (tests/python/csv/).
sys.modules["csv"] = _stdlib_csv
