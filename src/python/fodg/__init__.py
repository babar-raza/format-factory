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
from .exceptions import *  # noqa: F401, F403
from .models import FodgDocument  # noqa: F401
from .fodg_workflow import fodg_installed_workflow  # noqa: F401
from .fodg_page_iterator import fodg_iter_pages  # noqa: F401
# Compute public API: all non-private names loaded so far
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
__capability_level__ = "alpha-foss-preview"
__commercial_ready__ = False
