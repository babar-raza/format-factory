"""Oracle test package init.

Extends __path__ to include tools/oracle/ so that
``from oracle.oracle_test_adapter import ...`` works whether this package
is imported as ``oracle`` (pytest importlib mode) or via sys.path manipulation.
"""
from pathlib import Path as _Path
_REPO_ROOT = _Path(__file__).resolve().parents[2]
_TOOLS_ORACLE = str(_REPO_ROOT / "tools" / "oracle")
if _TOOLS_ORACLE not in __path__:
    __path__.append(_TOOLS_ORACLE)
