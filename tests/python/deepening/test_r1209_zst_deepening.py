"""Sprint 655 ZST analytics deepening tests - primes 1511, 1523."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1511_text():
    from zst.zst_analytics import zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384
    assert zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384(str(TEXT)) == 4006638


def test_mod1511_minimal():
    from zst.zst_analytics import zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384
    assert zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384(str(MINIMAL)) == 142221


def test_mod1511_random():
    from zst.zst_analytics import zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384
    assert zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384(str(RANDOM)) == 4304928


def test_mod1523_text():
    from zst.zst_analytics import zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386
    assert zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386(str(TEXT)) == 4035162


def test_mod1523_minimal():
    from zst.zst_analytics import zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386
    assert zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386(str(MINIMAL)) == 143243


def test_mod1523_random():
    from zst.zst_analytics import zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386
    assert zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386(str(RANDOM)) == 4335128


def test_mod1511_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384
    assert isinstance(zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384(str(TEXT)), int)


def test_mod1523_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386
    assert isinstance(zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386(str(TEXT)), int)


def test_mod1511_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384
    assert zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384(str(TEXT)) >= 0


def test_mod1523_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386
    assert zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386(str(TEXT)) >= 0


def test_mod1511_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384
    fn = zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1523_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386
    fn = zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1511_importable_from_package():
    from zst import zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384
    assert callable(zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384)


def test_mod1523_importable_from_package():
    from zst import zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386
    assert callable(zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386)
