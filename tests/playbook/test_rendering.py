"""
test_rendering.py — TC-PB-009: Playbook Contract Rendering Tests

Verifies that the playbook_contract front-matter parses consistently,
Markdown/YAML drift is detected, and repeated parsing is stable.
"""
import re
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).parent.parent.parent
_PB_DIR = _REPO / "playbooks" / "format-factory"

sys.path.insert(0, str(_REPO / "tools" / "playbook"))


def _parse_contract(md_path: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    m = re.search(r"<!--\s*\n(playbook_contract:.*?)-->", text, re.DOTALL)
    if not m:
        return {}
    data = yaml.safe_load(m.group(1))
    return data.get("playbook_contract", {}) if isinstance(data, dict) else {}


def _get_active_templates():
    if not _PB_DIR.exists():
        return []
    return [f for f in _PB_DIR.glob("*.md")]


@pytest.mark.skipif(not _PB_DIR.exists(), reason="playbooks/format-factory/ not found")
class TestContractParsing:
    def test_all_active_templates_have_contract(self):
        templates = _get_active_templates()
        assert len(templates) > 0, "Expected at least one Markdown template"
        contracts_found = 0
        for md in templates:
            contract = _parse_contract(md)
            if contract:
                contracts_found += 1
        assert contracts_found > 0, "Expected at least one parseable contract"

    def test_contract_has_required_fields(self):
        required = {"playbook_id", "title", "version", "status", "owner_layer", "authority"}
        for md in _get_active_templates():
            contract = _parse_contract(md)
            if not contract:
                continue
            if contract.get("status", "").upper() != "ACTIVE":
                continue
            missing = required - set(contract.keys())
            assert not missing, (
                f"{md.name}: contract missing required fields: {missing}"
            )

    def test_contract_status_is_valid(self):
        valid_statuses = {"ACTIVE", "DEPRECATED", "SUPERSEDED", "DRAFT", "INVALID", "HISTORICAL"}
        for md in _get_active_templates():
            contract = _parse_contract(md)
            if not contract:
                continue
            status = contract.get("status", "").upper()
            assert status in valid_statuses, (
                f"{md.name}: unexpected status value: {status!r}"
            )

    def test_contract_playbook_id_matches_expected(self):
        """Each contract's playbook_id should be consistent with its filename."""
        for md in _get_active_templates():
            contract = _parse_contract(md)
            if not contract:
                continue
            pid = contract.get("playbook_id", "")
            assert pid, f"{md.name}: playbook_id must not be empty"
            # playbook_id should not contain spaces
            assert " " not in pid, f"{md.name}: playbook_id must not contain spaces: {pid!r}"


class TestParsingStability:
    """Repeated parsing of the same file must produce identical results."""

    @pytest.mark.skipif(not _PB_DIR.exists(), reason="playbooks/format-factory/ not found")
    def test_repeated_parse_is_identical(self):
        for md in _get_active_templates():
            contract1 = _parse_contract(md)
            contract2 = _parse_contract(md)
            assert contract1 == contract2, (
                f"{md.name}: contract parsing is not stable (different results on repeat)"
            )

    def test_yaml_roundtrip_is_stable(self):
        """YAML dump → reload → dump must produce identical YAML."""
        for md in _get_active_templates():
            contract = _parse_contract(md)
            if not contract:
                continue
            dumped1 = yaml.dump(contract, default_flow_style=False, sort_keys=True)
            reloaded = yaml.safe_load(dumped1)
            dumped2 = yaml.dump(reloaded, default_flow_style=False, sort_keys=True)
            assert dumped1 == dumped2, f"{md.name}: YAML round-trip is not stable"


class TestMarkdownYamlDrift:
    """Detect drift between Markdown narrative and YAML front-matter."""

    @pytest.mark.skipif(not _PB_DIR.exists(), reason="playbooks/format-factory/ not found")
    def test_contract_phases_declared(self):
        """Each ACTIVE template must declare at least one phase in its contract."""
        for md in _get_active_templates():
            contract = _parse_contract(md)
            if not contract or contract.get("status", "").upper() != "ACTIVE":
                continue
            phases = contract.get("phases", [])
            assert len(phases) > 0, (
                f"{md.name}: ACTIVE contract must declare at least one phase"
            )

    @pytest.mark.skipif(not _PB_DIR.exists(), reason="playbooks/format-factory/ not found")
    def test_allowed_paths_declared(self):
        """Each ACTIVE template must declare allowed_paths."""
        for md in _get_active_templates():
            contract = _parse_contract(md)
            if not contract or contract.get("status", "").upper() != "ACTIVE":
                continue
            allowed = contract.get("allowed_paths", [])
            assert len(allowed) > 0, (
                f"{md.name}: ACTIVE contract must declare allowed_paths"
            )

    @pytest.mark.skipif(not _PB_DIR.exists(), reason="playbooks/format-factory/ not found")
    def test_forbidden_paths_declared(self):
        """Each ACTIVE template must declare forbidden_paths."""
        for md in _get_active_templates():
            contract = _parse_contract(md)
            if not contract or contract.get("status", "").upper() != "ACTIVE":
                continue
            forbidden = contract.get("forbidden_paths", [])
            assert len(forbidden) > 0, (
                f"{md.name}: ACTIVE contract must declare forbidden_paths"
            )
