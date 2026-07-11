"""format-factory: PPM (Portable Pixmap) FOSS Python track.

Minimal FOSS implementation for .ppm format support.
Acquisition Gates 1-7 PASSED.

FOSS track only — no commercial readiness implied.
"""
from .ppm_parser import *  # noqa: F401, F403
from .ppm_stats import *  # noqa: F401, F403
from .color_image import *  # noqa: F401, F403
from .ppm_image_analytics import *  # noqa: F401, F403
from .ppm_to_pgm import *  # noqa: F401, F403
from .exceptions import *  # noqa: F401, F403
from .models import PpmDocument  # noqa: F401
from .ppm_workflow import ppm_installed_workflow  # noqa: F401
from .ppm_pixmap_iterator import ppm_iter_pixmaps  # noqa: F401

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
