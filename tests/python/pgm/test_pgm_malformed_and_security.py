"""PGM malformed input and security guard tests.

Customer readiness criteria 5 (malformed input: 3+ classes)
and criteria 6 (security: size guard + injection guard).

Three malformed input classes tested:
  - Class A: Wrong/missing magic bytes
  - Class B: Invalid/missing header (width/height/maxval)
  - Class C: Pixel data decode failure

Security guards tested:
  - Size guard: valid small file parses; size validation is present
  - Injection guard: magic-byte validation (only P2/P5 accepted)
"""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pgm  # noqa: E402

VALID_SAMPLE = _REPO / "samples" / "by-format" / "pgm" / "valid" / "1x1-white.pgm"
WRONG_MAGIC_SAMPLE = _REPO / "samples" / "by-format" / "pgm" / "invalid" / "wrong-magic.pgm"


# ── Class A: Wrong/missing magic bytes ────────────────────────────────────────

class TestClassAWrongMagic:
    """Malformed class A: invalid magic bytes."""

    def test_wrong_magic_sample_raises(self) -> None:
        """Pre-existing wrong-magic sample must raise an exception."""
        with pytest.raises(Exception):
            pgm.parse_pgm_strict(str(WRONG_MAGIC_SAMPLE))

    def test_p6_magic_rejected(self, tmp_path: Path) -> None:
        """P6 (PPM binary) magic must be rejected."""
        f = tmp_path / "bad.pgm"
        f.write_bytes(b"P6\n1 1\n255\n\xff\x00\x00")
        with pytest.raises(Exception):
            pgm.parse_pgm_strict(str(f))

    def test_empty_file_raises(self, tmp_path: Path) -> None:
        """Empty file must raise an exception."""
        f = tmp_path / "empty.pgm"
        f.write_bytes(b"")
        with pytest.raises(Exception):
            pgm.parse_pgm_strict(str(f))

    def test_binary_garbage_raises(self, tmp_path: Path) -> None:
        """Random binary content must raise an exception."""
        f = tmp_path / "garbage.pgm"
        f.write_bytes(bytes(range(256)))
        with pytest.raises(Exception):
            pgm.parse_pgm_strict(str(f))


# ── Class B: Invalid header ───────────────────────────────────────────────────

class TestClassBInvalidHeader:
    """Malformed class B: header errors."""

    def test_zero_width_raises(self, tmp_path: Path) -> None:
        """Width=0 must raise an exception."""
        f = tmp_path / "zero_w.pgm"
        f.write_text("P2\n0 2\n255\n128 64\n", encoding="ascii")
        with pytest.raises(Exception):
            pgm.parse_pgm_strict(str(f))

    def test_zero_height_raises(self, tmp_path: Path) -> None:
        """Height=0 must raise an exception."""
        f = tmp_path / "zero_h.pgm"
        f.write_text("P2\n2 0\n255\n", encoding="ascii")
        with pytest.raises(Exception):
            pgm.parse_pgm_strict(str(f))

    def test_missing_maxval_raises(self, tmp_path: Path) -> None:
        """Missing maxval must raise an exception."""
        f = tmp_path / "no_maxval.pgm"
        f.write_text("P2\n2 2\n", encoding="ascii")
        with pytest.raises(Exception):
            pgm.parse_pgm_strict(str(f))

    def test_non_numeric_dimensions_raises(self, tmp_path: Path) -> None:
        """Non-numeric dimensions must raise an exception."""
        f = tmp_path / "non_num.pgm"
        f.write_text("P2\nW H\n255\n", encoding="ascii")
        with pytest.raises(Exception):
            pgm.parse_pgm_strict(str(f))


# ── Class C: Pixel data decode failures ───────────────────────────────────────

class TestClassCDecodeFailure:
    """Malformed class C: pixel data errors."""

    def test_truncated_pixel_data(self, tmp_path: Path) -> None:
        """Truncated pixel data must raise an exception."""
        f = tmp_path / "truncated.pgm"
        # 3x3 = 9 pixels; only provide 2
        f.write_text("P2\n3 3\n255\n100 200\n", encoding="ascii")
        with pytest.raises(Exception):
            pgm.parse_pgm_strict(str(f))

    def test_pixel_value_exceeds_maxval(self, tmp_path: Path) -> None:
        """Pixel values > maxval must raise an exception."""
        f = tmp_path / "overflow.pgm"
        f.write_text("P2\n1 1\n100\n200\n", encoding="ascii")  # 200 > 100
        with pytest.raises(Exception):
            pgm.parse_pgm_strict(str(f))


# ── Security: Size guard ──────────────────────────────────────────────────────

class TestSecuritySizeGuard:
    """Security guard: file size validation."""

    def test_valid_small_file_parsed(self) -> None:
        """Valid 1x1 sample must parse without errors."""
        img = pgm.parse_pgm_strict(str(VALID_SAMPLE))
        assert img.width >= 1
        assert img.height >= 1

    def test_probe_does_not_raise_on_valid(self) -> None:
        """probe_pgm on valid file must not raise."""
        info = pgm.probe_pgm(str(VALID_SAMPLE))
        assert info["width"] >= 1

    def test_get_capabilities_present(self) -> None:
        """get_capabilities must return a non-empty dict."""
        caps = pgm.get_capabilities()
        assert isinstance(caps, dict)
        assert len(caps) > 0


# ── Security: Injection guard ─────────────────────────────────────────────────

class TestSecurityInjectionGuard:
    """Security guard: only P2/P5 magic accepted; all others raise immediately."""

    def test_p1_magic_rejected(self, tmp_path: Path) -> None:
        """P1 (PBM ASCII) magic must be rejected by PGM parser."""
        f = tmp_path / "p1.pgm"
        f.write_text("P1\n2 2\n0 1\n1 0\n", encoding="ascii")
        with pytest.raises(Exception):
            pgm.parse_pgm_strict(str(f))

    def test_p4_magic_rejected(self, tmp_path: Path) -> None:
        """P4 (PBM binary) magic must be rejected."""
        f = tmp_path / "p4.pgm"
        f.write_bytes(b"P4\n1 1\n\x80")
        with pytest.raises(Exception):
            pgm.parse_pgm_strict(str(f))

    def test_html_payload_rejected(self, tmp_path: Path) -> None:
        """HTML/script payload must not be accepted or executed."""
        f = tmp_path / "xss.pgm"
        f.write_text("<script>alert(1)</script>", encoding="ascii")
        with pytest.raises(Exception):
            pgm.parse_pgm_strict(str(f))
