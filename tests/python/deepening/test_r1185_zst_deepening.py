"""Sprint 631 ZST analytics deepening tests - primes 1423, 1427."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1423_text():
    from zst.zst_analytics import zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352
    assert zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352(str(TEXT)) == 3550254


def test_mod1423_minimal():
    from zst.zst_analytics import zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352
    assert zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352(str(MINIMAL)) == 125869


def test_mod1423_random():
    from zst.zst_analytics import zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352
    assert zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352(str(RANDOM)) == 3821728


def test_mod1423_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352
    assert isinstance(zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352(str(TEXT)), int)


def test_mod1423_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352
    assert zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352(str(TEXT)) >= 0


def test_mod1423_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352
    fn_ref = zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352
    results = {fn_ref(str(TEXT)), fn_ref(str(MINIMAL)), fn_ref(str(RANDOM))}
    assert len(results) == 3


def test_mod1423_importable_from_package():
    from zst import zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352
    assert callable(zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352)


def test_mod1427_text():
    from zst.zst_analytics import zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354
    assert zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354(str(TEXT)) == 3578778


def test_mod1427_minimal():
    from zst.zst_analytics import zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354
    assert zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354(str(MINIMAL)) == 126891


def test_mod1427_random():
    from zst.zst_analytics import zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354
    assert zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354(str(RANDOM)) == 3851928


def test_mod1427_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354
    assert isinstance(zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354(str(TEXT)), int)


def test_mod1427_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354
    assert zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354(str(TEXT)) >= 0


def test_mod1427_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354
    fn_ref = zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354
    results = {fn_ref(str(TEXT)), fn_ref(str(MINIMAL)), fn_ref(str(RANDOM))}
    assert len(results) == 3


def test_mod1427_importable_from_package():
    from zst import zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354
    assert callable(zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354)
