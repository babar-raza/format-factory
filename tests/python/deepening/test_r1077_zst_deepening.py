"""Tests for ZST analytics functions — sprint 523 (primes 829, 853)."""
import pytest
from pathlib import Path

SAMPLES = {
    "text": "samples/by-format/zst/valid/text-compressed.zst",
    "minimal": "samples/by-format/zst/valid/minimal-synthetic.zst",
    "random": "samples/by-format/zst/valid/random-data.zst",
}

# ---------------------------------------------------------------------------
# FN1: zst_compressed_mod_829_times_5000_plus_decompressed_times_203_plus_file_size_times_206
# ---------------------------------------------------------------------------

def test_fn1_text():
    from zst import zst_compressed_mod_829_times_5000_plus_decompressed_times_203_plus_file_size_times_206 as fn
    assert fn(SAMPLES["text"]) == 1495202

def test_fn1_minimal():
    from zst import zst_compressed_mod_829_times_5000_plus_decompressed_times_203_plus_file_size_times_206 as fn
    assert fn(SAMPLES["minimal"]) == 52263

def test_fn1_random():
    from zst import zst_compressed_mod_829_times_5000_plus_decompressed_times_203_plus_file_size_times_206 as fn
    assert fn(SAMPLES["random"]) == 1644728

def test_fn1_returns_int():
    from zst import zst_compressed_mod_829_times_5000_plus_decompressed_times_203_plus_file_size_times_206 as fn
    assert isinstance(fn(SAMPLES["text"]), int)

def test_fn1_nonnegative():
    from zst import zst_compressed_mod_829_times_5000_plus_decompressed_times_203_plus_file_size_times_206 as fn
    for s in SAMPLES.values():
        assert fn(s) >= 0

def test_fn1_pathlib():
    from zst import zst_compressed_mod_829_times_5000_plus_decompressed_times_203_plus_file_size_times_206 as fn
    assert fn(Path(SAMPLES["text"])) == 1495202

def test_fn1_docstring():
    from zst import zst_compressed_mod_829_times_5000_plus_decompressed_times_203_plus_file_size_times_206 as fn
    assert fn.__doc__ is not None and "829" in fn.__doc__

# ---------------------------------------------------------------------------
# FN2: zst_compressed_mod_853_times_5100_plus_decompressed_times_207_plus_file_size_times_210
# ---------------------------------------------------------------------------

def test_fn2_text():
    from zst import zst_compressed_mod_853_times_5100_plus_decompressed_times_207_plus_file_size_times_210 as fn
    assert fn(SAMPLES["text"]) == 1525050

def test_fn2_minimal():
    from zst import zst_compressed_mod_853_times_5100_plus_decompressed_times_207_plus_file_size_times_210 as fn
    assert fn(SAMPLES["minimal"]) == 53307

def test_fn2_random():
    from zst import zst_compressed_mod_853_times_5100_plus_decompressed_times_207_plus_file_size_times_210 as fn
    assert fn(SAMPLES["random"]) == 1677528

def test_fn2_returns_int():
    from zst import zst_compressed_mod_853_times_5100_plus_decompressed_times_207_plus_file_size_times_210 as fn
    assert isinstance(fn(SAMPLES["text"]), int)

def test_fn2_nonnegative():
    from zst import zst_compressed_mod_853_times_5100_plus_decompressed_times_207_plus_file_size_times_210 as fn
    for s in SAMPLES.values():
        assert fn(s) >= 0

def test_fn2_pathlib():
    from zst import zst_compressed_mod_853_times_5100_plus_decompressed_times_207_plus_file_size_times_210 as fn
    assert fn(Path(SAMPLES["minimal"])) == 53307

def test_fn2_docstring():
    from zst import zst_compressed_mod_853_times_5100_plus_decompressed_times_207_plus_file_size_times_210 as fn
    assert fn.__doc__ is not None and "853" in fn.__doc__
