"""format-factory: ODT (OpenDocument Text) FOSS Python track.

Minimal FOSS implementation for .odt format support.
Acquisition Gates 1-7 PASSED.

FOSS track only — no commercial readiness implied.
"""
from .odt_parser import *  # noqa: F401, F403
from .text_document import *  # noqa: F401, F403
from .exceptions import *  # noqa: F401, F403
from .odt_writer import write_odt, odt_from_text, odt_from_model  # noqa: F401
from .models import OdtModelDocument  # noqa: F401
from .odt_workflow import odt_installed_workflow  # noqa: F401
from .odt_paragraph_iterator import odt_iter_paragraphs  # noqa: F401
from .odt_heading_iterator import odt_iter_headings  # noqa: F401

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
