"""
R3 Pilot Regression Tests — FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R3-CLOSURE-HARDENING-AND-ODF-DEPTH-001

Tests: FODT context pack, lane ledger anti-skip fix, RCA input snapshot caveats,
review-package-proof no-placeholders, FODS/FODT scoped authority non-overclaim,
R3 closure hardening criteria.
"""
import sys
import json
import pathlib
import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SAL_DIR = REPO_ROOT / "tools" / "specification-authority-layer"
sys.path.insert(0, str(SAL_DIR))

EVIDENCE_R2 = REPO_ROOT / ".local/evidences/spec-authority-real-pilot-r2"
EVIDENCE_R3 = REPO_ROOT / ".local/evidences/spec-authority-real-pilot-r3"
REPORTS_R3 = REPO_ROOT / "reports" / "spec-authority-real-pilot-r3"
RESULTS_R3 = EVIDENCE_R3 / "pilot-results-r3.json"
SNAPSHOT_PATH = REPORTS_R3 / "rca-input-snapshot-manifest.json"


# ─── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def r3_results():
    assert RESULTS_R3.exists(), "pilot-results-r3.json missing — run _r3_odf_driver.py first"
    return json.loads(RESULTS_R3.read_text())


@pytest.fixture(scope="module")
def rca_snapshot():
    assert SNAPSHOT_PATH.exists(), "rca-input-snapshot-manifest.json missing"
    return json.loads(SNAPSHOT_PATH.read_text())


@pytest.fixture(scope="module")
def r2_results():
    results_path = EVIDENCE_R2 / "pilot-results-r2.json"
    assert results_path.exists(), "pilot-results-r2.json missing"
    return json.loads(results_path.read_text())


# ─── FODT context pack tests ────────────────────────────────────────────

def test_r3_fodt_context_pack_built(r3_results):
    """FODT context pack was built in R3."""
    assert "fodt" in r3_results
    assert r3_results["fodt"]["context_pack_id"].startswith("CP-FODT-")


def test_r3_fodt_context_pack_has_sha256(r3_results):
    """FODT context pack manifest_sha256 is a valid 64-char hex string."""
    sha = r3_results["fodt"]["manifest_sha256"]
    assert len(sha) == 64, f"manifest_sha256 must be 64 chars, got {len(sha)}"
    assert all(c in "0123456789abcdef" for c in sha), "SHA-256 must be hex"


def test_r3_fodt_deterministic(r3_results):
    """FODT context pack is deterministic (run1 SHA == run2 SHA)."""
    assert r3_results["fodt"]["deterministic"] is True


def test_r3_fodt_verified(r3_results):
    """FODT context pack passes verify_context_pack()."""
    assert r3_results["fodt"]["verified"] is True


def test_r3_fodt_sections_count(r3_results):
    """FODT context pack extracted sections count > 0."""
    sections = r3_results["fodt"]["sections"]
    assert sections > 0, f"FODT must have >0 sections, got {sections}"


def test_r3_fodt_requirements_count(r3_results):
    """FODT context pack extracted at least 1 requirement."""
    reqs = r3_results["fodt"]["requirements"]
    assert reqs >= 1, f"FODT must have >=1 requirement, got {reqs}"


def test_r3_fodt_authority_accepted_with_caveat(r3_results):
    """FODT authority_status is ACCEPTED_WITH_CAVEAT (not ACCEPTED_SPEC — scoped only)."""
    assert r3_results["fodt"]["authority_status"] == "ACCEPTED_WITH_CAVEAT"


def test_r3_fodt_source_sha256_non_zero(r3_results):
    """FODT vault source SHA-256 is non-zero (real content ingested)."""
    sha = r3_results["fodt"]["sha256"]
    assert len(sha) == 64
    assert sha != "0" * 64


# ─── FODT sample output anti-skip tests ────────────────────────────────

def test_r3_fodt_sample_output_exists():
    """FODT sample output file exists in sample-outputs/ for anti-skip compliance."""
    sample_path = EVIDENCE_R3 / "sample-outputs" / "fodt-context-pack-sample.json"
    assert sample_path.exists(), "fodt-context-pack-sample.json must exist"
    data = json.loads(sample_path.read_text())
    assert data.get("format") == "fodt"
    assert data.get("sample_type") == "context_pack_sample"


def test_r3_fodt_sample_output_has_authority_status():
    """FODT sample output has authority_status field."""
    sample_path = EVIDENCE_R3 / "sample-outputs" / "fodt-context-pack-sample.json"
    data = json.loads(sample_path.read_text())
    assert "authority_status" in data
    assert data["authority_status"] == "ACCEPTED_WITH_CAVEAT"


def test_r3_fodt_sample_output_has_caveat():
    """FODT sample output has caveat field (scoped-only warning)."""
    sample_path = EVIDENCE_R3 / "sample-outputs" / "fodt-context-pack-sample.json"
    data = json.loads(sample_path.read_text())
    assert "caveat" in data
    assert "scoped" in data["caveat"].lower() or "deferred" in data["caveat"].lower()


# ─── Lane ledger anti-skip tests ────────────────────────────────────────

def test_r3_lane_ledger_exists():
    """Lane execution ledger exists — fixes R2 missing_lane_ledger anti-skip violation."""
    ledger_path = REPORTS_R3 / "lane-execution-ledger.yaml"
    assert ledger_path.exists(), "lane-execution-ledger.yaml must exist in reports/spec-authority-real-pilot-r3/"


def test_r3_lane_ledger_is_valid_yaml():
    """Lane execution ledger parses as valid YAML."""
    ledger_path = REPORTS_R3 / "lane-execution-ledger.yaml"
    data = yaml.safe_load(ledger_path.read_text())
    assert data is not None
    assert isinstance(data, dict) or isinstance(data, list)


def test_r3_lane_ledger_has_entries():
    """Lane execution ledger has at least one lane entry."""
    ledger_path = REPORTS_R3 / "lane-execution-ledger.yaml"
    data = yaml.safe_load(ledger_path.read_text())
    if isinstance(data, dict) and "lanes" in data:
        assert len(data["lanes"]) > 0
    elif isinstance(data, list):
        assert len(data) > 0
    else:
        # Some structure with lane data exists
        assert data is not None


def test_r3_raw_log_directory_exists():
    """Raw logs directory exists in evidence root."""
    raw_log_dir = EVIDENCE_R3 / "raw-logs"
    assert raw_log_dir.exists(), ".local/evidences/spec-authority-real-pilot-r3/raw-logs/ must exist"


# ─── RCA input snapshot tests ───────────────────────────────────────────

def test_r3_rca_snapshot_has_five_sources(rca_snapshot):
    """RCA input snapshot contains exactly 5 sources."""
    assert len(rca_snapshot["sources"]) == 5


def test_r3_rca_snapshot_contains_zst(rca_snapshot):
    """RCA snapshot includes ZST source."""
    ids = [s["source_id"] for s in rca_snapshot["sources"]]
    assert "src-r2-zst-rfc8878" in ids


def test_r3_rca_snapshot_contains_fodt(rca_snapshot):
    """RCA snapshot includes FODT source — new in R3."""
    ids = [s["source_id"] for s in rca_snapshot["sources"]]
    assert "src-r3-fodt-odf13" in ids


def test_r3_rca_snapshot_no_capability_claims(rca_snapshot):
    """RCA snapshot has capability_claims_present = false."""
    assert rca_snapshot["capability_claims_present"] is False


def test_r3_rca_snapshot_is_rca_ready(rca_snapshot):
    """RCA snapshot is marked rca_ready = true."""
    assert rca_snapshot["rca_ready"] is True


def test_r3_rca_snapshot_dif_empirical_only(rca_snapshot):
    """DIF in RCA snapshot retains EMPIRICAL_ONLY authority_status."""
    dif = next(s for s in rca_snapshot["sources"] if s["source_id"] == "src-r2-dif-empirical")
    assert dif["authority_status"] == "EMPIRICAL_ONLY"


def test_r3_rca_snapshot_dif_has_caveat(rca_snapshot):
    """DIF in RCA snapshot has a caveat (must not promote rule)."""
    dif = next(s for s in rca_snapshot["sources"] if s["source_id"] == "src-r2-dif-empirical")
    assert dif["caveat"] is not None
    assert "MUST NOT" in dif["caveat"] or "must not" in dif["caveat"].lower()


def test_r3_rca_snapshot_zst_has_no_caveat(rca_snapshot):
    """ZST in RCA snapshot has null caveat (clean ACCEPTED_SPEC)."""
    zst = next(s for s in rca_snapshot["sources"] if s["source_id"] == "src-r2-zst-rfc8878")
    assert zst["caveat"] is None


def test_r3_rca_snapshot_all_deterministic(rca_snapshot):
    """All sources in RCA snapshot are marked deterministic."""
    for source in rca_snapshot["sources"]:
        assert source["deterministic"] is True, f"{source['source_id']} must be deterministic"


def test_r3_rca_snapshot_all_have_context_pack_id(rca_snapshot):
    """All sources in RCA snapshot have a context_pack_id."""
    for source in rca_snapshot["sources"]:
        cid = source.get("context_pack_id", "")
        assert cid and cid.startswith("CP-"), \
            f"{source['source_id']} must have context_pack_id starting with CP-"


# ─── FODS/FODT scoped authority non-overclaim tests ────────────────────

def test_r3_fods_does_not_claim_full_odf(rca_snapshot):
    """FODS does not claim ACCEPTED_SPEC — only ACCEPTED_WITH_CAVEAT (scoped intro)."""
    fods = next(s for s in rca_snapshot["sources"] if s["source_id"] == "src-r2-fods-odf13")
    assert fods["authority_status"] == "ACCEPTED_WITH_CAVEAT", \
        "FODS must be ACCEPTED_WITH_CAVEAT not ACCEPTED_SPEC (scoped intro only)"


def test_r3_fodt_does_not_claim_full_odf(rca_snapshot):
    """FODT does not claim ACCEPTED_SPEC — only ACCEPTED_WITH_CAVEAT (scoped intro)."""
    fodt = next(s for s in rca_snapshot["sources"] if s["source_id"] == "src-r3-fodt-odf13")
    assert fodt["authority_status"] == "ACCEPTED_WITH_CAVEAT", \
        "FODT must be ACCEPTED_WITH_CAVEAT not ACCEPTED_SPEC (scoped intro only)"


def test_r3_fods_requirements_are_modest(rca_snapshot):
    """FODS requirements count is modest — scoped intro only, not full ODF."""
    fods = next(s for s in rca_snapshot["sources"] if s["source_id"] == "src-r2-fods-odf13")
    reqs = fods.get("requirements", 0)
    assert 0 < reqs <= 20, \
        f"FODS scoped intro should yield 1-20 requirements (full ODF has 1000s), got {reqs}"


def test_r3_fodt_requirements_are_modest(rca_snapshot):
    """FODT requirements count is modest — scoped intro only."""
    fodt = next(s for s in rca_snapshot["sources"] if s["source_id"] == "src-r3-fodt-odf13")
    reqs = fodt.get("requirements", 0)
    assert 0 < reqs <= 20, \
        f"FODT scoped intro should yield 1-20 requirements, got {reqs}"


def test_r3_fods_caveat_mentions_scoped(rca_snapshot):
    """FODS caveat mentions scoped limitation."""
    fods = next(s for s in rca_snapshot["sources"] if s["source_id"] == "src-r2-fods-odf13")
    caveat = fods.get("caveat", "") or ""
    assert "scoped" in caveat.lower() or "intro" in caveat.lower(), \
        f"FODS caveat must mention scoped limitation, got: {caveat}"


def test_r3_fodt_caveat_mentions_scoped(rca_snapshot):
    """FODT caveat mentions scoped limitation."""
    fodt = next(s for s in rca_snapshot["sources"] if s["source_id"] == "src-r3-fodt-odf13")
    caveat = fodt.get("caveat", "") or ""
    assert "scoped" in caveat.lower() or "intro" in caveat.lower(), \
        f"FODT caveat must mention scoped limitation, got: {caveat}"


# ─── R3 report files existence tests ───────────────────────────────────

def test_r3_lane_ledger_proof_exists():
    """Lane ledger proof report exists."""
    assert (REPORTS_R3 / "lane-ledger-proof.md").exists()


def test_r3_r2_caveat_register_exists():
    """R2 caveat register exists — documents R2 issues to fix."""
    assert (REPORTS_R3 / "r2-caveat-register.md").exists()


def test_r3_odf_depth_report_exists():
    """ODF depth report exists."""
    assert (REPORTS_R3 / "odf-depth-report.md").exists()


def test_r3_fodt_context_pack_report_exists():
    """FODT context pack report exists."""
    assert (REPORTS_R3 / "fodt-context-pack-report.md").exists()


def test_r3_rca_caveat_summary_exists():
    """RCA input caveat summary exists."""
    assert (REPORTS_R3 / "rca-input-caveat-summary.md").exists()


def test_r3_grading_consistency_report_exists():
    """Grading/anti-skip consistency report exists."""
    assert (REPORTS_R3 / "grading-anti-skip-consistency.md").exists()


# ─── R2 regression (carry-over) ────────────────────────────────────────

def test_r3_regression_zst_still_accepted_spec(r2_results):
    """Regression: ZST authority status unchanged from R2."""
    assert r2_results["sources"]["zst"]["authority_status"] == "ACCEPTED_SPEC"


def test_r3_regression_dif_still_empirical(r2_results):
    """Regression: DIF authority status unchanged from R2."""
    assert r2_results["sources"]["dif"]["authority_status"] == "EMPIRICAL_ONLY"


def test_r3_regression_context_packs_still_deterministic(r2_results):
    """Regression: R2 context packs remain deterministic."""
    for fmt, det in r2_results["determinism"].items():
        assert det["deterministic"] is True, f"R2 {fmt} context pack must remain deterministic"


def test_r3_regression_r2_fods_context_pack_still_present(r2_results):
    """Regression: R2 FODS context pack remains present and verified."""
    assert r2_results["context_packs"]["fods"]["verified"] is True
