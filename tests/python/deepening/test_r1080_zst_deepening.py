"""Tests for ZST analytics functions — sprint 526 (primes 883, 907)."""
from pathlib import Path

SAMPLES = {
    "text": "samples/by-format/zst/valid/text-compressed.zst",
    "minimal": "samples/by-format/zst/valid/minimal-synthetic.zst",
    "random": "samples/by-format/zst/valid/random-data.zst",
}

def test_fn1_text():
    from zst import zst_compressed_mod_883_times_5200_plus_decompressed_times_209_plus_file_size_times_212 as fn
    assert fn(SAMPLES["text"]) == 1553574

def test_fn1_minimal():
    from zst import zst_compressed_mod_883_times_5200_plus_decompressed_times_209_plus_file_size_times_212 as fn
    assert fn(SAMPLES["minimal"]) == 54329

def test_fn1_random():
    from zst import zst_compressed_mod_883_times_5200_plus_decompressed_times_209_plus_file_size_times_212 as fn
    assert fn(SAMPLES["random"]) == 1707728

def test_fn1_int():
    from zst import zst_compressed_mod_883_times_5200_plus_decompressed_times_209_plus_file_size_times_212 as fn
    assert isinstance(fn(SAMPLES["text"]), int)

def test_fn1_nonneg():
    from zst import zst_compressed_mod_883_times_5200_plus_decompressed_times_209_plus_file_size_times_212 as fn
    for s in SAMPLES.values():
        assert fn(s) >= 0

def test_fn1_path():
    from zst import zst_compressed_mod_883_times_5200_plus_decompressed_times_209_plus_file_size_times_212 as fn
    assert fn(Path(SAMPLES["text"])) == 1553574

def test_fn1_doc():
    from zst import zst_compressed_mod_883_times_5200_plus_decompressed_times_209_plus_file_size_times_212 as fn
    assert fn.__doc__ is not None and "883" in fn.__doc__

def test_fn2_text():
    from zst import zst_compressed_mod_907_times_5300_plus_decompressed_times_211_plus_file_size_times_214 as fn
    assert fn(SAMPLES["text"]) == 1582098

def test_fn2_minimal():
    from zst import zst_compressed_mod_907_times_5300_plus_decompressed_times_211_plus_file_size_times_214 as fn
    assert fn(SAMPLES["minimal"]) == 55351

def test_fn2_random():
    from zst import zst_compressed_mod_907_times_5300_plus_decompressed_times_211_plus_file_size_times_214 as fn
    assert fn(SAMPLES["random"]) == 1737928

def test_fn2_int():
    from zst import zst_compressed_mod_907_times_5300_plus_decompressed_times_211_plus_file_size_times_214 as fn
    assert isinstance(fn(SAMPLES["text"]), int)

def test_fn2_nonneg():
    from zst import zst_compressed_mod_907_times_5300_plus_decompressed_times_211_plus_file_size_times_214 as fn
    for s in SAMPLES.values():
        assert fn(s) >= 0

def test_fn2_path():
    from zst import zst_compressed_mod_907_times_5300_plus_decompressed_times_211_plus_file_size_times_214 as fn
    assert fn(Path(SAMPLES["minimal"])) == 55351

def test_fn2_doc():
    from zst import zst_compressed_mod_907_times_5300_plus_decompressed_times_211_plus_file_size_times_214 as fn
    assert fn.__doc__ is not None and "907" in fn.__doc__
