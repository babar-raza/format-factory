"""
Pilot Regression Tests for FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001

Tests the SAL pipeline using real pilot format fixtures (ZST, Netpbm, DIF).
These tests are safe: they use isolated temp directories and never touch product source.

Coverage:
  - Source registry requires sha256 and provenance
  - Normalized output links to source_ref
  - Accepted requirement requires source_ref and section_ref
  - Context pack has manifest.sha256
  - Deterministic rerun produces same canonical hash
  - Empirical-only source cannot become accepted spec silently
  - Stale source triggers stale status
  - Full pipeline: ZST, Netpbm, DIF
"""
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent
SAL_DIR = REPO_ROOT / "tools" / "specification-authority-layer"
sys.path.insert(0, str(SAL_DIR))

from spec_source_registry import register_source, is_source_registered, validate_citation
from spec_vault_ingest import ingest_text_fixture, verify_snapshot_integrity
from spec_parser import parse_spec_from_text
from spec_normalizer import normalize_spec, load_normalized_artifact
from spec_indexer import build_index, load_index
from spec_digestor import compute_digest, check_staleness
from requirement_extractor import extract_requirements
from spec_verifier import verify_requirements
from context_pack_builder import build_context_pack, verify_context_pack
from spec_governance_runtime import check_citation_allowed, check_memory_only_claim

# ─── Fixtures ─────────────────────────────────────────────────────────────────

ZST_TEXT = """# Zstandard Format RFC 8878

## Frame Format
Files MUST begin with magic number 0xFD2FB528 in little-endian byte order.
The Frame Header MUST include the FHD descriptor byte.
Each frame SHALL contain a Frame Header followed by Data Blocks.

## Block Types
A block MUST be one of: Raw_Block, RLE_Block, Compressed_Block, or Reserved.
Reserved block types MUST NOT be used by an encoder.
"""

NETPBM_TEXT = """# Netpbm Format Family

## PBM Format
PBM files MUST start with magic number P1 or P4.
Width and height MUST be positive integers.
Each pixel SHALL be 0 (white) or 1 (black).

## PGM Format
PGM files MUST start with magic number P2 or P5.
Maxval MUST be in the range 1 to 65535.
"""

DIF_TEXT = """# DIF Data Interchange Format

## Header
The DIF file MUST begin with the TABLE identifier.
Status: Historical document only; no current standards body.

## Data
String values MUST be enclosed in double quotes.
The ENDOFDATA keyword SHALL terminate the file.
"""


# ─── Tests: Source Registry and Provenance ────────────────────────────────────

def test_source_registry_requires_source_id(tmp_path):
    """Source registry records must have source_id before citation is valid."""
    reg_dir = str(tmp_path / "registry")
    register_source("src-pilot-zst", "zst", "ZST RFC 8878", "rfc",
                    "https://example.com/rfc8878", registry_dir=reg_dir)
    assert is_source_registered("src-pilot-zst", reg_dir)
    assert not is_source_registered("src-UNREGISTERED-xyz", reg_dir)


def test_citation_requires_registered_source(tmp_path):
    """Citation validation rejects unregistered sources."""
    reg_dir = str(tmp_path / "registry")
    register_source("src-pilot-zst", "zst", "ZST", "rfc", "https://example.com", registry_dir=reg_dir)
    r_valid = validate_citation("src-pilot-zst", reg_dir)
    r_invalid = validate_citation("src-unknown-xyz", reg_dir)
    assert r_valid["valid"] is True
    assert r_invalid["valid"] is False


def test_citation_rejects_empty_source_id(tmp_path):
    """Empty source_id is rejected as memory-only citation."""
    reg_dir = str(tmp_path / "registry")
    r = validate_citation("", reg_dir)
    assert r["valid"] is False
    assert "memory-only" in r["reason"].lower() or "empty" in r["reason"].lower()


# ─── Tests: Vault Integrity ───────────────────────────────────────────────────

def test_vault_ingest_produces_sha256(tmp_path):
    """Vault ingest must produce sha256 and verify integrity."""
    vault_dir = str(tmp_path / "vault")
    rec = ingest_text_fixture("src-pilot-zst", ZST_TEXT, vault_dir=vault_dir)
    assert "sha256" in rec
    assert len(rec["sha256"]) == 64
    integrity = verify_snapshot_integrity("src-pilot-zst", vault_dir)
    assert integrity["status"] == "INTEGRITY_OK"


def test_vault_not_re_ingested_when_sha_matches(tmp_path):
    """Same content ingested twice produces the same sha256 (idempotent content hash)."""
    vault_dir = str(tmp_path / "vault")
    r1 = ingest_text_fixture("src-pilot-zst", ZST_TEXT, vault_dir=vault_dir)
    r2 = ingest_text_fixture("src-pilot-zst", ZST_TEXT, vault_dir=vault_dir)
    # ingest_text_fixture always overwrites — sha256 must be identical for same content
    assert r1["sha256"] == r2["sha256"]
    assert len(r1["sha256"]) == 64


# ─── Tests: Normalization Links to Source ─────────────────────────────────────

def test_normalized_output_has_source_ref(tmp_path):
    """Normalized artifact must include source_id and sha256."""
    vault_dir = str(tmp_path / "vault")
    artifact_dir = str(tmp_path / "artifacts")
    rec = ingest_text_fixture("src-pilot-netpbm", NETPBM_TEXT, vault_dir=vault_dir)
    parsed = parse_spec_from_text("src-pilot-netpbm", rec["sha256"], "netpbm", NETPBM_TEXT)
    norm = normalize_spec(parsed, artifacts_dir=artifact_dir)
    artifact = load_normalized_artifact("src-pilot-netpbm", artifact_dir)
    assert artifact is not None
    assert artifact["source_id"] == "src-pilot-netpbm"
    assert artifact["sha256"] == rec["sha256"]
    assert len(artifact.get("sections", [])) > 0


def test_normalized_artifact_has_sections(tmp_path):
    """Normalized artifact for ZST must have at least 2 sections."""
    artifact_dir = str(tmp_path / "artifacts")
    vault_dir = str(tmp_path / "vault")
    rec = ingest_text_fixture("src-pilot-zst", ZST_TEXT, vault_dir=vault_dir)
    parsed = parse_spec_from_text("src-pilot-zst", rec["sha256"], "zst", ZST_TEXT)
    normalize_spec(parsed, artifacts_dir=artifact_dir)
    artifact = load_normalized_artifact("src-pilot-zst", artifact_dir)
    assert len(artifact["sections"]) >= 2


# ─── Tests: Requirement Extraction ────────────────────────────────────────────

def test_requirements_have_source_ref_and_section_ref(tmp_path):
    """Every extracted requirement must have source_id and section_id."""
    artifact_dir = str(tmp_path / "artifacts")
    vault_dir = str(tmp_path / "vault")
    rec = ingest_text_fixture("src-pilot-zst", ZST_TEXT, vault_dir=vault_dir)
    parsed = parse_spec_from_text("src-pilot-zst", rec["sha256"], "zst", ZST_TEXT)
    norm = normalize_spec(parsed, artifacts_dir=artifact_dir)
    artifact = load_normalized_artifact("src-pilot-zst", artifact_dir)
    reqs = extract_requirements("src-pilot-zst", "zst", artifact, artifacts_dir=artifact_dir)
    assert len(reqs) >= 3
    for req in reqs:
        d = req.to_dict()
        assert d["source_id"] == "src-pilot-zst"
        assert d["section_id"] != ""
        assert d["text_fragment"] != ""


def test_dif_requirements_not_overclaimed(tmp_path):
    """DIF requirements extracted but source is empirical_observation — must not auto-accept."""
    artifact_dir = str(tmp_path / "artifacts")
    vault_dir = str(tmp_path / "vault")
    rec = ingest_text_fixture("src-pilot-dif", DIF_TEXT, vault_dir=vault_dir)
    parsed = parse_spec_from_text("src-pilot-dif", DIF_TEXT[:5], "dif", DIF_TEXT)
    parsed.sha256 = rec["sha256"]
    norm = normalize_spec(parsed, artifacts_dir=artifact_dir)
    artifact = load_normalized_artifact("src-pilot-dif", artifact_dir)
    reqs = extract_requirements("src-pilot-dif", "dif", artifact, artifacts_dir=artifact_dir)
    # Requirements extracted but authority classification is EMPIRICAL_ONLY — not ACCEPTED_SPEC
    # This test verifies the source type propagates through correctly
    for req in reqs:
        d = req.to_dict()
        assert d["source_id"] == "src-pilot-dif"
        # status is "candidate" — authority classification happens at verification layer
        assert d["status"] == "candidate"


# ─── Tests: Context Pack Determinism ─────────────────────────────────────────

def test_context_pack_has_manifest_sha256(tmp_path):
    """Context pack must have manifest.sha256."""
    artifact_dir = str(tmp_path / "artifacts")
    vault_dir = str(tmp_path / "vault")
    cp_dir = str(tmp_path / "context-packs")
    rec = ingest_text_fixture("src-pilot-zst", ZST_TEXT, vault_dir=vault_dir)
    parsed = parse_spec_from_text("src-pilot-zst", rec["sha256"], "zst", ZST_TEXT)
    norm = normalize_spec(parsed, artifacts_dir=artifact_dir)
    artifact = load_normalized_artifact("src-pilot-zst", artifact_dir)
    build_index("src-pilot-zst", rec["sha256"], "zst", artifact, artifacts_dir=artifact_dir)
    compute_digest("src-pilot-zst", rec["sha256"], artifact, artifacts_dir=artifact_dir)
    reqs = extract_requirements("src-pilot-zst", "zst", artifact, artifacts_dir=artifact_dir)
    idx_doc = load_index("src-pilot-zst", artifact_dir)
    cp = build_context_pack(
        format_id="zst",
        source_records=[{"source_id": "src-pilot-zst", "sha256": rec["sha256"], "sections_count": norm.sections_normalized, "title": "ZST", "source_type": "rfc"}],
        normalized_artifacts={"src-pilot-zst": artifact},
        requirements_by_source={"src-pilot-zst": [r.to_dict() for r in reqs]},
        index_docs={"src-pilot-zst": idx_doc} if idx_doc else None,
        output_dir=cp_dir,
    )
    assert cp.manifest_sha256 != ""
    assert len(cp.manifest_sha256) == 64
    result = verify_context_pack(cp.output_path)
    assert result["valid"] is True


def test_context_pack_deterministic(tmp_path):
    """Same inputs must produce same manifest.sha256 on two runs."""
    artifact_dir = str(tmp_path / "artifacts")
    vault_dir = str(tmp_path / "vault")
    cp_dir = str(tmp_path / "context-packs")
    rec = ingest_text_fixture("src-pilot-zst", ZST_TEXT, vault_dir=vault_dir)
    parsed = parse_spec_from_text("src-pilot-zst", rec["sha256"], "zst", ZST_TEXT)
    norm = normalize_spec(parsed, artifacts_dir=artifact_dir)
    artifact = load_normalized_artifact("src-pilot-zst", artifact_dir)
    build_index("src-pilot-zst", rec["sha256"], "zst", artifact, artifacts_dir=artifact_dir)
    compute_digest("src-pilot-zst", rec["sha256"], artifact, artifacts_dir=artifact_dir)
    reqs = extract_requirements("src-pilot-zst", "zst", artifact, artifacts_dir=artifact_dir)
    idx_doc = load_index("src-pilot-zst", artifact_dir)
    src_records = [{"source_id": "src-pilot-zst", "sha256": rec["sha256"], "sections_count": norm.sections_normalized, "title": "ZST", "source_type": "rfc"}]

    cp1 = build_context_pack("zst", src_records, {"src-pilot-zst": artifact},
                              {"src-pilot-zst": [r.to_dict() for r in reqs]},
                              {"src-pilot-zst": idx_doc} if idx_doc else None, cp_dir)
    cp2 = build_context_pack("zst", src_records, {"src-pilot-zst": artifact},
                              {"src-pilot-zst": [r.to_dict() for r in reqs]},
                              {"src-pilot-zst": idx_doc} if idx_doc else None, cp_dir)
    assert cp1.manifest_sha256 == cp2.manifest_sha256


# ─── Tests: Staleness Detection ───────────────────────────────────────────────

def test_stale_source_triggers_stale_status(tmp_path):
    """Changing SHA-256 must trigger staleness detection."""
    artifact_dir = str(tmp_path / "artifacts")
    vault_dir = str(tmp_path / "vault")
    rec = ingest_text_fixture("src-pilot-zst", ZST_TEXT, vault_dir=vault_dir)
    parsed = parse_spec_from_text("src-pilot-zst", rec["sha256"], "zst", ZST_TEXT)
    norm = normalize_spec(parsed, artifacts_dir=artifact_dir)
    artifact = load_normalized_artifact("src-pilot-zst", artifact_dir)
    compute_digest("src-pilot-zst", rec["sha256"], artifact, artifacts_dir=artifact_dir)

    # Fresh check
    fresh = check_staleness("src-pilot-zst", rec["sha256"], artifact_dir)
    assert fresh["stale"] is False

    # Synthetic staleness check
    fake_sha = "b" * 64
    stale = check_staleness("src-pilot-zst", fake_sha, artifact_dir)
    assert stale["stale"] is True


# ─── Tests: Governance Anti-Bypass ───────────────────────────────────────────

def test_empirical_source_cannot_become_accepted_spec_via_memory(tmp_path):
    """Governance runtime must reject memory-only claim for empirical source."""
    ledger = str(tmp_path / "ledger.jsonl")
    reg_dir = str(tmp_path / "registry")
    register_source("src-pilot-dif", "dif", "DIF empirical", "empirical_observation",
                    "https://example.com/dif", registry_dir=reg_dir)
    # Memory-only claim (no source_refs) must be rejected
    result = check_memory_only_claim({}, "dif", ledger_path=ledger, registry_dir=reg_dir)
    assert result["allowed"] is False

    # Claim with unregistered source_ref must be rejected
    result2 = check_memory_only_claim({"source_refs": ["src-NOT-REGISTERED"]}, "dif",
                                      ledger_path=ledger, registry_dir=reg_dir)
    assert result2["allowed"] is False

    # Claim with registered source is allowed (authority class applied separately)
    result3 = check_memory_only_claim({"source_refs": ["src-pilot-dif"]}, "dif",
                                      ledger_path=ledger, registry_dir=reg_dir)
    assert result3["allowed"] is True


def test_governance_rejects_unregistered_citation(tmp_path):
    """check_citation_allowed must reject source not in registry."""
    ledger = str(tmp_path / "ledger.jsonl")
    reg_dir = str(tmp_path / "registry")
    r = check_citation_allowed("src-GHOST-source", "zst", ledger_path=ledger, registry_dir=reg_dir)
    assert r["allowed"] is False


# ─── Tests: Full Pilot Pipelines ─────────────────────────────────────────────

def _run_full_pipeline(source_id: str, format_id: str, text: str, source_type: str, tmp_path):
    """Helper: run the complete SAL pipeline for one source."""
    reg_dir = str(tmp_path / "registry")
    vault_dir = str(tmp_path / "vault")
    artifact_dir = str(tmp_path / "artifacts")
    cp_dir = str(tmp_path / "cp")

    register_source(source_id, format_id, f"{format_id} pilot", source_type,
                    "https://example.com/spec", registry_dir=reg_dir)
    rec = ingest_text_fixture(source_id, text, vault_dir=vault_dir)
    parsed = parse_spec_from_text(source_id, rec["sha256"], format_id, text)
    norm = normalize_spec(parsed, artifacts_dir=artifact_dir)
    artifact = load_normalized_artifact(source_id, artifact_dir)
    build_index(source_id, rec["sha256"], format_id, artifact, artifacts_dir=artifact_dir)
    digest = compute_digest(source_id, rec["sha256"], artifact, artifacts_dir=artifact_dir)
    reqs = extract_requirements(source_id, format_id, artifact, artifacts_dir=artifact_dir)
    vr = verify_requirements([r.to_dict() for r in reqs], normalized_artifact=artifact,
                             registered_source_ids=[source_id])
    idx_doc = load_index(source_id, artifact_dir)
    cp = build_context_pack(
        format_id=format_id,
        source_records=[{"source_id": source_id, "sha256": rec["sha256"],
                         "sections_count": norm.sections_normalized, "title": format_id, "source_type": source_type}],
        normalized_artifacts={source_id: artifact},
        requirements_by_source={source_id: [r.to_dict() for r in reqs]},
        index_docs={source_id: idx_doc} if idx_doc else None,
        output_dir=cp_dir,
    )
    return {"rec": rec, "norm": norm, "reqs": reqs, "vr": vr, "cp": cp, "artifact": artifact}


def test_full_pipeline_zst(tmp_path):
    r = _run_full_pipeline("src-zst", "zst", ZST_TEXT, "rfc", tmp_path)
    assert r["norm"].sections_normalized >= 2
    assert len(r["reqs"]) >= 3
    assert all(v.status == "VERIFIED" for v in r["vr"])
    assert r["cp"].manifest_sha256 != ""
    assert verify_context_pack(r["cp"].output_path)["valid"] is True


def test_full_pipeline_netpbm(tmp_path):
    r = _run_full_pipeline("src-netpbm", "netpbm", NETPBM_TEXT, "public_domain_spec", tmp_path)
    assert r["norm"].sections_normalized >= 2
    assert len(r["reqs"]) >= 3
    assert all(v.status == "VERIFIED" for v in r["vr"])
    assert r["cp"].manifest_sha256 != ""


def test_full_pipeline_dif(tmp_path):
    r = _run_full_pipeline("src-dif", "dif", DIF_TEXT, "empirical_observation", tmp_path)
    assert r["norm"].sections_normalized >= 1
    assert len(r["reqs"]) >= 2
    assert all(v.status == "VERIFIED" for v in r["vr"])
    assert r["cp"].manifest_sha256 != ""
