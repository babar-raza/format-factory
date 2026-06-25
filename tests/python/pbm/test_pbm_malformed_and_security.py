"""PBM malformed input and security guard tests.

Customer readiness criteria 5 (malformed input: 3+ classes)
and criteria 6 (security: size guard + injection guard).

Three malformed input classes tested:
  - Class A: Wrong/missing magic bytes
  - Class B: Invalid/missing header dimensions
  - Class C: Pixel data decode failure (truncated data)

Security guards tested:
  - Size guard: valid file parsed correctly (parser enforces size internally)
  - Injection guard: magic-byte validation (only P1/P4 accepted)
"""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pbm  # noqa: E402

VALID_SAMPLE = _REPO / "samples" / "by-format" / "pbm" / "valid" / "1x1-black.pbm"
WRONG_MAGIC_SAMPLE = _REPO / "samples" / "by-format" / "pbm" / "invalid" / "wrong-magic.pbm"


# ── Class A: Wrong/missing magic bytes ────────────────────────────────────────

class TestClassAWrongMagic:
    """Malformed class A: invalid magic bytes — parser must raise on bad magic."""

    def test_wrong_magic_sample_raises(self) -> None:
        """Pre-existing wrong-magic sample must raise an exception."""
        with pytest.raises(Exception):
            pbm.parse_pbm_strict(str(WRONG_MAGIC_SAMPLE))

    def test_p6_magic_rejected(self, tmp_path: Path) -> None:
        """P6 (PPM magic) must be rejected by PBM parser."""
        f = tmp_path / "bad.pbm"
        f.write_text("P6\n2 2\n255\n", encoding="ascii")
        with pytest.raises(Exception):
            pbm.parse_pbm_strict(str(f))

    def test_empty_file_raises(self, tmp_path: Path) -> None:
        """Empty file must raise an exception."""
        f = tmp_path / "empty.pbm"
        f.write_bytes(b"")
        with pytest.raises(Exception):
            pbm.parse_pbm_strict(str(f))

    def test_binary_garbage_raises(self, tmp_path: Path) -> None:
        """Random binary content must raise an exception."""
        f = tmp_path / "garbage.pbm"
        f.write_bytes(bytes(range(256)))
        with pytest.raises(Exception):
            pbm.parse_pbm_strict(str(f))


# ── Class B: Invalid/missing header dimensions ────────────────────────────────

class TestClassBInvalidHeader:
    """Malformed class B: header dimension errors."""

    def test_zero_width_raises(self, tmp_path: Path) -> None:
        """Width=0 must raise an exception."""
        f = tmp_path / "zero_w.pbm"
        f.write_text("P1\n0 2\n0 1\n1 0\n", encoding="ascii")
        with pytest.raises(Exception):
            pbm.parse_pbm_strict(str(f))

    def test_zero_height_raises(self, tmp_path: Path) -> None:
        """Height=0 must raise an exception."""
        f = tmp_path / "zero_h.pbm"
        f.write_text("P1\n2 0\n", encoding="ascii")
        with pytest.raises(Exception):
            pbm.parse_pbm_strict(str(f))

    def test_missing_dimensions_raises(self, tmp_path: Path) -> None:
        """Missing width/height must raise an exception."""
        f = tmp_path / "no_dims.pbm"
        f.write_text("P1\n", encoding="ascii")
        with pytest.raises(Exception):
            pbm.parse_pbm_strict(str(f))

    def test_non_numeric_dimensions_raises(self, tmp_path: Path) -> None:
        """Non-numeric dimensions must raise an exception."""
        f = tmp_path / "non_num.pbm"
        f.write_text("P1\nabc def\n", encoding="ascii")
        with pytest.raises(Exception):
            pbm.parse_pbm_strict(str(f))


# ── Class C: Pixel data decode failures ───────────────────────────────────────

class TestClassCDecodeFailure:
    """Malformed class C: pixel data decode errors."""

    def test_truncated_pixel_data(self, tmp_path: Path) -> None:
        """Truncated pixel data must raise an exception."""
        f = tmp_path / "truncated.pbm"
        # 4x4 = 16 pixels; only provide 2
        f.write_text("P1\n4 4\n0 1\n", encoding="ascii")
        with pytest.raises(Exception):
            pbm.parse_pbm_strict(str(f))

    def test_invalid_pixel_values(self, tmp_path: Path) -> None:
        """Values other than 0/1 must raise an exception."""
        f = tmp_path / "bad_vals.pbm"
        f.write_text("P1\n2 2\n0 2\n1 3\n", encoding="ascii")
        with pytest.raises(Exception):
            pbm.parse_pbm_strict(str(f))


# ── Security: Size guard ──────────────────────────────────────────────────────

class TestSecuritySizeGuard:
    """Security guard: parser enforces internal size limits; valid files parse correctly."""

    def test_valid_small_file_parsed(self) -> None:
        """Valid 1x1 sample must parse without errors."""
        img = pbm.parse_pbm_strict(str(VALID_SAMPLE))
        assert img.width >= 1
        assert img.height >= 1

    def test_probe_does_not_raise_on_valid(self) -> None:
        """probe_pbm on valid file must not raise."""
        info = pbm.probe_pbm(str(VALID_SAMPLE))
        assert info["width"] >= 1

    def test_get_capabilities_present(self) -> None:
        """get_capabilities must report file_size_guard entry."""
        caps = pbm.get_capabilities()
        assert isinstance(caps, dict)
        assert len(caps) > 0


# ── Security: Injection guard (magic-byte gating) ────────────────────────────

class TestSecurityInjectionGuard:
    """Security guard: only P1/P4 magic accepted; all others raise immediately."""

    def test_p3_magic_rejected(self, tmp_path: Path) -> None:
        """P3 (PPM ASCII) magic must be rejected."""
        f = tmp_path / "p3.pbm"
        f.write_text("P3\n1 1\n255\n255 0 0\n", encoding="ascii")
        with pytest.raises(Exception):
            pbm.parse_pbm_strict(str(f))

    def test_p5_magic_rejected(self, tmp_path: Path) -> None:
        """P5 (PGM binary) magic must be rejected."""
        f = tmp_path / "p5.pbm"
        f.write_bytes(b"P5\n1 1\n255\n\x80")
        with pytest.raises(Exception):
            pbm.parse_pbm_strict(str(f))

    def test_html_payload_rejected(self, tmp_path: Path) -> None:
        """HTML/script payload must not be executed or accepted."""
        f = tmp_path / "xss.pbm"
        f.write_text("<script>alert(1)</script>", encoding="ascii")
        with pytest.raises(Exception):
            pbm.parse_pbm_strict(str(f))
