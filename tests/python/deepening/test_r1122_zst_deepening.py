"""Sprint 568 ZST analytics deepening tests - primes 1091, 1093."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1091_text():
    from zst.zst_analytics import zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268
    assert zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268(str(TEXT)) == 2352246


def test_mod1091_minimal():
    from zst.zst_analytics import zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268
    assert zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268(str(MINIMAL)) == 82945


def test_mod1091_random():
    from zst.zst_analytics import zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268
    assert zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268(str(RANDOM)) == 2553328


def test_mod1093_text():
    from zst.zst_analytics import zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270
    assert zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270(str(TEXT)) == 2380770


def test_mod1093_minimal():
    from zst.zst_analytics import zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270
    assert zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270(str(MINIMAL)) == 83967


def test_mod1093_random():
    from zst.zst_analytics import zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270
    assert zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270(str(RANDOM)) == 2583528


def test_mod1091_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268
    assert isinstance(zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268(str(TEXT)), int)


def test_mod1093_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270
    assert isinstance(zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270(str(TEXT)), int)


def test_mod1091_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268
    assert zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268(str(TEXT)) >= 0


def test_mod1093_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270
    assert zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270(str(TEXT)) >= 0


def test_mod1091_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268
    fn = zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1093_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270
    fn = zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1091_importable_from_package():
    from zst import zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268
    assert callable(zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268)


def test_mod1093_importable_from_package():
    from zst import zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270
    assert callable(zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270)
