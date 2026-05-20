"""
R35 Lane I: Evidence guard hardening tests.

Prevents recurrence of:
- R34-style bundle metadata/repo contract mismatch
- emergency_blocker_bundle inconsistency
- report namespace collision across parallel tracks
- gate correction without previous_claimed_gate
- probe_only falsely claiming release candidacy
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src" / "python"))

try:
    import yaml
except ImportError:
    yaml = None

skipif_no_yaml = pytest.mark.skipif(yaml is None, reason="PyYAML not installed")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    """Load YAML file. Handles both PyYAML and basic fallback."""
    text = path.read_text(encoding="utf-8")
    if yaml:
        return yaml.safe_load(text)
    # Minimal fallback for key: value lines
    result = {}
    for line in text.splitlines():
        if ":" in line and not line.strip().startswith("#"):
            k, _, v = line.partition(":")
            result[k.strip()] = v.strip().strip('"').strip("'")
    return result


# ---------------------------------------------------------------------------
# 1. Contract/Bundle Metadata Consistency Guards
# ---------------------------------------------------------------------------

class TestContractConsistency:
    """Ensure evidence contracts are internally consistent."""

    @skipif_no_yaml
    def test_r34_contract_no_emergency_blocker(self):
        """R34 repo contract must NOT have emergency_blocker_bundle=true."""
        contract_path = REPO / "tools" / "evidence" / "contracts" / "r34-r33-scope-separation-repair.yaml"
        if not contract_path.exists():
            pytest.skip("R34 contract not found")
        data = _load_yaml(contract_path)
        assert data.get("emergency_blocker_bundle") is not True or data.get("emergency_blocker_bundle") == "false"

    @skipif_no_yaml
    def test_r33_drift_contract_require_clean_git(self):
        """R33 drift recovery contract must have require_clean_git=true."""
        contract_path = REPO / "tools" / "evidence" / "contracts" / "r33-drift-recovery-overclaim-deepening.yaml"
        if not contract_path.exists():
            pytest.skip("R33 drift contract not found")
        data = _load_yaml(contract_path)
        assert data.get("require_clean_git") in (True, "true")

    @skipif_no_yaml
    def test_all_contracts_have_sprint_id(self):
        """Every evidence contract must have a sprint_id field."""
        contracts = REPO / "tools" / "evidence" / "contracts"
        for f in contracts.glob("*.yaml"):
            data = _load_yaml(f)
            assert data.get("sprint_id") or data.get("contract_id"), \
                f"{f.name} missing sprint_id/contract_id"


# ---------------------------------------------------------------------------
# 2. Report Namespace Collision Guards
# ---------------------------------------------------------------------------

class TestReportNamespaceCollision:
    """Ensure R33 reports/ and AI reports/ don't collide."""

    def test_r33_dir_has_no_ai_artifacts(self):
        """reports/r33/ must not contain AI pipeline artifacts."""
        r33_dir = REPO / "reports" / "r33"
        if not r33_dir.exists():
            pytest.skip("reports/r33/ not found")
        ai_keywords = ["ai-runner", "pipeline-truth", "synthesis", "telemetry"]
        for f in r33_dir.rglob("*"):
            if f.is_file():
                name_lower = f.name.lower()
                for kw in ai_keywords:
                    assert kw not in name_lower, \
                        f"AI artifact {f.name} found in reports/r33/"

    def test_ai_r33_artifacts_relocated(self):
        """AI R33 artifacts must be in reports/ai/r33-runner-pipeline-truth-20260519/."""
        ai_dir = REPO / "reports" / "ai" / "r33-runner-pipeline-truth-20260519"
        if not ai_dir.exists():
            pytest.skip("AI R33 artifacts dir not found")
        assert any(ai_dir.iterdir()), "AI R33 artifacts dir is empty"

    @skipif_no_yaml
    def test_r33_sprint_state_identifies_drift_recovery(self):
        """R33 sprint-state.yaml must identify drift recovery, not AI pipeline."""
        state_path = REPO / "reports" / "r33" / "sprint-state.yaml"
        if not state_path.exists():
            pytest.skip("R33 sprint-state.yaml not found")
        data = _load_yaml(state_path)
        sprint_id = data.get("sprint_id", "")
        assert "DRIFT-RECOVERY" in sprint_id.upper(), \
            f"R33 sprint-state has wrong sprint_id: {sprint_id}"


# ---------------------------------------------------------------------------
# 3. Gate Correction Guards
# ---------------------------------------------------------------------------

class TestGateCorrectionGuards:
    """Ensure gate corrections preserve historical claims."""

    @skipif_no_yaml
    def test_corrected_pack_yamls_have_previous_claimed_gate(self):
        """Pack.yamls with gate_correction must have previous_claimed_gate."""
        for fmt in ["fodp", "fodg", "gnumeric", "abw"]:
            pack_path = REPO / "acquisition-packs" / fmt / "pack.yaml"
            if not pack_path.exists():
                continue
            text = pack_path.read_text(encoding="utf-8")
            if "gate_correction:" in text:
                assert "previous_claimed_gate" in text, \
                    f"{fmt}/pack.yaml has gate_correction but no previous_claimed_gate"

    @skipif_no_yaml
    def test_corrected_pack_yamls_have_evidence_backed_gate(self):
        """Pack.yamls with gate_correction must have evidence_backed_gate."""
        for fmt in ["fodp", "fodg", "gnumeric", "abw"]:
            pack_path = REPO / "acquisition-packs" / fmt / "pack.yaml"
            if not pack_path.exists():
                continue
            text = pack_path.read_text(encoding="utf-8")
            if "gate_correction:" in text:
                assert "evidence_backed_gate" in text, \
                    f"{fmt}/pack.yaml has gate_correction but no evidence_backed_gate"

    @skipif_no_yaml
    def test_corrected_pack_yamls_have_maturity_class(self):
        """Pack.yamls with gate_correction must have maturity_class."""
        for fmt in ["fodp", "fodg", "gnumeric", "abw"]:
            pack_path = REPO / "acquisition-packs" / fmt / "pack.yaml"
            if not pack_path.exists():
                continue
            text = pack_path.read_text(encoding="utf-8")
            if "gate_correction:" in text:
                assert "maturity_class" in text, \
                    f"{fmt}/pack.yaml has gate_correction but no maturity_class"


# ---------------------------------------------------------------------------
# 4. Probe-Only Release Candidacy Guard
# ---------------------------------------------------------------------------

class TestProbeOnlyReleaseGuard:
    """Ensure probe_only formats don't falsely claim release candidacy."""

    @skipif_no_yaml
    def test_probe_only_formats_not_publication_authorized(self):
        """Formats with gate_correction to probe_only must not have publication_authorized=true."""
        for fmt in ["fodp", "fodg", "gnumeric", "abw"]:
            pack_path = REPO / "acquisition-packs" / fmt / "pack.yaml"
            if not pack_path.exists():
                continue
            text = pack_path.read_text(encoding="utf-8")
            if "maturity_class: probe_only" in text:
                assert "publication_authorized: true" not in text, \
                    f"{fmt} is probe_only but claims publication_authorized"

    @skipif_no_yaml
    def test_probe_only_formats_not_commercial_ready(self):
        """Formats with probe_only maturity must not claim commercial_product_ready."""
        for fmt in ["fodp", "fodg", "gnumeric", "abw"]:
            pack_path = REPO / "acquisition-packs" / fmt / "pack.yaml"
            if not pack_path.exists():
                continue
            text = pack_path.read_text(encoding="utf-8")
            if "maturity_class: probe_only" in text:
                assert "commercial_product_ready: true" not in text, \
                    f"{fmt} is probe_only but claims commercial_product_ready"


# ---------------------------------------------------------------------------
# 5. Scope Finalization Guards
# ---------------------------------------------------------------------------

class TestScopeFinalizationGuards:
    """Ensure scope_finalization sections are complete."""

    @skipif_no_yaml
    def test_scope_finalized_pack_yamls_have_scope_description(self):
        """Pack.yamls with scope_finalization must have scope_description."""
        for fmt in ["xcf", "ppm", "pgm", "pbm"]:
            pack_path = REPO / "acquisition-packs" / fmt / "pack.yaml"
            if not pack_path.exists():
                continue
            text = pack_path.read_text(encoding="utf-8")
            if "scope_finalization:" in text:
                assert "scope_description" in text, \
                    f"{fmt}/pack.yaml has scope_finalization but no scope_description"

    @skipif_no_yaml
    def test_scope_finalized_pack_yamls_record_binary_status(self):
        """Image format pack.yamls with scope_finalization must document binary variant status."""
        for fmt in ["ppm", "pgm", "pbm"]:
            pack_path = REPO / "acquisition-packs" / fmt / "pack.yaml"
            if not pack_path.exists():
                continue
            text = pack_path.read_text(encoding="utf-8")
            if "scope_finalization:" in text:
                assert "binary_p" in text.lower() or "not_implemented" in text, \
                    f"{fmt}/pack.yaml scope_finalization missing binary variant status"
