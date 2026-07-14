"""
TC-ACP-014-01 — Capability opt-in tests (FF-AGENTS-PARITY-001)

Verifies that inventory_capabilities.py uses opt-in (not opt-out) defaults
for codex and kilo agent surfaces, and that all active skills have agent_surfaces
documented in skill-registry.yaml.
"""
import pathlib
import yaml


REPO = pathlib.Path(__file__).resolve().parent.parent.parent
INVENTORY_PY = REPO / "tools" / "capability_sync" / "inventory_capabilities.py"
SKILL_REG = REPO / ".supervisor" / "skill-registry.yaml"


def test_no_skill_uses_opt_out_default():
    """Verify inventory_capabilities.py does not contain the banned opt-out pattern."""
    source = INVENTORY_PY.read_text(encoding="utf-8")
    # TC-ACP-002: replaced opt-out (codex_excluded) with opt-in (codex_supported)
    assert "not skill.get(\"codex_excluded" not in source, (
        "FAIL: opt-out pattern 'not skill.get(\"codex_excluded' still present "
        "in inventory_capabilities.py — TC-ACP-002 regression"
    )


def test_codex_opt_in_present_in_inventory():
    """Verify compute_agent_surfaces uses codex_supported (opt-in) not codex_excluded (opt-out)."""
    source = INVENTORY_PY.read_text(encoding="utf-8")
    assert "codex_supported" in source, (
        "FAIL: opt-in field 'codex_supported' not found in inventory_capabilities.py"
    )
    assert "kilo_supported" in source, (
        "FAIL: opt-in field 'kilo_supported' not found in inventory_capabilities.py"
    )


def test_all_active_skills_have_agent_surfaces_schema():
    """Verify skill-registry.yaml has skill_agent_surface_schema documenting opt-in fields."""
    reg = yaml.safe_load(SKILL_REG.read_text(encoding="utf-8"))
    assert "skill_agent_surface_schema" in reg, (
        "FAIL: skill_agent_surface_schema block missing from skill-registry.yaml — "
        "TC-ACP-002 requires opt-in field documentation"
    )
    schema = reg["skill_agent_surface_schema"]
    assert "codex_supported" in schema, "codex_supported field not in skill_agent_surface_schema"
    assert "kilo_supported" in schema, "kilo_supported field not in skill_agent_surface_schema"
