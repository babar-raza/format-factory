"""XLIFF codecs."""

from .preservation import LossReport, PreservationMode, canonicalize, check_preservation
from .reader import SUPPORTED_VERSIONS, XLIFF_NAMESPACE, load, loads, probe
from .writer import dump, dumps

__all__ = [
    "SUPPORTED_VERSIONS",
    "XLIFF_NAMESPACE",
    "LossReport",
    "PreservationMode",
    "canonicalize",
    "check_preservation",
    "dump",
    "dumps",
    "load",
    "loads",
    "probe",
]
