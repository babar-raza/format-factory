"""
R43 Lane 5C: PBM Gate 9 deepening tests.

Gate 9 = deep-dive capability verification.
- Structural invariants (width * height == pixel_count)
- Magic number must be P1 (ASCII PBM)
- Dimensions must be positive
- Field completeness contract
- Invalid samples produce ok=False
"""
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
VALID = REPO_ROOT / "samples" / "by-format" / "pbm" / "valid"
INVALID = REPO_ROOT / "samples" / "by-format" / "pbm" / "invalid"

sys.path.insert(0, str(REPO_ROOT / "src" / "python"))
from pbm.pbm_parser import parse_pbm


class TestPbmGate9StructuralInvariants:
    """Gate 9: pixel_count == width * height for all valid samples."""

    def test_all_valid_pixel_count_matches(self):
        if not VALID.exists():
            pytest.skip("No valid PBM samples")
        failed = []
        for f in sorted(VALID.glob("*.pbm")):
            result = parse_pbm(str(f))
            if result.get("ok"):
                expected = result["width"] * result["height"]
                if result["pixel_count"] != expected:
                    failed.append(f"{f.name}: pixel_count={result['pixel_count']} != {expected}")
        assert not failed, f"pixel_count invariant violated: {failed}"

    def test_all_valid_magic_is_p1(self):
        if not VALID.exists():
            pytest.skip("No valid PBM samples")
        for f in sorted(VALID.glob("*.pbm")):
            result = parse_pbm(str(f))
            if result.get("ok"):
                assert result["magic"] == "P1", f"{f.name}: magic={result['magic']!r} != P1"

    def test_all_valid_dimensions_positive(self):
        if not VALID.exists():
            pytest.skip("No valid PBM samples")
        for f in sorted(VALID.glob("*.pbm")):
            result = parse_pbm(str(f))
            if result.get("ok"):
                assert result["width"] > 0 and result["height"] > 0, (
                    f"{f.name}: non-positive dimension w={result['width']} h={result['height']}"
                )


class TestPbmGate9FieldCompleteness:
    """Gate 9: All required neutral model fields must be present."""

    REQUIRED_FIELDS = {"ok", "path", "width", "height", "magic", "pixel_count"}

    def test_1x1_black_field_completeness(self):
        sample = VALID / "1x1-black.pbm"
        if not sample.exists():
            pytest.skip("1x1-black.pbm not found")
        result = parse_pbm(str(sample))
        missing = self.REQUIRED_FIELDS - set(result.keys())
        assert not missing, f"Missing fields: {missing}"
        assert result["ok"] is True
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["pixel_count"] == 1
        assert result["magic"] == "P1"

    def test_all_valid_have_required_fields(self):
        if not VALID.exists():
            pytest.skip("No valid PBM samples")
        for f in sorted(VALID.glob("*.pbm")):
            result = parse_pbm(str(f))
            missing = self.REQUIRED_FIELDS - set(result.keys())
            assert not missing, f"{f.name}: missing fields {missing}"


class TestPbmGate9InvalidSamples:
    """Gate 9: Invalid samples must return ok=False."""

    def test_invalid_samples_all_fail(self):
        if not INVALID.exists():
            pytest.skip("No invalid PBM samples")
        for f in sorted(INVALID.glob("*.pbm")):
            result = parse_pbm(str(f))
            assert result.get("ok") is False, (
                f"Invalid sample {f.name} should return ok=False, got: {result}"
            )
