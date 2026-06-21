"""Sprint 607 ZST analytics deepening tests - primes 1283, 1289."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"

def test_mod1283_text():
    from zst.zst_analytics import zst_compressed_mod_1283_times_10600_plus_decompressed_times_317_plus_file_size_times_320
    assert zst_compressed_mod_1283_times_10600_plus_decompressed_times_317_plus_file_size_times_320(str(TEXT)) == 3093870

def test_mod1283_minimal():
    from zst.zst_analytics import zst_compressed_mod_1283_times_10600_plus_decompressed_times_317_plus_file_size_times_320
    assert zst_compressed_mod_1283_times_10600_plus_decompressed_times_317_plus_file_size_times_320(str(MINIMAL)) == 109517

def test_mod1283_random():
    from zst.zst_analytics import zst_compressed_mod_1283_times_10600_plus_decompressed_times_317_plus_file_size_times_320
    assert zst_compressed_mod_1283_times_10600_plus_decompressed_times_317_plus_file_size_times_320(str(RANDOM)) == 3338528

def test_mod1289_text():
    from zst.zst_analytics import zst_compressed_mod_1289_times_10700_plus_decompressed_times_319_plus_file_size_times_322
    assert zst_compressed_mod_1289_times_10700_plus_decompressed_times_319_plus_file_size_times_322(str(TEXT)) == 3122394

def test_mod1289_minimal():
    from zst.zst_analytics import zst_compressed_mod_1289_times_10700_plus_decompressed_times_319_plus_file_size_times_322
    assert zst_compressed_mod_1289_times_10700_plus_decompressed_times_319_plus_file_size_times_322(str(MINIMAL)) == 110539

def test_mod1289_random():
    from zst.zst_analytics import zst_compressed_mod_1289_times_10700_plus_decompressed_times_319_plus_file_size_times_322
    assert zst_compressed_mod_1289_times_10700_plus_decompressed_times_319_plus_file_size_times_322(str(RANDOM)) == 3368728

def test_mod1283_positive():
    from zst.zst_analytics import zst_compressed_mod_1283_times_10600_plus_decompressed_times_317_plus_file_size_times_320
    assert zst_compressed_mod_1283_times_10600_plus_decompressed_times_317_plus_file_size_times_320(str(TEXT)) > 0

def test_mod1289_positive():
    from zst.zst_analytics import zst_compressed_mod_1289_times_10700_plus_decompressed_times_319_plus_file_size_times_322
    assert zst_compressed_mod_1289_times_10700_plus_decompressed_times_319_plus_file_size_times_322(str(TEXT)) > 0

def test_mod1283_neq_mod1289():
    from zst.zst_analytics import zst_compressed_mod_1283_times_10600_plus_decompressed_times_317_plus_file_size_times_320, zst_compressed_mod_1289_times_10700_plus_decompressed_times_319_plus_file_size_times_322
    assert zst_compressed_mod_1283_times_10600_plus_decompressed_times_317_plus_file_size_times_320(str(RANDOM)) != zst_compressed_mod_1289_times_10700_plus_decompressed_times_319_plus_file_size_times_322(str(RANDOM))

def test_mod1283_consistent():
    from zst.zst_analytics import zst_compressed_mod_1283_times_10600_plus_decompressed_times_317_plus_file_size_times_320
    assert zst_compressed_mod_1283_times_10600_plus_decompressed_times_317_plus_file_size_times_320(str(MINIMAL)) == zst_compressed_mod_1283_times_10600_plus_decompressed_times_317_plus_file_size_times_320(str(MINIMAL))
