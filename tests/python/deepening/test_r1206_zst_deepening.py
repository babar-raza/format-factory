"""Sprint 652 ZST analytics deepening tests - primes 1493, 1499."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1493_text():
    from zst.zst_analytics import zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380
    assert zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380(str(TEXT)) == 3949590


def test_mod1493_minimal():
    from zst.zst_analytics import zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380
    assert zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380(str(MINIMAL)) == 140177


def test_mod1493_random():
    from zst.zst_analytics import zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380
    assert zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380(str(RANDOM)) == 4244528


def test_mod1499_text():
    from zst.zst_analytics import zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382
    assert zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382(str(TEXT)) == 3978114


def test_mod1499_minimal():
    from zst.zst_analytics import zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382
    assert zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382(str(MINIMAL)) == 141199


def test_mod1499_random():
    from zst.zst_analytics import zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382
    assert zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382(str(RANDOM)) == 4274728


def test_mod1493_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380
    assert isinstance(zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380(str(TEXT)), int)


def test_mod1499_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382
    assert isinstance(zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382(str(TEXT)), int)


def test_mod1493_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380
    assert zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380(str(TEXT)) >= 0


def test_mod1499_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382
    assert zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382(str(TEXT)) >= 0


def test_mod1493_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380
    fn = zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1499_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382
    fn = zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1493_importable_from_package():
    from zst import zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380
    assert callable(zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380)


def test_mod1499_importable_from_package():
    from zst import zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382
    assert callable(zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382)
