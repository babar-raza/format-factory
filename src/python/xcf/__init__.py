"""
format-factory-xcf — XCF (GIMP Native Image Format) parser prototype.

Gate 4 prototype. FOSS track. No third-party dependencies.
Acquisition gates 1-3 passed. Implementation authorized: R28.
commercial_product_ready: false
"""

# Import all core parser functions and exception/model classes
from .xcf_parser import *  # noqa: F401, F403

# Capture core API names before loading analytics (for __all__)
import sys as _sys
_core_names = [k for k in vars(_sys.modules[__name__]) if not k.startswith("_")]
del _sys

# Analytics functions available for backwards compatibility (not in core __all__)
try:
    from .xcf_analytics import *  # noqa: F401, F403
except ImportError:
    pass

__all__ = _core_names
del _core_names

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
