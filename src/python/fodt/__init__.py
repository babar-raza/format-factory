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
from .exporters import fodt_to_txt, fodt_to_markdown, fodt_to_html  # noqa: F401
from .exceptions import *  # noqa: F401, F403
from .constants import *  # noqa: F401, F403

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
