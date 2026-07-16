"""Exceptions for the ubl codec."""

try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception  # type: ignore[misc,assignment]


class UblError(FormatFactoryError):
    """Base exception for ubl operations."""


class UblParseError(UblError):
    """Raised when a UBL file cannot be parsed."""


class UblWriteError(UblError):
    """Raised when a UBL file cannot be written."""


class UblTaxInconsistencyWarning(UserWarning):
    """Raised (as a warning, not an exception) when a UBL document's tax or
    monetary total figures fail an internal arithmetic consistency check.

    TC-S6P4-PROD-003 (select-6 Phase 4, closes D3): ubl_codec transcribes
    tax/monetary values it parses -- it does not independently compute or
    validate them, and never has. This warning flags a document whose own
    numbers don't add up (TaxAmount != TaxableAmount x Percent/100, subtotal
    sum != total, or PayableAmount != TaxInclusiveAmount with no allowance
    data to explain the difference) so that transcribing a broken source
    document doesn't happen silently. Non-fatal by design: the codec's job
    is round-trip fidelity, not being the authority on whether a document is
    a valid e-invoice -- see ubl_codec.check_tax_consistency() and
    reports/spec-coverage/ubl-deferred.json for the explicitly out-of-scope
    schema/Peppol validation this is not a substitute for.
    """
