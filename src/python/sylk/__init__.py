"""format-factory: SYLK (Symbolic Link) FOSS Python track.

Minimal FOSS implementation for .sylk format support.
Acquisition Gates 1-7 PASSED.

FOSS track only — no commercial readiness implied.
"""
from .exceptions import *  # noqa: F401, F403
from .sylk_parser import *  # noqa: F401, F403
from .spreadsheet_document import *  # noqa: F401, F403

import sys as _sys
__all__ = [k for k in vars(_sys.modules[__name__]) if not k.startswith("_")]
del _sys

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
