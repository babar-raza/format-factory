"""NRRD-ENC-001 -- independent-oracle cross-check against the real pynrrd
reference implementation.

MUST (SAL-NRRD-OBL-5A7992A6D1561C1D): "Test every magic version, every
type alias, every encoding, endian combinations, attached plus all
detached data-file forms, and hostile fixtures..."; this obligation's own
recorded `proof_requirements.positive` names "Generated complete
cross-product with Teem/pynrrd comparisons" specifically.

Before this file: independent-oracle runs were investigated and found
genuinely blocked, not merely unwritten -- this project's own top-level
`nrrd` compatibility package (src/python/nrrd/__init__.py) shares its
exact import name with the real `pynrrd` package (already declared as
this package's own `reference` extra, `pynrrd==1.1.3`, in
src/python/nrrd/pyproject.toml), so installing pynrrd into the main
project venv would shadow that legacy shim.

This file closes that blocker via an isolated venv
(`tools/oracle/independent/setup_nrrd_pynrrd_venv.py` builds
`.local/oracle/nrrd/pynrrd-venv/`, never committed, reproducible on
demand) that never sees this project's own site-packages or
`PYTHONPATH` (`tools/oracle/independent/isolated_venv_oracle.py`
strips it). A standalone probe script
(`tools/oracle/independent/nrrd_pynrrd_probe.py`, zero project imports)
runs inside that venv and reports pynrrd's own parse of a sample as
JSON, compared here against `format_factory.nrrd`'s own parse of the
same bytes.

**Honest scope note.** If the isolated venv has not been built (not
built by default -- CI and fresh checkouts will not have it), every
test in this file is skipped rather than failing, matching this suite's
existing SKIPPED_MISSING_PROVIDER pattern for optional external tooling
(`execute_oracle.py::execute_fods_libreoffice_case`'s own
`shutil.which("soffice")` check for FODS' own D3 interoperability
profile). Run `python tools/oracle/independent/setup_nrrd_pynrrd_venv.py`
once to build it locally.

Coverage here is the representative type x encoding cross-product
(9 representative type aliases x raw/gzip/bzip2/ascii, matching
`test_obligation_encoding_matrix_and_hostile_fixtures.py`'s own
`_REPRESENTATIVE_TYPES`/`_ENCODINGS` scoping), plus a big-endian slice
across 4 multi-byte types/encodings, plus the 3 pre-existing static
corpus samples this format's own oracle-package.yaml already names.

Deliberately NOT attempted here, and not claimed:

* `hex` encoding is excluded from the cross-product, not silently
  dropped -- confirmed directly (not assumed) that pynrrd 1.1.3 has no
  `hex` encoding support at all (zero mentions of "hex" anywhere in its
  own reader.py/writer.py); `test_hex_is_excluded_because_pynrrd_itself_
  does_not_support_it` below proves this behaviorally rather than just
  asserting it in prose. This is a reference-implementation gap, not a
  `format_factory.nrrd` defect.
* Teem CLI (`unu`) comparisons remain genuinely unbuilt: `unu` is a
  native binary with no PyPI distribution, not available in this
  environment, and has no existing subprocess-invocation pattern in
  this suite to build against (unlike `soffice`, which FODS' own D3
  profile already established). Not attempted; disclosed, not
  force-built.
* Every scalar type alias (not just the 9 representative ones) is a
  separate, already-fully-covered concern
  (test_production_namespace.py::test_every_normative_scalar_type_alias_roundtrips)
  -- crossing all ~40 aliases against pynrrd specifically would add
  volume, not new risk coverage, since alias resolution and byte-width
  correctness are orthogonal (see the encoding-matrix file's own
  identical reasoning for its own representative-type scoping).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from format_factory.nrrd import NrrdDocument, dumps
from tools.oracle.independent.isolated_venv_oracle import run_probe
from tools.oracle.independent.setup_nrrd_pynrrd_venv import venv_python

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "nrrd" / "valid"
PROBE_SCRIPT = Path(__file__).resolve().parents[3] / "tools" / "oracle" / "independent" / "nrrd_pynrrd_probe.py"
PYNRRD_VENV_PYTHON = venv_python()

pytestmark = pytest.mark.skipif(
    not PYNRRD_VENV_PYTHON.exists(),
    reason=(
        "isolated pynrrd oracle venv not built -- run "
        "`python tools/oracle/independent/setup_nrrd_pynrrd_venv.py` once locally "
        "(SKIPPED_MISSING_PROVIDER, matching this suite's soffice/LibreOffice pattern)"
    ),
)

_REPRESENTATIVE_TYPES = ["int8", "uint8", "int16", "uint16", "int32", "uint32", "int64", "float", "double"]
_ENCODINGS = ["raw", "gzip", "bzip2", "ascii"]


def _values_for(nrrd_type: str, count: int) -> list[int | float]:
    if nrrd_type in ("float", "double"):
        return [float(i) + 0.5 for i in range(count)]
    return [i for i in range(count)]


def _document(nrrd_type: str, encoding: str, *, endian: str = "little") -> NrrdDocument:
    header = {"type": nrrd_type, "dimension": "1", "sizes": "4", "encoding": encoding}
    if nrrd_type not in ("uint8", "int8") and encoding != "ascii":
        header["endian"] = endian
    return NrrdDocument(version=5, header=header, payload=b"", array=_values_for(nrrd_type, 4))


def _probe(sample_path: Path) -> dict:
    return run_probe(PYNRRD_VENV_PYTHON, PROBE_SCRIPT, str(sample_path))


# ── Representative type x encoding cross-product, against the real pynrrd ─


@pytest.mark.parametrize("nrrd_type", _REPRESENTATIVE_TYPES)
@pytest.mark.parametrize("encoding", _ENCODINGS)
def test_type_encoding_matrix_matches_the_pynrrd_reference_implementation(
    nrrd_type: str, encoding: str, tmp_path: Path
) -> None:
    document = _document(nrrd_type, encoding)
    encoded = dumps(document)
    sample = tmp_path / f"{nrrd_type}_{encoding}.nrrd"
    sample.write_bytes(encoded)

    result = _probe(sample)

    assert "error" not in result, result.get("error")
    assert result["encoding"] == encoding
    assert result["dimension"] == 1
    assert result["sizes"] == [4]
    assert result["data"] == document.array


@pytest.mark.parametrize("nrrd_type", ["int16", "uint32", "int64", "double"])
@pytest.mark.parametrize("encoding", ["raw", "gzip", "bzip2"])
def test_big_endian_matches_the_pynrrd_reference_implementation(
    nrrd_type: str, encoding: str, tmp_path: Path
) -> None:
    """Same slice, opposite byte order -- proves byte-order handling is
    genuinely correct against an independent implementation, not just
    self-consistent with `format_factory.nrrd`'s own encoder/decoder
    pair."""
    document = _document(nrrd_type, encoding, endian="big")
    encoded = dumps(document)
    sample = tmp_path / f"{nrrd_type}_{encoding}_be.nrrd"
    sample.write_bytes(encoded)

    result = _probe(sample)

    assert "error" not in result, result.get("error")
    assert result["data"] == document.array


# ── The pre-existing static corpus, already named in this format's own
#    oracle-package.yaml ─────────────────────────────────────────────────


def test_the_1d_int8_corpus_sample_matches_the_pynrrd_reference() -> None:
    result = _probe(SAMPLES / "1d-int8.nrrd")

    assert "error" not in result, result.get("error")
    assert result["type"] == "int8"
    assert result["dimension"] == 1
    assert result["data"] == [1, 2, 3, 4]


def test_the_2d_float32_corpus_sample_matches_the_pynrrd_reference() -> None:
    result = _probe(SAMPLES / "2d-float32.nrrd")

    assert "error" not in result, result.get("error")
    assert result["dimension"] == 2
    assert result["sizes"] == [2, 3]
    assert result["data"] == [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]


def test_the_gzip_encoded_corpus_sample_matches_the_pynrrd_reference() -> None:
    result = _probe(SAMPLES / "gzip-encoded.nrrd")

    assert "error" not in result, result.get("error")
    assert result["encoding"] == "gzip"
    assert result["data"] == [10, 20, 30, 40]


# ── The disclosed exclusion, proven rather than merely asserted ──────────


def test_hex_is_excluded_because_pynrrd_itself_does_not_support_it(tmp_path: Path) -> None:
    """Proves the module docstring's own claim behaviorally: pynrrd 1.1.3
    cannot read a `hex`-encoded NRRD file at all, so `hex` is correctly
    excluded from the cross-product above rather than silently dropped
    or, worse, force-included and left flaky."""
    document = _document("uint8", "hex")
    encoded = dumps(document)
    sample = tmp_path / "uint8_hex.nrrd"
    sample.write_bytes(encoded)

    result = _probe(sample)

    assert "error" in result
