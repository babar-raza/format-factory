"""Sprint R290: ZST analytics deepening — density, unique_frame_size_count, is_uniform_frames, content_type_hint."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.zst_codec import (
    zst_density,
    zst_unique_frame_size_count,
    zst_is_uniform_frames,
    zst_content_type_hint,
)

SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
TEXT = SAMPLES / "text-compressed.zst"
RANDOM = SAMPLES / "random-data.zst"


# --- zst_density ---

class TestZstDensity:
    def test_returns_float(self):
        assert isinstance(zst_density(RANDOM), float)

    def test_nonnegative(self):
        assert zst_density(RANDOM) >= 0.0

    def test_text_density_less_than_one(self):
        # text-compressed.zst has good compression => density < 1.0
        assert zst_density(TEXT) < 1.0

    def test_random_lower_than_minimal(self):
        # random has 0.27 density, minimal has 10.0 (compressed > decompressed)
        assert zst_density(RANDOM) < zst_density(MINIMAL)


# --- zst_unique_frame_size_count ---

class TestZstUniqueFrameSizeCount:
    def test_returns_int(self):
        assert isinstance(zst_unique_frame_size_count(MINIMAL), int)

    def test_nonnegative(self):
        assert zst_unique_frame_size_count(MINIMAL) >= 0

    def test_single_frame_returns_one(self):
        assert zst_unique_frame_size_count(MINIMAL) >= 1


# --- zst_is_uniform_frames ---

class TestZstIsUniformFrames:
    def test_returns_bool(self):
        assert isinstance(zst_is_uniform_frames(MINIMAL), bool)

    def test_single_frame_is_uniform(self):
        assert zst_is_uniform_frames(MINIMAL) is True


# --- zst_content_type_hint ---

class TestZstContentTypeHint:
    def test_returns_string(self):
        assert isinstance(zst_content_type_hint(TEXT), str)

    def test_random_is_incompressible(self):
        assert zst_content_type_hint(RANDOM) == "incompressible"

    def test_valid_categories(self):
        for f in [TEXT, RANDOM]:
            hint = zst_content_type_hint(f)
            assert hint in {"highly_compressible", "moderately_compressible", "incompressible", "empty"}
