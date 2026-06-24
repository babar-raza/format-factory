"""format-factory: ABW (AbiWord) FOSS Python track.

Minimal FOSS implementation for .abw format support.
AWML 1.0 plain XML format.
Acquisition Gates 1-7 PASSED.

FOSS track only — no commercial readiness implied.
"""
from .abw_codec import *  # noqa: F401, F403
from .abw_word_stats import *  # noqa: F401, F403
from .word_document import *  # noqa: F401, F403
from .exceptions import *  # noqa: F401, F403

import sys as _sys
__all__ = [k for k in vars(_sys.modules[__name__]) if not k.startswith("_")]
del _sys

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
