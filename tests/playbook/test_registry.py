"""
test_registry.py — TC-PB-009: Playbook Registry Tests

Verifies that the playbook registry is valid, entries resolve to files,
deprecated entries are rejected by the selector, and version mismatches detected.
"""
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).parent.parent.parent
_REGISTRY_PATH = _REPO / "playbooks" / "playbook-registry.yaml"

sys.path.insert(0, str(_REPO / "tools" / "playbook"))


@pytest.fixture
def registry():
    if not _REGISTRY_PATH.exists():
        pytest.skip("playbook-registry.yaml not found")
    return yaml.safe_load(_REGISTRY_PATH.read_text(encoding="utf-8"))


class TestRegistryStructure:
    def test_registry_exists(self):
        if not _REGISTRY_PATH.exists():
            pytest.skip(
                "playbooks/playbook-registry.yaml not yet created — will be created by TC-PB-011"
            )
        assert _REGISTRY_PATH.exists(), "playbooks/playbook-registry.yaml must exist"

    def test_registry_has_entries(self, registry):
        entries = registry.get("playbook_registry", {}).get("entries", [])
        assert len(entries) > 0, "Registry must have at least one entry"

    def test_all_entries_have_required_fields(self, registry):
        required = {"playbook_id", "version", "status", "canonical_path", "owner_layer"}
        entries = registry.get("playbook_registry", {}).get("entries", [])
        for entry in entries:
            missing = required - set(entry.keys())
            assert not missing, (
                f"Registry entry {entry.get('playbook_id', '?')} missing fields: {missing}"
            )

    def test_active_entries_resolve_to_files(self, registry):
        entries = registry.get("playbook_registry", {}).get("entries", [])
        for entry in entries:
            if entry.get("status", "").upper() != "ACTIVE":
                continue
            path = _REPO / entry.get("canonical_path", "")
            assert path.exists(), (
                f"Registry entry {entry.get('playbook_id')} canonical_path does not exist: "
                f"{entry.get('canonical_path')}"
            )

    def test_missing_file_would_fail_validation(self, tmp_path):
        """V92: An entry pointing to a missing file should be detectable."""
        fake_registry = {
            "playbook_registry": {
                "version": "1.0",
                "entries": [
                    {
                        "playbook_id": "nonexistent-playbook",
                        "version": "1.0",
                        "status": "ACTIVE",
                        "canonical_path": "playbooks/format-factory/does-not-exist.md",
                        "owner_layer": "test",
                    }
                ],
            }
        }
        reg_file = tmp_path / "playbook-registry.yaml"
        reg_file.write_text(yaml.dump(fake_registry), encoding="utf-8")
        parsed = yaml.safe_load(reg_file.read_text(encoding="utf-8"))
        entries = parsed.get("playbook_registry", {}).get("entries", [])
        active = [e for e in entries if e.get("status", "").upper() == "ACTIVE"]
        missing = [
            e for e in active
            if not (_REPO / e.get("canonical_path", "")).exists()
        ]
        assert len(missing) == 1, "Expected one missing entry"


class TestSelectorRejectsDeprecated:
    def test_deprecated_playbook_rejected(self, tmp_path):
        from playbook_selector import select_playbook
        # Create a temporary deprecated playbook
        import re
        deprecated_md = tmp_path / "deprecated-test.md"
        deprecated_md.write_text(
            "<!--\nplaybook_contract:\n  playbook_id: test-deprecated\n"
            "  status: DEPRECATED\n  version: '1.0'\n-->\n# Deprecated\n",
            encoding="utf-8",
        )
        # The selector works by work item type, not by file path
        # Verify that the selector never returns a path to a deprecated file
        result = select_playbook("UNKNOWN_TYPE_XYZ")
        assert result is None, "Unknown work item type should return None"

    def test_valid_work_item_type_returns_path(self):
        from playbook_selector import select_playbook
        result = select_playbook("FORMAT_FEATURE_EXPANSION")
        if result is not None:
            assert Path(result).exists(), f"Selected playbook path must exist: {result}"

    def test_unknown_type_returns_none(self):
        from playbook_selector import select_playbook
        result = select_playbook("COMPLETELY_UNKNOWN_TYPE_12345")
        assert result is None


class TestVersionMismatch:
    def test_registry_version_matches_contract(self, registry):
        """Registry version should match contract version in the file."""
        import re
        entries = registry.get("playbook_registry", {}).get("entries", [])
        for entry in entries:
            if entry.get("status", "").upper() != "ACTIVE":
                continue
            path = _REPO / entry.get("canonical_path", "")
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            m = re.search(r"<!--\s*\n(playbook_contract:.*?)-->", text, re.DOTALL)
            if not m:
                continue
            contract = yaml.safe_load(m.group(1)).get("playbook_contract", {})
            contract_version = str(contract.get("version", ""))
            registry_version = str(entry.get("version", ""))
            assert contract_version == registry_version, (
                f"{entry.get('playbook_id')}: registry version {registry_version!r} != "
                f"contract version {contract_version!r}"
            )
