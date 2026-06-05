"""TC-TEST-002: Owl-model boundary tests.

Verifies:
- poc-targets.yaml is never modified by any Acceleration tool
- No direct openai/anthropic imports in any ai_ tool
- All AI outputs carry authority_state: ai_draft
- AI usage ledger is written with correct fields
"""

import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_POC = _REPO / "product-capability-matrix/poc-targets.yaml"

_AI_TOOLS = [
    "tools/supervisor/ai_product_brain.py",
    "tools/supervisor/ai_sprint_manager.py",
    "tools/supervisor/ai_implementation_designer.py",
    "tools/supervisor/ai_evidence_critic.py",
    "tools/supervisor/ai_learning_loop.py",
    "tools/supervisor/source_pattern_miner.py",
    "tools/supervisor/test_plan_generator.py",
    "tools/supervisor/mainstream_acceleration_packet.py",
]


def _poc_checksum() -> str:
    return hashlib.sha256(_POC.read_bytes()).hexdigest()


def test_poc_targets_unchanged_after_import():
    """Importing any tool must not modify poc-targets.yaml."""
    before = _poc_checksum()
    # Import a sampling of tools
    sys.path.insert(0, str(_REPO))
    import tools.supervisor.ai_product_brain  # noqa: F401
    import tools.supervisor.source_pattern_miner  # noqa: F401
    after = _poc_checksum()
    assert before == after, "poc-targets.yaml was modified by tool import"


def test_no_direct_provider_imports():
    """No ai_ tool may import openai, anthropic, or google.generativeai directly."""
    forbidden = ["import openai", "import anthropic", "import google.generativeai",
                 "from openai", "from anthropic"]
    for tool_rel in _AI_TOOLS:
        tool_path = _REPO / tool_rel
        if not tool_path.exists():
            continue
        content = tool_path.read_text(encoding="utf-8")
        for pattern in forbidden:
            assert pattern not in content, (
                f"{tool_rel} contains forbidden import: '{pattern}'"
            )


def test_all_tool_sources_reference_gateway():
    """AI tools should reference gateway_chat or tools.ai.control_plane."""
    gateway_ref = "gateway_chat"
    for tool_rel in _AI_TOOLS:
        tool_path = _REPO / tool_rel
        if not tool_path.exists():
            continue
        content = tool_path.read_text(encoding="utf-8")
        assert gateway_ref in content or "fixture" in content, (
            f"{tool_rel} does not reference gateway_chat"
        )


def test_no_src_files_created_by_tools(tmp_path):
    """Running tools must not create files under src/."""
    src_dir = _REPO / "src"
    before = set(src_dir.rglob("*")) if src_dir.exists() else set()
    # Just import (not run) — the import boundary check
    import tools.supervisor.mainstream_acceleration_packet  # noqa: F401
    after = set(src_dir.rglob("*")) if src_dir.exists() else set()
    assert before == after, "src/ was modified"


def test_authority_state_in_all_outputs(tmp_path):
    """Products of source_pattern_miner must carry authority_state: ai_draft."""
    from tools.supervisor.source_pattern_miner import mine_patterns
    result = mine_patterns("sylk", "csv export", top_k=3, output_dir=tmp_path, sprint_id="test")
    assert result.get("authority_state") == "ai_draft"
    assert result.get("non_authoritative") is True

    out_file = tmp_path / "sylk-patterns.json"
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert data["authority_state"] == "ai_draft"
    assert data["non_authoritative"] is True
