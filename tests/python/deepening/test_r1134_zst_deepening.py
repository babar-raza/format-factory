"""Sprint 580 ZST analytics deepening tests - primes 1151, 1153."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"

def test_mod1151_text():
    from zst.zst_analytics import zst_compressed_mod_1151_times_8800_plus_decompressed_times_281_plus_file_size_times_284
    assert zst_compressed_mod_1151_times_8800_plus_decompressed_times_281_plus_file_size_times_284(str(TEXT)) == 2580438

def test_mod1151_minimal():
    from zst.zst_analytics import zst_compressed_mod_1151_times_8800_plus_decompressed_times_281_plus_file_size_times_284
    assert zst_compressed_mod_1151_times_8800_plus_decompressed_times_281_plus_file_size_times_284(str(MINIMAL)) == 91121

def test_mod1151_random():
    from zst.zst_analytics import zst_compressed_mod_1151_times_8800_plus_decompressed_times_281_plus_file_size_times_284
    assert zst_compressed_mod_1151_times_8800_plus_decompressed_times_281_plus_file_size_times_284(str(RANDOM)) == 2794928

def test_mod1153_text():
    from zst.zst_analytics import zst_compressed_mod_1153_times_8900_plus_decompressed_times_283_plus_file_size_times_286
    assert zst_compressed_mod_1153_times_8900_plus_decompressed_times_283_plus_file_size_times_286(str(TEXT)) == 2608962

def test_mod1153_minimal():
    from zst.zst_analytics import zst_compressed_mod_1153_times_8900_plus_decompressed_times_283_plus_file_size_times_286
    assert zst_compressed_mod_1153_times_8900_plus_decompressed_times_283_plus_file_size_times_286(str(MINIMAL)) == 92143

def test_mod1153_random():
    from zst.zst_analytics import zst_compressed_mod_1153_times_8900_plus_decompressed_times_283_plus_file_size_times_286
    assert zst_compressed_mod_1153_times_8900_plus_decompressed_times_283_plus_file_size_times_286(str(RANDOM)) == 2825128

def test_mod1151_positive():
    from zst.zst_analytics import zst_compressed_mod_1151_times_8800_plus_decompressed_times_281_plus_file_size_times_284
    assert zst_compressed_mod_1151_times_8800_plus_decompressed_times_281_plus_file_size_times_284(str(TEXT)) > 0

def test_mod1153_positive():
    from zst.zst_analytics import zst_compressed_mod_1153_times_8900_plus_decompressed_times_283_plus_file_size_times_286
    assert zst_compressed_mod_1153_times_8900_plus_decompressed_times_283_plus_file_size_times_286(str(TEXT)) > 0

def test_mod1151_neq_mod1153():
    from zst.zst_analytics import zst_compressed_mod_1151_times_8800_plus_decompressed_times_281_plus_file_size_times_284, zst_compressed_mod_1153_times_8900_plus_decompressed_times_283_plus_file_size_times_286
    assert zst_compressed_mod_1151_times_8800_plus_decompressed_times_281_plus_file_size_times_284(str(TEXT)) != zst_compressed_mod_1153_times_8900_plus_decompressed_times_283_plus_file_size_times_286(str(TEXT))

def test_mod1151_consistent():
    from zst.zst_analytics import zst_compressed_mod_1151_times_8800_plus_decompressed_times_281_plus_file_size_times_284
    assert zst_compressed_mod_1151_times_8800_plus_decompressed_times_281_plus_file_size_times_284(str(TEXT)) == zst_compressed_mod_1151_times_8800_plus_decompressed_times_281_plus_file_size_times_284(str(TEXT))
