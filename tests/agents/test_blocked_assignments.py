"""
TC-ACP-014-04 — Blocked capability assignment tests (FF-AGENTS-PARITY-001)

Verifies that BLOCKED capabilities in agent-inventory.yaml have proper
limitations documented (not silently blocked without explanation).
"""
import pathlib
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
INVENTORY_FILE = REPO / "docs" / "agents" / "agent-inventory.yaml"


def _load_inventory() -> dict:
    assert INVENTORY_FILE.exists(), f"agent-inventory.yaml missing at {INVENTORY_FILE}"
    return yaml.safe_load(INVENTORY_FILE.read_text(encoding="utf-8"))


def test_codex_blocked_capabilities_documented():
    """Every codex-BLOCKED capability has limitations documented."""
    inv = _load_inventory()
    codex_blocked = [
        e for e in inv.get("implementations", [])
        if e.get("agent") == "codex" and e.get("current_status") == "BLOCKED"
    ]
    assert codex_blocked, "No BLOCKED codex entries found — expected at least RC-016, RC-017"
    for entry in codex_blocked:
        lims = entry.get("limitations", [])
        assert lims, (
            f"Missing limitations for BLOCKED codex entry {entry.get('capability_id')}"
        )


def test_kilo_blocked_capabilities_documented():
    """Every kilo-BLOCKED capability has limitations documented."""
    inv = _load_inventory()
    kilo_blocked = [
        e for e in inv.get("implementations", [])
        if e.get("agent") == "kilo" and e.get("current_status") == "BLOCKED"
    ]
    assert kilo_blocked, "No BLOCKED kilo entries found — expected at least RC-004, RC-016, RC-017"
    for entry in kilo_blocked:
        lims = entry.get("limitations", [])
        assert lims, (
            f"Missing limitations for BLOCKED kilo entry {entry.get('capability_id')}"
        )


def test_no_codex_entry_claims_complete_verified():
    """No codex entry may claim COMPLETE_VERIFIED (unverifiable without live instantiation)."""
    inv = _load_inventory()
    bad = [
        e for e in inv.get("implementations", [])
        if e.get("agent") == "codex" and e.get("current_status") == "COMPLETE_VERIFIED"
    ]
    assert not bad, (
        f"Codex entries incorrectly claiming COMPLETE_VERIFIED: "
        f"{[e['capability_id'] for e in bad]}"
    )


def test_no_kilo_entry_claims_complete_verified():
    """No kilo entry may claim COMPLETE_VERIFIED (platform unverifiable)."""
    inv = _load_inventory()
    bad = [
        e for e in inv.get("implementations", [])
        if e.get("agent") == "kilo" and e.get("current_status") == "COMPLETE_VERIFIED"
    ]
    assert not bad, (
        f"Kilo entries incorrectly claiming COMPLETE_VERIFIED: "
        f"{[e['capability_id'] for e in bad]}"
    )
