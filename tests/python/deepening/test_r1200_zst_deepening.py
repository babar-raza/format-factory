"""Sprint 646 ZST analytics deepening tests - primes 1481, 1483."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1481_text():
    from zst.zst_analytics import zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372
    assert zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372(str(TEXT)) == 3835494


def test_mod1481_minimal():
    from zst.zst_analytics import zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372
    assert zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372(str(MINIMAL)) == 136089


def test_mod1481_random():
    from zst.zst_analytics import zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372
    assert zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372(str(RANDOM)) == 4123728


def test_mod1483_text():
    from zst.zst_analytics import zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374
    assert zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374(str(TEXT)) == 3864018


def test_mod1483_minimal():
    from zst.zst_analytics import zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374
    assert zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374(str(MINIMAL)) == 137111


def test_mod1483_random():
    from zst.zst_analytics import zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374
    assert zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374(str(RANDOM)) == 4153928


def test_mod1481_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372
    assert isinstance(zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372(str(TEXT)), int)


def test_mod1483_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374
    assert isinstance(zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374(str(TEXT)), int)


def test_mod1481_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372
    assert zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372(str(TEXT)) >= 0


def test_mod1483_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374
    assert zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374(str(TEXT)) >= 0


def test_mod1481_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372
    fn = zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1483_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374
    fn = zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1481_importable_from_package():
    from zst import zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372
    assert callable(zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372)


def test_mod1483_importable_from_package():
    from zst import zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374
    assert callable(zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374)
