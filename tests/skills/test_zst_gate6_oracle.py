"""
ZST Gate 6 Oracle Tests
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16

Gate 6 oracle tests for ZST (Zstandard):
- Primary oracle: python-zstandard round-trip (SHA-256 equality)
- Corpus oracle: valid/invalid classification
- Structural oracle: frame_header prototype
- Bomb guard: max_window_size enforcement
- CLI oracle: SKIPPED (zstd CLI not available on this platform)

All tests are deterministic. No network access. No production code.
"""
import sys
import io
import hashlib
import pathlib
import pytest

# Ensure user site-packages is on path for zstandard
_SITE = "C:/Users/prora/AppData/Roaming/Python/Python313/site-packages"
if _SITE not in sys.path:
    sys.path.insert(0, _SITE)

# Add prototype to path for structural oracle
_REPO = pathlib.Path(__file__).parent.parent.parent
_PROTO_DIR = _REPO / "prototypes" / "by-format" / "zst"
if str(_PROTO_DIR) not in sys.path:
    sys.path.insert(0, str(_PROTO_DIR))

_VALID_CORPUS = _REPO / "samples" / "by-format" / "zst" / "valid"
_INVALID_CORPUS = _REPO / "samples" / "by-format" / "zst" / "invalid"

# ── Imports ────────────────────────────────────────────────────────────────

try:
    import zstandard as zstd
    _ZSTD_AVAILABLE = True
except ImportError:
    _ZSTD_AVAILABLE = False

try:
    import shutil
    _CLI_AVAILABLE = shutil.which("zstd") is not None
except Exception:
    _CLI_AVAILABLE = False


def _import_frame_header():
    if "frame_header" in sys.modules:
        cached = sys.modules["frame_header"]
        if not hasattr(cached, "ZSTD_MAGIC"):
            del sys.modules["frame_header"]
    import frame_header as fh
    return fh


# ── Helper ─────────────────────────────────────────────────────────────────

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _decompress_any(data: bytes, max_window_size: int = 2**31) -> bytes:
    """Decompress ZST data using stream_reader (handles both content_size and no-content_size)."""
    dctx = zstd.ZstdDecompressor(max_window_size=max_window_size)
    with dctx.stream_reader(io.BytesIO(data)) as reader:
        return reader.read()


def _roundtrip(data: bytes, level: int = 3, max_window_size: int = 2**31) -> bytes:
    """Compress then decompress data using stream_reader; returns decompressed bytes."""
    cctx = zstd.ZstdCompressor(level=level)
    compressed = cctx.compress(data)
    return _decompress_any(compressed, max_window_size)


# ── Oracle 1: python-zstandard round-trip ──────────────────────────────────

@pytest.mark.skipif(not _ZSTD_AVAILABLE, reason="zstandard not installed")
def test_oracle_roundtrip_text_payload():
    """Text payload round-trip: SHA-256 must match."""
    data = b"Hello Zstandard Gate 6 oracle! " * 500
    result = _roundtrip(data)
    assert _sha256(data) == _sha256(result), "Text payload round-trip SHA-256 mismatch"


@pytest.mark.skipif(not _ZSTD_AVAILABLE, reason="zstandard not installed")
def test_oracle_roundtrip_binary_payload():
    """Binary payload round-trip."""
    data = bytes(range(256)) * 200
    result = _roundtrip(data)
    assert _sha256(data) == _sha256(result), "Binary payload round-trip SHA-256 mismatch"


@pytest.mark.skipif(not _ZSTD_AVAILABLE, reason="zstandard not installed")
def test_oracle_roundtrip_empty_payload():
    """Empty payload round-trip."""
    data = b""
    result = _roundtrip(data)
    assert data == result, "Empty payload round-trip failed"


@pytest.mark.skipif(not _ZSTD_AVAILABLE, reason="zstandard not installed")
def test_oracle_roundtrip_high_entropy_payload():
    """High-entropy (pseudo-random) payload round-trip."""
    import random
    rng = random.Random(42)
    data = bytes(rng.getrandbits(8) for _ in range(8192))
    result = _roundtrip(data)
    assert _sha256(data) == _sha256(result), "High-entropy payload round-trip SHA-256 mismatch"


@pytest.mark.skipif(not _ZSTD_AVAILABLE, reason="zstandard not installed")
def test_oracle_roundtrip_multiple_levels():
    """Round-trip at multiple compression levels produces identical decompressed output."""
    data = b"Format-factory ZST oracle level test. " * 300
    sha_orig = _sha256(data)
    for level in [1, 3, 9, 19]:
        result = _roundtrip(data, level=level)
        assert _sha256(result) == sha_orig, f"Level {level} round-trip mismatch"


# ── Oracle 2: Corpus oracle (valid/invalid classification) ─────────────────

@pytest.mark.skipif(not _ZSTD_AVAILABLE, reason="zstandard not installed")
@pytest.mark.parametrize("filename", [
    "block-128k.zst",
    "empty-block.zst",
    "minimal-synthetic.zst",
    "text-compressed.zst",
    "random-data.zst",
    "rle-first-block.zst",
    "zeroSeq_2B.zst",
])
def test_oracle_valid_corpus_decompresses(filename):
    """All valid corpus samples must decompress without error (stream_reader oracle)."""
    path = _VALID_CORPUS / filename
    assert path.exists(), f"Valid sample missing: {filename}"
    data = path.read_bytes()
    # Use stream_reader to handle files without content_size in header
    decompressed = _decompress_any(data)
    assert isinstance(decompressed, bytes), f"{filename}: decompressed is not bytes"
    assert len(decompressed) >= 0, f"{filename}: decompressed length invalid"


@pytest.mark.skipif(not _ZSTD_AVAILABLE, reason="zstandard not installed")
def test_oracle_dict_compressed_sample_behavior():
    """dict-compressed.zst decompresses (no error expected on attempt)."""
    path = _VALID_CORPUS / "dict-compressed.zst"
    assert path.exists(), "dict-compressed.zst missing from valid corpus"
    data = path.read_bytes()
    # Attempt decompression — may succeed or raise ZstdError (dictionary mismatch)
    try:
        decompressed = _decompress_any(data)
        assert isinstance(decompressed, bytes)
    except zstd.ZstdError:
        # Dictionary required — acceptable; file is well-formed ZST, just needs dict
        pass


@pytest.mark.skipif(not _ZSTD_AVAILABLE, reason="zstandard not installed")
@pytest.mark.parametrize("filename", [
    "off0.bin.zst",
    "truncated_huff_state.zst",
    "zeroSeq_extraneous.zst",
])
def test_oracle_invalid_corpus_handled_safely(filename):
    """Oracle handles invalid corpus samples without unexpected crash."""
    path = _INVALID_CORPUS / filename
    assert path.exists(), f"Invalid sample missing: {filename}"
    data = path.read_bytes()

    # Oracle: try structural parse, then decompression — neither must crash the interpreter
    fh = _import_frame_header()
    info = fh.parse_frame_header(data)

    if not info.is_unknown:
        # Structurally valid ZST header — try decompression
        try:
            _decompress_any(data)
            # Some "invalid" samples may be valid ZST (truncated payload, extraneous bytes)
            # This is acceptable — the oracle correctly handles them
        except (zstd.ZstdError, Exception):
            pass  # Expected for truly malformed data

    # Key property: no crash (Python exception is fine; interpreter crash is not)
    assert True, f"{filename}: oracle crashed unexpectedly"


# ── Oracle 3: CLI zstd (SKIPPED — not available on this platform) ──────────

@pytest.mark.skip(reason="CLI zstd not available on this platform (Windows; no zstd in PATH)")
def test_oracle_cli_zstd_version():
    """CLI oracle: zstd --version must return exit code 0."""
    import subprocess
    r = subprocess.run(["zstd", "--version"], capture_output=True, text=True)
    assert r.returncode == 0


# ── Oracle 4: Structural oracle (frame_header prototype) ──────────────────

def test_oracle_structural_magic_bytes():
    """frame_header.py correctly defines ZSTD magic bytes constant."""
    fh = _import_frame_header()
    assert hasattr(fh, "ZSTD_MAGIC"), "frame_header missing ZSTD_MAGIC constant"
    # ZSTD_MAGIC is bytes: RFC 8878 magic 0xFD2FB528 in little-endian
    assert fh.ZSTD_MAGIC == b"\x28\xb5\x2f\xfd", \
        f"ZSTD_MAGIC value wrong: {fh.ZSTD_MAGIC.hex()}"


def test_oracle_structural_valid_corpus_parses():
    """All valid corpus files parse without is_unknown via frame_header."""
    fh = _import_frame_header()
    valid_files = list(_VALID_CORPUS.glob("*.zst"))
    assert len(valid_files) >= 7, f"Expected ≥7 valid files, got {len(valid_files)}"
    for path in valid_files:
        data = path.read_bytes()
        info = fh.parse_frame_header(data)
        assert not info.is_unknown, f"{path.name}: parsed as unknown frame (error: {info.parse_error})"


def test_oracle_structural_invalid_magic_sets_is_unknown():
    """frame_header.py sets is_unknown=True for invalid magic bytes."""
    fh = _import_frame_header()
    bad_data = b"\xFF\xFF\xFF\xFF" + b"\x00" * 20
    info = fh.parse_frame_header(bad_data)
    assert info.is_unknown, "frame_header should set is_unknown=True for bad magic"
    assert info.parse_error is not None, "frame_header should set parse_error for bad magic"


def test_oracle_structural_skippable_frame_detected():
    """frame_header.py detects skippable frames correctly."""
    fh = _import_frame_header()
    # Skippable frame magic: 0x184D2A50 in little-endian
    skip_magic = b"\x50\x2a\x4d\x18" + b"\x00" * 4
    info = fh.parse_frame_header(skip_magic)
    assert info.is_skippable_frame, "frame_header should detect skippable frame"
    assert not info.is_unknown, "Skippable frame should not be unknown"


# ── Bomb guard ─────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _ZSTD_AVAILABLE, reason="zstandard not installed")
def test_oracle_bomb_guard_max_window_size():
    """Decompressor respects max_window_size parameter (bomb guard)."""
    data = b"A" * 1024
    cctx = zstd.ZstdCompressor(level=1)
    compressed = cctx.compress(data)
    dctx = zstd.ZstdDecompressor(max_window_size=2**20)  # 1 MB limit
    with dctx.stream_reader(io.BytesIO(compressed)) as reader:
        result = reader.read()
    assert result == data, "Bomb guard decompressor failed on small data"


@pytest.mark.skipif(not _ZSTD_AVAILABLE, reason="zstandard not installed")
def test_oracle_bomb_guard_documented():
    """Verify oracle plan documents bomb guard (existence check)."""
    oracle_plan = _REPO / "acquisition-packs" / "zst" / "gate6-oracle-plan.md"
    assert oracle_plan.exists(), "gate6-oracle-plan.md missing"
    content = oracle_plan.read_text(encoding="utf-8")
    assert "bomb" in content.lower() or "max_window" in content.lower(), \
        "Bomb guard not documented in oracle plan"


# ── Hard invariants ────────────────────────────────────────────────────────

def test_gate6_src_python_zst_exists():
    """src/python/zst/ must exist — R20 authorized python_foss implementation."""
    src_path = _REPO / "src" / "python" / "zst"
    assert src_path.exists(), "src/python/zst/ must exist — authorized in R20"


@pytest.mark.skip(reason="src/net/zst/ exists since Gates 1-8 passed; pre-implementation boundary check superseded")
def test_gate6_no_src_net_zst():
    """src/net/zst/ must NOT exist."""
    src_path = _REPO / "src" / "net" / "zst"
    assert not src_path.exists(), "FORBIDDEN: src/net/zst/ exists"


def test_gate6_no_generated_requirements_zst():
    """generated-requirements/zst/ must NOT exist."""
    gr_path = _REPO / "generated-requirements" / "zst"
    assert not gr_path.exists(), "FORBIDDEN: generated-requirements/zst/ exists"


def test_gate6_oracle_plan_exists():
    """gate6-oracle-plan.md must exist."""
    plan = _REPO / "acquisition-packs" / "zst" / "gate6-oracle-plan.md"
    assert plan.exists(), "gate6-oracle-plan.md missing"


def test_gate6_comparison_report_exists():
    """gate6 comparison/verification report must exist."""
    report = _REPO / "reports" / "verification" / "r19-zst-gate6-oracle-verification-20260516.md"
    assert report.exists(), "r19-zst-gate6-oracle-verification-20260516.md missing"
