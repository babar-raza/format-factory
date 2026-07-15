"""Format Factory xliff (XLIFF) FOSS Python codec."""

from __future__ import annotations

from xliff.xliff_codec import (
    get_file_count,
    get_unit_count,
    load_xliff,
    probe_xliff,
    roundtrip,
    write_xliff,
    xliff_installed_workflow,
)
from xliff.exceptions import XliffError, XliffParseError, XliffWriteError
from xliff.models import XliffDocument

__all__ = [
    "get_file_count",
    "get_unit_count",
    "load_xliff",
    "probe_xliff",
    "roundtrip",
    "write_xliff",
    "xliff_installed_workflow",
    "XliffDocument",
    "XliffError",
    "XliffParseError",
    "XliffWriteError",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False

probe = probe_xliff
load = load_xliff
write = write_xliff
