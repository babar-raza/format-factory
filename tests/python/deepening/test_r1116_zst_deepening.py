"""Sprint 562 ZST analytics deepening tests - primes 1061, 1063."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1061_text():
    from zst.zst_analytics import zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260
    assert zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260(str(TEXT)) == 2238150


def test_mod1061_minimal():
    from zst.zst_analytics import zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260
    assert zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260(str(MINIMAL)) == 78857


def test_mod1061_random():
    from zst.zst_analytics import zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260
    assert zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260(str(RANDOM)) == 2432528


def test_mod1063_text():
    from zst.zst_analytics import zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262
    assert zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262(str(TEXT)) == 2266674


def test_mod1063_minimal():
    from zst.zst_analytics import zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262
    assert zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262(str(MINIMAL)) == 79879


def test_mod1063_random():
    from zst.zst_analytics import zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262
    assert zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262(str(RANDOM)) == 2462728


def test_mod1061_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260
    assert isinstance(zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260(str(TEXT)), int)


def test_mod1063_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262
    assert isinstance(zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262(str(TEXT)), int)


def test_mod1061_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260
    assert zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260(str(TEXT)) >= 0


def test_mod1063_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262
    assert zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262(str(TEXT)) >= 0


def test_mod1061_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260
    fn = zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1063_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262
    fn = zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1061_importable_from_package():
    from zst import zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260
    assert callable(zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260)


def test_mod1063_importable_from_package():
    from zst import zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262
    assert callable(zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262)
