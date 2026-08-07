"""UBL exception hierarchy."""

from format_factory.core import (
    FormatFactoryError,
    FormatParseError,
    FormatValidationError,
    FormatWriteError,
)


class UblError(FormatFactoryError):
    """Base exception for UBL operations."""


class UblParseError(FormatParseError, UblError):
    """The input is malformed, unsafe, or outside the UBL 2.3 profile."""


class UblWriteError(FormatWriteError, UblError):
    """The document cannot be serialized safely."""


class UblValidationError(FormatValidationError, UblError):
    """The document violates a supported UBL model invariant."""


class SchemaValidationUnavailable(UblError):
    """The optional `xmlschema` dependency is not installed.

    Install the ``schema`` extra (``pip install format-factory-ubl[schema]``)
    to enable XSD conformance checking against the bundled UBL 2.3 schema.
    """
