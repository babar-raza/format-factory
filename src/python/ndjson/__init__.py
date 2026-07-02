"""
format-factory: NDJSON (Newline-Delimited JSON) FOSS Python track.

Minimal FOSS implementation for .ndjson / .jsonl format support.
Spec: https://ndjson.org/ — royalty-free, public domain format.
Uses stdlib json only — no external dependencies.
Acquisition Gates 1-4 initiated.

FOSS track only — no commercial readiness implied.
"""

# Import all core codec functions and exception classes
from .ndjson_codec import *  # noqa: F401, F403

# Import spec-level domain module (Compat facade)
from .Compat.ndjson_record import NdjsonRecord  # noqa: F401

# Import domain model
from .models import NdjsonDocument  # noqa: F401
from .ndjson_workflow import ndjson_installed_workflow  # noqa: F401
from .ndjson_record_iterator import ndjson_iter_records  # noqa: F401
from .ndjson_field_iterator import ndjson_iter_fields  # noqa: F401

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
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
