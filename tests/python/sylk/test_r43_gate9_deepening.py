"""
R43 Lane 5C: SYLK Gate 9 deepening tests.

Gate 9 = deep-dive capability verification.
- Structural invariants (cell_count > 0 for valid files)
- ID line starts with 'ID;'
- Rows and cols must be positive integers
- Field completeness contract
- Invalid samples produce ok=False
"""
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
VALID = REPO_ROOT / "samples" / "by-format" / "sylk" / "valid"
INVALID = REPO_ROOT / "samples" / "by-format" / "sylk" / "invalid"

sys.path.insert(0, str(REPO_ROOT / "src" / "python"))
from sylk.sylk_parser import parse_sylk


class TestSylkGate9StructuralInvariants:
    """Gate 9: Structural invariants for all valid SYLK samples."""

    def test_all_valid_cell_count_positive(self):
        if not VALID.exists():
            pytest.skip("No valid SYLK samples")
        for f in sorted(VALID.glob("*.slk")):
            result = parse_sylk(str(f))
            if result.get("ok"):
                assert result["cell_count"] >= 0, (
                    f"{f.name}: cell_count={result['cell_count']} should be non-negative"
                )

    def test_all_valid_id_line_starts_with_id(self):
        if not VALID.exists():
            pytest.skip("No valid SYLK samples")
        for f in sorted(VALID.glob("*.slk")):
            result = parse_sylk(str(f))
            if result.get("ok"):
                id_line = result.get("id_line", "")
                assert id_line.startswith("ID;"), (
                    f"{f.name}: id_line={id_line!r} should start with 'ID;'"
                )

    def test_all_valid_rows_cols_positive(self):
        if not VALID.exists():
            pytest.skip("No valid SYLK samples")
        for f in sorted(VALID.glob("*.slk")):
            result = parse_sylk(str(f))
            if result.get("ok"):
                assert result["rows"] >= 0 and result["cols"] >= 0, (
                    f"{f.name}: rows={result['rows']} cols={result['cols']} should be non-negative"
                )


class TestSylkGate9FieldCompleteness:
    """Gate 9: All required neutral model fields must be present."""

    REQUIRED_FIELDS = {"ok", "path", "rows", "cols", "cell_count", "id_line"}

    def test_minimal_2x2_field_completeness(self):
        sample = VALID / "minimal-2x2.slk"
        if not sample.exists():
            pytest.skip("minimal-2x2.slk not found")
        result = parse_sylk(str(sample))
        missing = self.REQUIRED_FIELDS - set(result.keys())
        assert not bool(missing), f"Missing fields: {missing}"
        assert result["ok"] is True
        assert result["rows"] == 2
        assert result["cols"] == 2
        assert result["cell_count"] == 4

    def test_all_valid_have_required_fields(self):
        if not VALID.exists():
            pytest.skip("No valid SYLK samples")
        for f in sorted(VALID.glob("*.slk")):
            result = parse_sylk(str(f))
            missing = self.REQUIRED_FIELDS - set(result.keys())
            assert not bool(missing), f"{f.name}: missing fields {missing}"


class TestSylkGate9InvalidSamples:
    """Gate 9: Invalid samples must return ok=False."""

    def test_invalid_samples_all_fail(self):
        if not INVALID.exists():
            pytest.skip("No invalid SYLK samples")
        for f in sorted(INVALID.glob("*.slk")):
            result = parse_sylk(str(f))
            assert result.get("ok") is False, (
                f"Invalid sample {f.name} should return ok=False, got: {result}"
            )
