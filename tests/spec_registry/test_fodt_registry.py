"""Tests for shared/qname-registry/fodt.yaml (TC-SRC-REVIEW-003)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
_TOOLS_SPEC = _REPO / "tools" / "spec"
if str(_TOOLS_SPEC) not in sys.path:
    sys.path.insert(0, str(_TOOLS_SPEC))

from validate_spec_registry import validate_registry  # noqa: E402

_REGISTRY = _REPO / "shared" / "qname-registry" / "fodt.yaml"

# All expected QNames in the FODT registry
EXPECTED_QNAMES = [
    "office:body",
    "text:p",
    "text:h",
    "text:span",
    "text:list",
    "text:list-item",
    "table:table",
    "table:table-row",
    "table:table-cell",
]


class TestFodtRegistryExists:
    def test_fodt_yaml_exists(self):
        """shared/qname-registry/fodt.yaml must exist."""
        assert _REGISTRY.exists(), f"fodt.yaml not found at {_REGISTRY}"

    def test_fodt_yaml_is_nonempty(self):
        """fodt.yaml must not be empty."""
        assert _REGISTRY.stat().st_size > 0, "fodt.yaml is empty"


class TestFodtRegistryContents:
    def _load_entries(self) -> list[dict]:
        try:
            import yaml
            data = yaml.safe_load(_REGISTRY.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except ImportError:
            pass
        # Minimal fallback
        entries: list[dict] = []
        current: dict = {}
        for line in _REGISTRY.read_text(encoding="utf-8").splitlines():
            if line.startswith("- "):
                if current:
                    entries.append(current)
                current = {}
                if ":" in line[2:]:
                    k, _, v = line[2:].strip().partition(":")
                    val = v.strip().strip('"').strip("'")
                    current[k.strip()] = None if val in ("null", "~", "") else val
            elif line.startswith("  ") and ":" in line:
                k, _, v = line.strip().partition(":")
                val = v.strip().strip('"').strip("'")
                if val.startswith("["):
                    current[k.strip()] = []
                else:
                    current[k.strip()] = None if val in ("null", "~", "") else val
        if current:
            entries.append(current)
        return entries

    def test_all_expected_qnames_present(self):
        """All 9 expected QNames must be present in fodt.yaml."""
        entries = self._load_entries()
        found_qnames = {e.get("qname") for e in entries}
        for qname in EXPECTED_QNAMES:
            assert qname in found_qnames, f"QName '{qname}' missing from fodt.yaml"

    def test_entry_count_is_9(self):
        """fodt.yaml must have exactly 9 entries."""
        entries = self._load_entries()
        assert len(entries) == 9, f"Expected 9 entries, got {len(entries)}"

    def test_all_required_fields_present(self):
        """All required fields must be present in every entry."""
        required = ["qname", "namespace_uri", "local_name", "canonical_class", "spec_fact_ref", "status", "source_layer"]
        entries = self._load_entries()
        for entry in entries:
            for field in required:
                assert field in entry and entry[field] is not None, (
                    f"Entry '{entry.get('qname', '?')}' missing required field '{field}'"
                )

    def test_office_body_has_null_python_file(self):
        """office:body must have python_file: null (Python has no FodtBody class)."""
        entries = self._load_entries()
        body_entry = next((e for e in entries if e.get("qname") == "office:body"), None)
        assert body_entry is not None, "office:body entry not found"
        assert body_entry.get("python_file") is None, (
            "office:body should have python_file: null (Python uses FodtDocument, not FodtBody)"
        )

    def test_text_p_maps_to_text_paragraph(self):
        """text:p must map to Text.Paragraph."""
        entries = self._load_entries()
        p_entry = next((e for e in entries if e.get("qname") == "text:p"), None)
        assert p_entry is not None
        assert p_entry.get("canonical_class") == "Text.Paragraph"
        assert p_entry.get("spec_fact_ref") == "FACT-FODT-003"

    def test_all_statuses_are_at_least_seeded(self):
        """All entries must be at status: architecture_only (stubs generated) or beyond."""
        valid_statuses = {"seeded", "architecture_only", "implementing", "implemented", "stable"}
        entries = self._load_entries()
        for entry in entries:
            assert entry.get("status") in valid_statuses, (
                f"Entry '{entry.get('qname')}' has invalid status='{entry.get('status')}'"
            )
        # After stubs are generated, all entries should be at architecture_only or beyond
        for entry in entries:
            assert entry.get("status") != "seeded", (
                f"Entry '{entry.get('qname')}' is still at status=seeded; "
                "run generate_canonical_stubs.py and advance to architecture_only"
            )

    def test_spec_fact_refs_cover_fact_001_to_007(self):
        """spec_fact_refs must reference FACT-FODT-002 through FACT-FODT-007."""
        entries = self._load_entries()
        fact_refs = {e.get("spec_fact_ref") for e in entries}
        for expected in ["FACT-FODT-002", "FACT-FODT-003", "FACT-FODT-004", "FACT-FODT-005", "FACT-FODT-006", "FACT-FODT-007"]:
            assert expected in fact_refs, f"spec_fact_ref '{expected}' not referenced in any entry"


class TestFodtRegistryValidation:
    def test_validate_registry_passes(self):
        """validate_spec_registry must return exit code 0 (PASS) for fodt.yaml."""
        exit_code, errors, warnings = validate_registry(
            registry_path=_REGISTRY,
            format_name="fodt",
            repo_root=_REPO,
        )
        assert errors == [], f"Registry validation errors: {errors}"
        assert exit_code == 0, f"Expected exit 0 (PASS), got {exit_code}. Warnings: {warnings}"

    def test_spec_fact_refs_resolvable(self):
        """All spec_fact_refs must be resolvable in the SAL context pack."""
        exit_code, errors, warnings = validate_registry(
            registry_path=_REGISTRY,
            format_name="fodt",
            repo_root=_REPO,
        )
        # No warnings about spec_fact_ref not found when context pack is available
        unresolved = [w for w in warnings if "not found in context pack" in w]
        assert unresolved == [], (
            f"Some spec_fact_refs unresolvable in context pack:\n" + "\n".join(unresolved)
        )
