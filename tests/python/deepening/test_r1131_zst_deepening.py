"""Sprint 577 ZST analytics deepening tests - primes 1123, 1129."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1123_text():
    from zst.zst_analytics import zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280
    assert zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280(str(TEXT)) == 2523390


def test_mod1123_minimal():
    from zst.zst_analytics import zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280
    assert zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280(str(MINIMAL)) == 89077


def test_mod1123_random():
    from zst.zst_analytics import zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280
    assert zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280(str(RANDOM)) == 2734528


def test_mod1129_text():
    from zst.zst_analytics import zst_compressed_mod_1129_times_8700_plus_decompressed_times_279_plus_file_size_times_282
    assert zst_compressed_mod_1129_times_8700_plus_decompressed_times_279_plus_file_size_times_282(str(TEXT)) == 2551914


def test_mod1129_minimal():
    from zst.zst_analytics import zst_compressed_mod_1129_times_8700_plus_decompressed_times_279_plus_file_size_times_282
    assert zst_compressed_mod_1129_times_8700_plus_decompressed_times_279_plus_file_size_times_282(str(MINIMAL)) == 90099


def test_mod1129_random():
    from zst.zst_analytics import zst_compressed_mod_1129_times_8700_plus_decompressed_times_279_plus_file_size_times_282
    assert zst_compressed_mod_1129_times_8700_plus_decompressed_times_279_plus_file_size_times_282(str(RANDOM)) == 2764728


def test_mod1123_text_positive():
    from zst.zst_analytics import zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280
    assert zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280(str(TEXT)) > 0


def test_mod1129_text_positive():
    from zst.zst_analytics import zst_compressed_mod_1129_times_8700_plus_decompressed_times_279_plus_file_size_times_282
    assert zst_compressed_mod_1129_times_8700_plus_decompressed_times_279_plus_file_size_times_282(str(TEXT)) > 0


def test_mod1123_neq_mod1129_text():
    from zst.zst_analytics import (
        zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280,
        zst_compressed_mod_1129_times_8700_plus_decompressed_times_279_plus_file_size_times_282,
    )
    assert zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280(str(TEXT)) != zst_compressed_mod_1129_times_8700_plus_decompressed_times_279_plus_file_size_times_282(str(TEXT))


def test_mod1123_consistent():
    from zst.zst_analytics import zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280
    assert zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280(str(TEXT)) == zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280(str(TEXT))
