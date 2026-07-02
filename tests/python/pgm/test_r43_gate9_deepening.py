"""
R43 Lane 5C: PGM Gate 9 deepening tests.

Gate 9 = deep-dive capability verification.
- Structural invariants (width * height == pixel_count)
- Magic number must be P2 (ASCII PGM)
- Maxval range enforcement (1-65535)
- Multi-image gradient traversal
- Field completeness contract
- Invalid samples produce ok=False
"""
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
VALID = REPO_ROOT / "samples" / "by-format" / "pgm" / "valid"
INVALID = REPO_ROOT / "samples" / "by-format" / "pgm" / "invalid"

sys.path.insert(0, str(REPO_ROOT / "src" / "python"))
from pgm.pgm_parser import parse_pgm


class TestPgmGate9StructuralInvariants:
    """Gate 9: pixel_count == width * height for all valid samples."""

    def test_all_valid_pixel_count_matches(self):
        if not VALID.exists():
            pytest.skip("No valid PGM samples")
        failed = []
        for f in sorted(VALID.glob("*.pgm")):
            result = parse_pgm(str(f))
            if result.get("ok"):
                expected = result["width"] * result["height"]
                if result["pixel_count"] != expected:
                    failed.append(f"{f.name}: pixel_count={result['pixel_count']} != {expected}")
        assert not bool(failed), f"pixel_count invariant violated: {failed}"

    def test_all_valid_magic_is_p2(self):
        if not VALID.exists():
            pytest.skip("No valid PGM samples")
        for f in sorted(VALID.glob("*.pgm")):
            result = parse_pgm(str(f))
            if result.get("ok"):
                assert result["magic"] == "P2", f"{f.name}: magic={result['magic']!r} != P2"

    def test_all_valid_maxval_in_range(self):
        if not VALID.exists():
            pytest.skip("No valid PGM samples")
        for f in sorted(VALID.glob("*.pgm")):
            result = parse_pgm(str(f))
            if result.get("ok"):
                assert 1 <= result["maxval"] <= 65535, (
                    f"{f.name}: maxval={result['maxval']} out of range"
                )

    def test_all_valid_dimensions_positive(self):
        if not VALID.exists():
            pytest.skip("No valid PGM samples")
        for f in sorted(VALID.glob("*.pgm")):
            result = parse_pgm(str(f))
            if result.get("ok"):
                assert result["width"] > 0 and result["height"] > 0, (
                    f"{f.name}: non-positive dimension w={result['width']} h={result['height']}"
                )


class TestPgmGate9FieldCompleteness:
    """Gate 9: All required neutral model fields must be present."""

    REQUIRED_FIELDS = {"ok", "path", "width", "height", "maxval", "magic", "pixel_count"}

    def test_valid_sample_has_all_fields(self):
        if not VALID.exists():
            pytest.skip("No valid PGM samples")
        for f in sorted(VALID.glob("*.pgm")):
            result = parse_pgm(str(f))
            missing = self.REQUIRED_FIELDS - set(result.keys())
            assert not bool(missing), f"{f.name}: missing fields {missing}"
            break  # one sample sufficient for completeness

    def test_gradient_2x2_field_completeness(self):
        sample = VALID / "2x2-gradient.pgm"
        if not sample.exists():
            pytest.skip("2x2-gradient.pgm not found")
        result = parse_pgm(str(sample))
        missing = self.REQUIRED_FIELDS - set(result.keys())
        assert not bool(missing), f"Missing fields: {missing}"
        assert result["ok"] is True
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["pixel_count"] == 4


class TestPgmGate9InvalidSamples:
    """Gate 9: Invalid samples must return ok=False."""

    def test_invalid_samples_all_fail(self):
        if not INVALID.exists():
            pytest.skip("No invalid PGM samples")
        for f in sorted(INVALID.glob("*.pgm")):
            result = parse_pgm(str(f))
            assert result.get("ok") is False, (
                f"Invalid sample {f.name} should return ok=False, got: {result}"
            )
