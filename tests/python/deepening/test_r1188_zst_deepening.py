"""Sprint 634 ZST analytics deepening tests - primes 1429, 1433."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1429_text():
    from zst.zst_analytics import zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356
    assert zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356(str(TEXT)) == 3607302


def test_mod1429_minimal():
    from zst.zst_analytics import zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356
    assert zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356(str(MINIMAL)) == 127913


def test_mod1429_random():
    from zst.zst_analytics import zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356
    assert zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356(str(RANDOM)) == 3882128


def test_mod1429_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356
    assert isinstance(zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356(str(TEXT)), int)


def test_mod1429_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356
    assert zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356(str(TEXT)) >= 0


def test_mod1429_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356
    fn_ref = zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356
    results = {fn_ref(str(TEXT)), fn_ref(str(MINIMAL)), fn_ref(str(RANDOM))}
    assert len(results) == 3


def test_mod1429_importable_from_package():
    from zst import zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356
    assert callable(zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356)


def test_mod1433_text():
    from zst.zst_analytics import zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358
    assert zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358(str(TEXT)) == 3635826


def test_mod1433_minimal():
    from zst.zst_analytics import zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358
    assert zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358(str(MINIMAL)) == 128935


def test_mod1433_random():
    from zst.zst_analytics import zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358
    assert zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358(str(RANDOM)) == 3912328


def test_mod1433_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358
    assert isinstance(zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358(str(TEXT)), int)


def test_mod1433_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358
    assert zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358(str(TEXT)) >= 0


def test_mod1433_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358
    fn_ref = zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358
    results = {fn_ref(str(TEXT)), fn_ref(str(MINIMAL)), fn_ref(str(RANDOM))}
    assert len(results) == 3


def test_mod1433_importable_from_package():
    from zst import zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358
    assert callable(zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358)
