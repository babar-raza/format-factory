"""Production SafeTensors API."""

from .codec import dump, dumps, load, loads, probe, safe_open
from .errors import (
    SafeTensorsError,
    SafeTensorsParseError,
    SafeTensorsWriteError,
)
from .model import DType, SafeTensorsDocument, TensorDescriptor
from .validation import validate

__all__ = [
    "DType",
    "SafeTensorsDocument",
    "SafeTensorsError",
    "SafeTensorsParseError",
    "SafeTensorsWriteError",
    "TensorDescriptor",
    "dump",
    "dumps",
    "load",
    "loads",
    "probe",
    "safe_open",
    "validate",
]

__version__ = "0.2.0.dev0"
