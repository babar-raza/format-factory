"""format-factory: PGM (Portable Graymap) FOSS Python track.

Minimal FOSS implementation for .pgm format support.
Acquisition Gates 1-7 PASSED.

FOSS track only — no commercial readiness implied.
"""
from .pgm_parser import *  # noqa: F401, F403
from .grayscale_image import *  # noqa: F401, F403
from .pgm_to_ppm import *  # noqa: F401, F403
from .exceptions import *  # noqa: F401, F403
from .pgm_image_analytics import *  # noqa: F401, F403
from .models import PgmDocument  # noqa: F401
from .pgm_workflow import pgm_installed_workflow  # noqa: F401
from .pgm_graymap_iterator import pgm_iter_graymaps  # noqa: F401

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

__version__ = "0.1.0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
