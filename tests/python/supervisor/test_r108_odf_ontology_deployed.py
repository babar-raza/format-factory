"""Tests that the ODF ontology YAMLs are deployed to registry/odf-ontology/ and
that the qname-to-code-map is valid and consumable."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

ONTOLOGY_ROOT = _REPO / "registry" / "odf-ontology"

REQUIRED_FILES = [
    "prefix-namespace-registry.yaml",
    "qname-to-code-map.yaml",
    "namespace-tree.yaml",
    "canonical-class-inventory.yaml",
    "attribute-property-map.yaml",
    "containment-graph.yaml",
    "naming-exceptions.yaml",
    "legacy-alias-map.yaml",
    "migration-plan.yaml",
]


class TestOdfOntologyDeployed:
    def test_ontology_directory_exists(self):
        assert ONTOLOGY_ROOT.is_dir(), f"registry/odf-ontology/ not found at {ONTOLOGY_ROOT}"

    @pytest.mark.parametrize("filename", REQUIRED_FILES)
    def test_required_file_present(self, filename):
        path = ONTOLOGY_ROOT / filename
        assert path.exists(), f"{filename} missing from registry/odf-ontology/"

    def test_all_nine_files_present(self):
        present = [f for f in REQUIRED_FILES if (ONTOLOGY_ROOT / f).exists()]
        assert len(present) == 9, f"Expected 9 files, found {len(present)}"

    def test_qname_map_is_valid_yaml(self):
        import yaml
        path = ONTOLOGY_ROOT / "qname-to-code-map.yaml"
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict), "qname-to-code-map.yaml must be a YAML mapping"

    def test_qname_map_has_mappings_key(self):
        import yaml
        path = ONTOLOGY_ROOT / "qname-to-code-map.yaml"
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "mappings" in data, "qname-to-code-map.yaml missing 'mappings' key"

    def test_qname_map_has_at_least_20_entries(self):
        import yaml
        path = ONTOLOGY_ROOT / "qname-to-code-map.yaml"
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        mappings = data.get("mappings", {})
        assert len(mappings) >= 20, f"Expected >=20 QName mappings, found {len(mappings)}"

    def test_qname_entries_have_canonical_class(self):
        import yaml
        path = ONTOLOGY_ROOT / "qname-to-code-map.yaml"
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        mappings = data.get("mappings", {})
        missing = [k for k, v in mappings.items() if not isinstance(v, dict) or "canonical_class" not in v]
        assert not missing, f"QName entries missing canonical_class: {missing[:5]}"

    def test_validator_consumer_passes(self):
        from tools.requirements_authority.validate_odf_ontology import validate_all_ontology_files
        result = validate_all_ontology_files()
        assert result["all_files_present"], "Not all ontology files present"
        assert result["qname_map_valid"]["ok"], f"qname map invalid: {result['qname_map_valid'].get('issues')}"
