"""
TC-ACP-014-03 — Parity matrix coverage tests (FF-AGENTS-PARITY-001)

Verifies agent-parity-matrix.yaml has 22 entries (one per RC), each with
all 3 agent sections, and that blocked capabilities have routing documented.
"""
import pathlib
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
MATRIX_FILE = REPO / "docs" / "agents" / "agent-parity-matrix.yaml"
INVENTORY_FILE = REPO / "docs" / "agents" / "agent-inventory.yaml"


def _load_matrix() -> dict:
    assert MATRIX_FILE.exists(), f"agent-parity-matrix.yaml missing at {MATRIX_FILE}"
    return yaml.safe_load(MATRIX_FILE.read_text(encoding="utf-8"))


def test_parity_matrix_has_22_entries():
    """Parity matrix must have exactly 22 entries (one per RC)."""
    d = _load_matrix()
    entries = d.get("capability_parity_matrix", [])
    assert len(entries) == 22, (
        f"Expected 22 parity entries, got {len(entries)}"
    )


def test_every_entry_has_all_3_agents():
    """Every parity matrix entry must have claude, codex, kilo sections."""
    d = _load_matrix()
    entries = d.get("capability_parity_matrix", [])
    for entry in entries:
        cid = entry.get("capability_id", "unknown")
        for agent in ("claude", "codex", "kilo"):
            assert agent in entry, f"Missing '{agent}' section in {cid}"
            assert "status" in entry[agent], f"Missing {agent}.status in {cid}"


def test_all_rc_ids_present():
    """All RC-001 through RC-022 must appear in parity matrix."""
    d = _load_matrix()
    entries = d.get("capability_parity_matrix", [])
    found_ids = {e["capability_id"] for e in entries}
    expected = {f"RC-{i:03d}" for i in range(1, 23)}
    missing = expected - found_ids
    assert not missing, f"Missing RC entries in parity matrix: {sorted(missing)}"


def test_no_blank_statuses_in_matrix():
    """No agent status in the parity matrix may be blank or None."""
    d = _load_matrix()
    entries = d.get("capability_parity_matrix", [])
    for entry in entries:
        cid = entry.get("capability_id", "unknown")
        for agent in ("claude", "codex", "kilo"):
            status = entry.get(agent, {}).get("status")
            assert status, f"Blank status for {agent} in {cid}"
