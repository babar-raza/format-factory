"""Sprint 625 ZST analytics deepening tests - primes 1373, 1381."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1373_text():
    from zst.zst_analytics import zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344
    assert zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344(str(TEXT)) == 3436158


def test_mod1373_minimal():
    from zst.zst_analytics import zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344
    assert zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344(str(MINIMAL)) == 121781


def test_mod1373_random():
    from zst.zst_analytics import zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344
    assert zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344(str(RANDOM)) == 3700928


def test_mod1381_text():
    from zst.zst_analytics import zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346
    assert zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346(str(TEXT)) == 3464682


def test_mod1381_minimal():
    from zst.zst_analytics import zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346
    assert zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346(str(MINIMAL)) == 122803


def test_mod1381_random():
    from zst.zst_analytics import zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346
    assert zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346(str(RANDOM)) == 3731128


def test_mod1373_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344
    assert isinstance(zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344(str(TEXT)), int)


def test_mod1381_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346
    assert isinstance(zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346(str(TEXT)), int)


def test_mod1373_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344
    assert zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344(str(TEXT)) >= 0


def test_mod1381_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346
    assert zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346(str(TEXT)) >= 0


def test_mod1373_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344
    fn = zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1381_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346
    fn = zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1373_importable_from_package():
    from zst import zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344
    assert callable(zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344)


def test_mod1381_importable_from_package():
    from zst import zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346
    assert callable(zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346)
