"""Sprint 559 ZST analytics deepening tests - primes 1049, 1051."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1049_text():
    from zst.zst_analytics import zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256
    assert zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256(str(TEXT)) == 2181102


def test_mod1049_minimal():
    from zst.zst_analytics import zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256
    assert zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256(str(MINIMAL)) == 76813


def test_mod1049_random():
    from zst.zst_analytics import zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256
    assert zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256(str(RANDOM)) == 2372128


def test_mod1051_text():
    from zst.zst_analytics import zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258
    assert zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258(str(TEXT)) == 2209626


def test_mod1051_minimal():
    from zst.zst_analytics import zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258
    assert zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258(str(MINIMAL)) == 77835


def test_mod1051_random():
    from zst.zst_analytics import zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258
    assert zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258(str(RANDOM)) == 2402328


def test_mod1049_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256
    assert isinstance(zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256(str(TEXT)), int)


def test_mod1051_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258
    assert isinstance(zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258(str(TEXT)), int)


def test_mod1049_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256
    assert zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256(str(TEXT)) >= 0


def test_mod1051_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258
    assert zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258(str(TEXT)) >= 0


def test_mod1049_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256
    fn = zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1051_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258
    fn = zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1049_importable_from_package():
    from zst import zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256
    assert callable(zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256)


def test_mod1051_importable_from_package():
    from zst import zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258
    assert callable(zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258)
