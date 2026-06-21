"""Tests for ZST analytics functions - sprint 532 (primes 929, 937)."""
from pathlib import Path
SAMPLES = {"text": "samples/by-format/zst/valid/text-compressed.zst", "minimal": "samples/by-format/zst/valid/minimal-synthetic.zst", "random": "samples/by-format/zst/valid/random-data.zst"}

def test_fn1_text():
    from zst import zst_compressed_mod_929_times_5600_plus_decompressed_times_217_plus_file_size_times_220 as fn
    assert fn(SAMPLES["text"]) == 1667670
def test_fn1_minimal():
    from zst import zst_compressed_mod_929_times_5600_plus_decompressed_times_217_plus_file_size_times_220 as fn
    assert fn(SAMPLES["minimal"]) == 58417
def test_fn1_random():
    from zst import zst_compressed_mod_929_times_5600_plus_decompressed_times_217_plus_file_size_times_220 as fn
    assert fn(SAMPLES["random"]) == 1828528
def test_fn1_int():
    from zst import zst_compressed_mod_929_times_5600_plus_decompressed_times_217_plus_file_size_times_220 as fn
    assert isinstance(fn(SAMPLES["text"]), int)
def test_fn1_nonneg():
    from zst import zst_compressed_mod_929_times_5600_plus_decompressed_times_217_plus_file_size_times_220 as fn
    for s in SAMPLES.values(): assert fn(s) >= 0
def test_fn1_path():
    from zst import zst_compressed_mod_929_times_5600_plus_decompressed_times_217_plus_file_size_times_220 as fn
    assert fn(Path(SAMPLES["text"])) == 1667670
def test_fn1_doc():
    from zst import zst_compressed_mod_929_times_5600_plus_decompressed_times_217_plus_file_size_times_220 as fn
    assert fn.__doc__ is not None and "929" in fn.__doc__
def test_fn2_text():
    from zst import zst_compressed_mod_937_times_5700_plus_decompressed_times_219_plus_file_size_times_222 as fn
    assert fn(SAMPLES["text"]) == 1696194
def test_fn2_minimal():
    from zst import zst_compressed_mod_937_times_5700_plus_decompressed_times_219_plus_file_size_times_222 as fn
    assert fn(SAMPLES["minimal"]) == 59439
def test_fn2_random():
    from zst import zst_compressed_mod_937_times_5700_plus_decompressed_times_219_plus_file_size_times_222 as fn
    assert fn(SAMPLES["random"]) == 1858728
def test_fn2_int():
    from zst import zst_compressed_mod_937_times_5700_plus_decompressed_times_219_plus_file_size_times_222 as fn
    assert isinstance(fn(SAMPLES["text"]), int)
def test_fn2_nonneg():
    from zst import zst_compressed_mod_937_times_5700_plus_decompressed_times_219_plus_file_size_times_222 as fn
    for s in SAMPLES.values(): assert fn(s) >= 0
def test_fn2_path():
    from zst import zst_compressed_mod_937_times_5700_plus_decompressed_times_219_plus_file_size_times_222 as fn
    assert fn(Path(SAMPLES["minimal"])) == 59439
def test_fn2_doc():
    from zst import zst_compressed_mod_937_times_5700_plus_decompressed_times_219_plus_file_size_times_222 as fn
    assert fn.__doc__ is not None and "937" in fn.__doc__
