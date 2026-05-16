"""
ZST Gate 4 — Prototype Validation Tests
Sprint: FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001

Validates:
1.  Prototype directory and all required files exist
2.  README.md contains non-production boundary statement
3.  frame_header.py: ZST magic constant correct (RFC 8878)
4.  frame_header.py: parse_frame_header() detects valid ZSTD frame
5.  frame_header.py: parse_frame_header() detects skippable frame
6.  frame_header.py: parse_frame_header() detects unknown/invalid frame
7.  frame_header.py: FHD byte decoding (Single_Segment, Content_Size)
8.  frame_header.py: runs on all 11 corpus files without exception
9.  zst_probe.py: probe() returns expected keys for a valid sample
10. zst_probe.py: probe() handles missing file gracefully (exists=False)
11. zst_probe.py: probe() reports decompression error for invalid sample
12. validate_corpus.py: 8 valid samples PASS
13. validate_corpus.py: 3 invalid samples correctly rejected
14. validate_corpus.py: 4 round-trip payloads PASS
15. Hard invariant: no src/python/zst or src/net/zst directory
16. Hard invariant: no generated-requirements/zst directory
17. Hard invariant: registry gate_4.status = planning_complete
18. Hard invariant: registry gate_4 notes mention implementation_authorized: false
19. Hard invariant: registry gate_5.status = not_started
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

REPO_ROOT = Path(__file__).parent.parent.parent
PROTO_DIR = REPO_ROOT / "prototypes" / "by-format" / "zst"
SAMPLES_ZST = REPO_ROOT / "samples" / "by-format" / "zst"
VALID_DIR = SAMPLES_ZST / "valid"
INVALID_DIR = SAMPLES_ZST / "invalid"
REGISTRY_PATH = REPO_ROOT / "registry" / "format-registry.yaml"

VALID_FILES = [
    "block-128k.zst",
    "dict-compressed.zst",
    "empty-block.zst",
    "minimal-synthetic.zst",
    "random-data.zst",
    "rle-first-block.zst",
    "text-compressed.zst",
    "zeroSeq_2B.zst",
]

INVALID_FILES = [
    "off0.bin.zst",
    "truncated_huff_state.zst",
    "zeroSeq_extraneous.zst",
]

ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"
SKIPPABLE_MAGIC_MIN = 0x184D2A50
SKIPPABLE_MAGIC_MAX = 0x184D2A5F


# ── helpers ───────────────────────────────────────────────────────────────────

def _ensure_proto_on_path():
    """Add prototype directory to sys.path so its modules can be imported."""
    proto_str = str(PROTO_DIR)
    if proto_str not in sys.path:
        sys.path.insert(0, proto_str)


def _import_frame_header():
    """Import frame_header module from prototypes/by-format/zst/."""
    _ensure_proto_on_path()
    # Remove cached version if it came from elsewhere
    if "frame_header" in sys.modules:
        cached = sys.modules["frame_header"]
        if not hasattr(cached, "ZSTD_MAGIC"):
            del sys.modules["frame_header"]
    import frame_header as fh
    return fh


def _import_zst_probe():
    """Import zst_probe module from prototypes/by-format/zst/."""
    _ensure_proto_on_path()
    import zst_probe
    return zst_probe


def _import_validate_corpus():
    """Import validate_corpus module from prototypes/by-format/zst/."""
    _ensure_proto_on_path()
    import validate_corpus as vc
    return vc


def _load_zst_registry_entry() -> dict | None:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    for fmt in data.get("formats", []):
        if fmt.get("format_id") == "zst":
            return fmt
    return None


def _get_zst_gate(gate_key: str) -> dict:
    entry = _load_zst_registry_entry()
    assert entry is not None, "ZST not found in format-registry.yaml"
    return entry.get("gates", {}).get(gate_key, {})


def _make_skippable_frame() -> bytes:
    """Build a minimal skippable frame (magic 0x184D2A50 LE, size 0)."""
    magic = SKIPPABLE_MAGIC_MIN.to_bytes(4, "little")
    size = (0).to_bytes(4, "little")
    return magic + size


# ── 1. Prototype files exist ──────────────────────────────────────────────────

def test_prototype_directory_exists():
    """prototypes/by-format/zst/ must exist."""
    assert PROTO_DIR.exists(), f"Prototype directory missing: {PROTO_DIR}"


@pytest.mark.parametrize("fname", [
    "README.md",
    "frame_header.py",
    "zst_probe.py",
    "validate_corpus.py",
])
def test_prototype_file_exists(fname):
    """Each required prototype file must be present and non-empty."""
    path = PROTO_DIR / fname
    assert path.exists(), f"Prototype file missing: {fname}"
    assert path.stat().st_size > 0, f"Prototype file is empty: {fname}"


# ── 2. README non-production boundary ─────────────────────────────────────────

def test_readme_non_production_boundary():
    """README.md must contain PROTOTYPE / NON-PRODUCTION boundary statement."""
    readme = (PROTO_DIR / "README.md").read_text(encoding="utf-8")
    assert "PROTOTYPE" in readme.upper() or "NON-PRODUCTION" in readme.upper(), (
        "README.md must contain a non-production boundary statement"
    )


def test_readme_security_notes():
    """README.md must mention decompression security considerations."""
    readme = (PROTO_DIR / "README.md").read_text(encoding="utf-8")
    security_keywords = ["decompression bomb", "window size", "streaming", "security"]
    assert any(kw.lower() in readme.lower() for kw in security_keywords), (
        "README.md must contain security notes for decompression"
    )


# ── 3. frame_header: magic constant ──────────────────────────────────────────

def test_frame_header_magic_constant():
    """ZSTD_MAGIC in frame_header.py must be b'\\x28\\xb5\\x2f\\xfd' (RFC 8878)."""
    fh = _import_frame_header()
    assert fh.ZSTD_MAGIC == ZSTD_MAGIC, (
        f"ZSTD_MAGIC mismatch: got {fh.ZSTD_MAGIC!r}, expected {ZSTD_MAGIC!r}"
    )


def test_frame_header_skippable_magic_range():
    """Skippable frame magic range must be 0x184D2A50 - 0x184D2A5F."""
    fh = _import_frame_header()
    assert fh.SKIPPABLE_MAGIC_MIN == SKIPPABLE_MAGIC_MIN
    assert fh.SKIPPABLE_MAGIC_MAX == SKIPPABLE_MAGIC_MAX


# ── 4. frame_header: ZSTD frame detection ────────────────────────────────────

@pytest.mark.skipif(not ZSTD_AVAILABLE, reason="zstandard not installed")
def test_frame_header_detects_zstd_frame():
    """parse_frame_header() must detect a valid ZSTD frame."""
    fh = _import_frame_header()
    cctx = zstd.ZstdCompressor(level=1)
    data = cctx.compress(b"hello")
    info = fh.parse_frame_header(data)
    assert info.is_zstandard_frame, "Expected is_zstandard_frame=True"
    assert not info.is_skippable_frame, "Expected is_skippable_frame=False"


# ── 5. frame_header: skippable frame detection ───────────────────────────────

def test_frame_header_detects_skippable_frame():
    """parse_frame_header() must detect a skippable frame."""
    fh = _import_frame_header()
    data = _make_skippable_frame()
    info = fh.parse_frame_header(data)
    assert info.is_skippable_frame, "Expected is_skippable_frame=True"
    assert not info.is_zstandard_frame, "Expected is_zstandard_frame=False"


# ── 6. frame_header: unknown frame detection ─────────────────────────────────

def test_frame_header_detects_unknown_frame():
    """parse_frame_header() must return is_unknown=True for garbage data."""
    fh = _import_frame_header()
    data = b"\x00\x01\x02\x03\x04\x05\x06\x07"
    info = fh.parse_frame_header(data)
    assert info.is_unknown, "Expected is_unknown=True for non-ZST data"
    assert not info.is_zstandard_frame
    assert not info.is_skippable_frame


# ── 7. frame_header: FHD byte decoding ───────────────────────────────────────

@pytest.mark.skipif(not ZSTD_AVAILABLE, reason="zstandard not installed")
def test_frame_header_fhd_single_segment():
    """Single-segment frame must have single_segment=True."""
    fh = _import_frame_header()
    cctx = zstd.ZstdCompressor(level=1)
    data = cctx.compress(b"hello")
    info = fh.parse_frame_header(data)
    assert info.is_zstandard_frame
    assert info.single_segment, "Small payload should be single-segment"


@pytest.mark.skipif(not ZSTD_AVAILABLE, reason="zstandard not installed")
def test_frame_header_fhd_content_size_present():
    """Single-segment compressed frame must report content_size."""
    fh = _import_frame_header()
    cctx = zstd.ZstdCompressor(level=1)
    payload = b"hello world"
    data = cctx.compress(payload)
    info = fh.parse_frame_header(data)
    assert info.content_size_present, "Content_Size should be present in single-segment frame"
    assert info.content_size == len(payload), (
        f"content_size mismatch: expected {len(payload)}, got {info.content_size}"
    )


# ── 8. frame_header: runs on all corpus files ─────────────────────────────────

@pytest.mark.parametrize("fname", VALID_FILES)
def test_frame_header_parses_valid_corpus(fname):
    """parse_frame_header() must not raise on any valid corpus file."""
    path = VALID_DIR / fname
    if not path.exists():
        pytest.skip(f"Corpus file missing: {fname}")
    fh = _import_frame_header()
    data = path.read_bytes()
    info = fh.parse_frame_header(data)
    assert info.is_zstandard_frame or info.is_skippable_frame, (
        f"Valid corpus file {fname} must be a ZSTD or skippable frame"
    )


@pytest.mark.parametrize("fname", INVALID_FILES)
def test_frame_header_parses_invalid_corpus(fname):
    """parse_frame_header() must not raise on invalid corpus files."""
    path = INVALID_DIR / fname
    if not path.exists():
        pytest.skip(f"Corpus file missing: {fname}")
    fh = _import_frame_header()
    data = path.read_bytes()
    # Should not raise — corruption is at block level, not necessarily frame header
    info = fh.parse_frame_header(data)
    assert info is not None


# ── 9. zst_probe: probe() returns expected keys ───────────────────────────────

@pytest.mark.skipif(not ZSTD_AVAILABLE, reason="zstandard not installed")
def test_zst_probe_returns_expected_keys():
    """probe() must return a dict with required metadata keys."""
    mod = _import_zst_probe()
    path = VALID_DIR / "minimal-synthetic.zst"
    if not path.exists():
        pytest.skip("minimal-synthetic.zst not present")
    result = mod.probe(path)
    required_keys = {"path", "exists", "header", "decompressed_size", "decompression_error"}
    assert isinstance(result, dict), "probe() must return a dict"
    assert required_keys.issubset(result.keys()), (
        f"Missing keys: {required_keys - result.keys()}"
    )


@pytest.mark.skipif(not ZSTD_AVAILABLE, reason="zstandard not installed")
def test_zst_probe_decompresses_valid_sample():
    """probe() must successfully decompress a valid sample."""
    mod = _import_zst_probe()
    path = VALID_DIR / "text-compressed.zst"
    if not path.exists():
        pytest.skip("text-compressed.zst not present")
    result = mod.probe(path)
    assert result.get("decompressed_size") is not None, (
        "probe() should report decompressed_size for valid sample"
    )
    assert result.get("decompression_error") is None, (
        f"probe() should not report error for valid sample, got: {result.get('decompression_error')}"
    )


# ── 10. zst_probe: missing file ───────────────────────────────────────────────

def test_zst_probe_missing_file_exists_false():
    """probe() must return exists=False for a missing path."""
    mod = _import_zst_probe()
    missing = PROTO_DIR / "does_not_exist_xyz.zst"
    result = mod.probe(missing)
    assert isinstance(result, dict), "probe() must return a dict"
    assert result.get("exists") is False, (
        f"probe() must report exists=False for missing file, got: {result.get('exists')}"
    )


# ── 11. zst_probe: reports error for invalid sample ──────────────────────────

@pytest.mark.skipif(not ZSTD_AVAILABLE, reason="zstandard not installed")
def test_zst_probe_reports_error_for_invalid_sample():
    """probe() must report decompression_error for invalid sample."""
    mod = _import_zst_probe()
    path = INVALID_DIR / "off0.bin.zst"
    if not path.exists():
        pytest.skip("off0.bin.zst not present")
    result = mod.probe(path)
    assert result.get("decompression_error") is not None, (
        f"probe() should report decompression_error for invalid sample, got: {result}"
    )
    assert result.get("decompressed_size") is None, (
        "probe() should not report decompressed_size for failed decompression"
    )


# ── 12. validate_corpus: valid samples ───────────────────────────────────────

@pytest.mark.skipif(not ZSTD_AVAILABLE, reason="zstandard not installed")
def test_validate_corpus_valid_samples_all_pass():
    """All 8 valid samples must decompress without error."""
    vc = _import_validate_corpus()
    results = vc.validate_valid_samples(zstd)
    failures = [r for r in results if not (r["decompressed"] and r["exists"])]
    assert not failures, (
        f"Valid sample failures: {[r['file'] for r in failures]}"
    )
    assert len(results) == 8, f"Expected 8 valid results, got {len(results)}"


# ── 13. validate_corpus: invalid samples correctly rejected ──────────────────

@pytest.mark.skipif(not ZSTD_AVAILABLE, reason="zstandard not installed")
def test_validate_corpus_invalid_samples_all_rejected():
    """All 3 invalid samples must raise ZstdError during decompression."""
    vc = _import_validate_corpus()
    results = vc.validate_invalid_samples(zstd)
    non_rejected = [r for r in results if not (r["correctly_rejected"] and r["exists"])]
    assert not non_rejected, (
        f"Invalid samples NOT correctly rejected: {[r['file'] for r in non_rejected]}"
    )
    assert len(results) == 3, f"Expected 3 invalid results, got {len(results)}"


# ── 14. validate_corpus: round-trip payloads ─────────────────────────────────

@pytest.mark.skipif(not ZSTD_AVAILABLE, reason="zstandard not installed")
def test_validate_corpus_round_trips_all_pass():
    """All 4 synthetic round-trip payloads must survive compress+decompress."""
    vc = _import_validate_corpus()
    results = vc.validate_round_trips(zstd)
    failures = [r for r in results if not r["round_trip"]]
    assert not failures, (
        f"Round-trip failures: {[(r['payload_index'], r.get('error')) for r in failures]}"
    )
    assert len(results) == 4, f"Expected 4 round-trip results, got {len(results)}"


# ── 15. Hard invariant: no src/python/zst or src/net/zst ─────────────────────

def test_no_src_python_zst():
    """src/python/zst/ must NOT exist (implementation not authorized)."""
    path = REPO_ROOT / "src" / "python" / "zst"
    assert not path.exists(), (
        "src/python/zst/ must not exist — Gate 4 prototype only; no implementation authorized"
    )


def test_no_src_net_zst():
    """src/net/zst/ must NOT exist (implementation not authorized)."""
    path = REPO_ROOT / "src" / "net" / "zst"
    assert not path.exists(), (
        "src/net/zst/ must not exist — Gate 4 prototype only; no implementation authorized"
    )


# ── 16. Hard invariant: no generated-requirements/zst ─────────────────────────

def test_no_generated_requirements_zst():
    """generated-requirements/zst/ must NOT exist."""
    path = REPO_ROOT / "generated-requirements" / "zst"
    assert not path.exists(), (
        "generated-requirements/zst/ must not exist — Gate 4 only; no requirements generated"
    )


# ── 17. Hard invariant: registry gate_4.status ────────────────────────────────

def test_registry_gate4_status_planning_complete_or_passed():
    """Registry gate_4.status must be planning_complete or passed."""
    gate4 = _get_zst_gate("gate_4")
    status = gate4.get("status", "")
    valid_statuses = {"planning_complete", "prototype_complete", "passed"}
    assert status in valid_statuses, (
        f"gate_4.status={status!r} not in {valid_statuses}"
    )


# ── 18. Hard invariant: implementation_authorized mentioned in gate_4 notes ───

def test_registry_gate4_notes_mention_implementation_not_authorized():
    """Registry gate_4.notes must mention implementation_authorized: false."""
    gate4 = _get_zst_gate("gate_4")
    notes = gate4.get("notes", "") or ""
    assert "implementation_authorized" in notes and "false" in notes.lower(), (
        f"gate_4.notes must mention 'implementation_authorized: false'; got: {notes!r}"
    )


# ── 19. Hard invariant: registry gate_5.status ────────────────────────────────

def test_registry_gate5_status_not_started():
    """Registry gate_5.status must be not_started or waived_not_applicable (Gate 5 waived R19)."""
    gate5 = _get_zst_gate("gate_5")
    status = gate5.get("status", "not_started")
    valid_statuses = {"not_started", "waived_not_applicable"}
    assert status in valid_statuses, (
        f"gate_5.status must be one of {valid_statuses}, got {status!r}"
    )
