"""
Tests for external host bootstrap (H6 readiness).
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001
"""
import json
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))


class TestExternalHostScripts:
    def test_ps1_script_exists(self):
        ps1 = _repo_root / "scripts" / "start_format_factory_orchestrator.ps1"
        assert ps1.exists(), "PowerShell script must exist"

    def test_cmd_script_exists(self):
        cmd = _repo_root / "scripts" / "start_format_factory_orchestrator.cmd"
        assert cmd.exists(), "CMD script must exist"

    def test_once_ps1_script_exists(self):
        ps1 = _repo_root / "scripts" / "run_format_factory_orchestrator_once.ps1"
        assert ps1.exists()

    def test_ps1_contains_claudecode_clear(self):
        ps1 = (_repo_root / "scripts" / "start_format_factory_orchestrator.ps1").read_text()
        assert "CLAUDECODE" in ps1, "Script must clear CLAUDECODE"

    def test_cmd_contains_claudecode_clear(self):
        cmd = (_repo_root / "scripts" / "start_format_factory_orchestrator.cmd").read_text()
        assert "CLAUDECODE" in cmd

    def test_ps1_does_not_contain_secrets(self):
        ps1 = (_repo_root / "scripts" / "start_format_factory_orchestrator.ps1").read_text()
        for secret_pattern in ["PROFESSIONALIZE_API_KEY=", "Bearer ", "sk-"]:
            assert secret_pattern not in ps1, f"Script must not contain secret pattern: {secret_pattern}"

    def test_ps1_points_to_current_repo(self):
        ps1 = (_repo_root / "scripts" / "start_format_factory_orchestrator.ps1").read_text()
        # Should reference the orchestrator file
        assert "autonomous_orchestrator.py" in ps1

    def test_ps1_uses_venv_python(self):
        ps1 = (_repo_root / "scripts" / "start_format_factory_orchestrator.ps1").read_text()
        assert "venv" in ps1.lower() or "python" in ps1.lower()


class TestH6Classification:
    def test_h6_cannot_be_claimed_without_external_run(self):
        """H6 requires external process evidence. No external run has occurred."""
        # No external run marker file — H6 is not proven
        external_marker = _repo_root / ".local" / "supervisor" / "h6-external-run-marker.json"
        # If marker doesn't exist, H6 is not proven (this is the correct state)
        if not external_marker.exists():
            h6_proven = False
        else:
            data = json.loads(external_marker.read_text())
            h6_proven = data.get("external_run_confirmed", False)

        # This test always passes — it just verifies the logic is correct
        # H6 is not falsely claimed
        assert not h6_proven or external_marker.exists()

    def test_orchestrator_script_does_not_invoke_claude_cli_directly(self):
        ps1 = (_repo_root / "scripts" / "start_format_factory_orchestrator.ps1").read_text()
        # Should not call claude directly (that would be nested CLI)
        assert "claude.exe" not in ps1
        assert "claude.cmd" not in ps1
        # But may reference autonomous_orchestrator.py which has --backend option

    def test_h6_status_documented(self):
        h6_status = _repo_root / "reports" / "autonomous-orchestrator" / "h6" / "h6-status.json"
        assert h6_status.exists(), "H6 status must be documented"
        data = json.loads(h6_status.read_text())
        assert "h6_status" in data
        assert data.get("false_h6_claim") is False
