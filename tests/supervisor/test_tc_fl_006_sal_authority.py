"""TC-FL-006: Tests for SAL authority declaration and V70 validator.

Tests assert:
1. The sal-authority-declaration.yaml file exists and has the required fields
2. All 10 FOSS qname registries have authority_source field
3. V70 WARNs when spec_fact_refs cited for code_introspection formats
4. V70 PASSes when no spec_fact_refs are cited for non-authoritative formats
5. V70 is non-blocking
"""

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
sys.path.insert(0, str(_REPO))

import pytest
import yaml


_FOSS_FORMATS = ["abw", "csv", "dif", "gnumeric", "ndjson", "sylk", "toml", "tsv", "xcf", "zst"]
_NON_AUTHORITATIVE = {"code_introspection", "community_informal_spec", "informational_rfc"}


class TestSalAuthorityDeclaration:
    """Tests for sal-authority-declaration.yaml."""

    def test_declaration_file_exists(self):
        path = _REPO / ".local" / "evidences" / "ff-layer-forensics-20260625" / "sal-authority-declaration.yaml"
        assert path.exists(), "sal-authority-declaration.yaml must exist"

    def test_declaration_has_required_fields(self):
        path = _REPO / ".local" / "evidences" / "ff-layer-forensics-20260625" / "sal-authority-declaration.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert "formats_with_spec_parser" in data
        assert "formats_with_code_introspection" in data
        assert "code_introspection_authority_status" in data
        assert data["code_introspection_authority_status"] == "ACCEPTED_EMPIRICAL_EVIDENCE"

    def test_declaration_lists_10_foss_formats(self):
        path = _REPO / ".local" / "evidences" / "ff-layer-forensics-20260625" / "sal-authority-declaration.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        foss_formats = data["formats_with_code_introspection"]
        assert len(foss_formats) >= 10

    def test_declaration_has_upgrade_path(self):
        path = _REPO / ".local" / "evidences" / "ff-layer-forensics-20260625" / "sal-authority-declaration.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert "upgrade_path" in data
        assert len(data["upgrade_path"]) > 50  # non-trivial content


class TestQnameRegistryAuthoritySource:
    """All 10 FOSS qname registries must have authority_source field."""

    @pytest.mark.parametrize("fmt", _FOSS_FORMATS)
    def test_registry_has_authority_source(self, fmt):
        path = _REPO / "shared" / "qname-registry" / f"{fmt}.yaml"
        assert path.exists(), f"{fmt}.yaml must exist"
        entries = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(entries, list) and len(entries) > 0
        # At least first entry must have authority_source
        first = entries[0]
        assert "authority_source" in first, f"{fmt}.yaml first entry must have authority_source"
        assert first["authority_source"] in _NON_AUTHORITATIVE, (
            f"{fmt}.yaml authority_source must be one of {_NON_AUTHORITATIVE}"
        )

    @pytest.mark.parametrize("fmt", _FOSS_FORMATS)
    def test_registry_has_spec_parser_available_false(self, fmt):
        path = _REPO / "shared" / "qname-registry" / f"{fmt}.yaml"
        entries = yaml.safe_load(path.read_text(encoding="utf-8"))
        first = entries[0]
        assert "spec_parser_available" in first, f"{fmt}.yaml first entry must have spec_parser_available"
        assert first["spec_parser_available"] is False


class TestV70SalAuthorityChainValidator:
    """V70 validator behavior tests."""

    def test_passes_for_authoritative_format_with_spec_refs(self):
        """FODS has spec_parser=True; citing spec_fact_refs is valid."""
        from governance_validators_ext import validate_sal_authority_chain
        decl = {"planned_work_items": [{
            "item_id": "TEST-001",
            "item_type": "PRODUCT_SOURCE",
            "format_id": "fods",
            "spec_fact_refs": ["FACT-FODS-001"],
        }]}
        result = validate_sal_authority_chain(decl, _REPO)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_warns_for_code_introspection_format_with_spec_refs(self):
        """XCF is code_introspection; citing spec_fact_refs should WARN."""
        from governance_validators_ext import validate_sal_authority_chain
        decl = {"planned_work_items": [{
            "item_id": "TEST-002",
            "item_type": "PRODUCT_SOURCE",
            "format_id": "xcf",
            "spec_fact_refs": ["FACT-XCF-001"],
        }]}
        result = validate_sal_authority_chain(decl, _REPO)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False

    def test_passes_when_no_spec_refs_for_code_introspection_format(self):
        """XCF without spec_fact_refs is clean."""
        from governance_validators_ext import validate_sal_authority_chain
        decl = {"planned_work_items": [{
            "item_id": "TEST-003",
            "item_type": "PRODUCT_SOURCE",
            "format_id": "xcf",
            "spec_fact_refs": [],
        }]}
        result = validate_sal_authority_chain(decl, _REPO)
        assert result["result"] == "PASS"

    def test_warns_for_ndjson_community_informal(self):
        """NDJSON is community_informal_spec; spec_fact_refs should WARN."""
        from governance_validators_ext import validate_sal_authority_chain
        decl = {"planned_work_items": [{
            "item_id": "TEST-004",
            "item_type": "PRODUCT_SOURCE",
            "format_id": "ndjson",
            "spec_fact_refs": ["FACT-NDJSON-001"],
        }]}
        result = validate_sal_authority_chain(decl, _REPO)
        assert result["result"] == "WARN"

    def test_non_product_items_not_checked(self):
        from governance_validators_ext import validate_sal_authority_chain
        decl = {"planned_work_items": [{
            "item_id": "TEST-005",
            "item_type": "DOCUMENTATION",
            "format_id": "xcf",
            "spec_fact_refs": ["FACT-XCF-001"],
        }]}
        result = validate_sal_authority_chain(decl, _REPO)
        assert result["result"] == "PASS"

    def test_v70_registered_in_runner(self):
        from governance_validator_runner import run_all_governance_validators
        decl = {"planned_work_items": []}
        output = run_all_governance_validators(decl, _REPO)
        validator_names = [r["validator"] for r in output.get("validators", [])]
        assert "validate_sal_authority_chain" in validator_names
