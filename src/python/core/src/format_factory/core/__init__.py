"""Public API for :mod:`format_factory.core`.

visibility: generated
generated_by: codex
"""

from .diagnostics import Diagnostic, Severity, SourceLocation, ValidationReport
from .errors import (
    FormatFactoryError,
    FormatParseError,
    FormatValidationError,
    FormatWriteError,
    ResourceLimitError,
)
from .limits import DEFAULT_LIMITS, ResourceLimits
from .protocols import (
    BinaryDestination,
    BinarySource,
    ProbeResult,
    ReadableBinary,
    ReadableText,
    SeekableBinary,
    TextDestination,
    TextSource,
    WritableBinary,
    WritableText,
)

__all__ = [
    "DEFAULT_LIMITS",
    "BinaryDestination",
    "BinarySource",
    "Diagnostic",
    "FormatFactoryError",
    "FormatParseError",
    "FormatValidationError",
    "FormatWriteError",
    "ProbeResult",
    "ReadableBinary",
    "ReadableText",
    "ResourceLimitError",
    "ResourceLimits",
    "SeekableBinary",
    "Severity",
    "SourceLocation",
    "TextDestination",
    "TextSource",
    "ValidationReport",
    "WritableBinary",
    "WritableText",
]

__version__ = "0.1.0.dev0"
