"""Format Factory xliff (XLIFF) FOSS Python codec."""

from __future__ import annotations

from xliff.xliff_codec import (
    get_file_count,
    get_unit_count,
    iter_file_units,
    load_xliff,
    probe_xliff,
    roundtrip,
    write_xliff,
    xliff_installed_workflow,
)
from xliff.exceptions import XliffError, XliffParseError, XliffWriteError
from xliff.models import XliffDocument
from xliff.xliff_inline import (
    InlineElement,
    parse_inline_content,
    serialize_inline_content,
)
from xliff.xliff_analytics import (
    xliff_average_source_length,
    xliff_translated_segment_count,
    xliff_untranslated_segment_count,
)

__all__ = [
    "get_file_count",
    "get_unit_count",
    "iter_file_units",
    "load_xliff",
    "probe_xliff",
    "roundtrip",
    "write_xliff",
    "xliff_installed_workflow",
    "XliffDocument",
    "XliffError",
    "XliffParseError",
    "XliffWriteError",
    "InlineElement",
    "parse_inline_content",
    "serialize_inline_content",
    "xliff_average_source_length",
    "xliff_translated_segment_count",
    "xliff_untranslated_segment_count",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False

probe = probe_xliff
load = load_xliff
write = write_xliff
