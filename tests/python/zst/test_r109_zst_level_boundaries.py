# R109 Lane F: ZST compression level boundary tests
# Tests compression at extreme levels and error paths

import pytest

def test_import_zst():
    """ZST module imports successfully."""
    import zst
    assert hasattr(zst, 'compress_bytes')
    assert hasattr(zst, 'decompress_bytes')

def test_compress_level_1():
    """Compression at minimum level 1 works."""
    from zst import compress_bytes, decompress_bytes
    data = b"R109 level 1 test data " * 100
    compressed = compress_bytes(data, level=1)
    assert len(compressed) < len(data)
    assert decompress_bytes(compressed) == data

def test_compress_level_3_default():
    """Default level 3 compression roundtrips."""
    from zst import compress_bytes, decompress_bytes
    data = b"R109 default level roundtrip " * 50
    compressed = compress_bytes(data)
    assert decompress_bytes(compressed) == data

def test_compress_level_22_max():
    """Maximum compression level 22 roundtrips."""
    from zst import compress_bytes, decompress_bytes
    data = b"R109 max level 22 data " * 100
    compressed = compress_bytes(data, level=22)
    assert decompress_bytes(compressed) == data

def test_higher_level_smaller_or_equal():
    """Higher levels produce same or smaller output."""
    from zst import compress_bytes
    data = b"Compare compression levels " * 200
    c1 = compress_bytes(data, level=1)
    c22 = compress_bytes(data, level=22)
    assert len(c22) <= len(c1)

def test_decompress_empty_raises():
    """Decompressing empty bytes raises an error."""
    from zst import decompress_bytes
    with pytest.raises(Exception):
        decompress_bytes(b"")

def test_decompress_garbage_raises():
    """Decompressing random non-zst data raises an error."""
    from zst import decompress_bytes
    with pytest.raises(Exception):
        decompress_bytes(b"this is not zstandard data at all")

def test_compress_empty():
    """Compressing empty bytes produces valid output that decompresses to empty."""
    from zst import compress_bytes, decompress_bytes
    compressed = compress_bytes(b"")
    result = decompress_bytes(compressed)
    assert result == b""
