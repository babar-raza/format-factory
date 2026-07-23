"""SafeTensors model and input validation."""

from __future__ import annotations

from format_factory.core import Diagnostic, ResourceLimits, Severity, ValidationReport

from ..model import SafeTensorsDocument


def _model_diagnostics(document: SafeTensorsDocument) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    expected_start = 0
    ordered = sorted(document.tensors.values(), key=lambda item: item.data_offsets)
    for tensor in ordered:
        start, end = tensor.data_offsets
        if start != expected_start:
            diagnostics.append(
                Diagnostic(
                    "SAFETENSORS_OFFSET_COVERAGE",
                    f"tensor {tensor.name!r} starts at {start}, expected {expected_start}",
                )
            )
        try:
            expected_size = tensor.byte_length
        except ValueError as exc:
            diagnostics.append(Diagnostic("SAFETENSORS_SUBBYTE_ALIGNMENT", str(exc)))
        else:
            if end - start != expected_size:
                diagnostics.append(
                    Diagnostic(
                        "SAFETENSORS_TENSOR_SIZE",
                        f"tensor {tensor.name!r} spans {end - start} bytes, expected {expected_size}",
                    )
                )
        expected_start = end
    if expected_start != document.payload_size:
        diagnostics.append(
            Diagnostic(
                "SAFETENSORS_TRAILING_DATA",
                f"tensor offsets cover {expected_start} of {document.payload_size} payload bytes",
            )
        )
    if any(not isinstance(k, str) or not isinstance(v, str) for k, v in document.metadata.items()):
        diagnostics.append(
            Diagnostic("SAFETENSORS_METADATA_TYPE", "metadata keys and values must be strings")
        )
    return diagnostics


def validate(
    value: SafeTensorsDocument | bytes | bytearray | memoryview | str,
    *,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> ValidationReport:
    del profile
    if isinstance(value, SafeTensorsDocument):
        return ValidationReport(_model_diagnostics(value))
    try:
        from ..codec.reader import load

        with load(value, limits=limits) as document:
            return ValidationReport(_model_diagnostics(document))
    except Exception as exc:  # public validation reports instead of raising
        return ValidationReport(
            [Diagnostic("SAFETENSORS_INVALID", str(exc), Severity.ERROR)]
        )
