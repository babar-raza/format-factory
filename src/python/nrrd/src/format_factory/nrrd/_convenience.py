"""Top-level convenience wrappers over the nrrd codec/model/convert layers.

Kept separate from `__init__.py` (a pure re-export surface, matching this
repo's own established package convention) so the public API's import
statements and `__all__` declaration stay readable independent of how many
convenience functions the package exposes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from format_factory.core import BinarySource

from .codec import dump, dumps, load, probe
from .codec.payload import decode_binary, encode_binary
from .errors import NrrdWriteError
from .model import NrrdDocument, PreservationReport
from .security import NRRD_DEFAULT_LIMITS


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
