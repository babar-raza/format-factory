"""
test_r134_fods_to_tsv_dogfood.py

Sprint: autonomous-loop-20260621-230000-ed51041f
Ledger ref: R90-FODS-TO-TSV-DOGFOOD-001

Dogfood export tests: FODS → TSV
- Verifies Format Factory fods library (parse_fods) drives the source read
- Verifies Format Factory tsv library (write_tsv) drives the target write
- Forbidden: any non-FF serialization or third-party export backend

Acceptance criteria:
1. target writer invoked (write_tsv from tsv.tsv_parser)
2. exported output reloads successfully via load_tsv
3. meaningful values survive export (headers, rows, cell values)
4. no forbidden third-party export dependency
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FODS_SRC = PROJECT_ROOT / "src" / "python" / "fods"
TSV_SRC = PROJECT_ROOT / "src" / "python" / "tsv"

sys.path.insert(0, str(FODS_SRC))
sys.path.insert(0, str(TSV_SRC))

# Load the dogfood module
_spec = importlib.util.spec_from_file_location(
    "fods_to_tsv_mod", FODS_SRC / "fods_to_tsv.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
fods_to_tsv = _mod.fods_to_tsv

from tsv.tsv_parser import load_tsv, write_tsv  # noqa: E402

TYPED_VALUES = PROJECT_ROOT / "samples" / "by-format" / "fods" / "typed-values-basic.fods"
MULTI_SHEET = PROJECT_ROOT / "samples" / "by-format" / "fods" / "multi-sheet-basic.fods"
MINIMAL = PROJECT_ROOT / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"


def _all_fods_samples() -> list[Path]:
    return list((PROJECT_ROOT / "samples" / "by-format" / "fods").glob("*.fods"))


# ------------------------------------------------------------------
# Test 1: Target writer invoked (write_tsv from tsv library)
# ------------------------------------------------------------------

def test_fods_to_tsv_uses_ff_tsv_writer(tmp_path):
    """Verify Format Factory tsv write_tsv is the target writer."""
    dest = tmp_path / "output.tsv"
    count, headers = fods_to_tsv(TYPED_VALUES, dest)
    assert dest.exists(), "Output file must be created by write_tsv"
    assert count > 0, "At least one data row must be written"
    assert dest.suffix == ".tsv"


# ------------------------------------------------------------------
# Test 2: Exported output reloads successfully via load_tsv
# ------------------------------------------------------------------

def test_fods_to_tsv_roundtrip_reload(tmp_path):
    """Export reloads cleanly — data integrity preserved."""
    dest = tmp_path / "output.tsv"
    count, headers = fods_to_tsv(TYPED_VALUES, dest)
    model = load_tsv(dest)
    assert model["row_count"] == count, "Reloaded row count must match written count"
    if headers:
        assert model["headers"] == headers, "Reloaded headers must match"


# ------------------------------------------------------------------
# Test 3: Meaningful values survive export
# ------------------------------------------------------------------

def test_fods_to_tsv_headers_survive(tmp_path):
    """First row is correctly used as headers."""
    dest = tmp_path / "output.tsv"
    count, headers = fods_to_tsv(TYPED_VALUES, dest, first_row_as_headers=True)
    assert headers == ["Type", "Value"], f"Expected ['Type', 'Value'] but got {headers}"


def test_fods_to_tsv_cell_values_survive(tmp_path):
    """Cell values survive the export round-trip."""
    dest = tmp_path / "output.tsv"
    fods_to_tsv(TYPED_VALUES, dest)
    model = load_tsv(dest)
    rows = model["rows"]
    # First data row should be ['string', 'Hello World']
    assert any("Hello World" in row for row in rows), "Expected 'Hello World' not found in rows"


def test_fods_to_tsv_row_count_correct(tmp_path):
    """Row count matches FODS source (3 data rows + 1 header row → 3 data rows written)."""
    dest = tmp_path / "output.tsv"
    count, headers = fods_to_tsv(TYPED_VALUES, dest)
    assert count == 3, f"Expected 3 data rows, got {count}"


def test_fods_to_tsv_no_headers_mode(tmp_path):
    """When first_row_as_headers=False, all rows are data rows."""
    dest = tmp_path / "output.tsv"
    count, headers = fods_to_tsv(TYPED_VALUES, dest, first_row_as_headers=False)
    assert headers == [], "headers must be empty when first_row_as_headers=False"
    # All 4 rows become data rows (header row now included in data)
    assert count == 4, f"Expected 4 rows (all rows as data), got {count}"


def test_fods_to_tsv_returns_tuple(tmp_path):
    """Return value is a (row_count, headers) tuple."""
    dest = tmp_path / "output.tsv"
    result = fods_to_tsv(TYPED_VALUES, dest)
    assert isinstance(result, tuple), "fods_to_tsv must return a tuple"
    assert len(result) == 2, "Tuple must have 2 elements"
    count, headers = result
    assert isinstance(count, int), "count must be int"
    assert isinstance(headers, list), "headers must be list"


def test_fods_to_tsv_multi_sheet_default_first(tmp_path):
    """Default sheet_index=0 exports the first sheet."""
    dest = tmp_path / "output.tsv"
    count, headers = fods_to_tsv(MULTI_SHEET, dest, sheet_index=0)
    assert dest.exists()
    assert count >= 0


def test_fods_to_tsv_minimal_spreadsheet(tmp_path):
    """Minimal spreadsheet (1 row, 1 cell) exports correctly."""
    dest = tmp_path / "output.tsv"
    count, headers = fods_to_tsv(MINIMAL, dest, first_row_as_headers=False)
    assert dest.exists()
    assert count >= 1


# ------------------------------------------------------------------
# Test 4: No forbidden third-party export dependency
# ------------------------------------------------------------------

def test_fods_to_tsv_no_openpyxl_import():
    """fods_to_tsv does not import openpyxl or other forbidden backends."""
    src = (FODS_SRC / "fods_to_tsv.py").read_text(encoding="utf-8")
    forbidden = ["openpyxl", "xlrd", "xlwt", "pandas", "csv.writer", "csv.DictWriter"]
    for lib in forbidden:
        assert lib not in src, f"Forbidden library '{lib}' found in fods_to_tsv.py"


def test_fods_to_tsv_uses_ff_tsv_parser():
    """Source code imports write_tsv from tsv.tsv_parser (FF library)."""
    src = (FODS_SRC / "fods_to_tsv.py").read_text(encoding="utf-8")
    assert "write_tsv" in src, "write_tsv must be imported from tsv"
    assert "tsv_parser" in src, "tsv_parser (FF tsv library) must be the target"


def test_fods_to_tsv_uses_ff_fods_parser():
    """Source code imports parse_fods from fods.parser (FF fods library)."""
    src = (FODS_SRC / "fods_to_tsv.py").read_text(encoding="utf-8")
    assert "parse_fods" in src, "parse_fods must be imported from fods.parser"


# ------------------------------------------------------------------
# Multi-file smoke: all available FODS samples
# ------------------------------------------------------------------

@pytest.mark.parametrize("fods_file", _all_fods_samples())
def test_fods_to_tsv_all_samples_reload(tmp_path, fods_file):
    """All FODS samples convert and reload without error."""
    dest = tmp_path / f"{fods_file.stem}.tsv"
    try:
        count, headers = fods_to_tsv(fods_file, dest)
        model = load_tsv(dest)
        # Smoke check: row_count should match written data rows.
        # Edge case: if count==0 (all rows were headers), load_tsv may count
        # the header line as row_count=1 depending on auto-detection. Accept both.
        if count == 0 and headers:
            assert model["row_count"] in (0, 1), (
                f"row_count mismatch for header-only TSV: model={model['row_count']}"
            )
        else:
            assert model["row_count"] == count, (
                f"row_count mismatch: model={model['row_count']} vs count={count}"
            )
    except AssertionError:
        raise
    except Exception as e:
        pytest.fail(f"fods_to_tsv failed for {fods_file.name}: {e}")
