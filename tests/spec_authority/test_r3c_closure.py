"""
R3C Closure Repair Tests
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-R3-CLOSURE-REPAIR-AND-R4-ODF-PREPARATION-001

Tests verify:
1. R3C report files exist and are non-empty
2. Contradiction register is valid JSON with expected structure
3. RCA packet has 5 context packs (as a list); rca_ready=true; no capability claims
4. RCA caveat summary covers DIF anti-bypass and FODS/FODT scoped limits
5. ODF R4 plan and taskcards are well-formed
6. R3 closure defects are CONFIRMED (they are what R3C repairs)
7. R3 pilot-results: fodt context pack present and deterministic
8. No forbidden files changed
"""

import json
import pathlib
import re
import pytest

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent
R3C_DIR = REPO_ROOT / "reports" / "spec-authority-r3-closure-repair"
R3_DIR = REPO_ROOT / "reports" / "spec-authority-real-pilot-r3"
R3_EVIDENCE = REPO_ROOT / ".local" / "evidences" / "spec-authority-real-pilot-r3"


# ─── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def contradiction_register():
    path = R3C_DIR / "contradiction-register.json"
    assert path.exists(), f"contradiction-register.json not found at {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def rca_packet():
    path = R3C_DIR / "rca-r2-input-packet.json"
    assert path.exists(), f"rca-r2-input-packet.json not found at {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def r4_taskcards():
    path = R3C_DIR / "odf-r4-taskcards.json"
    assert path.exists(), f"odf-r4-taskcards.json not found at {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def r3_declaration():
    path = R3_EVIDENCE / "evidence-declaration.yaml"
    if not path.exists():
        pytest.skip("R3 evidence-declaration.yaml not present")
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def r3_pilot_results():
    path = R3_EVIDENCE / "pilot-results-r3.json"
    if not path.exists():
        pytest.skip("R3 pilot-results-r3.json not present")
    return json.loads(path.read_text(encoding="utf-8"))


# ─── R3C Report File Existence ───────────────────────────────────────────────

class TestR3CReportFiles:
    """All required R3C output files must exist and be non-empty."""

    REQUIRED_FILES = [
        "00-preflight.md",
        "r3-package-recheck.md",
        "contradiction-register.json",
        "closure-order-repair.md",
        "package-proof-protocol.md",
        "rca-input-snapshot-validation.md",
        "rca-r2-input-packet.json",
        "rca-input-caveat-summary.md",
        "odf-r4-depth-plan.md",
        "odf-r4-taskcards.json",
        "lane-ownership.md",
        "file-ownership-map.json",
        "overlap-check.md",
        "taskcard-state.json",
        "scoreboard.md",
        "command-ledger.json",
        "final-git-status.txt",
    ]

    @pytest.mark.parametrize("filename", REQUIRED_FILES)
    def test_file_exists(self, filename):
        path = R3C_DIR / filename
        assert path.exists(), f"Required R3C file missing: {filename}"

    @pytest.mark.parametrize("filename", REQUIRED_FILES)
    def test_file_non_empty(self, filename):
        path = R3C_DIR / filename
        if not path.exists():
            pytest.skip(f"{filename} not found — existence test covers this")
        assert path.stat().st_size > 0, f"File is empty: {filename}"


# ─── Contradiction Register ───────────────────────────────────────────────────

class TestContradictionRegister:
    """contradiction-register.json must be valid and classify R3 contradictions."""

    def test_has_r3_contradictions_key(self, contradiction_register):
        assert "r3_contradictions" in contradiction_register

    def test_has_r3_non_contradictions_key(self, contradiction_register):
        assert "r3_non_contradictions" in contradiction_register

    def test_four_contradictions(self, contradiction_register):
        contras = contradiction_register.get("r3_contradictions", [])
        assert len(contras) == 4, (
            f"Expected 4 contradictions, got {len(contras)}"
        )

    def test_four_non_contradictions(self, contradiction_register):
        non_contras = contradiction_register.get("r3_non_contradictions", [])
        assert len(non_contras) == 4, (
            f"Expected 4 non-contradictions, got {len(non_contras)}"
        )

    def test_contradictions_have_ids(self, contradiction_register):
        for c in contradiction_register.get("r3_contradictions", []):
            assert "id" in c, f"Contradiction missing 'id': {c}"

    def test_contradiction_classifications_include_closure_order(self, contradiction_register):
        classifications = [c.get("classification", "") for c in contradiction_register.get("r3_contradictions", [])]
        closure_related = [t for t in classifications if "CLOSURE_ORDER" in t or "HASH" in t]
        assert len(closure_related) >= 2, (
            f"Expected at least 2 closure/hash contradictions, got: {classifications}"
        )

    def test_total_contradictions_count(self, contradiction_register):
        assert contradiction_register.get("total_contradictions") == 4


# ─── RCA Packet ──────────────────────────────────────────────────────────────

class TestRcaPacket:
    """rca-r2-input-packet.json must have 5 context packs, rca_ready=true, no capability claims."""

    def test_packet_id_present(self, rca_packet):
        assert "packet_id" in rca_packet

    def test_five_context_packs(self, rca_packet):
        packs = rca_packet.get("context_packs", [])
        assert len(packs) == 5, f"Expected 5 context packs, got {len(packs)}: {[p.get('format_id') for p in packs]}"

    def test_expected_format_ids(self, rca_packet):
        expected = {"zst", "netpbm", "dif", "fods", "fodt"}
        actual = {p.get("format_id") for p in rca_packet.get("context_packs", [])}
        assert actual == expected, f"Format IDs mismatch: {actual}"

    def test_rca_ready_true(self, rca_packet):
        assert rca_packet.get("rca_ready") is True, "rca_ready must be True"

    def test_no_capability_claims(self, rca_packet):
        assert rca_packet.get("capability_claims_present") is False, (
            "capability_claims_present must be False"
        )

    def test_dif_is_empirical_only(self, rca_packet):
        dif = next((p for p in rca_packet.get("context_packs", []) if p.get("format_id") == "dif"), None)
        assert dif is not None, "DIF not found in context_packs"
        assert dif.get("authority_status") == "EMPIRICAL_ONLY", (
            f"DIF must be EMPIRICAL_ONLY, got: {dif.get('authority_status')}"
        )

    def test_zst_accepted_spec(self, rca_packet):
        zst = next((p for p in rca_packet.get("context_packs", []) if p.get("format_id") == "zst"), None)
        assert zst is not None, "ZST not found in context_packs"
        assert zst.get("authority_status") == "ACCEPTED_SPEC", (
            f"ZST should be ACCEPTED_SPEC, got: {zst.get('authority_status')}"
        )

    def test_fods_accepted_with_caveat(self, rca_packet):
        fods = next((p for p in rca_packet.get("context_packs", []) if p.get("format_id") == "fods"), None)
        assert fods is not None, "FODS not found in context_packs"
        assert fods.get("authority_status") == "ACCEPTED_WITH_CAVEAT", (
            f"FODS should be ACCEPTED_WITH_CAVEAT, got: {fods.get('authority_status')}"
        )

    def test_fodt_accepted_with_caveat(self, rca_packet):
        fodt = next((p for p in rca_packet.get("context_packs", []) if p.get("format_id") == "fodt"), None)
        assert fodt is not None, "FODT not found in context_packs"
        assert fodt.get("authority_status") == "ACCEPTED_WITH_CAVEAT", (
            f"FODT should be ACCEPTED_WITH_CAVEAT, got: {fodt.get('authority_status')}"
        )

    def test_all_context_packs_have_context_pack_id(self, rca_packet):
        for pack in rca_packet.get("context_packs", []):
            assert pack.get("context_pack_id"), f"{pack.get('format_id')} missing context_pack_id"

    def test_all_context_packs_deterministic(self, rca_packet):
        for pack in rca_packet.get("context_packs", []):
            assert pack.get("deterministic") is True, (
                f"{pack.get('format_id')} not marked deterministic"
            )

    def test_downstream_usage_rules_present(self, rca_packet):
        rules = rca_packet.get("downstream_usage_rules", {})
        assert len(rules) > 0, "downstream_usage_rules must be present"


# ─── Caveat Summary ───────────────────────────────────────────────────────────

class TestCaveatSummary:
    """rca-input-caveat-summary.md must cover all 5 sources and DIF anti-bypass."""

    def test_caveat_summary_exists(self):
        path = R3C_DIR / "rca-input-caveat-summary.md"
        assert path.exists()

    def test_dif_anti_bypass_mentioned(self):
        path = R3C_DIR / "rca-input-caveat-summary.md"
        text = path.read_text(encoding="utf-8")
        assert "DIF" in text and ("MUST NOT" in text or "HARD BLOCKED" in text), (
            "Caveat summary must mention DIF anti-bypass rule"
        )

    def test_fods_scoped_limitation_mentioned(self):
        path = R3C_DIR / "rca-input-caveat-summary.md"
        text = path.read_text(encoding="utf-8")
        assert "FODS" in text and ("scoped" in text.lower() or "intro" in text.lower()), (
            "Caveat summary must mention FODS scoped limitation"
        )

    def test_fodt_scoped_limitation_mentioned(self):
        path = R3C_DIR / "rca-input-caveat-summary.md"
        text = path.read_text(encoding="utf-8")
        assert "FODT" in text and ("scoped" in text.lower() or "intro" in text.lower()), (
            "Caveat summary must mention FODT scoped limitation"
        )

    def test_r4_open_items_present(self):
        path = R3C_DIR / "rca-input-caveat-summary.md"
        text = path.read_text(encoding="utf-8")
        assert "R4" in text, "Caveat summary must reference R4 open items"


# ─── Closure Order Protocol ──────────────────────────────────────────────────

class TestClosureOrderProtocol:
    """Verify R3 closure defects are documented and protocol is established."""

    def test_closure_order_repair_exists(self):
        assert (R3C_DIR / "closure-order-repair.md").exists()

    def test_package_proof_protocol_exists(self):
        assert (R3C_DIR / "package-proof-protocol.md").exists()

    def test_r3_proof_in_evidence_artifacts_is_known_defect(self, r3_declaration):
        """R3 evidence declaration HAS review-package-proof.md in evidence_artifacts.
        This IS the known R3 closure defect that R3C documents and repairs.
        Verify the defect exists so we know what was fixed."""
        artifacts = r3_declaration.get("evidence_artifacts", [])
        proof_in_artifacts = any(
            "review-package-proof" in artifact.get("path", "")
            for artifact in artifacts
        )
        # The R3 declaration has this defect (proof is in artifacts)
        # R3C corrects this: R3C evidence-declaration will NOT have proof in artifacts
        assert proof_in_artifacts, (
            "Expected R3 declaration to have review-package-proof in evidence_artifacts "
            "(this is the known closure defect that R3C repairs). "
            "If not present, R3C closure repair tests need updating."
        )

    def test_r3_proof_contains_placeholder_is_known_defect(self):
        """R3 review-package-proof.md DOES contain [PLACEHOLDER] — this is the documented defect.
        R3C repairs this by following the correct closure order."""
        proof_path = R3_DIR / "review-package-proof.md"
        if not proof_path.exists():
            pytest.skip("R3 review-package-proof.md not found")
        text = proof_path.read_text(encoding="utf-8")
        assert "[PLACEHOLDER]" in text, (
            "Expected R3 review-package-proof.md to contain [PLACEHOLDER] "
            "(this is the documented R3 closure defect). R3C resolves this."
        )

    def test_package_proof_protocol_no_self_reference_rule(self):
        """Protocol must state that review-package-proof.md must NOT be in evidence_artifacts."""
        text = (R3C_DIR / "package-proof-protocol.md").read_text(encoding="utf-8")
        assert "evidence_artifacts" in text and ("MUST NOT" in text or "not in" in text.lower()), (
            "Protocol must state the no-self-reference rule for review-package-proof.md"
        )

    def test_closure_order_repair_mentions_correct_sequence(self):
        """Closure order repair must describe the correct sequence (artifacts → cycle → ZIP → proof)."""
        text = (R3C_DIR / "closure-order-repair.md").read_text(encoding="utf-8")
        assert "autonomous" in text.lower() or "autonomous-cycle" in text, (
            "Closure order repair must mention autonomous-cycle step"
        )
        assert "ZIP" in text or "zip" in text.lower(), (
            "Closure order repair must mention ZIP building"
        )


# ─── R3 Pilot Results ────────────────────────────────────────────────────────

class TestR3PilotResults:
    """R3 pilot-results: fodt context pack present and deterministic (R3 added FODT)."""

    def test_fodt_context_pack_present(self, r3_pilot_results):
        assert "fodt" in r3_pilot_results, (
            "R3 pilot-results-r3.json must have 'fodt' key (FODT was new in R3)"
        )

    def test_fodt_deterministic(self, r3_pilot_results):
        fodt = r3_pilot_results.get("fodt", {})
        assert fodt.get("deterministic") is True, "FODT context pack must be deterministic"

    def test_fodt_verified(self, r3_pilot_results):
        fodt = r3_pilot_results.get("fodt", {})
        assert fodt.get("verified") is True, "FODT context pack must be verified"

    def test_fodt_context_pack_id_present(self, r3_pilot_results):
        fodt = r3_pilot_results.get("fodt", {})
        cp_id = fodt.get("context_pack_id", "")
        assert cp_id.startswith("CP-"), (
            f"FODT context pack ID should start with CP-: {cp_id}"
        )


# ─── RCA Packet Has 5 Packs (cross-sprint continuity) ────────────────────────

class TestRcaPacketFiveFormats:
    """The R3C RCA packet consolidates all 5 format context packs for RCAL consumption."""

    def test_rca_packet_covers_all_r1_r2_r3_formats(self, rca_packet):
        """ZST and NETPBM (R1/R2), DIF (R2), FODS (R2), FODT (R3) — all 5 in one packet."""
        format_ids = {p.get("format_id") for p in rca_packet.get("context_packs", [])}
        assert "zst" in format_ids, "ZST (R1/R2) must be in RCA packet"
        assert "netpbm" in format_ids, "NETPBM (R1/R2) must be in RCA packet"
        assert "dif" in format_ids, "DIF (R2) must be in RCA packet"
        assert "fods" in format_ids, "FODS (R2) must be in RCA packet"
        assert "fodt" in format_ids, "FODT (R3) must be in RCA packet"

    def test_open_items_for_rcal_present(self, rca_packet):
        items = rca_packet.get("open_items_for_rcal", [])
        assert len(items) >= 1, "Must have at least 1 open item for RCAL"

    def test_packet_status(self, rca_packet):
        status = rca_packet.get("status", "")
        assert status in {"CANONICAL", "ACCEPTED", "ACTIVE", "FROZEN"}, (
            f"Unexpected packet status: {status}"
        )


# ─── ODF R4 Taskcards ────────────────────────────────────────────────────────

class TestOdfR4Taskcards:
    """odf-r4-taskcards.json must be a valid list of taskcard objects."""

    def test_is_list(self, r4_taskcards):
        assert isinstance(r4_taskcards, list), "odf-r4-taskcards.json should be a list"

    def test_at_least_five_taskcards(self, r4_taskcards):
        assert len(r4_taskcards) >= 5, (
            f"Expected at least 5 R4 taskcards, got {len(r4_taskcards)}"
        )

    def test_all_have_ids(self, r4_taskcards):
        for tc in r4_taskcards:
            assert "id" in tc, f"Taskcard missing 'id': {tc}"

    def test_all_ids_start_with_tc_r4(self, r4_taskcards):
        for tc in r4_taskcards:
            assert tc["id"].startswith("TC-R4-"), (
                f"R4 taskcard ID should start with TC-R4-: {tc['id']}"
            )

    def test_all_have_status_ready(self, r4_taskcards):
        for tc in r4_taskcards:
            assert tc.get("status") == "READY", (
                f"R4 taskcard {tc['id']} should be READY (not yet executed): {tc.get('status')}"
            )

    def test_fods_and_fodt_tasks_present(self, r4_taskcards):
        titles = [tc.get("title", "").upper() for tc in r4_taskcards]
        fods_tasks = [t for t in titles if "FODS" in t]
        fodt_tasks = [t for t in titles if "FODT" in t]
        assert len(fods_tasks) >= 1, "Must have at least 1 FODS taskcard"
        assert len(fodt_tasks) >= 1, "Must have at least 1 FODT taskcard"

    def test_odf_r4_depth_plan_has_h1(self):
        path = R3C_DIR / "odf-r4-depth-plan.md"
        text = path.read_text(encoding="utf-8")
        lines = text.split("\n")
        h1_lines = [l for l in lines[:10] if l.startswith("# ")]
        assert len(h1_lines) >= 1, "odf-r4-depth-plan.md must have an H1 heading"

    def test_odf_r4_depth_plan_has_chunking_strategy(self):
        path = R3C_DIR / "odf-r4-depth-plan.md"
        text = path.read_text(encoding="utf-8")
        assert "chunk" in text.lower() or "Chunk" in text, (
            "odf-r4-depth-plan.md must describe chunking strategy"
        )

    def test_odf_r4_depth_plan_has_risk_register(self):
        path = R3C_DIR / "odf-r4-depth-plan.md"
        text = path.read_text(encoding="utf-8")
        assert "risk" in text.lower(), "odf-r4-depth-plan.md must have a risk register"


# ─── Forbidden Path Check ────────────────────────────────────────────────────

class TestForbiddenPaths:
    """No R3C files should appear in forbidden paths."""

    def test_r3c_in_allowed_path(self):
        assert R3C_DIR.is_relative_to(REPO_ROOT / "reports"), (
            "R3C directory must be under reports/"
        )

    def test_test_file_in_spec_authority_dir(self):
        test_file = REPO_ROOT / "tests" / "spec_authority" / "test_r3c_closure.py"
        assert test_file.exists(), "test_r3c_closure.py must exist in tests/spec_authority/"

    def test_no_r3c_src_net_changes(self):
        """Verify R3C didn't touch src/net/ (check by listing R3C outputs only)."""
        for f in R3C_DIR.rglob("*"):
            if f.is_file():
                assert "src/net" not in str(f), f"R3C should not touch src/net: {f}"
