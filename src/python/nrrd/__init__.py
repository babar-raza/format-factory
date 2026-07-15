"""Format Factory nrrd (Nearly Raw Raster Data) FOSS Python codec."""

from __future__ import annotations

from nrrd.nrrd_codec import (
    get_dimension,
    get_encoding,
    load_nrrd,
    nrrd_installed_workflow,
    probe_nrrd,
    roundtrip,
    write_nrrd,
)
from nrrd.exceptions import NrrdError, NrrdParseError, NrrdWriteError
from nrrd.models import NrrdDocument

__all__ = [
    "get_dimension",
    "get_encoding",
    "load_nrrd",
    "nrrd_installed_workflow",
    "probe_nrrd",
    "roundtrip",
    "write_nrrd",
    "NrrdDocument",
    "NrrdError",
    "NrrdParseError",
    "NrrdWriteError",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False

probe = probe_nrrd
load = load_nrrd
write = write_nrrd
