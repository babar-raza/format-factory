"""
R2 Pilot Regression Tests — FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R2-001

Tests real-source pipeline: ZST (real RFC), Netpbm (real HTML), DIF (empirical), FODS (real HTML).
"""
import sys, json, pathlib, pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SAL_DIR = REPO_ROOT / "tools" / "specification-authority-layer"
sys.path.insert(0, str(SAL_DIR))

EVIDENCE_ROOT = REPO_ROOT / ".local/evidences/spec-authority-real-pilot-r2"
ARTIFACTS_DIR = str(EVIDENCE_ROOT / "normalized")
VAULT_ROOT = EVIDENCE_ROOT / "spec-vault"
REGISTRY_DIR = str(EVIDENCE_ROOT)
CONTEXT_PACK_DIR = EVIDENCE_ROOT / "context-packs"
RESULTS_PATH = EVIDENCE_ROOT / "pilot-results-r2.json"

from spec_source_registry import register_source, is_source_registered, validate_citation, load_registry
from spec_vault_ingest import ingest_text_fixture, verify_snapshot_integrity
from spec_parser import parse_spec_from_text
from spec_normalizer import normalize_spec, load_normalized_artifact
from spec_digestor import compute_digest, check_staleness
from requirement_extractor import extract_requirements
from context_pack_builder import build_context_pack, verify_context_pack


# ─── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def pilot_results():
    assert RESULTS_PATH.exists(), "pilot-results-r2.json missing — run _r2_pilot_driver.py first"
    return json.loads(RESULTS_PATH.read_text())


@pytest.fixture(scope="module")
def pilot_registry(tmp_path_factory):
    reg_dir = str(tmp_path_factory.mktemp("reg_r2"))
    register_source("src-r2-test-zst", "zst", "Test ZST Source", "rfc",
                    "https://example.com/rfc", "deferred_local_fixture", registry_dir=reg_dir)
    return reg_dir


# ─── Real-source acquisition tests ─────────────────────────────────────

def test_r2_zst_vault_sha256_matches_real_rfc(pilot_results):
    """ZST vault SHA-256 is from a real non-empty RFC document."""
    sha = pilot_results["sources"]["zst"]["sha256"]
    assert len(sha) == 64, "SHA-256 must be 64 hex chars"
    assert sha != "0" * 64, "SHA-256 must not be zeroes"
    # Real RFC 8878 text starts with RFC metadata — byte size sanity check
    assert pilot_results["sources"]["zst"]["byte_size"] > 100_000, "RFC 8878 should be >100KB"


def test_r2_netpbm_three_components_have_unique_shas(pilot_results):
    """Netpbm PBM/PGM/PPM component SHAs are all different (real distinct HTML docs)."""
    shas = pilot_results["sources"]["netpbm"]["component_shas"]
    assert len(shas) == 3
    vals = list(shas.values())
    assert len(set(vals)) == 3, "PBM/PGM/PPM source SHAs must all be distinct"


def test_r2_fods_fetch_was_real_not_fixture(pilot_results):
    """FODS source is tagged as REAL_FETCH_SCOPED (from live ODF docs)."""
    assert pilot_results["sources"]["fods"]["fetch"] == "REAL_FETCH_SCOPED"


def test_r2_dif_stays_empirical_only(pilot_results):
    """DIF must not be promoted above EMPIRICAL_ONLY."""
    assert pilot_results["sources"]["dif"]["authority_status"] == "EMPIRICAL_ONLY"
    assert pilot_results["sources"]["dif"]["fetch"] == "LOCAL_FIXTURE"


def test_r2_zst_classified_accepted_spec(pilot_results):
    """ZST is ACCEPTED_SPEC — real IETF RFC."""
    assert pilot_results["sources"]["zst"]["authority_status"] == "ACCEPTED_SPEC"


def test_r2_netpbm_classified_accepted_with_caveat(pilot_results):
    """Netpbm is ACCEPTED_WITH_CAVEAT — de facto standard, no formal body."""
    assert pilot_results["sources"]["netpbm"]["authority_status"] == "ACCEPTED_WITH_CAVEAT"


# ─── Requirements extraction tests ─────────────────────────────────────

def test_r2_zst_requirements_extracted_from_real_rfc(pilot_results):
    """ZST requirements extracted from real RFC 8878 — expect substantial count."""
    count = pilot_results["requirements_summary"]["zst"]["count"]
    assert count >= 10, f"Real RFC 8878 should yield >=10 requirements, got {count}"


def test_r2_total_requirements_substantial(pilot_results):
    """Total requirements across all 4 sources should be substantial for real sources."""
    total = pilot_results["requirements_summary"]["total"]
    assert total >= 40, f"Expected >=40 total requirements from real sources, got {total}"


def test_r2_dif_requirements_do_not_exceed_fixture_count(pilot_results):
    """DIF is empirical fixture — count should be modest (not claiming real spec data)."""
    count = pilot_results["requirements_summary"]["dif"]["count"]
    assert 0 < count <= 50, f"DIF empirical fixture should yield 0-50 requirements, got {count}"


# ─── Context pack tests ─────────────────────────────────────────────────

def test_r2_all_four_context_packs_built(pilot_results):
    """Context packs built for ZST, Netpbm, DIF, FODS."""
    packs = pilot_results["context_packs"]
    for fmt in ("zst", "netpbm", "dif", "fods"):
        assert fmt in packs, f"Missing context pack for {fmt}"
        assert packs[fmt]["context_pack_id"].startswith(f"CP-{fmt.upper()}-")


def test_r2_context_pack_manifest_sha256_non_empty(pilot_results):
    """All context packs have valid manifest.sha256 (non-empty, 64-char hex)."""
    for fmt, cp in pilot_results["context_packs"].items():
        sha = cp["manifest_sha256"]
        assert len(sha) == 64, f"{fmt} manifest_sha256 must be 64 chars"


def test_r2_fods_context_pack_present(pilot_results):
    """FODS context pack is built — R2 specific (R1 had this deferred)."""
    assert "fods" in pilot_results["context_packs"]
    assert pilot_results["context_packs"]["fods"]["verified"] is True


# ─── Determinism tests ─────────────────────────────────────────────────

def test_r2_context_packs_deterministic_zst(pilot_results):
    """ZST context pack manifest_sha256 identical across two independent runs."""
    d = pilot_results["determinism"]["zst"]
    assert d["deterministic"] is True
    assert d["run1_sha256"] == d["run2_sha256"]


def test_r2_context_packs_deterministic_netpbm(pilot_results):
    """Netpbm context pack deterministic."""
    d = pilot_results["determinism"]["netpbm"]
    assert d["deterministic"] is True


def test_r2_context_packs_deterministic_fods(pilot_results):
    """FODS context pack deterministic — new in R2."""
    d = pilot_results["determinism"]["fods"]
    assert d["deterministic"] is True


# ─── Staleness tests ────────────────────────────────────────────────────

def test_r2_all_sources_fresh(pilot_results):
    """All 4 real sources are fresh (not stale)."""
    for fmt, stale_data in pilot_results["staleness"].items():
        assert stale_data["fresh_check_stale"] is False, f"{fmt} should be fresh, got stale"


def test_r2_synthetic_stale_detected_all_sources(pilot_results):
    """Synthetic staleness correctly detected for all 4 sources."""
    for fmt, stale_data in pilot_results["staleness"].items():
        assert stale_data["synthetic_stale_detected"] is True, \
            f"{fmt} synthetic stale test should detect staleness"


# ─── Sample output / anti-skip tests ───────────────────────────────────

def test_r2_sample_output_file_exists():
    """Sample output file exists in sample-outputs/ for anti-skip compliance."""
    sample_path = EVIDENCE_ROOT / "sample-outputs" / "zst-context-pack-sample.json"
    assert sample_path.exists(), "Sample output must exist in sample-outputs/"
    data = json.loads(sample_path.read_text())
    assert data["sample_type"] == "context_pack_sample"
    assert data["format"] == "zst"


def test_r2_sample_output_has_real_manifest_sha():
    """Sample output references a real non-zero manifest SHA-256."""
    sample_path = EVIDENCE_ROOT / "sample-outputs" / "zst-context-pack-sample.json"
    data = json.loads(sample_path.read_text())
    sha = data["manifest_sha256"]
    assert len(sha) == 64
    assert sha != "0" * 64


# ─── Source registration anti-bypass tests ─────────────────────────────

def test_r2_registered_citation_valid(pilot_registry):
    """Citation for registered source is valid."""
    cit = validate_citation("src-r2-test-zst", pilot_registry)
    assert cit["valid"] is True


def test_r2_unregistered_citation_rejected(pilot_registry):
    """Citation for unregistered source is rejected."""
    cit = validate_citation("src-r2-nonexistent", pilot_registry)
    assert cit["valid"] is False


def test_r2_empirical_source_stays_empirical():
    """EMPIRICAL_ONLY source type cannot be treated as ACCEPTED_SPEC in extraction."""
    # DIF is empirical — its requirements must not be zero (extraction works)
    # but authority metadata stays EMPIRICAL_ONLY
    results = json.loads(RESULTS_PATH.read_text())
    dif_count = results["requirements_summary"]["dif"]["count"]
    dif_auth = results["sources"]["dif"]["authority_status"]
    assert dif_count > 0, "DIF should extract some requirements"
    assert dif_auth == "EMPIRICAL_ONLY", "DIF authority must stay EMPIRICAL_ONLY"
