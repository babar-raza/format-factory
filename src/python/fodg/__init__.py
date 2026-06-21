"""
format-factory: FODG (Flat OpenDocument Graphics) FOSS Python track.

Minimal FOSS implementation for .fodg format support.
ODF 1.3 Part 3 specification — OASIS Royalty-Free Category 1.
Acquisition Gates 1-3 PASSED. Gates 4-7 delegated PASS (R20).

FOSS track only — no commercial readiness implied.
"""

# Import all core codec functions and exception/model classes
from .fodg_codec import *  # noqa: F401, F403

# Capture core API names before loading analytics (for __all__)
import sys as _sys
_core_names = [k for k in vars(_sys.modules[__name__]) if not k.startswith("_")]
del _sys

# Analytics functions available for backwards compatibility (not in core __all__)
try:
    from .fodg_analytics import *  # noqa: F401, F403
except ImportError:
    pass

__all__ = _core_names
del _core_names

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
