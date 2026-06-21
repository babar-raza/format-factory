"""Sprint 583 ZST analytics deepening tests - primes 1163, 1171."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"

def test_mod1163_text():
    from zst.zst_analytics import zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288
    assert zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288(str(TEXT)) == 2637486

def test_mod1163_minimal():
    from zst.zst_analytics import zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288
    assert zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288(str(MINIMAL)) == 93165

def test_mod1163_random():
    from zst.zst_analytics import zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288
    assert zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288(str(RANDOM)) == 2855328

def test_mod1171_text():
    from zst.zst_analytics import zst_compressed_mod_1171_times_9100_plus_decompressed_times_287_plus_file_size_times_290
    assert zst_compressed_mod_1171_times_9100_plus_decompressed_times_287_plus_file_size_times_290(str(TEXT)) == 2666010

def test_mod1171_minimal():
    from zst.zst_analytics import zst_compressed_mod_1171_times_9100_plus_decompressed_times_287_plus_file_size_times_290
    assert zst_compressed_mod_1171_times_9100_plus_decompressed_times_287_plus_file_size_times_290(str(MINIMAL)) == 94187

def test_mod1171_random():
    from zst.zst_analytics import zst_compressed_mod_1171_times_9100_plus_decompressed_times_287_plus_file_size_times_290
    assert zst_compressed_mod_1171_times_9100_plus_decompressed_times_287_plus_file_size_times_290(str(RANDOM)) == 2885528

def test_mod1163_positive():
    from zst.zst_analytics import zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288
    assert zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288(str(TEXT)) > 0

def test_mod1171_positive():
    from zst.zst_analytics import zst_compressed_mod_1171_times_9100_plus_decompressed_times_287_plus_file_size_times_290
    assert zst_compressed_mod_1171_times_9100_plus_decompressed_times_287_plus_file_size_times_290(str(TEXT)) > 0

def test_mod1163_neq_mod1171():
    from zst.zst_analytics import zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288, zst_compressed_mod_1171_times_9100_plus_decompressed_times_287_plus_file_size_times_290
    assert zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288(str(TEXT)) != zst_compressed_mod_1171_times_9100_plus_decompressed_times_287_plus_file_size_times_290(str(TEXT))

def test_mod1163_consistent():
    from zst.zst_analytics import zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288
    assert zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288(str(TEXT)) == zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288(str(TEXT))
