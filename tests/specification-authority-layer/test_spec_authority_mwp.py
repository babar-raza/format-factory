"""
Tests for the Specification Authority Layer MWP.

Coverage:
  - Source registration and anti-bypass
  - Vault ingest (fixture mode)
  - Spec parsing and normalization
  - Indexing
  - Digest and staleness detection
  - Requirement extraction
  - Requirement verification (anti-bypass)
  - Context pack building and verification
  - Usage ledger append-only
  - Pilot lifecycle: ZST, Netpbm, DIF
"""
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure repo root and spec-authority-layer dir are on sys.path
REPO_ROOT = Path(__file__).parent.parent.parent
SAL_DIR = REPO_ROOT / "tools" / "specification-authority-layer"
sys.path.insert(0, str(SAL_DIR))
sys.path.insert(0, str(REPO_ROOT))

from spec_source_registry import (
    register_source, get_source, is_source_registered, validate_citation, load_registry
)
from spec_vault_ingest import (
    ingest_text_fixture, get_snapshot_meta, verify_snapshot_integrity
)
from spec_parser import parse_spec_from_text
from spec_normalizer import normalize_spec, load_normalized_artifact
from spec_indexer import build_index, search_index
from spec_digestor import compute_digest, check_staleness, load_digest
from requirement_extractor import extract_requirements
from spec_verifier import verify_requirements, check_anti_bypass
from requirement_graph import build_requirement_graph
from context_pack_builder import build_context_pack, verify_context_pack
from spec_governance_runtime import (
    check_citation_allowed, check_context_pack_use_allowed,
    check_memory_only_claim, load_usage_ledger
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

ZST_FIXTURE = """
# Zstandard Compression Format

## Overview

The Zstandard (zstd) format provides lossless compression.
Files MUST begin with a magic number of 0xFD2FB528.
The decompressor SHALL handle multiple frames.

## Frame Format

Each frame SHALL contain a Frame Header followed by Data Blocks.
The Frame Header MUST include FHD (Frame Header Descriptor).

## Compression Levels

The compressor MAY operate at levels 1-22.
Default level SHOULD be 3 for balanced performance.
"""

NETPBM_FIXTURE = """
# Netpbm Format Family

## PBM — Portable Bitmap Format

PBM files MUST start with a magic number (P1 or P4).
Width and height MUST be positive integers.
Each pixel value SHALL be 0 (white) or 1 (black).

## PGM — Portable Graymap Format

PGM files MUST start with P2 (ASCII) or P5 (binary).
Maxval MUST be between 1 and 65535.

## PPM — Portable Pixmap Format

PPM files MUST start with P3 (ASCII) or P6 (binary).
Each pixel SHALL have three components: Red, Green, Blue.
"""

DIF_FIXTURE = """
# DIF (Data Interchange Format)

## Record Structure

DIF files MUST begin with a TABLE header record.
Each data record SHALL contain a type indicator and value.

## Data Types

Values MUST be enclosed in double quotes for string data.
Numeric data SHOULD be represented without quotes.
"""


@pytest.fixture
def tmpdir_str():
    with tempfile.TemporaryDirectory() as d:
        yield d


# ── Source Registration Tests ─────────────────────────────────────────────────

def test_register_source(tmpdir_str):
    """Source registration appends to registry."""
    src = register_source(
        source_id="ZST-SPEC-001",
        format_id="zst",
        title="Zstandard Format Specification",
        source_type="public_spec",
        url_or_path="https://facebook.github.io/zstd/zstd_manual.html",
        fetch_policy="deferred_local_fixture",
        registry_dir=tmpdir_str,
    )
    assert src.source_id == "ZST-SPEC-001"
    assert src.format_id == "zst"
    assert is_source_registered("ZST-SPEC-001", tmpdir_str)


def test_source_not_registered(tmpdir_str):
    """Unknown source returns not-registered."""
    assert not is_source_registered("NONEXISTENT-001", tmpdir_str)


def test_validate_citation_rejects_unregistered(tmpdir_str):
    """Anti-bypass: citation of unregistered source is rejected."""
    result = validate_citation("FAKE-SOURCE-001", tmpdir_str)
    assert result["valid"] is False
    assert "not found" in result["reason"].lower()


def test_validate_citation_rejects_empty(tmpdir_str):
    """Anti-bypass: empty source_id is rejected."""
    result = validate_citation("", tmpdir_str)
    assert result["valid"] is False


def test_validate_citation_allows_registered(tmpdir_str):
    """Registered source is allowed."""
    register_source(
        "NETPBM-SPEC-001", "netpbm", "Netpbm Spec", "public_domain_spec",
        "https://netpbm.sourceforge.net/doc/pbm.html", registry_dir=tmpdir_str
    )
    result = validate_citation("NETPBM-SPEC-001", tmpdir_str)
    assert result["valid"] is True


# ── Vault Ingest Tests ────────────────────────────────────────────────────────

def test_ingest_text_fixture(tmpdir_str):
    """Fixture ingest stores content with SHA-256."""
    result = ingest_text_fixture(
        source_id="ZST-SPEC-001",
        content=ZST_FIXTURE,
        label="zstd-spec",
        vault_dir=tmpdir_str,
    )
    assert result["status"] == "INGESTED_FROM_FIXTURE"
    assert len(result["sha256"]) == 64
    assert result["fetch_note"] == "FETCH_DEFERRED_WITH_LOCAL_FIXTURE"
    assert Path(result["vault_path"]).exists()


def test_snapshot_meta_available_after_ingest(tmpdir_str):
    """Snapshot metadata is retrievable after ingest."""
    ingest_text_fixture("NETPBM-SPEC-001", NETPBM_FIXTURE, vault_dir=tmpdir_str)
    meta = get_snapshot_meta("NETPBM-SPEC-001", tmpdir_str)
    assert meta is not None
    assert meta["source_id"] == "NETPBM-SPEC-001"


def test_snapshot_integrity_check(tmpdir_str):
    """Snapshot integrity check passes for freshly ingested fixture."""
    result = ingest_text_fixture("DIF-SPEC-001", DIF_FIXTURE, vault_dir=tmpdir_str)
    integrity = verify_snapshot_integrity("DIF-SPEC-001", tmpdir_str)
    assert integrity["status"] == "INTEGRITY_OK"
    assert integrity["sha256"] == result["sha256"]


# ── Parse Tests ───────────────────────────────────────────────────────────────

def test_parse_markdown_spec():
    """Markdown spec produces sections with headings."""
    sha256 = hashlib.sha256(ZST_FIXTURE.encode()).hexdigest()
    parsed = parse_spec_from_text("ZST-SPEC-001", sha256, "zst", ZST_FIXTURE)
    assert parsed.source_id == "ZST-SPEC-001"
    assert len(parsed.sections) >= 3
    assert parsed.parse_method == "markdown"
    headings = [s.heading for s in parsed.sections]
    assert any("Zstandard" in h for h in headings)


def test_parse_netpbm_spec():
    """Netpbm spec sections include PBM, PGM, PPM."""
    sha256 = hashlib.sha256(NETPBM_FIXTURE.encode()).hexdigest()
    parsed = parse_spec_from_text("NETPBM-SPEC-001", sha256, "netpbm", NETPBM_FIXTURE)
    headings = [s.heading for s in parsed.sections]
    assert any("PBM" in h for h in headings)
    assert any("PGM" in h for h in headings)


# ── Normalize Tests ───────────────────────────────────────────────────────────

def test_normalize_produces_artifact(tmpdir_str):
    """Normalization stores artifact JSON file."""
    sha256 = hashlib.sha256(ZST_FIXTURE.encode()).hexdigest()
    parsed = parse_spec_from_text("ZST-SPEC-001", sha256, "zst", ZST_FIXTURE)
    normalized = normalize_spec(parsed, artifacts_dir=tmpdir_str)
    assert normalized.sections_normalized > 0
    assert Path(normalized.artifact_path).exists()
    assert len(normalized.canonical_headings) > 0


# ── Index Tests ───────────────────────────────────────────────────────────────

def test_index_built_from_normalized_artifact(tmpdir_str):
    """Index build produces term lookup."""
    sha256 = hashlib.sha256(NETPBM_FIXTURE.encode()).hexdigest()
    parsed = parse_spec_from_text("NETPBM-SPEC-001", sha256, "netpbm", NETPBM_FIXTURE)
    normalize_spec(parsed, artifacts_dir=tmpdir_str)
    artifact = load_normalized_artifact("NETPBM-SPEC-001", tmpdir_str)
    idx = build_index("NETPBM-SPEC-001", sha256, "netpbm", artifact, artifacts_dir=tmpdir_str)
    assert idx.term_count > 0
    assert idx.section_count > 0


def test_search_index(tmpdir_str):
    """Index search returns results without error."""
    sha256 = hashlib.sha256(NETPBM_FIXTURE.encode()).hexdigest()
    parsed = parse_spec_from_text("NETPBM-SPEC-001", sha256, "netpbm", NETPBM_FIXTURE)
    normalize_spec(parsed, artifacts_dir=tmpdir_str)
    artifact = load_normalized_artifact("NETPBM-SPEC-001", tmpdir_str)
    build_index("NETPBM-SPEC-001", sha256, "netpbm", artifact, artifacts_dir=tmpdir_str)
    results = search_index("NETPBM-SPEC-001", "pixel bitmap", tmpdir_str)
    assert isinstance(results, list)


# ── Digest and Staleness Tests ────────────────────────────────────────────────

def test_digest_computed(tmpdir_str):
    """Digest computation produces deterministic result."""
    sha256 = hashlib.sha256(ZST_FIXTURE.encode()).hexdigest()
    parsed = parse_spec_from_text("ZST-SPEC-001", sha256, "zst", ZST_FIXTURE)
    normalize_spec(parsed, artifacts_dir=tmpdir_str)
    artifact = load_normalized_artifact("ZST-SPEC-001", tmpdir_str)
    digest = compute_digest("ZST-SPEC-001", sha256, artifact, artifacts_dir=tmpdir_str)
    assert len(digest.content_digest) == 64
    assert digest.sha256_snapshot == sha256

    digest2 = compute_digest("ZST-SPEC-001", sha256, artifact, artifacts_dir=tmpdir_str)
    assert digest.content_digest == digest2.content_digest


def test_staleness_detection(tmpdir_str):
    """Changed SHA triggers stale detection."""
    sha256 = hashlib.sha256(ZST_FIXTURE.encode()).hexdigest()
    parsed = parse_spec_from_text("ZST-SPEC-001", sha256, "zst", ZST_FIXTURE)
    normalize_spec(parsed, artifacts_dir=tmpdir_str)
    artifact = load_normalized_artifact("ZST-SPEC-001", tmpdir_str)
    compute_digest("ZST-SPEC-001", sha256, artifact, artifacts_dir=tmpdir_str)

    result = check_staleness("ZST-SPEC-001", sha256, tmpdir_str)
    assert result["stale"] is False

    result2 = check_staleness("ZST-SPEC-001", "deadbeef" * 8, tmpdir_str)
    assert result2["stale"] is True


# ── Requirement Extraction Tests ──────────────────────────────────────────────

def test_extract_requirements_from_spec(tmpdir_str):
    """Requirements with MUST/SHALL/SHOULD keywords are extracted."""
    sha256 = hashlib.sha256(ZST_FIXTURE.encode()).hexdigest()
    parsed = parse_spec_from_text("ZST-SPEC-001", sha256, "zst", ZST_FIXTURE)
    normalize_spec(parsed, artifacts_dir=tmpdir_str)
    artifact = load_normalized_artifact("ZST-SPEC-001", tmpdir_str)
    reqs = extract_requirements("ZST-SPEC-001", "zst", artifact, artifacts_dir=tmpdir_str)
    assert len(reqs) >= 3
    keywords = [r.keyword for r in reqs]
    assert any(k.upper() in ("MUST", "SHALL", "SHOULD", "MAY") for k in keywords)


# ── Verifier Anti-Bypass Tests ────────────────────────────────────────────────

def test_anti_bypass_rejects_no_source_refs():
    """Claim with no source_refs is rejected."""
    result = check_anti_bypass({"source_refs": []})
    assert result["pass"] is False
    assert len(result["violations"]) > 0


def test_anti_bypass_rejects_ai_summary_only():
    """Claim with raw_ai_summary_only=True is rejected."""
    result = check_anti_bypass({"source_refs": ["ZST-001"], "raw_ai_summary_only": True})
    assert result["pass"] is False


def test_anti_bypass_allows_valid_claim():
    """Claim with source_refs and no AI flag is allowed."""
    result = check_anti_bypass({"source_refs": ["ZST-SPEC-001"]})
    assert result["pass"] is True


def test_verifier_rejects_no_source_id():
    """Requirement without source_id is anti-bypass rejected."""
    reqs = [{"req_id": "REQ-001", "source_id": "", "text_fragment": "MUST have valid input."}]
    results = verify_requirements(reqs)
    assert results[0].status == "ANTI_BYPASS_REJECTED"


# ── Context Pack Tests ────────────────────────────────────────────────────────

def test_context_pack_built_deterministically(tmpdir_str):
    """Context pack has manifest.sha256 and is deterministic."""
    sources = [
        {"source_id": "ZST-SPEC-001", "title": "ZST Spec", "sha256": "abc123",
         "sections_count": 5, "source_type": "public_spec"},
    ]
    pack1 = build_context_pack("zst", sources, output_dir=tmpdir_str)
    pack2 = build_context_pack("zst", sources, output_dir=tmpdir_str)
    assert pack1.manifest_sha256 == pack2.manifest_sha256
    assert pack1.context_pack_id == pack2.context_pack_id


def test_context_pack_verify_passes(tmpdir_str):
    """Context pack verify passes for valid pack."""
    sources = [
        {"source_id": "ZST-SPEC-001", "title": "ZST Spec", "sha256": "abc123",
         "sections_count": 5, "source_type": "public_spec"},
    ]
    pack = build_context_pack("zst", sources, output_dir=tmpdir_str)
    result = verify_context_pack(pack.output_path)
    assert result["valid"] is True
    assert result["manifest_sha256"] == pack.manifest_sha256


def test_context_pack_verify_rejects_missing_sha(tmpdir_str):
    """Anti-bypass: context pack without manifest.sha256 is rejected."""
    bad_pack = {"format_id": "zst", "context_pack_id": "CP-ZST-001",
                "manifest": {}, "included_sources": []}
    bad_path = Path(tmpdir_str) / "bad-pack.json"
    with open(bad_path, "w") as f:
        json.dump(bad_pack, f)
    result = verify_context_pack(str(bad_path))
    assert result["valid"] is False
    assert "manifest.sha256" in result["reason"]


# ── Usage Ledger Tests ────────────────────────────────────────────────────────

def test_usage_ledger_appends(tmpdir_str):
    """Usage ledger grows with each action."""
    ledger_path = str(Path(tmpdir_str) / "ledger.jsonl")
    check_citation_allowed("ZST-SPEC-001", "zst", ledger_path=ledger_path)
    check_citation_allowed("", "zst", ledger_path=ledger_path)
    entries = load_usage_ledger(ledger_path)
    assert len(entries) == 2
    outcomes = [e["outcome"] for e in entries]
    assert "REJECTED" in outcomes


def test_memory_only_claim_rejected(tmpdir_str):
    """Memory-only claim is rejected and logged."""
    ledger_path = str(Path(tmpdir_str) / "ledger.jsonl")
    result = check_memory_only_claim({}, "zst", ledger_path=ledger_path)
    assert result["allowed"] is False
    entries = load_usage_ledger(ledger_path)
    assert len(entries) >= 1
    assert entries[-1]["outcome"] == "REJECTED"


# ── Pilot Lifecycle Tests ─────────────────────────────────────────────────────

def _run_pilot(source_id: str, format_id: str, content: str, tmpdir: str) -> dict:
    """Full pilot lifecycle."""
    src = register_source(source_id, format_id, f"{format_id} spec", "public_spec",
                          f"local://{source_id}", fetch_policy="deferred_local_fixture",
                          registry_dir=tmpdir)
    ingest_result = ingest_text_fixture(source_id, content, vault_dir=tmpdir)
    sha256 = ingest_result["sha256"]
    parsed = parse_spec_from_text(source_id, sha256, format_id, content)
    normalized = normalize_spec(parsed, artifacts_dir=tmpdir)
    artifact = load_normalized_artifact(source_id, tmpdir)
    idx = build_index(source_id, sha256, format_id, artifact, artifacts_dir=tmpdir)
    digest = compute_digest(source_id, sha256, artifact, artifacts_dir=tmpdir)
    reqs = extract_requirements(source_id, format_id, artifact, artifacts_dir=tmpdir)
    ver_results = verify_requirements(
        [r.to_dict() for r in reqs],
        normalized_artifact=artifact,
        registered_source_ids=[source_id],
    )
    graph = build_requirement_graph(
        source_id, format_id,
        [r.to_dict() for r in reqs],
        [vr.to_dict() for vr in ver_results],
        artifacts_dir=tmpdir,
    )
    source_records = [{
        "source_id": source_id, "title": f"{format_id} spec", "sha256": sha256,
        "sections_count": normalized.sections_normalized, "source_type": "public_spec"
    }]
    pack = build_context_pack(format_id, source_records, output_dir=tmpdir)
    return {
        "sections_normalized": normalized.sections_normalized,
        "requirements_extracted": len(reqs),
        "context_pack_id": pack.context_pack_id,
        "manifest_sha256": pack.manifest_sha256,
    }


def test_pilot_zst(tmpdir_str):
    """ZST pilot: full lifecycle passes."""
    result = _run_pilot("ZST-SPEC-001", "zst", ZST_FIXTURE, tmpdir_str)
    assert result["sections_normalized"] >= 3
    assert result["requirements_extracted"] >= 3
    assert result["manifest_sha256"]
    assert result["context_pack_id"].startswith("CP-ZST-")


def test_pilot_netpbm(tmpdir_str):
    """Netpbm pilot: full lifecycle passes."""
    result = _run_pilot("NETPBM-SPEC-001", "netpbm", NETPBM_FIXTURE, tmpdir_str)
    assert result["sections_normalized"] >= 3
    assert result["requirements_extracted"] >= 3
    assert result["context_pack_id"].startswith("CP-NETPBM-")


def test_pilot_dif(tmpdir_str):
    """DIF pilot: full lifecycle passes."""
    result = _run_pilot("DIF-SPEC-001", "dif", DIF_FIXTURE, tmpdir_str)
    assert result["sections_normalized"] >= 2
    assert result["requirements_extracted"] >= 2
    assert result["context_pack_id"].startswith("CP-DIF-")
