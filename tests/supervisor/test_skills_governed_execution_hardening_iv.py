"""
test_skills_governed_execution_hardening_iv.py
Independent hardening tests for Skills/Governed Execution sprint output.
Sprint: FORMAT-FACTORY-SKILLS-GOVERNED-EXECUTION-HARDENING-IV-001

Tests: 68 across 17 categories
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SPRINT_DIR = REPO_ROOT / "reports" / "skills-governed-execution-hardening"
SKILLS_DIR = REPO_ROOT / "reports" / "skills-product-first"
TEMPLATES_DIR = REPO_ROOT / "docs" / "prompt-templates" / "skills"


# ---------------------------------------------------------------------------
# 1. FODS packet schema / field validation
# ---------------------------------------------------------------------------
class TestFodsPacketSchema:
    def test_packet_parses_as_json(self):
        p = json.loads((SKILLS_DIR / "mainstream-consumption-packet.json").read_text())
        assert isinstance(p, dict)

    def test_packet_has_required_fields(self):
        p = json.loads((SKILLS_DIR / "mainstream-consumption-packet.json").read_text())
        required = [
            "packet_version", "selected_product_gap", "recommended_skill",
            "allowed_files", "forbidden_files", "acceptance_criteria",
            "downgrade_rules", "auto_repair_guidance",
        ]
        missing = [k for k in required if k not in p]
        assert not missing, f"Missing: {missing}"

    def test_packet_gap_id_is_fods(self):
        p = json.loads((SKILLS_DIR / "mainstream-consumption-packet.json").read_text())
        gap = p["selected_product_gap"]
        assert "fods" in gap.get("format_id", "").lower() or "FODS" in gap.get("gap_id", "")

    def test_packet_allowed_files_are_narrow(self):
        p = json.loads((SKILLS_DIR / "mainstream-consumption-packet.json").read_text())
        allowed = p["allowed_files"]
        assert len(allowed) <= 5, f"Too many allowed files: {len(allowed)} — must be narrow"
        # Wildcard patterns are not permitted in allowed_files
        wildcards = [f for f in allowed if "*" in f]
        assert not wildcards, f"Wildcards in allowed_files: {wildcards}"

    def test_packet_forbidden_includes_registry(self):
        p = json.loads((SKILLS_DIR / "mainstream-consumption-packet.json").read_text())
        forbidden = p["forbidden_files"]
        assert any("registry" in f for f in forbidden)

    def test_packet_forbidden_includes_master_plan(self):
        p = json.loads((SKILLS_DIR / "mainstream-consumption-packet.json").read_text())
        forbidden = p["forbidden_files"]
        assert any("master-plan" in f for f in forbidden)

    def test_packet_forbidden_includes_poc_targets(self):
        p = json.loads((SKILLS_DIR / "mainstream-consumption-packet.json").read_text())
        forbidden = p["forbidden_files"]
        assert any("poc-targets" in f for f in forbidden)

    def test_packet_forbidden_includes_vscode(self):
        p = json.loads((SKILLS_DIR / "mainstream-consumption-packet.json").read_text())
        forbidden = p["forbidden_files"]
        assert any("vscode" in f or "mcp.json" in f for f in forbidden)


# ---------------------------------------------------------------------------
# 2. FODS generated handoff path exists
# ---------------------------------------------------------------------------
class TestFodsHandoffExists:
    def test_handoff_path_field_present(self):
        p = json.loads((SKILLS_DIR / "mainstream-consumption-packet.json").read_text())
        assert "generated_handoff_path" in p

    def test_handoff_file_exists_on_disk(self):
        p = json.loads((SKILLS_DIR / "mainstream-consumption-packet.json").read_text())
        handoff_path = REPO_ROOT / p["generated_handoff_path"]
        assert handoff_path.exists(), f"Handoff not found: {handoff_path}"

    def test_handoff_parses_as_yaml(self):
        p = json.loads((SKILLS_DIR / "mainstream-consumption-packet.json").read_text())
        handoff_path = REPO_ROOT / p["generated_handoff_path"]
        data = yaml.safe_load(handoff_path.read_text())
        assert isinstance(data, dict)

    def test_handoff_has_skill_id(self):
        handoff_path = SKILLS_DIR / "generated-handoffs" / "handoff-spf-001-add-dotnet-api.yaml"
        data = yaml.safe_load(handoff_path.read_text())
        assert data.get("skill_id") == "add-dotnet-api"

    def test_handoff_has_forbidden_files(self):
        handoff_path = SKILLS_DIR / "generated-handoffs" / "handoff-spf-001-add-dotnet-api.yaml"
        data = yaml.safe_load(handoff_path.read_text())
        assert "forbidden_files" in data
        assert len(data["forbidden_files"]) > 0

    def test_handoff_has_rollback_note(self):
        handoff_path = SKILLS_DIR / "generated-handoffs" / "handoff-spf-001-add-dotnet-api.yaml"
        data = yaml.safe_load(handoff_path.read_text())
        assert "rollback_note" in data

    def test_template_path_exists_on_disk(self):
        p = json.loads((SKILLS_DIR / "mainstream-consumption-packet.json").read_text())
        template_path = REPO_ROOT / p["template_path"]
        assert template_path.exists(), f"Template not found: {template_path}"


# ---------------------------------------------------------------------------
# 3. add-dotnet-api template required fields
# ---------------------------------------------------------------------------
class TestAddDotnetApiTemplate:
    TEMPLATE = TEMPLATES_DIR / "add-dotnet-api-handoff-template.md"
    REQUIRED = [
        "Role", "Skill ID", "Allowed Files", "Forbidden Files",
        "Expected Source Diff", "Expected Test Files", "Validation Commands",
        "Transcript Schema", "Ledger Schema", "Capability Matrix Update",
        "Rollback Note", "Evidence Declaration Entries", "Auto-Repair Guidance",
        "Stop Conditions", "Continuation Conditions",
    ]

    def test_template_exists(self):
        assert self.TEMPLATE.exists()

    def test_template_has_all_15_sections(self):
        text = self.TEMPLATE.read_text()
        missing = [s for s in self.REQUIRED if s not in text]
        assert not missing, f"Missing sections: {missing}"

    def test_template_has_skill_id_value(self):
        text = self.TEMPLATE.read_text()
        assert "add-dotnet-api" in text

    def test_template_forbids_src_python(self):
        text = self.TEMPLATE.read_text()
        assert "src/python" in text

    def test_template_size_adequate(self):
        assert self.TEMPLATE.stat().st_size >= 1000


# ---------------------------------------------------------------------------
# 4. All six templates required fields
# ---------------------------------------------------------------------------
class TestAllTemplatesRequiredFields:
    PRODUCT_TEMPLATES = [
        "add-dotnet-api-handoff-template.md",
        "add-python-api-handoff-template.md",
        "add-export-handoff-template.md",
        "add-dogfood-pipeline-template.md",
        "add-roundtrip-test-template.md",
        "update-capability-matrix-template.md",
    ]
    REQUIRED = [
        "Role", "Skill ID", "Allowed Files", "Forbidden Files", "Stop Conditions",
        "Continuation Conditions",
    ]

    def test_six_product_templates_exist(self):
        for name in self.PRODUCT_TEMPLATES:
            assert (TEMPLATES_DIR / name).exists(), f"Missing: {name}"

    def test_all_templates_have_role_section(self):
        for name in self.PRODUCT_TEMPLATES:
            text = (TEMPLATES_DIR / name).read_text()
            assert "Role" in text, f"{name} missing Role"

    def test_all_templates_have_allowed_files(self):
        for name in self.PRODUCT_TEMPLATES:
            text = (TEMPLATES_DIR / name).read_text()
            assert "Allowed Files" in text, f"{name} missing Allowed Files"

    def test_all_templates_have_stop_conditions(self):
        for name in self.PRODUCT_TEMPLATES:
            text = (TEMPLATES_DIR / name).read_text()
            assert "Stop Conditions" in text, f"{name} missing Stop Conditions"

    def test_all_templates_have_continuation_conditions(self):
        for name in self.PRODUCT_TEMPLATES:
            text = (TEMPLATES_DIR / name).read_text()
            assert "Continuation Conditions" in text, f"{name} missing Continuation Conditions"


# ---------------------------------------------------------------------------
# 5. Transcript positive fixture passes
# ---------------------------------------------------------------------------
class TestTranscriptPositiveFixture:
    def test_existing_dry_run_transcript_validates(self):
        transcript_path = (
            SKILLS_DIR / "skill-transcripts" / "transcript-spf-001-add-dotnet-api-near-live.json"
        )
        assert transcript_path.exists()
        result = subprocess.run(
            [sys.executable, "tools/supervisor/validate_skill_transcript.py", str(transcript_path)],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        assert result.returncode == 0, f"Transcript validation failed:\n{result.stdout}\n{result.stderr}"

    def test_transcript_has_required_fields(self):
        path = SKILLS_DIR / "skill-transcripts" / "transcript-spf-001-add-dotnet-api-near-live.json"
        t = json.loads(path.read_text())
        required = ["invocation_id", "skill_id", "mode", "inputs", "allowed_files",
                    "actual_files_changed", "tests_run", "result"]
        missing = [f for f in required if f not in t]
        assert not missing, f"Missing fields: {missing}"

    def test_transcript_result_is_pass(self):
        path = SKILLS_DIR / "skill-transcripts" / "transcript-spf-001-add-dotnet-api-near-live.json"
        t = json.loads(path.read_text())
        assert t["result"] == "PASS"

    def test_dry_run_has_empty_actual_files(self):
        path = SKILLS_DIR / "skill-transcripts" / "transcript-spf-001-add-dotnet-api-near-live.json"
        t = json.loads(path.read_text())
        assert t["mode"] == "dry-run"
        assert t["actual_files_changed"] == []


# ---------------------------------------------------------------------------
# 6. Transcript missing required field fails
# ---------------------------------------------------------------------------
class TestTranscriptMissingFieldFails:
    def _make_bad_transcript(self, omit_field: str, tmp_path: Path) -> Path:
        path = (
            SKILLS_DIR / "skill-transcripts" / "transcript-spf-001-add-dotnet-api-near-live.json"
        )
        t = json.loads(path.read_text())
        t.pop(omit_field, None)
        out = tmp_path / f"bad_{omit_field}.json"
        out.write_text(json.dumps(t))
        return out

    def test_missing_invocation_id_fails(self, tmp_path):
        bad = self._make_bad_transcript("invocation_id", tmp_path)
        r = subprocess.run(
            [sys.executable, "tools/supervisor/validate_skill_transcript.py", str(bad)],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        assert r.returncode != 0 or "ERROR" in r.stdout or "FAIL" in r.stdout

    def test_missing_skill_id_fails(self, tmp_path):
        bad = self._make_bad_transcript("skill_id", tmp_path)
        r = subprocess.run(
            [sys.executable, "tools/supervisor/validate_skill_transcript.py", str(bad)],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        assert r.returncode != 0 or "ERROR" in r.stdout or "FAIL" in r.stdout

    def test_missing_allowed_files_fails(self, tmp_path):
        bad = self._make_bad_transcript("allowed_files", tmp_path)
        r = subprocess.run(
            [sys.executable, "tools/supervisor/validate_skill_transcript.py", str(bad)],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        assert r.returncode != 0 or "ERROR" in r.stdout or "FAIL" in r.stdout

    def test_missing_result_fails(self, tmp_path):
        bad = self._make_bad_transcript("result", tmp_path)
        r = subprocess.run(
            [sys.executable, "tools/supervisor/validate_skill_transcript.py", str(bad)],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        assert r.returncode != 0 or "ERROR" in r.stdout or "FAIL" in r.stdout


# ---------------------------------------------------------------------------
# 7. Transcript forbidden path fails
# ---------------------------------------------------------------------------
class TestTranscriptForbiddenPath:
    def test_file_outside_allowed_fails(self, tmp_path):
        path = (
            SKILLS_DIR / "skill-transcripts" / "transcript-spf-001-add-dotnet-api-near-live.json"
        )
        t = json.loads(path.read_text())
        # Inject a file outside allowed_files
        t["actual_files_changed"] = ["src/python/fodt/neutral_model.py"]
        out = tmp_path / "bad_outside_allowed.json"
        out.write_text(json.dumps(t))
        r = subprocess.run(
            [sys.executable, "tools/supervisor/validate_skill_transcript.py", str(out)],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        assert r.returncode != 0 or "outside" in r.stdout.lower() or "FAIL" in r.stdout

    def test_invalid_mode_fails(self, tmp_path):
        path = (
            SKILLS_DIR / "skill-transcripts" / "transcript-spf-001-add-dotnet-api-near-live.json"
        )
        t = json.loads(path.read_text())
        t["mode"] = "invalid-mode-xyz"
        out = tmp_path / "bad_mode.json"
        out.write_text(json.dumps(t))
        r = subprocess.run(
            [sys.executable, "tools/supervisor/validate_skill_transcript.py", str(out)],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        assert r.returncode != 0 or "mode" in r.stdout.lower() or "FAIL" in r.stdout


# ---------------------------------------------------------------------------
# 8. Transcript fixture results
# ---------------------------------------------------------------------------
class TestTranscriptFixtureResults:
    def test_fixture_results_exist(self):
        assert (SPRINT_DIR / "transcript-fixture-results.json").exists()

    def test_fixture_results_have_11_entries(self):
        r = json.loads((SPRINT_DIR / "transcript-fixture-results.json").read_text())
        assert r["summary"]["total"] == 11

    def test_all_fixtures_match(self):
        r = json.loads((SPRINT_DIR / "transcript-fixture-results.json").read_text())
        assert r["summary"]["all_match"] is True


# ---------------------------------------------------------------------------
# 9. Packet shell schema validates
# ---------------------------------------------------------------------------
class TestPacketShellSchema:
    def test_fodt_shell_exists(self):
        assert (SPRINT_DIR / "fodt-packet-shell.json").exists()

    def test_netpbm_shell_exists(self):
        assert (SPRINT_DIR / "netpbm-packet-shell.json").exists()

    def test_fodt_shell_has_required_fields(self):
        s = json.loads((SPRINT_DIR / "fodt-packet-shell.json").read_text())
        for field in ["family", "gap_id", "recommended_skill", "allowed_files_pattern",
                      "forbidden_files", "enforcement_tier", "limitations"]:
            assert field in s, f"Missing: {field}"

    def test_netpbm_shell_has_required_fields(self):
        s = json.loads((SPRINT_DIR / "netpbm-packet-shell.json").read_text())
        for field in ["family", "gap_id", "recommended_skill", "allowed_files_pattern",
                      "forbidden_files", "enforcement_tier", "limitations"]:
            assert field in s, f"Missing: {field}"


# ---------------------------------------------------------------------------
# 10. FODT shell forbids unrelated paths
# ---------------------------------------------------------------------------
class TestFodtShellForbidsUnrelatedPaths:
    def test_fodt_shell_forbids_src_python(self):
        s = json.loads((SPRINT_DIR / "fodt-packet-shell.json").read_text())
        forbidden = s["forbidden_files"]
        assert any("python" in f for f in forbidden)

    def test_fodt_shell_forbids_fods(self):
        s = json.loads((SPRINT_DIR / "fodt-packet-shell.json").read_text())
        forbidden = s["forbidden_files"]
        assert any("fods" in f for f in forbidden)

    def test_fodt_shell_forbids_registry(self):
        s = json.loads((SPRINT_DIR / "fodt-packet-shell.json").read_text())
        forbidden = s["forbidden_files"]
        assert any("registry" in f for f in forbidden)

    def test_fodt_shell_uses_proposed_delta(self):
        s = json.loads((SPRINT_DIR / "fodt-packet-shell.json").read_text())
        assert "proposed_capability_delta" in s
        assert s["proposed_capability_delta"].get("authority_update_required") is False


# ---------------------------------------------------------------------------
# 11. Netpbm shell forbids unrelated paths
# ---------------------------------------------------------------------------
class TestNetpbmShellForbidsUnrelatedPaths:
    def test_netpbm_shell_forbids_src_python(self):
        s = json.loads((SPRINT_DIR / "netpbm-packet-shell.json").read_text())
        forbidden = s["forbidden_files"]
        assert any("python" in f for f in forbidden)

    def test_netpbm_shell_forbids_fodt(self):
        s = json.loads((SPRINT_DIR / "netpbm-packet-shell.json").read_text())
        forbidden = s["forbidden_files"]
        assert any("fodt" in f for f in forbidden)

    def test_netpbm_shell_forbids_registry(self):
        s = json.loads((SPRINT_DIR / "netpbm-packet-shell.json").read_text())
        forbidden = s["forbidden_files"]
        assert any("registry" in f for f in forbidden)

    def test_netpbm_shell_uses_proposed_delta(self):
        s = json.loads((SPRINT_DIR / "netpbm-packet-shell.json").read_text())
        assert "proposed_capability_delta" in s
        assert s["proposed_capability_delta"].get("authority_update_required") is False


# ---------------------------------------------------------------------------
# 12. Product breadth index has 3 families
# ---------------------------------------------------------------------------
class TestProductBreadthIndex:
    def test_breadth_index_exists(self):
        assert (SPRINT_DIR / "product-breadth-packet-index.json").exists()

    def test_breadth_index_has_3_families(self):
        idx = json.loads((SPRINT_DIR / "product-breadth-packet-index.json").read_text())
        assert len(idx["families_covered"]) == 3

    def test_breadth_index_covers_fods_fodt_netpbm(self):
        idx = json.loads((SPRINT_DIR / "product-breadth-packet-index.json").read_text())
        families = idx["families_covered"]
        assert "FODS" in families
        assert "FODT" in families
        assert "Netpbm" in families

    def test_breadth_fods_is_full_packet(self):
        idx = json.loads((SPRINT_DIR / "product-breadth-packet-index.json").read_text())
        fods = next(p for p in idx["packets"] if p["family"] == "FODS")
        assert fods["packet_type"] == "FULL"

    def test_breadth_requirement_met(self):
        idx = json.loads((SPRINT_DIR / "product-breadth-packet-index.json").read_text())
        assert idx["breadth_requirement_met"] is True


# ---------------------------------------------------------------------------
# 13. Superpowers install absent
# ---------------------------------------------------------------------------
class TestSuperpowersInstallAbsent:
    def test_no_plugin_install_proof_exists(self):
        assert (SKILLS_DIR / "raw-logs" / "no-plugin-install-proof.txt").exists()

    def test_previous_proof_says_verified(self):
        text = (SKILLS_DIR / "raw-logs" / "no-plugin-install-proof.txt").read_text()
        assert "VERIFIED" in text

    def test_superpowers_decision_is_no_install(self):
        ev = json.loads((SKILLS_DIR / "superpowers-marketplace-evaluation.json").read_text())
        assert ev["overall_decision"] == "NO_INSTALL_THIS_SPRINT"

    def test_hardening_proof_exists(self):
        assert (SPRINT_DIR / "no-plugin-install-hardening-proof.md").exists()


# ---------------------------------------------------------------------------
# 14. .claude-plugin mutation absent
# ---------------------------------------------------------------------------
class TestClaudePluginMutationAbsent:
    def test_plugin_dir_does_not_exist(self):
        assert not (REPO_ROOT / ".claude-plugin").exists()

    def test_git_shows_no_plugin_changes(self):
        result = subprocess.run(
            ["git", "diff", "--diff-filter=A", "--name-only", "--", ".claude-plugin"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        assert result.stdout.strip() == ""

    def test_no_plugin_mutation_logged(self):
        text = (SPRINT_DIR / "external-skill-boundary-hardening.md").read_text()
        assert "DOES NOT EXIST" in text or "False" in text


# ---------------------------------------------------------------------------
# 15. External skill wrapper authority_state is skill_draft
# ---------------------------------------------------------------------------
class TestExternalSkillWrapperAuthority:
    def test_wrapper_template_exists(self):
        assert (TEMPLATES_DIR / "external-skill-wrapper-template.md").exists()

    def test_wrapper_has_authority_boundary(self):
        text = (TEMPLATES_DIR / "external-skill-wrapper-template.md").read_text()
        assert "authority" in text.lower() and "boundary" in text.lower()

    def test_wrapper_references_skill_draft(self):
        text = (TEMPLATES_DIR / "external-skill-wrapper-template.md").read_text()
        assert "skill_draft" in text

    def test_normalization_map_has_zero_active(self):
        m = json.loads((SKILLS_DIR / "local-skill-normalization-map.json").read_text())
        active = [s for s in m["skills"] if s.get("status") == "active"]
        assert len(active) == 0

    def test_wrapper_has_stop_conditions(self):
        text = (TEMPLATES_DIR / "external-skill-wrapper-template.md").read_text()
        assert "Stop" in text


# ---------------------------------------------------------------------------
# 16. No MCP registration
# ---------------------------------------------------------------------------
class TestNoMcpRegistration:
    def test_external_skill_fixtures_show_no_mcp(self):
        r = json.loads((SPRINT_DIR / "external-skill-fixture-results.json").read_text())
        mcp_check = next(e for e in r["results"] if e["check_id"] == "EXT-003")
        assert mcp_check["result"] == "PASS"

    def test_no_new_mcp_server_files(self):
        result = subprocess.run(
            ["git", "diff", "--diff-filter=A", "--name-only", "--", ".vscode/mcp.json"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        assert result.stdout.strip() == ""

    def test_boundary_hardening_confirms_no_mcp(self):
        text = (SPRINT_DIR / "external-skill-boundary-hardening.md").read_text()
        assert "No MCP registration" in text


# ---------------------------------------------------------------------------
# 17. No product source edits
# ---------------------------------------------------------------------------
class TestNoProductSourceEdits:
    def test_no_new_files_in_src_net(self):
        result = subprocess.run(
            ["git", "diff", "--diff-filter=A", "--name-only", "--", "src/net"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        assert result.stdout.strip() == ""

    def test_no_new_files_in_src_python(self):
        result = subprocess.run(
            ["git", "diff", "--diff-filter=A", "--name-only", "--", "src/python"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        assert result.stdout.strip() == ""

    def test_no_new_files_in_tests_net(self):
        result = subprocess.run(
            ["git", "diff", "--diff-filter=A", "--name-only", "--", "tests/net"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        assert result.stdout.strip() == ""

    def test_no_new_files_in_tests_python(self):
        result = subprocess.run(
            ["git", "diff", "--diff-filter=A", "--name-only", "--", "tests/python"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        assert result.stdout.strip() == ""

    def test_sprint_output_in_hardening_dir(self):
        # All hardening sprint output should be in allowed paths
        new_files = subprocess.run(
            ["git", "diff", "--diff-filter=A", "--name-only"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        ).stdout.strip().splitlines()
        for f in new_files:
            allowed = (
                f.startswith("reports/skills-governed-execution-hardening/")
                or f.startswith("tests/supervisor/test_skills_governed_execution_hardening")
                or f.startswith(".local/evidences/skills-governed-execution-hardening/")
                or f.startswith(".local/supervisor/reviews/skills-governed-execution-hardening/")
                or f.startswith("reports/skills-product-first/")
                or f.startswith("reports/supervisor/")
                or f.startswith(".local/supervisor/")
                or f.startswith(".supervisor/")
            )
            assert allowed, f"Unexpected new file outside allowed paths: {f}"
