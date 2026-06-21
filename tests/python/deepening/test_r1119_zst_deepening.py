"""Sprint 565 ZST analytics deepening tests - primes 1069, 1087."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1069_text():
    from zst.zst_analytics import zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264
    assert zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264(str(TEXT)) == 2295198


def test_mod1069_minimal():
    from zst.zst_analytics import zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264
    assert zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264(str(MINIMAL)) == 80901


def test_mod1069_random():
    from zst.zst_analytics import zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264
    assert zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264(str(RANDOM)) == 2492928


def test_mod1087_text():
    from zst.zst_analytics import zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266
    assert zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266(str(TEXT)) == 2323722


def test_mod1087_minimal():
    from zst.zst_analytics import zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266
    assert zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266(str(MINIMAL)) == 81923


def test_mod1087_random():
    from zst.zst_analytics import zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266
    assert zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266(str(RANDOM)) == 2523128


def test_mod1069_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264
    assert isinstance(zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264(str(TEXT)), int)


def test_mod1087_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266
    assert isinstance(zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266(str(TEXT)), int)


def test_mod1069_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264
    assert zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264(str(TEXT)) >= 0


def test_mod1087_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266
    assert zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266(str(TEXT)) >= 0


def test_mod1069_importable_from_package():
    from zst import zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264
    assert callable(zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264)


def test_mod1087_importable_from_package():
    from zst import zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266
    assert callable(zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266)


def test_mod1069_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264
    fn = zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1087_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266
    fn = zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3
