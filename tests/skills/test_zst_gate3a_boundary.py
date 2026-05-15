"""
ZST Gate 3A — Source Identification Boundary Tests
Sprint: FORMAT-FACTORY-R15A-ZST-GATE3A-SAMPLE-SOURCE-IDENTIFICATION-SWARM-001

Validates:
1. samples/by-format/zst/ does NOT exist (Gate 3 not passed)
2. acquisition-packs/zst/sample-sources.md exists and is non-empty
3. registry gate_3.status = source_identification_complete (NOT passed/not_started)
4. pack.yaml sample_sources.status = source_identification_complete
5. ZST-R16-GATE3B-SAMPLE-CORPUS-ACQUISITION.md taskcard exists
6. ZST-GATE3-IV.md taskcard exists
7. No _provenance.yaml files exist in samples/by-format/zst/ (corpus not created)
8. implementation_authorized remains false in registry
9. No src/python/zst/ or src/net/zst/ source directories exist
10. Gate 3 is NOT passed in registry
"""
import yaml
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
SAMPLES_ZST = REPO_ROOT / "samples" / "by-format" / "zst"
ACQUISITION_PACK = REPO_ROOT / "acquisition-packs" / "zst"
REGISTRY_PATH = REPO_ROOT / "registry" / "format-registry.yaml"
PACK_YAML = ACQUISITION_PACK / "pack.yaml"
TASKCARDS = REPO_ROOT / "taskcards"


# ── Hard invariant: corpus NOT created ────────────────────────────────────────

def test_samples_zst_directory_does_not_exist():
    """Gate 3 hard invariant: samples/by-format/zst/ must NOT exist in Gate 3A."""
    assert not SAMPLES_ZST.exists(), (
        "INVARIANT VIOLATED: samples/by-format/zst/ must not exist in Gate 3A. "
        "Corpus acquisition is Gate 3B work only."
    )


def test_no_provenance_yaml_in_samples_zst():
    """No _provenance.yaml should exist since corpus has not been acquired."""
    if SAMPLES_ZST.exists():
        provenance_files = list(SAMPLES_ZST.rglob("_provenance.yaml"))
        assert len(provenance_files) == 0, (
            f"Found _provenance.yaml files before Gate 3B: {provenance_files}"
        )


# ── Gate 3A artifact: sample-sources.md ───────────────────────────────────────

def test_sample_sources_md_exists():
    """acquisition-packs/zst/sample-sources.md must exist after Gate 3A."""
    sample_sources = ACQUISITION_PACK / "sample-sources.md"
    assert sample_sources.exists(), (
        "acquisition-packs/zst/sample-sources.md must be created in Gate 3A"
    )


def test_sample_sources_md_non_empty():
    """sample-sources.md must have meaningful content."""
    sample_sources = ACQUISITION_PACK / "sample-sources.md"
    if sample_sources.exists():
        content = sample_sources.read_text(encoding="utf-8")
        assert len(content) > 100, "sample-sources.md is too short to be valid"
        assert "SOURCE-001" in content, "sample-sources.md must list candidate sources"


def test_sample_sources_md_contains_preferred_candidates():
    """sample-sources.md must identify preferred sources."""
    sample_sources = ACQUISITION_PACK / "sample-sources.md"
    if sample_sources.exists():
        content = sample_sources.read_text(encoding="utf-8")
        assert "facebook/zstd" in content, "Must reference facebook/zstd as a source"
        assert "BSD-3" in content or "BSD-3-Clause" in content, "Must note BSD-3 license"


# ── Registry gate_3 state ──────────────────────────────────────────────────────

def _load_zst_registry_entry():
    """Load the ZST entry from format-registry.yaml."""
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    formats = data.get("formats", [])
    for fmt in formats:
        if fmt.get("format_id") == "zst":
            return fmt
    return None


def test_registry_zst_entry_exists():
    """ZST must have an entry in format-registry.yaml."""
    entry = _load_zst_registry_entry()
    assert entry is not None, "ZST entry missing from registry"


def test_registry_gate3_status_not_passed():
    """Gate 3 must NOT be set to passed in registry."""
    entry = _load_zst_registry_entry()
    if entry:
        gates = entry.get("gates", {})
        gate3 = gates.get("gate_3", {})
        status = gate3.get("status", "not_started")
        assert status != "passed", (
            f"INVARIANT VIOLATED: gate_3.status must not be 'passed' in Gate 3A. "
            f"Got: {status}"
        )


def test_registry_gate3_status_is_source_identification_complete():
    """Gate 3 status should be source_identification_complete after R15A."""
    entry = _load_zst_registry_entry()
    if entry:
        gates = entry.get("gates", {})
        gate3 = gates.get("gate_3", {})
        status = gate3.get("status", "")
        assert status == "source_identification_complete", (
            f"Expected gate_3.status = source_identification_complete, got: {status}"
        )


def test_registry_gate3_approved_by_is_null():
    """Gate 3 must not have a human approver set."""
    entry = _load_zst_registry_entry()
    if entry:
        gates = entry.get("gates", {})
        gate3 = gates.get("gate_3", {})
        approved_by = gate3.get("approved_by")
        assert approved_by is None, (
            f"INVARIANT VIOLATED: gate_3.approved_by must be null. Got: {approved_by}"
        )


def test_registry_gate3_source_identification_complete_flag():
    """gate_3.source_identification_complete must be true."""
    entry = _load_zst_registry_entry()
    if entry:
        gates = entry.get("gates", {})
        gate3 = gates.get("gate_3", {})
        flag = gate3.get("source_identification_complete", False)
        assert flag is True, (
            f"gate_3.source_identification_complete must be true after R15A. Got: {flag}"
        )


def test_registry_implementation_authorized_false():
    """implementation_authorized must remain false."""
    entry = _load_zst_registry_entry()
    if entry:
        impl_auth = entry.get("implementation_authorized", False)
        assert impl_auth is False, (
            f"INVARIANT VIOLATED: implementation_authorized must be false. Got: {impl_auth}"
        )


def test_registry_commercial_product_ready_false():
    """commercial_product_ready must remain false."""
    entry = _load_zst_registry_entry()
    if entry:
        ready = entry.get("commercial_product_ready", False)
        assert ready is False, (
            f"INVARIANT VIOLATED: commercial_product_ready must be false. Got: {ready}"
        )


# ── pack.yaml sample_sources state ────────────────────────────────────────────

def _load_pack_yaml():
    with open(PACK_YAML, encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_pack_yaml_sample_sources_status():
    """pack.yaml sample_sources.status must be source_identification_complete."""
    data = _load_pack_yaml()
    stages = data.get("stages", {})
    sample_sources = stages.get("sample_sources", {})
    status = sample_sources.get("status", "")
    assert status == "source_identification_complete", (
        f"Expected sample_sources.status = source_identification_complete, got: {status}"
    )


def test_pack_yaml_corpus_acquisition_status():
    """pack.yaml corpus_acquisition_status must be not_started."""
    data = _load_pack_yaml()
    stages = data.get("stages", {})
    sample_sources = stages.get("sample_sources", {})
    corpus_status = sample_sources.get("corpus_acquisition_status", "not_started")
    assert corpus_status == "not_started", (
        f"corpus_acquisition_status must be not_started. Got: {corpus_status}"
    )


# ── Taskcards ──────────────────────────────────────────────────────────────────

def test_r16_taskcard_exists():
    """ZST-R16-GATE3B-SAMPLE-CORPUS-ACQUISITION.md must exist."""
    taskcard = TASKCARDS / "ZST-R16-GATE3B-SAMPLE-CORPUS-ACQUISITION.md"
    assert taskcard.exists(), (
        "ZST-R16-GATE3B-SAMPLE-CORPUS-ACQUISITION.md must be created in Gate 3A"
    )


def test_gate3_iv_taskcard_exists():
    """ZST-GATE3-IV.md must exist."""
    taskcard = TASKCARDS / "ZST-GATE3-IV.md"
    assert taskcard.exists(), (
        "ZST-GATE3-IV.md must be created in Gate 3A"
    )


def test_r15_taskcard_completed():
    """ZST-R15-GATE3-SAMPLE-SOURCES.md must be marked completed."""
    taskcard = TASKCARDS / "ZST-R15-GATE3-SAMPLE-SOURCES.md"
    if taskcard.exists():
        content = taskcard.read_text(encoding="utf-8")
        assert "status: completed" in content, (
            "ZST-R15-GATE3-SAMPLE-SOURCES.md must have status: completed after R15A"
        )


# ── No src/ mutations ──────────────────────────────────────────────────────────

def test_no_zst_python_source():
    """src/python/zst/ must not exist."""
    zst_src = REPO_ROOT / "src" / "python" / "zst"
    assert not zst_src.exists(), (
        "src/python/zst/ must not exist — ZST implementation not authorized"
    )


def test_no_zst_net_source():
    """src/net/zst/ must not exist."""
    zst_net = REPO_ROOT / "src" / "net" / "zst"
    assert not zst_net.exists(), (
        "src/net/zst/ must not exist — ZST implementation not authorized"
    )
