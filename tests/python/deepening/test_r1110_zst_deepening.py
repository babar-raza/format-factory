"""Sprint 556 ZST analytics deepening tests - primes 1033, 1039."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1033_text():
    from zst.zst_analytics import zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252
    assert zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252(str(TEXT)) == 2124054


def test_mod1033_minimal():
    from zst.zst_analytics import zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252
    assert zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252(str(MINIMAL)) == 74769


def test_mod1033_random():
    from zst.zst_analytics import zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252
    assert zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252(str(RANDOM)) == 2311728


def test_mod1039_text():
    from zst.zst_analytics import zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254
    assert zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254(str(TEXT)) == 2152578


def test_mod1039_minimal():
    from zst.zst_analytics import zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254
    assert zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254(str(MINIMAL)) == 75791


def test_mod1039_random():
    from zst.zst_analytics import zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254
    assert zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254(str(RANDOM)) == 2341928


def test_mod1033_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252
    assert isinstance(zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252(str(TEXT)), int)


def test_mod1039_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254
    assert isinstance(zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254(str(TEXT)), int)


def test_mod1033_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252
    assert zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252(str(TEXT)) >= 0


def test_mod1039_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254
    assert zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254(str(TEXT)) >= 0


def test_mod1033_importable_from_package():
    from zst import zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252
    assert callable(zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252)


def test_mod1039_importable_from_package():
    from zst import zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254
    assert callable(zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254)


def test_mod1033_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252
    fn = zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1039_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254
    fn = zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3
