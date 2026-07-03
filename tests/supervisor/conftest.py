"""conftest.py for tests/supervisor — canonical import path for supervisor modules."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_SUPERVISOR = _REPO / "tools" / "supervisor"

if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
