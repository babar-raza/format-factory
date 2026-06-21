"""Sprint 664 ZST analytics deepening tests - primes 1559, 1567."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1559_text():
    from zst.zst_analytics import zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396
    assert zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396(str(TEXT)) == 4177782


def test_mod1559_minimal():
    from zst.zst_analytics import zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396
    assert zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396(str(MINIMAL)) == 148353


def test_mod1559_random():
    from zst.zst_analytics import zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396
    assert zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396(str(RANDOM)) == 4486128


def test_mod1567_text():
    from zst.zst_analytics import zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398
    assert zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398(str(TEXT)) == 4206306


def test_mod1567_minimal():
    from zst.zst_analytics import zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398
    assert zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398(str(MINIMAL)) == 149375


def test_mod1567_random():
    from zst.zst_analytics import zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398
    assert zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398(str(RANDOM)) == 4516328


def test_mod1559_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396
    assert isinstance(zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396(str(TEXT)), int)


def test_mod1567_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398
    assert isinstance(zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398(str(TEXT)), int)


def test_mod1559_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396
    assert zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396(str(TEXT)) >= 0


def test_mod1567_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398
    assert zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398(str(TEXT)) >= 0


def test_mod1559_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396
    fn = zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1567_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398
    fn = zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1559_importable_from_package():
    from zst import zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396
    assert callable(zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396)


def test_mod1567_importable_from_package():
    from zst import zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398
    assert callable(zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398)
