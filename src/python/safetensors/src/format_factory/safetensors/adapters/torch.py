from __future__ import annotations

import importlib
from typing import Any

from .numpy import to_numpy
from ..model import SafeTensorsDocument


def to_torch(document: SafeTensorsDocument, name: str, *, copy: bool = False) -> Any:
    torch: Any = importlib.import_module("torch")

    array = to_numpy(document, name, copy=copy)
    return torch.from_numpy(array)
