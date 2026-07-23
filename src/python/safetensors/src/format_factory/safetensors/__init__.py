"""Production SafeTensors API."""

from .codec import dump, dumps, load, loads, probe, read_header, safe_open
from .errors import (
    SafeTensorsError,
    SafeTensorsParseError,
    SafeTensorsWriteError,
)
from .model import (
    DType,
    PayloadAccess,
    PayloadAccessMode,
    SafeTensorsDocument,
    SafeTensorsHeader,
    TensorDescriptor,
)
from .validation import validate

__all__ = [
    "DType",
    "PayloadAccess",
    "PayloadAccessMode",
    "SafeTensorsDocument",
    "SafeTensorsError",
    "SafeTensorsHeader",
    "SafeTensorsParseError",
    "SafeTensorsWriteError",
    "TensorDescriptor",
    "dump",
    "dumps",
    "load",
    "loads",
    "probe",
    "read_header",
    "safe_open",
    "validate",
]

__version__ = "0.2.0.dev0"
