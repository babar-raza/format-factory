"""
Abstract base codec for Format Factory formats that support encode + decode.

Usage:
    from src.python._shared._base_codec import BaseCodec

    class ZstCodec(BaseCodec):
        def encode(self, model, path):
            ...
        def decode(self, path):
            ...
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseCodec(ABC):
    """Abstract base class for formats that support encode + decode."""

    @abstractmethod
    def encode(self, model: Any, path: Path) -> None:
        """Encode a domain model to file."""

    @abstractmethod
    def decode(self, path: Path) -> Any:
        """Decode a file to domain model."""
