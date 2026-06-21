"""Sprint 550 ZST analytics deepening tests - primes 1013, 1019."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")

def test_fn1_text():
    from zst import zst_compressed_mod_1013_times_6800_plus_decompressed_times_241_plus_file_size_times_244 as fn
    assert fn(str(SAMPLES / "text-compressed.zst")) == 2009958
def test_fn1_minimal():
    from zst import zst_compressed_mod_1013_times_6800_plus_decompressed_times_241_plus_file_size_times_244 as fn
    assert fn(str(SAMPLES / "minimal-synthetic.zst")) == 70681
def test_fn1_random():
    from zst import zst_compressed_mod_1013_times_6800_plus_decompressed_times_241_plus_file_size_times_244 as fn
    assert fn(str(SAMPLES / "random-data.zst")) == 2190928
def test_fn1_int():
    from zst import zst_compressed_mod_1013_times_6800_plus_decompressed_times_241_plus_file_size_times_244 as fn
    assert isinstance(fn(str(SAMPLES / "text-compressed.zst")), int)
def test_fn1_nonneg():
    from zst import zst_compressed_mod_1013_times_6800_plus_decompressed_times_241_plus_file_size_times_244 as fn
    for f in SAMPLES.iterdir(): assert fn(str(f)) >= 0
def test_fn1_path():
    from zst import zst_compressed_mod_1013_times_6800_plus_decompressed_times_241_plus_file_size_times_244 as fn
    assert fn(SAMPLES / "text-compressed.zst") == 2009958
def test_fn1_doc():
    from zst import zst_compressed_mod_1013_times_6800_plus_decompressed_times_241_plus_file_size_times_244 as fn
    assert fn.__doc__ is not None and "1013" in fn.__doc__
def test_fn2_text():
    from zst import zst_compressed_mod_1019_times_6900_plus_decompressed_times_243_plus_file_size_times_246 as fn
    assert fn(str(SAMPLES / "text-compressed.zst")) == 2038482
def test_fn2_minimal():
    from zst import zst_compressed_mod_1019_times_6900_plus_decompressed_times_243_plus_file_size_times_246 as fn
    assert fn(str(SAMPLES / "minimal-synthetic.zst")) == 71703
def test_fn2_random():
    from zst import zst_compressed_mod_1019_times_6900_plus_decompressed_times_243_plus_file_size_times_246 as fn
    assert fn(str(SAMPLES / "random-data.zst")) == 2221128
def test_fn2_int():
    from zst import zst_compressed_mod_1019_times_6900_plus_decompressed_times_243_plus_file_size_times_246 as fn
    assert isinstance(fn(str(SAMPLES / "text-compressed.zst")), int)
def test_fn2_nonneg():
    from zst import zst_compressed_mod_1019_times_6900_plus_decompressed_times_243_plus_file_size_times_246 as fn
    for f in SAMPLES.iterdir(): assert fn(str(f)) >= 0
def test_fn2_path():
    from zst import zst_compressed_mod_1019_times_6900_plus_decompressed_times_243_plus_file_size_times_246 as fn
    assert fn(SAMPLES / "minimal-synthetic.zst") == 71703
def test_fn2_doc():
    from zst import zst_compressed_mod_1019_times_6900_plus_decompressed_times_243_plus_file_size_times_246 as fn
    assert fn.__doc__ is not None and "1019" in fn.__doc__
