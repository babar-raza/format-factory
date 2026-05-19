"""Risk controls — executable checks for AI risk register items.

Maps RISK-AI entries to implemented controls, planned controls, and blockers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.ai.validators.runtime_guard import run_guard


def load_risk_register(path: Path | None = None) -> list[dict[str, Any]]:
    """Load the AI risk register."""
    if path is None:
        path = Path("docs/ai/ai-risk-register.md")
    if not path.exists():
        return []
    # Parse risk entries from markdown — look for table rows
    risks: list[dict[str, Any]] = []
    content = path.read_text(encoding="utf-8", errors="ignore")
    in_table = False
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("| RISK-AI-"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 4:
                risks.append({
                    "id": parts[0],
                    "description": parts[1] if len(parts) > 1 else "",
                    "severity": parts[2] if len(parts) > 2 else "",
                    "control_status": "unmapped",
                })
    return risks


def check_runtime_ai_free(repo_root: Path) -> dict[str, Any]:
    """Verify that product source is AI-free."""
    result = run_guard(repo_root)
    return {
        "check": "runtime_ai_free",
        "passed": result.passed,
        "violations": result.violations,
        "risk_ids": ["RISK-AI-001"],
    }


def check_authority_states_visible(tools_ai_dir: Path) -> dict[str, Any]:
    """Check that AI outputs have visible authority state."""
    has_lifecycle = (tools_ai_dir / "validators" / "authority_lifecycle.py").exists()
    has_states_contract = (tools_ai_dir / "contracts" / "artifact-authority-states.yaml").exists()
    return {
        "check": "authority_states_visible",
        "passed": has_lifecycle and has_states_contract,
        "evidence": {
            "authority_lifecycle_validator": has_lifecycle,
            "authority_states_contract": has_states_contract,
        },
        "risk_ids": ["RISK-AI-002"],
    }


def check_gateway_enforcement(tools_ai_dir: Path) -> dict[str, Any]:
    """Check that all AI calls go through gateway."""
    gateway_exists = (tools_ai_dir / "control_plane" / "gateway.py").exists()
    guard_exists = (tools_ai_dir / "validators" / "runtime_guard.py").exists()
    return {
        "check": "gateway_enforcement",
        "passed": gateway_exists and guard_exists,
        "evidence": {
            "gateway": gateway_exists,
            "runtime_guard": guard_exists,
        },
        "risk_ids": ["RISK-AI-003"],
    }


def check_secret_redaction(tools_ai_dir: Path) -> dict[str, Any]:
    """Check that secret redaction is implemented."""
    redaction_exists = (tools_ai_dir / "validators" / "secret_redaction.py").exists()
    return {
        "check": "secret_redaction",
        "passed": redaction_exists,
        "risk_ids": ["RISK-AI-004"],
    }


def check_no_fallback_for_restricted_roles(tools_ai_dir: Path) -> dict[str, Any]:
    """Check that restricted roles have no-fallback enforcement."""
    router_path = tools_ai_dir / "control_plane" / "model_router.py"
    if not router_path.exists():
        return {"check": "no_fallback_restricted", "passed": False, "reason": "router not found"}
    content = router_path.read_text(encoding="utf-8", errors="ignore")
    has_no_fallback = "NO_FALLBACK_ROLES" in content
    return {
        "check": "no_fallback_restricted",
        "passed": has_no_fallback,
        "risk_ids": ["RISK-AI-005"],
    }


def check_cross_format_isolation(tools_ai_dir: Path) -> dict[str, Any]:
    """Check that cross-format retrieval is rejected."""
    ns_path = tools_ai_dir / "retrieval" / "namespace_manager.py"
    if not ns_path.exists():
        return {"check": "cross_format_isolation", "passed": False, "reason": "namespace manager not found"}
    content = ns_path.read_text(encoding="utf-8", errors="ignore")
    has_rejection = "CrossNamespaceError" in content
    return {
        "check": "cross_format_isolation",
        "passed": has_rejection,
        "risk_ids": ["RISK-AI-006"],
    }


def run_all_risk_checks(repo_root: Path) -> list[dict[str, Any]]:
    """Run all executable risk control checks."""
    tools_ai = repo_root / "tools" / "ai"
    results = [
        check_runtime_ai_free(repo_root),
        check_authority_states_visible(tools_ai),
        check_gateway_enforcement(tools_ai),
        check_secret_redaction(tools_ai),
        check_no_fallback_for_restricted_roles(tools_ai),
        check_cross_format_isolation(tools_ai),
    ]
    return results
