"""
Tests for external tool governance integration (TC-EXT-001).
Verifies detection, classification, and authority boundary enforcement.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))



class TestExternalToolDetection:

    def test_detect_external_tools_returns_dict(self, tmp_path):
        from external_tool_governance import detect_external_tools
        result = detect_external_tools(tmp_path)
        assert isinstance(result, dict)
        assert "claude_flow_ruflo" in result
        assert "superpowers" in result
        assert "ghidra_mcp" in result

    def test_detect_reads_repo_root(self, tmp_path):
        """detect_external_tools is a read-only scan — safe to call on a tmp dir."""
        from external_tool_governance import detect_external_tools
        result = detect_external_tools(tmp_path)
        # No mcp.json in tmp_path → ruflo not detected there
        assert isinstance(result, dict)


class TestRufloClassification:

    def test_ruflo_absent_mode(self):
        from external_tool_governance import classify_ruflo_mode
        detection = {"claude_flow_ruflo": {"mcp_registered": False, "state_directory_present": False}}
        result = classify_ruflo_mode(detection)
        assert result == "ABSENT"

    def test_ruflo_detected_not_configured(self):
        from external_tool_governance import classify_ruflo_mode
        detection = {"claude_flow_ruflo": {"mcp_registered": True, "state_directory_present": False}}
        result = classify_ruflo_mode(detection)
        assert result == "DETECTED_NOT_CONFIGURED"

    def test_ruflo_verdict_absent(self):
        from external_tool_governance import get_ruflo_verdict
        verdict = get_ruflo_verdict("ABSENT")
        assert verdict == "RUFLO_ABSENT_CONTINUE_WITH_LOCAL_COORDINATOR"

    def test_ruflo_verdict_detected_not_configured(self):
        from external_tool_governance import get_ruflo_verdict
        verdict = get_ruflo_verdict("DETECTED_NOT_CONFIGURED")
        assert "APPROVAL_REQUIRED" in verdict


class TestExternalToolAuthority:

    def test_output_cannot_close_taskcard(self):
        from external_tool_governance import validate_external_tool_output_authority
        output = {"closes_taskcard": True, "approves_continuation": False}
        assert validate_external_tool_output_authority(output) is False

    def test_output_cannot_approve_continuation(self):
        from external_tool_governance import validate_external_tool_output_authority
        output = {"closes_taskcard": False, "approves_continuation": True}
        assert validate_external_tool_output_authority(output) is False

    def test_output_without_authority_claims_is_valid(self):
        from external_tool_governance import validate_external_tool_output_authority
        output = {"closes_taskcard": False, "approves_continuation": False, "data": "advisory only"}
        assert validate_external_tool_output_authority(output) is True

    def test_missing_closes_taskcard_field_defaults_safe(self):
        from external_tool_governance import validate_external_tool_output_authority
        output = {}
        assert validate_external_tool_output_authority(output) is True


class TestSuperpowersClassification:

    def test_superpowers_absent(self):
        from external_tool_governance import classify_superpowers_mode
        detection = {"superpowers": {"detected": False, "installed_plugins": []}}
        result = classify_superpowers_mode(detection)
        assert result == "ABSENT"

    def test_superpowers_installed_not_governed(self):
        from external_tool_governance import classify_superpowers_mode
        detection = {"superpowers": {"detected": True, "governed": False}}
        result = classify_superpowers_mode(detection)
        assert result in ("INSTALLED_NOT_GOVERNED", "INSTALLED_GOVERNED")


class TestGhidraMCPClassification:

    def test_ghidra_absent_disabled_default(self):
        from external_tool_governance import classify_ghidramcp_mode
        detection = {"ghidra_mcp": {"detected": False, "mcp_registered": False}}
        result = classify_ghidramcp_mode(detection)
        assert result in ("ABSENT", "DISABLED_DEFAULT")

    def test_ghidra_registered_without_authorization(self):
        from external_tool_governance import classify_ghidramcp_mode
        detection = {"ghidra_mcp": {"detected": True, "mcp_registered": True, "authorized_binary": False}}
        result = classify_ghidramcp_mode(detection)
        assert result == "BLOCKED_NEEDS_AUTHORIZATION"


class TestGovernanceVerdictBuilder:

    def test_build_verdict_schema(self):
        from external_tool_governance import build_external_tool_governance_verdict
        detections = {
            "claude_flow_ruflo": {"mcp_registered": True, "state_directory_present": False},
            "task_master_ai": {"mcp_registered": True},
            "superpowers": {"detected": False},
            "ghidra_mcp": {"detected": False, "mcp_registered": False},
        }
        verdict = build_external_tool_governance_verdict(detections)
        assert "overall_verdict" in verdict
        assert "deterministic_supervisor_retains_authority" in verdict
        assert verdict["deterministic_supervisor_retains_authority"] is True

    def test_no_invocations_verdict(self):
        from external_tool_governance import build_external_tool_governance_verdict
        detections = {
            "claude_flow_ruflo": {"mcp_registered": False, "state_directory_present": False},
            "task_master_ai": {"mcp_registered": False},
            "superpowers": {"detected": False},
            "ghidra_mcp": {"detected": False, "mcp_registered": False},
        }
        verdict = build_external_tool_governance_verdict(detections)
        assert verdict["deterministic_supervisor_retains_authority"] is True
