"""XLIFF codecs."""

from .reader import SUPPORTED_VERSIONS, XLIFF_NAMESPACE, load, loads, probe
from .writer import dump, dumps

__all__ = [
    "SUPPORTED_VERSIONS",
    "XLIFF_NAMESPACE",
    "dump",
    "dumps",
    "load",
    "loads",
    "probe",
]
