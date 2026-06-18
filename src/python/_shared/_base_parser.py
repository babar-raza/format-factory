"""
Abstract base parser for all Format Factory format parsers.

Usage:
    from src.python._shared._base_parser import BaseParser

    class FodsParser(BaseParser):
        def parse(self, path):
            ...
        def parse_bytes(self, data):
            ...
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseParser(ABC):
    """Abstract base class for all format parsers."""

    @abstractmethod
    def parse(self, path: Path) -> Any:
        """Parse a file and return a domain model object."""

    @abstractmethod
    def parse_bytes(self, data: bytes) -> Any:
        """Parse raw bytes and return a domain model object."""
