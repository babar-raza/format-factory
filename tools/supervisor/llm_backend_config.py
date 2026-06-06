"""
Format Factory — LLM Backend Config
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001

Reads LLM endpoint configuration from tools/llm/endpoints.yaml.
Never logs credential values.
"""
from __future__ import annotations
import os, sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))


ENDPOINTS_FILE = Path("tools/llm/endpoints.yaml")


def load_endpoints() -> List[Dict[str, Any]]:
    """Load endpoint configs from endpoints.yaml. Returns empty list on failure."""
    if not ENDPOINTS_FILE.exists():
        return []
    try:
        import yaml
        d = yaml.safe_load(ENDPOINTS_FILE.read_text(encoding="utf-8"))
        return d.get("endpoints", [])
    except Exception:
        return []


def get_ready_endpoints() -> List[Dict[str, Any]]:
    """
    Return endpoints that have credentials present.
    Never logs the credential values.
    """
    ready = []
    for ep in load_endpoints():
        if not ep.get("enabled", True):
            continue
        auth_env = ep.get("auth_env")
        if auth_env is None:
            # No auth required (local endpoints)
            ready.append({**ep, "_credential_status": "NOT_REQUIRED"})
        elif os.environ.get(auth_env):
            ready.append({**ep, "_credential_status": "PRESENT"})
        # else: skip silently — credential absent
    return ready


def classify_endpoint_availability(ep_id: str) -> str:
    """Classify a specific endpoint's availability."""
    for ep in load_endpoints():
        if ep.get("id") == ep_id:
            if not ep.get("enabled", True):
                return "DISABLED"
            auth_env = ep.get("auth_env")
            if auth_env is None:
                return "CONFIG_PRESENT_NO_AUTH_REQUIRED"
            elif os.environ.get(auth_env):
                return "CONFIG_PRESENT_CREDENTIAL_PRESENT"
            else:
                return "CONFIG_PRESENT_CREDENTIAL_ABSENT"
    return "NOT_FOUND"
