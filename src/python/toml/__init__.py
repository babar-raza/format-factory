"""format-factory: TOML (Tom's Obvious, Minimal Language) FOSS Python track.

Minimal FOSS implementation for .toml format support.
Acquisition Gates 1-7 PASSED.

FOSS track only — no commercial readiness implied.
"""
from .toml_codec import *  # noqa: F401, F403
from .toml_analytics import *  # noqa: F401, F403
from .toml_table_analytics import *  # noqa: F401, F403
from .exceptions import *  # noqa: F401, F403
from .models import TomlDocument  # noqa: F401
from .toml_workflow import toml_installed_workflow  # noqa: F401
from .toml_key_iterator import toml_iter_keys  # noqa: F401
from .toml_table_iterator import toml_iter_tables  # noqa: F401
from .toml_writer import write_toml, write_toml_str  # noqa: F401

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
