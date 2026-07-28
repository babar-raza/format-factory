"""Production SafeTensors API."""

from .codec import (
    dump,
    dump_index,
    dumps,
    dumps_index,
    load,
    load_index,
    loads,
    loads_index,
    probe,
    read_header,
    safe_open,
)
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
    SafeTensorsShardIndex,
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
    "SafeTensorsShardIndex",
    "SafeTensorsWriteError",
    "TensorDescriptor",
    "dump",
    "dump_index",
    "dumps",
    "dumps_index",
    "load",
    "load_index",
    "loads",
    "loads_index",
    "probe",
    "read_header",
    "safe_open",
    "validate",
]

__version__ = "0.2.0.dev0"
