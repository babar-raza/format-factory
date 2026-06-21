"""Sprint 586 ZST analytics deepening tests - primes 1181, 1187."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"

def test_mod1181_text():
    from zst.zst_analytics import zst_compressed_mod_1181_times_9200_plus_decompressed_times_289_plus_file_size_times_292
    assert zst_compressed_mod_1181_times_9200_plus_decompressed_times_289_plus_file_size_times_292(str(TEXT)) == 2694534

def test_mod1181_minimal():
    from zst.zst_analytics import zst_compressed_mod_1181_times_9200_plus_decompressed_times_289_plus_file_size_times_292
    assert zst_compressed_mod_1181_times_9200_plus_decompressed_times_289_plus_file_size_times_292(str(MINIMAL)) == 95209

def test_mod1181_random():
    from zst.zst_analytics import zst_compressed_mod_1181_times_9200_plus_decompressed_times_289_plus_file_size_times_292
    assert zst_compressed_mod_1181_times_9200_plus_decompressed_times_289_plus_file_size_times_292(str(RANDOM)) == 2915728

def test_mod1187_text():
    from zst.zst_analytics import zst_compressed_mod_1187_times_9300_plus_decompressed_times_291_plus_file_size_times_294
    assert zst_compressed_mod_1187_times_9300_plus_decompressed_times_291_plus_file_size_times_294(str(TEXT)) == 2723058

def test_mod1187_minimal():
    from zst.zst_analytics import zst_compressed_mod_1187_times_9300_plus_decompressed_times_291_plus_file_size_times_294
    assert zst_compressed_mod_1187_times_9300_plus_decompressed_times_291_plus_file_size_times_294(str(MINIMAL)) == 96231

def test_mod1187_random():
    from zst.zst_analytics import zst_compressed_mod_1187_times_9300_plus_decompressed_times_291_plus_file_size_times_294
    assert zst_compressed_mod_1187_times_9300_plus_decompressed_times_291_plus_file_size_times_294(str(RANDOM)) == 2945928

def test_mod1181_positive():
    from zst.zst_analytics import zst_compressed_mod_1181_times_9200_plus_decompressed_times_289_plus_file_size_times_292
    assert zst_compressed_mod_1181_times_9200_plus_decompressed_times_289_plus_file_size_times_292(str(TEXT)) > 0

def test_mod1187_positive():
    from zst.zst_analytics import zst_compressed_mod_1187_times_9300_plus_decompressed_times_291_plus_file_size_times_294
    assert zst_compressed_mod_1187_times_9300_plus_decompressed_times_291_plus_file_size_times_294(str(TEXT)) > 0

def test_mod1181_neq_mod1187():
    from zst.zst_analytics import zst_compressed_mod_1181_times_9200_plus_decompressed_times_289_plus_file_size_times_292, zst_compressed_mod_1187_times_9300_plus_decompressed_times_291_plus_file_size_times_294
    assert zst_compressed_mod_1181_times_9200_plus_decompressed_times_289_plus_file_size_times_292(str(TEXT)) != zst_compressed_mod_1187_times_9300_plus_decompressed_times_291_plus_file_size_times_294(str(TEXT))

def test_mod1181_consistent():
    from zst.zst_analytics import zst_compressed_mod_1181_times_9200_plus_decompressed_times_289_plus_file_size_times_292
    assert zst_compressed_mod_1181_times_9200_plus_decompressed_times_289_plus_file_size_times_292(str(MINIMAL)) == zst_compressed_mod_1181_times_9200_plus_decompressed_times_289_plus_file_size_times_292(str(MINIMAL))
