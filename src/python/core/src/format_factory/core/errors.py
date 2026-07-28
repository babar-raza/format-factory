"""Common Format Factory errors.

visibility: generated
generated_by: codex
"""

from __future__ import annotations

from typing import Any


class FormatFactoryError(Exception):
    """Base class for public Format Factory failures."""

    code = "format_factory_error"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or type(self).code
        self.context = dict(context or {})

    def __str__(self) -> str:
        return self.message


class FormatParseError(FormatFactoryError):
    """Input cannot be decoded as the selected format/profile."""

    code = "parse_error"


class FormatValidationError(FormatFactoryError):
    """A value violates a format or profile obligation."""

    code = "validation_error"


class FormatWriteError(FormatFactoryError):
    """A document cannot be encoded without violating its profile."""

    code = "write_error"


class ResourceLimitError(FormatFactoryError):
    """Processing would exceed a configured resource limit."""

    code = "resource_limit_exceeded"
