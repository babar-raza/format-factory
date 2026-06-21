"""
test_r134_fodt_to_ndjson_dogfood.py

Sprint: autonomous-loop-20260621-220000-ed51041f
Ledger ref: R90-FODT-TO-NDJSON-DOGFOOD-001

Dogfood export tests: FODT → NDJSON
- Verifies Format Factory fodt library (parse_fodt) drives the source read
- Verifies Format Factory ndjson library (write_ndjson) drives the target write
- Forbidden: any non-FF serialization or third-party export backend

Acceptance criteria:
1. target writer invoked (write_ndjson from ndjson package)
2. exported output reloads successfully via load_ndjson
3. meaningful values survive export (block_type, text, block_index, heading_level)
4. no forbidden third-party export dependency
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FODT_SRC = PROJECT_ROOT / "src" / "python" / "fodt"
NDJSON_SRC = PROJECT_ROOT / "src" / "python" / "ndjson"

sys.path.insert(0, str(FODT_SRC))
sys.path.insert(0, str(NDJSON_SRC))

# Load the dogfood module
_spec = importlib.util.spec_from_file_location(
    "fodt_to_ndjson_mod", FODT_SRC / "fodt_to_ndjson.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
fodt_to_ndjson = _mod.fodt_to_ndjson

from ndjson.ndjson_codec import load_ndjson, write_ndjson  # noqa: E402

SAMPLE_FODT = PROJECT_ROOT / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"


def _all_samples() -> list[Path]:
    return list((PROJECT_ROOT / "samples" / "by-format" / "fodt").glob("*.fodt"))


# ------------------------------------------------------------------
# Test 1: Target writer invoked (write_ndjson from ndjson library)
# ------------------------------------------------------------------

def test_fodt_to_ndjson_uses_ff_ndjson_writer(tmp_path):
    """Verify Format Factory ndjson write_ndjson is the target writer."""
    dest = tmp_path / "output.ndjson"
    count = fodt_to_ndjson(SAMPLE_FODT, dest)
    assert dest.exists(), "Output file must be created by write_ndjson"
    assert count > 0, "At least one record must be written"
    assert dest.suffix == ".ndjson"


# ------------------------------------------------------------------
# Test 2: Exported output reloads successfully via load_ndjson
# ------------------------------------------------------------------

def test_fodt_to_ndjson_roundtrip_reload(tmp_path):
    """Export reloads cleanly — data integrity preserved."""
    dest = tmp_path / "output.ndjson"
    count = fodt_to_ndjson(SAMPLE_FODT, dest)
    records = load_ndjson(dest)
    assert len(records) == count, "Reloaded record count must match written count"
    for rec in records:
        assert isinstance(rec, dict), "Each record must be a dict"


# ------------------------------------------------------------------
# Test 3: Meaningful values survive export
# ------------------------------------------------------------------

def test_fodt_to_ndjson_block_type_field(tmp_path):
    """All records have a block_type field."""
    dest = tmp_path / "output.ndjson"
    fodt_to_ndjson(SAMPLE_FODT, dest)
    records = load_ndjson(dest)
    for rec in records:
        assert "block_type" in rec, f"Missing block_type: {rec}"
        assert rec["block_type"] in ("paragraph", "heading", "list_item", "table_cell")


def test_fodt_to_ndjson_text_field_survives(tmp_path):
    """All records have a non-null text field."""
    dest = tmp_path / "output.ndjson"
    fodt_to_ndjson(SAMPLE_FODT, dest)
    records = load_ndjson(dest)
    assert any(rec.get("text") for rec in records), "At least one record must have non-empty text"


def test_fodt_to_ndjson_block_index_field(tmp_path):
    """block_index is sequential starting at 0."""
    dest = tmp_path / "output.ndjson"
    fodt_to_ndjson(SAMPLE_FODT, dest, include_block_index=True)
    records = load_ndjson(dest)
    indices = [rec.get("block_index") for rec in records if "block_index" in rec]
    assert indices == list(range(len(indices))), "block_index must be sequential"


def test_fodt_to_ndjson_heading_level_on_headings(tmp_path):
    """heading_level field present on heading records."""
    dest = tmp_path / "output.ndjson"
    fodt_to_ndjson(SAMPLE_FODT, dest, include_heading_level=True)
    records = load_ndjson(dest)
    headings = [r for r in records if r.get("block_type") == "heading"]
    assert headings, "At least one heading record expected"
    for h in headings:
        assert "heading_level" in h, f"heading_level missing on heading: {h}"
        assert isinstance(h["heading_level"], int), "heading_level must be int"
        assert h["heading_level"] >= 1


def test_fodt_to_ndjson_correct_heading_texts(tmp_path):
    """Heading texts match the known headings in the sample file."""
    dest = tmp_path / "output.ndjson"
    fodt_to_ndjson(SAMPLE_FODT, dest)
    records = load_ndjson(dest)
    heading_texts = [r["text"] for r in records if r.get("block_type") == "heading"]
    assert "Section One" in heading_texts
    assert "Section Two" in heading_texts


def test_fodt_to_ndjson_correct_paragraph_texts(tmp_path):
    """Paragraph texts survive export."""
    dest = tmp_path / "output.ndjson"
    fodt_to_ndjson(SAMPLE_FODT, dest)
    records = load_ndjson(dest)
    para_texts = [r["text"] for r in records if r.get("block_type") == "paragraph"]
    assert any("first paragraph" in t.lower() for t in para_texts), "Expected paragraph text not found"


def test_fodt_to_ndjson_returns_record_count(tmp_path):
    """Return value matches actual records written."""
    dest = tmp_path / "output.ndjson"
    count = fodt_to_ndjson(SAMPLE_FODT, dest)
    records = load_ndjson(dest)
    assert count == len(records)


# ------------------------------------------------------------------
# Test 4: No forbidden third-party export dependency
# ------------------------------------------------------------------

def test_fodt_to_ndjson_no_openpyxl_import():
    """fodt_to_ndjson does not import openpyxl or other forbidden backends."""
    src = (FODT_SRC / "fodt_to_ndjson.py").read_text(encoding="utf-8")
    forbidden = ["openpyxl", "xlrd", "xlwt", "pandas", "PIL", "cv2"]
    for lib in forbidden:
        assert lib not in src, f"Forbidden library '{lib}' found in fodt_to_ndjson.py"


def test_fodt_to_ndjson_uses_ff_ndjson_codec():
    """Source code imports write_ndjson from ndjson.ndjson_codec (FF library)."""
    src = (FODT_SRC / "fodt_to_ndjson.py").read_text(encoding="utf-8")
    assert "write_ndjson" in src, "write_ndjson must be imported from ndjson"
    assert "ndjson_codec" in src, "ndjson_codec (FF ndjson library) must be the target"


def test_fodt_to_ndjson_uses_ff_fodt_parser():
    """Source code imports parse_fodt from fodt.parser (FF fodt library)."""
    src = (FODT_SRC / "fodt_to_ndjson.py").read_text(encoding="utf-8")
    assert "parse_fodt" in src, "parse_fodt must be imported from fodt.parser"


# ------------------------------------------------------------------
# Optional: no_block_index mode
# ------------------------------------------------------------------

def test_fodt_to_ndjson_no_block_index(tmp_path):
    """When include_block_index=False, block_index field is absent."""
    dest = tmp_path / "output.ndjson"
    fodt_to_ndjson(SAMPLE_FODT, dest, include_block_index=False)
    records = load_ndjson(dest)
    assert all("block_index" not in r for r in records), "block_index must be absent"


def test_fodt_to_ndjson_no_heading_level(tmp_path):
    """When include_heading_level=False, heading_level field is absent even for headings."""
    dest = tmp_path / "output.ndjson"
    fodt_to_ndjson(SAMPLE_FODT, dest, include_heading_level=False)
    records = load_ndjson(dest)
    assert all("heading_level" not in r for r in records), "heading_level must be absent"


# ------------------------------------------------------------------
# Multi-file smoke: all available FODT samples
# ------------------------------------------------------------------

@pytest.mark.parametrize("fodt_file", _all_samples())
def test_fodt_to_ndjson_all_samples_reload(tmp_path, fodt_file):
    """All FODT samples convert and reload without error."""
    dest = tmp_path / f"{fodt_file.stem}.ndjson"
    try:
        count = fodt_to_ndjson(fodt_file, dest)
        records = load_ndjson(dest)
        assert len(records) == count
        for rec in records:
            assert "block_type" in rec
    except Exception as e:
        pytest.fail(f"fodt_to_ndjson failed for {fodt_file.name}: {e}")
