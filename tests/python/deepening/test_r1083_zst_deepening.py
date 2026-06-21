"""Tests for ZST analytics functions — sprint 529 (primes 911, 919)."""
from pathlib import Path
SAMPLES = {"text": "samples/by-format/zst/valid/text-compressed.zst", "minimal": "samples/by-format/zst/valid/minimal-synthetic.zst", "random": "samples/by-format/zst/valid/random-data.zst"}

def test_fn1_text():
    from zst import zst_compressed_mod_911_times_5400_plus_decompressed_times_213_plus_file_size_times_216 as fn
    assert fn(SAMPLES["text"]) == 1610622
def test_fn1_minimal():
    from zst import zst_compressed_mod_911_times_5400_plus_decompressed_times_213_plus_file_size_times_216 as fn
    assert fn(SAMPLES["minimal"]) == 56373
def test_fn1_random():
    from zst import zst_compressed_mod_911_times_5400_plus_decompressed_times_213_plus_file_size_times_216 as fn
    assert fn(SAMPLES["random"]) == 1768128
def test_fn1_int():
    from zst import zst_compressed_mod_911_times_5400_plus_decompressed_times_213_plus_file_size_times_216 as fn
    assert isinstance(fn(SAMPLES["text"]), int)
def test_fn1_nonneg():
    from zst import zst_compressed_mod_911_times_5400_plus_decompressed_times_213_plus_file_size_times_216 as fn
    for s in SAMPLES.values(): assert fn(s) >= 0
def test_fn1_path():
    from zst import zst_compressed_mod_911_times_5400_plus_decompressed_times_213_plus_file_size_times_216 as fn
    assert fn(Path(SAMPLES["text"])) == 1610622
def test_fn1_doc():
    from zst import zst_compressed_mod_911_times_5400_plus_decompressed_times_213_plus_file_size_times_216 as fn
    assert fn.__doc__ is not None and "911" in fn.__doc__

def test_fn2_text():
    from zst import zst_compressed_mod_919_times_5500_plus_decompressed_times_215_plus_file_size_times_218 as fn
    assert fn(SAMPLES["text"]) == 1639146
def test_fn2_minimal():
    from zst import zst_compressed_mod_919_times_5500_plus_decompressed_times_215_plus_file_size_times_218 as fn
    assert fn(SAMPLES["minimal"]) == 57395
def test_fn2_random():
    from zst import zst_compressed_mod_919_times_5500_plus_decompressed_times_215_plus_file_size_times_218 as fn
    assert fn(SAMPLES["random"]) == 1798328
def test_fn2_int():
    from zst import zst_compressed_mod_919_times_5500_plus_decompressed_times_215_plus_file_size_times_218 as fn
    assert isinstance(fn(SAMPLES["text"]), int)
def test_fn2_nonneg():
    from zst import zst_compressed_mod_919_times_5500_plus_decompressed_times_215_plus_file_size_times_218 as fn
    for s in SAMPLES.values(): assert fn(s) >= 0
def test_fn2_path():
    from zst import zst_compressed_mod_919_times_5500_plus_decompressed_times_215_plus_file_size_times_218 as fn
    assert fn(Path(SAMPLES["minimal"])) == 57395
def test_fn2_doc():
    from zst import zst_compressed_mod_919_times_5500_plus_decompressed_times_215_plus_file_size_times_218 as fn
    assert fn.__doc__ is not None and "919" in fn.__doc__
