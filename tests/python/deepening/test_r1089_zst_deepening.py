"""Tests for ZST analytics functions - sprint 535 (primes 941, 947)."""
from pathlib import Path
SAMPLES = {"text": "samples/by-format/zst/valid/text-compressed.zst", "minimal": "samples/by-format/zst/valid/minimal-synthetic.zst", "random": "samples/by-format/zst/valid/random-data.zst"}

def test_fn1_text():
    from zst import zst_compressed_mod_941_times_5800_plus_decompressed_times_221_plus_file_size_times_224 as fn
    assert fn(SAMPLES["text"]) == 1724718
def test_fn1_minimal():
    from zst import zst_compressed_mod_941_times_5800_plus_decompressed_times_221_plus_file_size_times_224 as fn
    assert fn(SAMPLES["minimal"]) == 60461
def test_fn1_random():
    from zst import zst_compressed_mod_941_times_5800_plus_decompressed_times_221_plus_file_size_times_224 as fn
    assert fn(SAMPLES["random"]) == 1888928
def test_fn1_int():
    from zst import zst_compressed_mod_941_times_5800_plus_decompressed_times_221_plus_file_size_times_224 as fn
    assert isinstance(fn(SAMPLES["text"]), int)
def test_fn1_nonneg():
    from zst import zst_compressed_mod_941_times_5800_plus_decompressed_times_221_plus_file_size_times_224 as fn
    for s in SAMPLES.values(): assert fn(s) >= 0
def test_fn1_path():
    from zst import zst_compressed_mod_941_times_5800_plus_decompressed_times_221_plus_file_size_times_224 as fn
    assert fn(Path(SAMPLES["text"])) == 1724718
def test_fn1_doc():
    from zst import zst_compressed_mod_941_times_5800_plus_decompressed_times_221_plus_file_size_times_224 as fn
    assert fn.__doc__ is not None and "941" in fn.__doc__
def test_fn2_text():
    from zst import zst_compressed_mod_947_times_5900_plus_decompressed_times_223_plus_file_size_times_226 as fn
    assert fn(SAMPLES["text"]) == 1753242
def test_fn2_minimal():
    from zst import zst_compressed_mod_947_times_5900_plus_decompressed_times_223_plus_file_size_times_226 as fn
    assert fn(SAMPLES["minimal"]) == 61483
def test_fn2_random():
    from zst import zst_compressed_mod_947_times_5900_plus_decompressed_times_223_plus_file_size_times_226 as fn
    assert fn(SAMPLES["random"]) == 1919128
def test_fn2_int():
    from zst import zst_compressed_mod_947_times_5900_plus_decompressed_times_223_plus_file_size_times_226 as fn
    assert isinstance(fn(SAMPLES["text"]), int)
def test_fn2_nonneg():
    from zst import zst_compressed_mod_947_times_5900_plus_decompressed_times_223_plus_file_size_times_226 as fn
    for s in SAMPLES.values(): assert fn(s) >= 0
def test_fn2_path():
    from zst import zst_compressed_mod_947_times_5900_plus_decompressed_times_223_plus_file_size_times_226 as fn
    assert fn(Path(SAMPLES["minimal"])) == 61483
def test_fn2_doc():
    from zst import zst_compressed_mod_947_times_5900_plus_decompressed_times_223_plus_file_size_times_226 as fn
    assert fn.__doc__ is not None and "947" in fn.__doc__
