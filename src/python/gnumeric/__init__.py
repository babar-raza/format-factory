"""format-factory: Gnumeric FOSS Python track.

Minimal FOSS implementation for .gnumeric format support.
Gzip-compressed XML, namespace http://www.gnumeric.org/v10.dtd.
Acquisition Gates 1-7 PASSED.

FOSS track only — no commercial readiness implied.
"""
from .gnumeric_codec import *  # noqa: F401, F403
from .gnumeric_workbook_stats import *  # noqa: F401, F403
from .gnumeric_analytics import *  # noqa: F401, F403
from .gnumeric_sheet_analytics import *  # noqa: F401, F403
from .exceptions import *  # noqa: F401, F403
from .models import GnumericDocument  # noqa: F401
from .gnumeric_sheet_iterator import gnumeric_iter_sheets  # noqa: F401

import sys as _sys
import types as _types
_FF_API_EXCLUDE = frozenset({
    "Any", "ClassVar", "Dict", "FrozenSet", "List", "Optional", "Path",
    "Set", "Tuple", "Type", "Union", "dataclass", "field", "TYPE_CHECKING",
})
__all__ = [
    k for k in vars(_sys.modules[__name__])
    if not k.startswith("_")
    and k not in _FF_API_EXCLUDE
    and not isinstance(getattr(_sys.modules[__name__], k), _types.ModuleType)
]
del _sys, _types, _FF_API_EXCLUDE

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
