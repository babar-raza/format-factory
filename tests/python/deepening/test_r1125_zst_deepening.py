"""Sprint 571 ZST analytics deepening tests - primes 1097, 1103."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"

def test_mod1097_text():
    from zst.zst_analytics import zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272
    assert zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272(str(TEXT)) == 2409294

def test_mod1097_minimal():
    from zst.zst_analytics import zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272
    assert zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272(str(MINIMAL)) == 84989

def test_mod1097_random():
    from zst.zst_analytics import zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272
    assert zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272(str(RANDOM)) == 2613728

def test_mod1103_text():
    from zst.zst_analytics import zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274
    assert zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274(str(TEXT)) == 2437818

def test_mod1103_minimal():
    from zst.zst_analytics import zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274
    assert zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274(str(MINIMAL)) == 86011

def test_mod1103_random():
    from zst.zst_analytics import zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274
    assert zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274(str(RANDOM)) == 2643928

def test_mod1097_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272
    assert isinstance(zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272(str(TEXT)), int)

def test_mod1097_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272
    assert zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272(str(TEXT)) >= 0

def test_mod1097_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272
    f=zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272
    assert len({f(str(TEXT)),f(str(MINIMAL)),f(str(RANDOM))})==3

def test_mod1097_importable_from_package():
    from zst import zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272
    assert callable(zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272)

def test_mod1103_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274
    assert isinstance(zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274(str(TEXT)), int)

def test_mod1103_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274
    assert zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274(str(TEXT)) >= 0

def test_mod1103_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274
    f=zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274
    assert len({f(str(TEXT)),f(str(MINIMAL)),f(str(RANDOM))})==3

def test_mod1103_importable_from_package():
    from zst import zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274
    assert callable(zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274)
