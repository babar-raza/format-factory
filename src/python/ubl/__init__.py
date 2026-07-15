"""Format Factory ubl (OASIS UBL) FOSS Python codec."""

from __future__ import annotations

from ubl.ubl_codec import (
    get_line_count,
    load_ubl,
    probe_ubl,
    roundtrip,
    ubl_installed_workflow,
    write_ubl,
)
from ubl.ubl_analytics import (
    ubl_document_type_summary,
    ubl_supplier_name,
    ubl_total_line_count,
)
from ubl.exceptions import UblError, UblParseError, UblWriteError
from ubl.models import UblDocument

__all__ = [
    "get_line_count",
    "load_ubl",
    "probe_ubl",
    "roundtrip",
    "ubl_installed_workflow",
    "write_ubl",
    "ubl_document_type_summary",
    "ubl_supplier_name",
    "ubl_total_line_count",
    "UblDocument",
    "UblError",
    "UblParseError",
    "UblWriteError",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False

probe = probe_ubl
load = load_ubl
write = write_ubl
