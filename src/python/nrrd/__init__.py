"""Format Factory nrrd (Nearly Raw Raster Data) FOSS Python codec."""

from __future__ import annotations

from nrrd.nrrd_codec import (
    decode_nrrd_data,
    get_array,
    get_dimension,
    get_encoding,
    load_nrrd,
    nrrd_installed_workflow,
    probe_nrrd,
    reshape_nrrd_array,
    roundtrip,
    write_nrrd,
)
from nrrd.exceptions import NrrdError, NrrdParseError, NrrdWriteError
from nrrd.models import NrrdDocument
from nrrd.nrrd_analytics import (
    nrrd_axis_sizes,
    nrrd_element_count,
    nrrd_is_compressed,
    nrrd_kinds,
    nrrd_to_array,
)

__all__ = [
    "decode_nrrd_data",
    "get_array",
    "get_dimension",
    "get_encoding",
    "load_nrrd",
    "nrrd_installed_workflow",
    "probe_nrrd",
    "reshape_nrrd_array",
    "roundtrip",
    "write_nrrd",
    "NrrdDocument",
    "NrrdError",
    "NrrdParseError",
    "NrrdWriteError",
    "nrrd_axis_sizes",
    "nrrd_element_count",
    "nrrd_is_compressed",
    "nrrd_kinds",
    "nrrd_to_array",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False

probe = probe_nrrd
load = load_nrrd
write = write_nrrd
