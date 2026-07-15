"""Format Factory safetensors FOSS Python codec."""

from __future__ import annotations

from safetensors.safetensors_codec import (
    get_tensor_count,
    get_tensor_names,
    load_safetensors,
    probe_safetensors,
    roundtrip,
    safetensors_installed_workflow,
    write_safetensors,
)
from safetensors.exceptions import (
    SafetensorsError,
    SafetensorsParseError,
    SafetensorsWriteError,
)
from safetensors.models import SafetensorsDocument

__all__ = [
    "get_tensor_count",
    "get_tensor_names",
    "load_safetensors",
    "probe_safetensors",
    "roundtrip",
    "safetensors_installed_workflow",
    "write_safetensors",
    "SafetensorsDocument",
    "SafetensorsError",
    "SafetensorsParseError",
    "SafetensorsWriteError",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False

probe = probe_safetensors
load = load_safetensors
write = write_safetensors
