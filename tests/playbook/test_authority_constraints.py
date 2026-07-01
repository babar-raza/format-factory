"""
test_authority_constraints.py — TC-PB-009: Authority Constraint Tests

Verifies that playbook contracts and generated taskcards cannot claim
gate approval authority, plan override, or evidence contract replacement.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "playbook"))


def _get_playbook_contracts():
    """Parse all playbook contracts from Markdown front-matter."""
    import re
    import yaml
    contracts = []
    pb_dir = _REPO / "playbooks" / "format-factory"
    if not pb_dir.exists():
        return contracts
    for md_file in pb_dir.glob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        m = re.search(r"<!--\s*\n(playbook_contract:.*?)-->", text, re.DOTALL)
        if m:
            data = yaml.safe_load(m.group(1))
            if isinstance(data, dict) and "playbook_contract" in data:
                entry = data["playbook_contract"]
                entry["_source"] = md_file.name
                contracts.append(entry)
    return contracts


class TestPlaybookGateAuthority:
    """Playbook contracts must not claim gate approval authority."""

    def test_all_active_playbooks_have_limitations(self):
        contracts = _get_playbook_contracts()
        active = [c for c in contracts if c.get("status", "").upper() == "ACTIVE"]
        assert len(active) > 0, "Expected at least one ACTIVE playbook contract"
        for c in active:
            assert c.get("limitations"), (
                f"{c.get('_source')}: active playbook must have limitations list"
            )

    def test_no_gate_approval_in_limitations(self):
        contracts = _get_playbook_contracts()
        for c in contracts:
            if c.get("status", "").upper() != "ACTIVE":
                continue
            limitations = c.get("limitations", [])
            has_gate_prohibition = any(
                "gate approval" in str(lim).lower() for lim in limitations
            )
            assert has_gate_prohibition, (
                f"{c.get('_source')}: must include 'No gate approval authority' in limitations"
            )

    def test_no_evidence_contract_replacement(self):
        contracts = _get_playbook_contracts()
        for c in contracts:
            if c.get("status", "").upper() != "ACTIVE":
                continue
            limitations = c.get("limitations", [])
            has_no_contract_replacement = any(
                "evidence contract" in str(lim).lower() for lim in limitations
            )
            assert has_no_contract_replacement, (
                f"{c.get('_source')}: must include 'No evidence contract replacement' in limitations"
            )

    def test_authority_field_is_task_template(self):
        contracts = _get_playbook_contracts()
        for c in contracts:
            if c.get("status", "").upper() != "ACTIVE":
                continue
            authority = c.get("authority", "")
            assert authority == "TASK_TEMPLATE", (
                f"{c.get('_source')}: authority must be TASK_TEMPLATE, got '{authority}'"
            )


class TestTaskcardAuthority:
    """Generated taskcards must carry authority_constraints with all false flags."""

    def test_generated_taskcard_has_authority_constraints(self):
        from generate_playbook_taskcards import parse_contract, generate_taskcards
        pb_path = _REPO / "playbooks" / "format-factory" / "format-feature-expansion.md"
        if not pb_path.exists():
            pytest.skip("format-feature-expansion.md not found")
        params = {
            "format_name": "tsv",
            "codec_file": "src/python/tsv/tsv_parser.py",
            "init_file": "src/python/tsv/__init__.py",
            "test_dir": "tests/python/tsv/",
            "function_name": "export_to_csv",
            "function_signature": "(source) -> str",
            "capability_label": "CSV_EXPORT",
        }
        contract = parse_contract(pb_path)
        taskcards = generate_taskcards(contract, plan_id="TEST-001", gap_ids=[], parameters=params)
        assert len(taskcards) > 0, "Expected at least one taskcard"
        for tc in taskcards:
            ac = tc.get("authority_constraints", {})
            assert ac.get("no_gate_approval") is True
            assert ac.get("no_mark_work_complete_without_evidence") is True
            assert ac.get("no_plan_override") is True
            assert ac.get("no_evidence_contract_replacement") is True
            assert len(ac.get("limitations", [])) > 0

    def test_taskcard_cannot_approve_gates(self):
        """Verify no field in generated taskcards contains gate-approval semantics."""
        from generate_playbook_taskcards import parse_contract, generate_taskcards
        pb_path = _REPO / "playbooks" / "format-factory" / "format-feature-expansion.md"
        if not pb_path.exists():
            pytest.skip("format-feature-expansion.md not found")
        params = {
            "format_name": "tsv",
            "codec_file": "src/python/tsv/tsv_parser.py",
            "init_file": "src/python/tsv/__init__.py",
            "test_dir": "tests/python/tsv/",
            "function_name": "export_to_csv",
            "function_signature": "(source) -> str",
            "capability_label": "CSV_EXPORT",
        }
        contract = parse_contract(pb_path)
        taskcards = generate_taskcards(contract, plan_id="TEST-001", gap_ids=[], parameters=params)
        for tc in taskcards:
            serialized = str(tc)
            assert "gate_approved" not in serialized.lower()
            assert "approve_gate" not in serialized.lower()
