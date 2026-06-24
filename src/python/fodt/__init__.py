"""format-factory-fodt -- Python FOSS parser/writer for OpenDocument Flat Text (FODT).

Minimal FOSS implementation for .fodt format support.
ODF 1.3 flat XML format.
Acquisition Gates 1-9 PASSED.

FOSS track only — no commercial readiness implied.
"""
from .parser import *  # noqa: F401, F403
from .writer import *  # noqa: F401, F403
from .neutral_model import *  # noqa: F401, F403
from .fodt_neutral_ops import *  # noqa: F401, F403
from .fodt_document_edit import *  # noqa: F401, F403
from .fodt_document_query import *  # noqa: F401, F403
from .text_document import *  # noqa: F401, F403
from .models import *  # noqa: F401, F403
from .exceptions import *  # noqa: F401, F403
from .constants import *  # noqa: F401, F403

import sys as _sys
__all__ = [k for k in vars(_sys.modules[__name__]) if not k.startswith("_")]
del _sys

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
