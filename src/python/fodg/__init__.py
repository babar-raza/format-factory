"""
format-factory: FODG (Flat OpenDocument Graphics) FOSS Python track.

Minimal FOSS implementation for .fodg format support.
ODF 1.3 Part 3 specification — OASIS Royalty-Free Category 1.
Acquisition Gates 1-3 PASSED. Gates 4-7 delegated PASS (R20).

FOSS track only — no commercial readiness implied.
"""

# Import all core codec functions and exception/model classes
from .fodg_codec import *  # noqa: F401, F403

# Import spec-level domain module (drawing document metrics and predicates).
# This import is placed BEFORE _core_names capture so all domain functions
# are included in __all__ and part of the public API.
from .drawing_document import *  # noqa: F401, F403

# Compute public API: all non-private names loaded so far
import sys as _sys
__all__ = [k for k in vars(_sys.modules[__name__]) if not k.startswith("_")]
del _sys

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
