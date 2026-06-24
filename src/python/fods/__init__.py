"""format-factory: FODS (OpenDocument Flat Spreadsheet) FOSS Python track.

Minimal FOSS implementation for .fods format support.
Acquisition Gates 1-7 PASSED.

FOSS track only — no commercial readiness implied.
"""
from .parser import *  # noqa: F401, F403
from .writer import *  # noqa: F401, F403
from .neutral_model import *  # noqa: F401, F403
from .spreadsheet_document import *  # noqa: F401, F403
from .spreadsheet_model_document import *  # noqa: F401, F403
from .models import *  # noqa: F401, F403
from .csv_exporter import *  # noqa: F401, F403
from .fods_to_tsv import *  # noqa: F401, F403
from .constants import *  # noqa: F401, F403
from .exceptions import *  # noqa: F401, F403

import sys as _sys
__all__ = [k for k in vars(_sys.modules[__name__]) if not k.startswith("_")]
del _sys

__version__ = "0.1.0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
