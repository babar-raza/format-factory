"""
ZST Gate 3B — Sample Corpus Acquisition Validation Tests
Sprint: FORMAT-FACTORY-R16-ZST-GATE3B-CORPUS-ACQUISITION-IV-AND-MULTI-FORMAT-INTAKE-SWARM-001

Validates:
1.  samples/by-format/zst/ directory exists with valid/ and invalid/ subdirs
2.  All 8 expected valid .zst files are present
3.  All 3 expected invalid .zst files are present
4.  SHA-256 hashes match _corpus-manifest.yaml for every file
5.  Valid samples decompress without error (zstandard)
6.  Invalid samples raise ZstdError on decompression
7.  _corpus-manifest.yaml exists and has correct summary counts
8.  _provenance.yaml exists and all entries have provenance_status: confirmed
9.  Gate 3A artifacts still intact (sample-sources.md, pack.yaml, registry)
10. No src/ mutations (hard invariant)
11. No generated-requirements/ for ZST
12. generation script exists and is non-empty
"""
import hashlib
import yaml
from pathlib import Path

import pytest

try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

REPO_ROOT = Path(__file__).parent.parent.parent
SAMPLES_ZST = REPO_ROOT / "samples" / "by-format" / "zst"
VALID_DIR = SAMPLES_ZST / "valid"
INVALID_DIR = SAMPLES_ZST / "invalid"
MANIFEST_PATH = SAMPLES_ZST / "_corpus-manifest.yaml"
PROVENANCE_PATH = SAMPLES_ZST / "_provenance.yaml"
ACQUISITION_PACK = REPO_ROOT / "acquisition-packs" / "zst"
REGISTRY_PATH = REPO_ROOT / "registry" / "format-registry.yaml"
PACK_YAML = ACQUISITION_PACK / "pack.yaml"
GENERATION_SCRIPT = SAMPLES_ZST / "source-materials" / "generation-scripts" / "generate_synthetic_zst.py"

EXPECTED_VALID_FILES = [
    "block-128k.zst",
    "empty-block.zst",
    "rle-first-block.zst",
    "zeroSeq_2B.zst",
    "minimal-synthetic.zst",
    "text-compressed.zst",
    "dict-compressed.zst",
    "random-data.zst",
]

EXPECTED_INVALID_FILES = [
    "off0.bin.zst",
    "truncated_huff_state.zst",
    "zeroSeq_extraneous.zst",
]

# Expected SHA-256 from _corpus-manifest.yaml (authoritative)
EXPECTED_SHA256 = {
    "valid/block-128k.zst":         "sha256:6a226ab40e6abcfc4a36baa04bf48f7ee56f166b8a26fbe2adb8fe771dceccba",
    "valid/empty-block.zst":        "sha256:ab5463fa31429bf81ced9f05e99b96b2fe88b1da37235a233f6bc96242332fbc",
    "valid/rle-first-block.zst":    "sha256:dd31b3fa6bb8601710cbde2c625660763bf38adc5255501e3d3a681cc0e4e1a4",
    "valid/zeroSeq_2B.zst":         "sha256:8505867ac00fb49eb455da1b1e44e7cba5126f03114a72fb195170f7c95f2ca7",
    "valid/minimal-synthetic.zst":  "sha256:7a4c6310840830c5b9c7f58c5b50fbf6489f91d9dcb538a69e0682c06244defe",
    "valid/text-compressed.zst":    "sha256:3f4e90410fee63e1d355f7d6f90608bda9e697be406c31f7967662a45f2a05fb",
    "valid/dict-compressed.zst":    "sha256:f40fca81d33f3540929049edb3fb7555df97a2c4ad7bacf9c714b4d5a9ce5257",
    "valid/random-data.zst":        "sha256:393b84637a36b28c049e3d9b5b2e11d7f83be3182ee3c7dca7830e8e698498bf",
    "invalid/off0.bin.zst":         "sha256:144e2f029389c67c361bd3879ac142671592802f01f805a6c0c2b3e564d8022c",
    "invalid/truncated_huff_state.zst": "sha256:c91a09d8824609d0643291803cbfb04b14213c02c890d5637bc3aed18e8a24f8",
    "invalid/zeroSeq_extraneous.zst": "sha256:85d7b2010abde2ff96ab8e6798b422d3cb78f8dd2108f83dbdd488da7056a6db",
}


# ── helpers ───────────────────────────────────────────────────────────────────

def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return f"sha256:{h.hexdigest()}"


def _load_manifest() -> dict:
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_provenance() -> list:
    with open(PROVENANCE_PATH, encoding="utf-8") as f:
        return list(yaml.safe_load_all(f))


def _load_zst_registry_entry() -> dict | None:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    for fmt in data.get("formats", []):
        if fmt.get("format_id") == "zst":
            return fmt
    return None


# ── 1. Directory structure ─────────────────────────────────────────────────────

def test_samples_zst_directory_exists():
    """samples/by-format/zst/ must exist after Gate 3B corpus acquisition."""
    assert SAMPLES_ZST.exists(), "samples/by-format/zst/ must exist after corpus acquisition"


def test_valid_subdirectory_exists():
    """samples/by-format/zst/valid/ must exist."""
    assert VALID_DIR.exists(), "valid/ subdirectory must exist"


def test_invalid_subdirectory_exists():
    """samples/by-format/zst/invalid/ must exist."""
    assert INVALID_DIR.exists(), "invalid/ subdirectory must exist"


# ── 2. All expected valid files present ───────────────────────────────────────

@pytest.mark.parametrize("filename", EXPECTED_VALID_FILES)
def test_valid_file_present(filename):
    """Each expected valid .zst file must be present in valid/."""
    path = VALID_DIR / filename
    assert path.exists(), f"valid/{filename} is missing from corpus"
    assert path.stat().st_size > 0, f"valid/{filename} is empty"


# ── 3. All expected invalid files present ─────────────────────────────────────

@pytest.mark.parametrize("filename", EXPECTED_INVALID_FILES)
def test_invalid_file_present(filename):
    """Each expected invalid .zst file must be present in invalid/."""
    path = INVALID_DIR / filename
    assert path.exists(), f"invalid/{filename} is missing from corpus"
    assert path.stat().st_size > 0, f"invalid/{filename} is empty"


# ── 4. SHA-256 integrity ───────────────────────────────────────────────────────

@pytest.mark.parametrize("rel_path,expected_hash", list(EXPECTED_SHA256.items()))
def test_sha256_integrity(rel_path, expected_hash):
    """Every corpus file must match its expected SHA-256 hash."""
    file_path = SAMPLES_ZST / rel_path
    if not file_path.exists():
        pytest.skip(f"{rel_path} not present")
    actual = _sha256_file(file_path)
    assert actual == expected_hash, (
        f"SHA-256 mismatch for {rel_path}:\n"
        f"  expected: {expected_hash}\n"
        f"  actual:   {actual}"
    )


# ── 5. Valid samples decompress without error ─────────────────────────────────

@pytest.mark.skipif(not ZSTD_AVAILABLE, reason="zstandard not installed")
@pytest.mark.parametrize("filename", EXPECTED_VALID_FILES)
def test_valid_sample_decompresses(filename):
    """Every valid .zst file must decompress without error.

    Uses stream_reader to handle frames without Content_Size in the header
    (some upstream golden-decompression fixtures omit this field).
    """
    path = VALID_DIR / filename
    if not path.exists():
        pytest.skip(f"valid/{filename} not present")
    dctx = zstd.ZstdDecompressor()
    with dctx.stream_reader(path.read_bytes()) as reader:
        data = reader.read()
    assert isinstance(data, bytes), f"decompression of {filename} did not return bytes"


# ── 6. Invalid samples raise ZstdError ────────────────────────────────────────

@pytest.mark.skipif(not ZSTD_AVAILABLE, reason="zstandard not installed")
@pytest.mark.parametrize("filename", EXPECTED_INVALID_FILES)
def test_invalid_sample_raises_error(filename):
    """Every invalid .zst file must raise ZstdError on decompression."""
    path = INVALID_DIR / filename
    if not path.exists():
        pytest.skip(f"invalid/{filename} not present")
    dctx = zstd.ZstdDecompressor()
    with pytest.raises(zstd.ZstdError):
        with dctx.stream_reader(path.read_bytes()) as reader:
            reader.read()


# ── 7. _corpus-manifest.yaml structure ────────────────────────────────────────

def test_corpus_manifest_exists():
    """_corpus-manifest.yaml must exist."""
    assert MANIFEST_PATH.exists(), "_corpus-manifest.yaml must exist in samples/by-format/zst/"


def test_corpus_manifest_valid_count():
    """_corpus-manifest.yaml summary.valid_count must be 8."""
    if not MANIFEST_PATH.exists():
        pytest.skip("manifest not present")
    data = _load_manifest()
    summary = data.get("summary", {})
    assert summary.get("valid_count") == 8, (
        f"Expected valid_count=8, got: {summary.get('valid_count')}"
    )


def test_corpus_manifest_invalid_count():
    """_corpus-manifest.yaml summary.invalid_count must be 3."""
    if not MANIFEST_PATH.exists():
        pytest.skip("manifest not present")
    data = _load_manifest()
    summary = data.get("summary", {})
    assert summary.get("invalid_count") == 3, (
        f"Expected invalid_count=3, got: {summary.get('invalid_count')}"
    )


def test_corpus_manifest_total_count():
    """_corpus-manifest.yaml summary.total_count must be 11."""
    if not MANIFEST_PATH.exists():
        pytest.skip("manifest not present")
    data = _load_manifest()
    summary = data.get("summary", {})
    assert summary.get("total_count") == 11, (
        f"Expected total_count=11, got: {summary.get('total_count')}"
    )


def test_corpus_manifest_gate3_categories_met():
    """_corpus-manifest.yaml summary.gate_3_categories_met must be true."""
    if not MANIFEST_PATH.exists():
        pytest.skip("manifest not present")
    data = _load_manifest()
    summary = data.get("summary", {})
    assert summary.get("gate_3_categories_met") is True, (
        "gate_3_categories_met must be true"
    )


def test_corpus_manifest_valid_samples_all_pass():
    """All valid_samples in manifest must have decompression_test: PASS."""
    if not MANIFEST_PATH.exists():
        pytest.skip("manifest not present")
    data = _load_manifest()
    for sample in data.get("valid_samples", []):
        filename = sample.get("filename")
        result = sample.get("decompression_test")
        assert result == "PASS", (
            f"Expected PASS for {filename}, got: {result}"
        )


def test_corpus_manifest_invalid_samples_all_expected_error():
    """All invalid_samples in manifest must have expected_error: true."""
    if not MANIFEST_PATH.exists():
        pytest.skip("manifest not present")
    data = _load_manifest()
    for sample in data.get("invalid_samples", []):
        filename = sample.get("filename")
        flag = sample.get("expected_error")
        assert flag is True, (
            f"Expected expected_error=true for {filename}, got: {flag}"
        )


# ── 8. _provenance.yaml completeness ──────────────────────────────────────────

def test_provenance_yaml_exists():
    """_provenance.yaml must exist."""
    assert PROVENANCE_PATH.exists(), "_provenance.yaml must exist in samples/by-format/zst/"


def _load_provenance_entries() -> list:
    """Load provenance sample entries from _provenance.yaml.

    The file has a header mapping (format_id, etc.) followed by a YAML list
    of sample entries. We extract entries by finding the first '- sample_id:'
    line and parsing from there as a sequence.
    """
    content = PROVENANCE_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()
    list_start = next(
        (i for i, ln in enumerate(lines) if ln.startswith("- sample_id:")), None
    )
    if list_start is None:
        return []
    list_yaml = "\n".join(lines[list_start:])
    result = yaml.safe_load(list_yaml)
    return result if isinstance(result, list) else []


def test_provenance_all_confirmed():
    """All provenance entries must have provenance_status: confirmed."""
    if not PROVENANCE_PATH.exists():
        pytest.skip("provenance not present")
    entries = _load_provenance_entries()
    assert len(entries) == 11, f"Expected 11 provenance entries, got: {len(entries)}"
    for entry in entries:
        sid = entry.get("sample_id")
        status = entry.get("provenance_status")
        assert status == "confirmed", (
            f"provenance_status not confirmed for {sid}: {status}"
        )


def test_provenance_all_have_sha256():
    """All provenance entries must have a sha256 field."""
    if not PROVENANCE_PATH.exists():
        pytest.skip("provenance not present")
    entries = _load_provenance_entries()
    for entry in entries:
        sid = entry.get("sample_id")
        sha = entry.get("sha256")
        assert sha is not None and sha.startswith("sha256:"), (
            f"Missing or invalid sha256 for {sid}: {sha}"
        )


# ── 9. Gate 3A artifacts still intact ─────────────────────────────────────────

def test_sample_sources_md_still_intact():
    """acquisition-packs/zst/sample-sources.md must still exist after Gate 3B."""
    assert (ACQUISITION_PACK / "sample-sources.md").exists()


def test_registry_zst_entry_exists():
    """ZST must have an entry in format-registry.yaml."""
    entry = _load_zst_registry_entry()
    assert entry is not None, "ZST entry missing from registry"


def test_registry_implementation_authorized_true():
    """implementation_authorized must be true — R20 authorized python_foss_only."""
    entry = _load_zst_registry_entry()
    if entry:
        assert entry.get("implementation_authorized", False) is True, (
            "Expected implementation_authorized=true after R20"
        )


def test_registry_commercial_product_ready_false():
    """commercial_product_ready must remain false."""
    entry = _load_zst_registry_entry()
    if entry:
        assert entry.get("commercial_product_ready", False) is False, (
            "INVARIANT VIOLATED: commercial_product_ready must remain false"
        )


def test_r16_taskcard_exists():
    """ZST-R16-GATE3B-SAMPLE-CORPUS-ACQUISITION.md must still exist."""
    taskcard = REPO_ROOT / "taskcards" / "ZST-R16-GATE3B-SAMPLE-CORPUS-ACQUISITION.md"
    assert taskcard.exists()


def test_gate3_iv_taskcard_exists():
    """ZST-GATE3-IV.md must still exist."""
    taskcard = REPO_ROOT / "taskcards" / "ZST-GATE3-IV.md"
    assert taskcard.exists()


# ── 10. No src/ mutations ──────────────────────────────────────────────────────

def test_zst_python_source_exists():
    """src/python/zst/ must exist — R20 authorized and created python_foss source."""
    assert (REPO_ROOT / "src" / "python" / "zst").exists(), (
        "src/python/zst/ must exist — ZST implementation authorized in R20"
    )


def test_no_zst_net_source():
    """src/net/zst/ must not exist — implementation not authorized."""
    assert not (REPO_ROOT / "src" / "net" / "zst").exists(), (
        "INVARIANT VIOLATED: src/net/zst/ must not exist"
    )


# ── 11. No generated-requirements/ for ZST ────────────────────────────────────

def test_no_zst_generated_requirements():
    """generated-requirements/zst/ must not exist — not at that gate."""
    zst_genreq = REPO_ROOT / "generated-requirements" / "zst"
    assert not zst_genreq.exists(), (
        "INVARIANT VIOLATED: generated-requirements/zst/ must not exist at Gate 3"
    )


# ── 12. Generation script exists ──────────────────────────────────────────────

def test_generation_script_exists():
    """generate_synthetic_zst.py must exist."""
    assert GENERATION_SCRIPT.exists(), (
        "source-materials/generation-scripts/generate_synthetic_zst.py must exist"
    )


def test_generation_script_non_empty():
    """generate_synthetic_zst.py must be non-trivial."""
    if not GENERATION_SCRIPT.exists():
        pytest.skip("script not present")
    content = GENERATION_SCRIPT.read_text(encoding="utf-8")
    assert len(content) > 200, "generation script is suspiciously short"
    assert "zstandard" in content or "zstd" in content, "script must use zstandard"
