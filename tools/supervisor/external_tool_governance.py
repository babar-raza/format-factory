"""
external_tool_governance.py — Read-only detection and governance of external runtime tools.

Governs: Ruflo/claude-flow, Superpowers, GhidraMCP, task-master-ai.
All detection is read-only — no tool invocations, no installs, no MCP server starts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def detect_external_tools(repo_root: Path) -> dict[str, Any]:
    """Scan repo for Ruflo/claude-flow, Superpowers, GhidraMCP.

    Returns detection dict with mode and verdict per tool.
    Reads .vscode/mcp.json, checks for .claude-flow/, .claude-plugin/.
    Never invokes any tool. Read-only scan only.
    """
    result: dict[str, Any] = {}

    # Read mcp.json if present
    mcp_json_path = repo_root / ".vscode" / "mcp.json"
    mcp_servers: dict[str, Any] = {}
    if mcp_json_path.exists():
        try:
            mcp_servers = json.loads(mcp_json_path.read_text(encoding="utf-8")).get(
                "servers", {}
            )
        except (json.JSONDecodeError, OSError):
            pass

    # Ruflo / claude-flow detection
    claude_flow_registered = "claude-flow" in mcp_servers
    claude_flow_cmd = ""
    if claude_flow_registered:
        entry = mcp_servers["claude-flow"]
        args = entry.get("args", [])
        claude_flow_cmd = " ".join([entry.get("command", "")] + args)

    state_dir_present = (repo_root / ".claude-flow").exists()
    package_json_present = (repo_root / "package.json").exists()

    result["claude_flow_ruflo"] = {
        "detected": claude_flow_registered or state_dir_present,
        "mcp_registered": claude_flow_registered,
        "mcp_server_name": "claude-flow" if claude_flow_registered else None,
        "mcp_command": claude_flow_cmd if claude_flow_cmd else None,
        "state_directory_present": state_dir_present,
        "hooks_detected": False,  # hooks would be in claude config, not detectable here
        "daemon_detected": False,
        "package_json_present": package_json_present,
        "workspace_mutations": [],
        "auto_install_risk": "-y" in claude_flow_cmd,
    }

    # task-master-ai detection
    tm_registered = "task-master-ai" in mcp_servers
    tm_cmd = ""
    if tm_registered:
        entry = mcp_servers["task-master-ai"]
        args = entry.get("args", [])
        tm_cmd = " ".join([entry.get("command", "")] + args)

    result["task_master_ai"] = {
        "detected": tm_registered,
        "mcp_registered": tm_registered,
        "mcp_server_name": "task-master-ai" if tm_registered else None,
        "mcp_command": tm_cmd if tm_cmd else None,
        "auto_install_risk": "-y" in tm_cmd,
    }

    # Superpowers detection
    plugin_dir = repo_root / ".claude-plugin"
    plugins_present = plugin_dir.exists()
    result["superpowers"] = {
        "detected": plugins_present,
        "state_directory_present": plugins_present,
        "installed_plugins": list(plugin_dir.iterdir()) if plugins_present else [],
        "sessionstart_injection_detected": False,
    }

    # GhidraMCP detection
    ghidra_registered = "ghidra" in mcp_servers or "ghidra-mcp" in mcp_servers
    result["ghidra_mcp"] = {
        "detected": ghidra_registered,
        "mcp_registered": ghidra_registered,
    }

    return result


def classify_ruflo_mode(detection: dict[str, Any]) -> str:
    """Classify Ruflo/claude-flow operational mode.

    Returns: ABSENT | DETECTED_NOT_CONFIGURED | PLUGIN_LITE |
             FULL_LOOP_PRESENT_NOT_APPROVED | FULL_LOOP_APPROVED |
             DISABLED_DUE_RISK
    """
    cf = detection.get("claude_flow_ruflo", {})

    if not cf.get("detected") and not cf.get("mcp_registered"):
        return "ABSENT"

    state_dir = cf.get("state_directory_present", False)
    mcp_registered = cf.get("mcp_registered", False)

    if mcp_registered and not state_dir:
        return "DETECTED_NOT_CONFIGURED"

    if state_dir and not mcp_registered:
        return "PLUGIN_LITE"

    if state_dir and mcp_registered:
        # Would need explicit approval signal — absent by default
        return "FULL_LOOP_PRESENT_NOT_APPROVED"

    return "ABSENT"


def get_ruflo_verdict(mode: str) -> str:
    """Map Ruflo mode to governance verdict string."""
    verdicts = {
        "ABSENT": "RUFLO_ABSENT_CONTINUE_WITH_LOCAL_COORDINATOR",
        "DETECTED_NOT_CONFIGURED": "RUFLO_DETECTED_NOT_CONFIGURED_APPROVAL_REQUIRED_FOR_INVOCATION",
        "PLUGIN_LITE": "RUFLO_LITE_AVAILABLE_NOT_REQUIRED",
        "FULL_LOOP_PRESENT_NOT_APPROVED": "RUFLO_FULL_LOOP_BLOCKED_PENDING_APPROVAL",
        "FULL_LOOP_APPROVED": "RUFLO_FULL_LOOP_ALLOWED_AS_RUNTIME_ONLY",
        "DISABLED_DUE_RISK": "RUFLO_DISABLED_DUE_RISK",
    }
    return verdicts.get(mode, "RUFLO_UNKNOWN_MODE")


def validate_external_tool_output_authority(output: dict[str, Any]) -> bool:
    """Validate that external tool output does not claim forbidden authority.

    Returns False if output attempts to close taskcard or approve continuation.
    """
    if output.get("closes_taskcard"):
        return False
    if output.get("approves_continuation"):
        return False
    if output.get("authority_state") == "authoritative":
        return False
    return True


def classify_superpowers_mode(detection: dict[str, Any]) -> str:
    """Classify Superpowers plugin operational mode.

    Returns: ABSENT | INSTALLED_NOT_GOVERNED | INSTALLED_GOVERNED
    """
    sp = detection.get("superpowers", {})
    if not sp.get("detected"):
        return "ABSENT"
    if sp.get("sessionstart_injection_detected"):
        return "INSTALLED_NOT_GOVERNED"
    return "INSTALLED_GOVERNED"


def classify_ghidramcp_mode(detection: dict[str, Any]) -> str:
    """Classify GhidraMCP operational mode.

    Returns: ABSENT | DISABLED_DEFAULT | ALLOWED_AUTHORIZED_FIXTURE_ONLY |
             BLOCKED_NEEDS_AUTHORIZATION | REJECTED_FOR_POC
    """
    gm = detection.get("ghidra_mcp", {})
    if not gm.get("detected") and not gm.get("mcp_registered"):
        return "ABSENT"
    # If detected but no authorization provided
    if gm.get("mcp_registered") and not gm.get("authorized_binary_present"):
        return "BLOCKED_NEEDS_AUTHORIZATION"
    return "DISABLED_DEFAULT"


def build_external_tool_governance_verdict(detections: dict[str, Any]) -> dict[str, Any]:
    """Build the external-tool-governance-verdict.json content."""
    ruflo_mode = classify_ruflo_mode(detections)
    ruflo_verdict = get_ruflo_verdict(ruflo_mode)

    tm = detections.get("task_master_ai", {})
    tm_verdict = (
        "TASKMASTER_DETECTED_NOT_CONFIGURED_APPROVAL_REQUIRED_FOR_INVOCATION"
        if tm.get("mcp_registered")
        else "TASKMASTER_ABSENT"
    )

    sp_mode = classify_superpowers_mode(detections)
    sp_verdict = (
        "SUPERPOWERS_NOT_INSTALLED_EVALUATE_ONLY"
        if sp_mode == "ABSENT"
        else "SUPERPOWERS_INSTALLED_REQUIRES_GOVERNANCE"
    )

    gm_mode = classify_ghidramcp_mode(detections)
    gm_verdict = (
        "GHIDRA_MCP_DISABLED_DEFAULT"
        if gm_mode in ("ABSENT", "DISABLED_DEFAULT")
        else "GHIDRA_MCP_BLOCKED_NEEDS_AUTHORIZATION"
    )

    all_non_active = all([
        ruflo_mode in ("ABSENT", "DETECTED_NOT_CONFIGURED"),
        not tm.get("mcp_registered") or tm.get("mode") == "DETECTED_NOT_CONFIGURED",
        sp_mode == "ABSENT",
        gm_mode in ("ABSENT", "DISABLED_DEFAULT"),
    ])

    return {
        "claude_flow_ruflo": ruflo_verdict,
        "task_master_ai": tm_verdict,
        "superpowers": sp_verdict,
        "ghidra_mcp": gm_verdict,
        "overall_verdict": "EXTERNAL_TOOLS_GOVERNED_LOCAL_COORDINATOR_ACTIVE",
        "continuation_impact": "none — all external tools non-active" if all_non_active else "review required",
        "deterministic_supervisor_retains_authority": True,
    }
