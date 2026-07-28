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
from .ndjson_record_stats import *  # noqa: F401, F403
from .exceptions import *  # noqa: F401, F403

# NOTE: ndjson_field_analytics.py defines 10 names that collide with
# already-wired, already-tested functions of the same name in json_stream.py
# (re-exported via ndjson_codec.py) and/or ndjson_record_stats.py, but with an
# INCOMPATIBLE signature (raw source str/bytes/Path vs. an already-parsed
# record list). A blind `import *` would silently shadow the canonical,
# tested implementations -- exactly the defect class this fix exists to
# eliminate. Only the genuinely non-colliding names are imported here; the
# 10 colliding duplicates in ndjson_field_analytics.py remain dead code,
# tracked as a separate cleanup (see found-issue-register.yaml FI-025).
from .ndjson_field_analytics import (  # noqa: F401
    ndjson_first_record_keys,
    ndjson_first_record_field_count,
    ndjson_has_consistent_keys,
    ndjson_sorted_key_names,
    ndjson_all_key_names,
    ndjson_last_record_keys,
    ndjson_has_nested_records,
    ndjson_has_arrays,
)

# Import spec-level domain module (Compat facade)
from .Compat.ndjson_record import NdjsonRecord  # noqa: F401

# Import domain model
from .models import NdjsonDocument  # noqa: F401
from .ndjson_workflow import ndjson_installed_workflow  # noqa: F401
from .ndjson_record_iterator import ndjson_iter_records  # noqa: F401
from .ndjson_field_iterator import ndjson_iter_fields  # noqa: F401
from .ndjson_writer import write_ndjson, write_ndjson_str  # noqa: F401

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
