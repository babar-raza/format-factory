"""
TOML format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class TomlError(FormatFactoryError):
    """Base exception for all toml format errors."""


class TomlParseError(TomlError):
    """Raised when a toml file cannot be parsed."""


class TomlWriteError(TomlError):
    """Raised when a toml file cannot be written."""


class TomlInputError(TomlError):
    """Raised when toml input is invalid or cannot be read."""
