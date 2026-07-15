"""
NRRD analytics — statistics and metrics functions over parsed NRRD documents.

Each function operates on a freshly-loaded value obtained by calling
``nrrd.nrrd_codec.load_nrrd`` internally — callers pass a path/bytes source,
not a pre-built ``NrrdDocument`` model object. No I/O beyond the codec's own
``load_nrrd`` call; no mutation.

Generated via the /format-feature-expansion governed skill
(taskcard TC-PROLIB-NRRD-001, transcript
reports/skills-r1/skill-transcripts/format-feature-expansion-nrrd.json).
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

from nrrd.nrrd_codec import load_nrrd

spec_qname = "nrrd:header"
spec_fact_ref = "FACT-NRRD-002"

SourceType = Union[str, Path, bytes]


def nrrd_axis_sizes(source: SourceType) -> list[int]:
    """Return the header's ``sizes`` field parsed into a list of ints.

    The NRRD header field ``sizes`` is a space-separated list of per-axis
    lengths (one integer per dimension). Returns an empty list if the field
    is absent or empty.

    Spec: NRRD header sizes field, part of the key:value header block
    terminated by a blank line (FACT-NRRD-002).

    Args:
        source: Path, Path-like string, or raw bytes of an NRRD file.

    Returns:
        List of per-axis sizes in header order. Empty list if ``sizes`` is
        missing or blank.

    Raises:
        NrrdParseError: if the source cannot be parsed as NRRD.
    """
    model = load_nrrd(source)
    sizes_str = model.get("header", {}).get("sizes", "")
    if not sizes_str:
        return []
    return [int(s) for s in sizes_str.split()]


def nrrd_is_compressed(source: SourceType) -> bool:
    """Return True if the header's ``encoding`` field is not ``raw``.

    NRRD data payloads may use any of six encodings: raw, ascii, hex, gzip,
    bzip2, or zlib. This function reports whether a non-raw (i.e. gzip or any
    other compressed/alternate) encoding is declared.

    Spec: NRRD data encoding field — one of raw, ascii, hex, gzip, bzip2,
    zlib (FACT-NRRD-003).

    Args:
        source: Path, Path-like string, or raw bytes of an NRRD file.

    Returns:
        True if ``encoding`` is anything other than ``raw`` (defaults to
        ``raw`` — i.e. False — if the field is absent).

    Raises:
        NrrdParseError: if the source cannot be parsed as NRRD.
    """
    model = load_nrrd(source)
    encoding = model.get("header", {}).get("encoding", "raw")
    return encoding != "raw"


def nrrd_element_count(source: SourceType) -> int:
    """Return the total element count: the product of all axis sizes.

    Computed from the same ``sizes`` header field as :func:`nrrd_axis_sizes`.
    Returns 0 if the header has no ``sizes`` field.

    Spec: NRRD header sizes field (FACT-NRRD-002).

    Args:
        source: Path, Path-like string, or raw bytes of an NRRD file.

    Returns:
        Product of all per-axis sizes (total number of data elements).
        0 if ``sizes`` is missing or blank.

    Raises:
        NrrdParseError: if the source cannot be parsed as NRRD.
    """
    sizes = nrrd_axis_sizes(source)
    if not sizes:
        return 0
    count = 1
    for size in sizes:
        count *= size
    return count
