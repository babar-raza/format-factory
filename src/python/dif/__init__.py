"""
format-factory-dif — Python FOSS parser for DIF (Data Interchange Format).

Public API:
    parse_dif(file_path)        — returns result dict (never raises)
    parse_dif_strict(file_path) — raises DifError subclasses on failure
    probe_dif(file_path)        — returns header metadata without full parse
    get_capabilities()          — returns capability dict
    dif_to_csv(file_path)       — export DIF as CSV string (R84 Train N)

License: Apache-2.0
Package: format-factory-dif v0.1.0
Gate history: Gates 1-9 PASSED; Gate 10 R59
"""

from .dif_parser import (
    parse_dif,
    parse_dif_strict,
    probe_dif,
    get_capabilities,
    dif_to_csv,
    DifError,
    DifInvalidFormatError,
    DifSizeError,
    DifCell,
    DifDocument,
)

__version__ = "0.1.0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_dif",
    "parse_dif_strict",
    "probe_dif",
    "get_capabilities",
    "dif_to_csv",
    "DifError",
    "DifInvalidFormatError",
    "DifSizeError",
    "DifCell",
    "DifDocument",
]
