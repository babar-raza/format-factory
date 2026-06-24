"""format-factory: Gnumeric FOSS Python track.

Minimal FOSS implementation for .gnumeric format support.
Gzip-compressed XML, namespace http://www.gnumeric.org/v10.dtd.
Acquisition Gates 1-7 PASSED.

FOSS track only — no commercial readiness implied.
"""
from .gnumeric_codec import *  # noqa: F401, F403
from .gnumeric_workbook_stats import *  # noqa: F401, F403
from .workbook_document import *  # noqa: F401, F403
from .exceptions import *  # noqa: F401, F403

import sys as _sys
__all__ = [k for k in vars(_sys.modules[__name__]) if not k.startswith("_")]
del _sys

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
