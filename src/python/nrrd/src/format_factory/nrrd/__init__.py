"""Production NRRD lifecycle API."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from format_factory.core import BinarySource

from .analytics import axis_sizes, element_count, is_compressed
from .codec import (
    NrrdHeader,
    NrrdLazyPayload,
    PayloadAccess,
    PayloadAccessMode,
    dump,
    dump_detached,
    dump_multifile,
    dump_multifile_printf,
    dumps,
    load,
    loads,
    open_lazy_payload,
    probe,
    read_header,
)
from .codec.payload import available_encodings, decode_binary, encode_binary
from .convert import (
    ConversionReport,
    EncodingConversionReport,
    OverflowPolicy,
    RoundingPolicy,
    convert_dtype,
    convert_encoding,
    convert_endian,
)
from .errors import NrrdError, NrrdParseError, NrrdWriteError
from .space import (
    SpaceTransform,
    build_space_transform,
    named_space_dimension,
    parse_space_directions,
    parse_space_origin,
)
from .model import (
    DOMAIN_KINDS,
    NrrdDocument,
    PreservationIssue,
    PreservationReport,
    reshape_nrrd_array,
)
from .security import NRRD_DEFAULT_LIMITS
from .validation import validate

__all__ = [
    "ConversionReport", "DOMAIN_KINDS", "EncodingConversionReport",
    "NRRD_DEFAULT_LIMITS", "NrrdDocument",
    "NrrdError", "NrrdHeader", "NrrdLazyPayload", "NrrdParseError",
    "NrrdWriteError", "OverflowPolicy", "PayloadAccess", "PayloadAccessMode",
    "PreservationIssue", "PreservationReport", "RoundingPolicy",
    "SpaceTransform",
    "available_encodings",
    "axis_sizes", "build_space_transform", "convert_dtype", "convert_encoding",
    "convert_endian",
    "decode_nrrd_data", "dump", "dump_detached", "dump_multifile", "dump_multifile_printf",
    "dumps", "element_count",
    "encode_nrrd_data",
    "get_array", "get_dimension", "get_encoding", "is_compressed", "load",
    "load_nrrd", "loads", "named_space_dimension", "nrrd_installed_workflow",
    "open_lazy_payload",
    "parse_space_directions", "parse_space_origin", "preservation_report",
    "probe", "probe_nrrd", "read_header", "reshape_nrrd_array", "roundtrip",
    "validate", "write_nrrd",
]

__version__ = "0.2.0.dev0"


def probe_nrrd(source: BinarySource) -> bool:
    return bool(probe(source))


def load_nrrd(source: BinarySource) -> dict[str, Any]:
    return load(source).to_dict()


def write_nrrd(
    model: NrrdDocument | Mapping[str, Any],
    dest: str | Path | None = None,
    data: bytes | None = None,
) -> bytes:
    if data is not None:
        raise NrrdWriteError(
            "the production API does not accept an untyped payload override; "
            "provide a document with matching array values"
        )
    result = dumps(model)
    if dest is not None:
        dump(model, dest)
    return result


def decode_nrrd_data(
    type_str: str,
    sizes: list[int],
    payload: bytes,
    endian: str | None = None,
) -> list[Any]:
    return decode_binary(
        type_str,
        sizes,
        payload,
        endian=endian,
        limits=NRRD_DEFAULT_LIMITS,
    )


def encode_nrrd_data(
    type_str: str,
    values: list[Any],
    endian: str | None = None,
    *,
    sizes: list[int] | None = None,
) -> bytes:
    return encode_binary(
        type_str,
        sizes or [len(values)],
        values,
        endian=endian,
        limits=NRRD_DEFAULT_LIMITS,
    )


def get_array(model: NrrdDocument | Mapping[str, Any]) -> Any:
    value = model if isinstance(model, NrrdDocument) else NrrdDocument.from_mapping(model)
    return value.to_array()


def get_dimension(model: NrrdDocument | Mapping[str, Any]) -> int:
    value = model if isinstance(model, NrrdDocument) else NrrdDocument.from_mapping(model)
    return value.dimension


def get_encoding(model: NrrdDocument | Mapping[str, Any]) -> str:
    value = model if isinstance(model, NrrdDocument) else NrrdDocument.from_mapping(model)
    return value.encoding


def preservation_report(model: NrrdDocument | Mapping[str, Any]) -> PreservationReport:
    """Describe whether ``model`` can be emitted in exact-preservation mode."""

    value = model if isinstance(model, NrrdDocument) else NrrdDocument.from_mapping(model)
    return value.preservation_report()


def roundtrip(source: BinarySource, destination: str | Path) -> dict[str, Any]:
    document = load(source)
    dump(document, destination)
    return load(destination).to_dict()


def nrrd_installed_workflow(source: BinarySource) -> dict[str, Any]:
    document = load(source)
    return {
        "format": "nrrd",
        "loaded": True,
        "version": document.version,
        "encoding": document.encoding,
        "dimension": document.dimension,
        "data_size": document.data_size,
    }
