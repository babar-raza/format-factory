"""Sprint 658 ZST analytics deepening tests - primes 1531, 1543."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1531_text():
    from zst.zst_analytics import zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388
    assert zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388(str(TEXT)) == 4063686


def test_mod1531_minimal():
    from zst.zst_analytics import zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388
    assert zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388(str(MINIMAL)) == 144265


def test_mod1531_random():
    from zst.zst_analytics import zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388
    assert zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388(str(RANDOM)) == 4365328


def test_mod1543_text():
    from zst.zst_analytics import zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390
    assert zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390(str(TEXT)) == 4092210


def test_mod1543_minimal():
    from zst.zst_analytics import zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390
    assert zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390(str(MINIMAL)) == 145287


def test_mod1543_random():
    from zst.zst_analytics import zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390
    assert zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390(str(RANDOM)) == 4395528


def test_mod1531_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388
    assert isinstance(zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388(str(TEXT)), int)


def test_mod1543_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390
    assert isinstance(zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390(str(TEXT)), int)


def test_mod1531_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388
    assert zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388(str(TEXT)) >= 0


def test_mod1543_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390
    assert zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390(str(TEXT)) >= 0


def test_mod1531_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388
    fn = zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1543_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390
    fn = zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1531_importable_from_package():
    from zst import zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388
    assert callable(zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388)


def test_mod1543_importable_from_package():
    from zst import zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390
    assert callable(zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390)
