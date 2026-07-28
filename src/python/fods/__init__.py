"""format-factory: FODS (OpenDocument Flat Spreadsheet) FOSS Python track.

Primary API (class-based — use this):
    from fods import FodsDocument
    doc = FodsDocument.from_file("spreadsheet.fods")
    print(doc.sheet_count, doc.sheets[0].name)

Legacy dict API (still supported, but not the primary surface):
    from fods import parse_fods, write_fods
    model = parse_fods("spreadsheet.fods")

FOSS track only — no commercial readiness implied.
Acquisition Gates 1-7 PASSED.
"""
from .parser import *  # noqa: F401, F403
from .writer import *  # noqa: F401, F403
from .neutral_model import *  # noqa: F401, F403
# Analytics modules — canonical names (PCG-003/004 migration complete 2026-07-03)
from .fods_analytics import *  # noqa: F401, F403
from .fods_analytics_extended import *  # noqa: F401, F403
from .models import *  # noqa: F401, F403
from .csv_exporter import *  # noqa: F401, F403
from .fods_to_tsv import *  # noqa: F401, F403
from .fods_workflow import *  # noqa: F401, F403
from .fods_sheet_iterator import *  # noqa: F401, F403
from .fods_cell_iterator import *  # noqa: F401, F403
from .constants import *  # noqa: F401, F403
from .exceptions import *  # noqa: F401, F403
from .fods_file_analytics import *  # noqa: F401, F403

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
