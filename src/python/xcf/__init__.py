"""
format-factory-xcf — XCF (GIMP Native Image Format) parser prototype.

Gate 4 prototype. FOSS track. No third-party dependencies.
Acquisition gates 1-3 passed. Implementation authorized: R28.
commercial_product_ready: false
"""

# Import all core parser functions and exception/model classes
from .xcf_parser import *  # noqa: F401, F403

# Import spec-level domain module (image document metrics)
# This import happens BEFORE __all__ computation so xcf_is_landscape
# and other spec-level functions are part of the public API.
from .image_document import *  # noqa: F401, F403

# Compute public API: all non-private names loaded so far
import sys as _sys
__all__ = [k for k in vars(_sys.modules[__name__]) if not k.startswith("_")]
del _sys

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
