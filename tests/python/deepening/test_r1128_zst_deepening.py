"""Sprint 574 ZST analytics deepening tests - primes 1109, 1117."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1109_text():
    from zst.zst_analytics import zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276
    assert zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276(str(TEXT)) == 2466342


def test_mod1109_minimal():
    from zst.zst_analytics import zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276
    assert zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276(str(MINIMAL)) == 87033


def test_mod1109_random():
    from zst.zst_analytics import zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276
    assert zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276(str(RANDOM)) == 2674128


def test_mod1117_text():
    from zst.zst_analytics import zst_compressed_mod_1117_times_8500_plus_decompressed_times_275_plus_file_size_times_278
    assert zst_compressed_mod_1117_times_8500_plus_decompressed_times_275_plus_file_size_times_278(str(TEXT)) == 2494866


def test_mod1117_minimal():
    from zst.zst_analytics import zst_compressed_mod_1117_times_8500_plus_decompressed_times_275_plus_file_size_times_278
    assert zst_compressed_mod_1117_times_8500_plus_decompressed_times_275_plus_file_size_times_278(str(MINIMAL)) == 88055


def test_mod1117_random():
    from zst.zst_analytics import zst_compressed_mod_1117_times_8500_plus_decompressed_times_275_plus_file_size_times_278
    assert zst_compressed_mod_1117_times_8500_plus_decompressed_times_275_plus_file_size_times_278(str(RANDOM)) == 2704328


def test_mod1109_text_positive():
    from zst.zst_analytics import zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276
    assert zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276(str(TEXT)) > 0


def test_mod1117_text_positive():
    from zst.zst_analytics import zst_compressed_mod_1117_times_8500_plus_decompressed_times_275_plus_file_size_times_278
    assert zst_compressed_mod_1117_times_8500_plus_decompressed_times_275_plus_file_size_times_278(str(TEXT)) > 0


def test_mod1109_neq_mod1117_text():
    from zst.zst_analytics import (
        zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276,
        zst_compressed_mod_1117_times_8500_plus_decompressed_times_275_plus_file_size_times_278,
    )
    assert zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276(str(TEXT)) != zst_compressed_mod_1117_times_8500_plus_decompressed_times_275_plus_file_size_times_278(str(TEXT))


def test_mod1109_consistent():
    from zst.zst_analytics import zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276
    assert zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276(str(TEXT)) == zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276(str(TEXT))
