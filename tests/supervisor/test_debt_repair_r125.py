"""
test_debt_repair_r125.py
Sprint: SPEC-AUTHORITY-LAYER-PILOT-CLOSURE-DEBT-REPAIR-001
Added: 2026-06-08

Tests for the debt repair sprint:
  Lane 1 — Fact ID existence lookup (DEBT-004 closure)
  Lane 2 — schema_authority_available cannot gate READINESS (DEBT-005 closure)
"""
import sys
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))

from validate_spec_fact_refs import (
    check_item,
    get_fact_registry,
    reset_fact_registry_cache,
    DEBT_ONLY_EXCEPTIONS,
    READINESS_ALLOWED_EXCEPTIONS,
    _build_fact_registry,
)


# ============================================================
# Lane 1 — Fact ID existence lookup tests
# ============================================================


class TestFactRegistryBuilder:
    """Tests for _build_fact_registry and get_fact_registry."""

    def setup_method(self):
        reset_fact_registry_cache()

    def teardown_method(self):
        reset_fact_registry_cache()

    def test_no_registry_dir_returns_empty(self, tmp_path):
        """No .local/spec-cache/ directory → empty registry (graceful degradation)."""
        registry = _build_fact_registry(repo_root=tmp_path)
        assert registry == {}

    def test_empty_cache_dir_returns_empty(self, tmp_path):
        """Empty .local/spec-cache/ → empty registry."""
        cache_dir = tmp_path / ".local" / "spec-cache"
        cache_dir.mkdir(parents=True)
        registry = _build_fact_registry(repo_root=tmp_path)
        assert registry == {}

    def test_loads_fact_ids_from_verified_facts_file(self, tmp_path):
        """Facts from verified-facts-review.yaml are loaded into registry."""
        workbench = tmp_path / ".local" / "spec-cache" / "fods" / "1.3" / "workbench"
        workbench.mkdir(parents=True)
        facts_file = workbench / "verified-facts-review.yaml"
        facts_file.write_text(
            """
facts:
  - claim_id: FACT-FODS-001
    provenance:
      verification_status: verified
  - claim_id: FACT-FODS-002
    provenance:
      verification_status: needs_review
""",
            encoding="utf-8",
        )
        registry = _build_fact_registry(repo_root=tmp_path)
        assert "FACT-FODS-001" in registry
        assert registry["FACT-FODS-001"] == "verified"
        assert "FACT-FODS-002" in registry
        assert registry["FACT-FODS-002"] == "needs_review"

    def test_fact_id_field_also_accepted(self, tmp_path):
        """fact_id field (alternate name) is also loaded."""
        workbench = tmp_path / ".local" / "spec-cache" / "fodt" / "workbench"
        workbench.mkdir(parents=True)
        facts_file = workbench / "verified-facts-review.yaml"
        facts_file.write_text(
            """
facts:
  - fact_id: FACT-FODT-001
    provenance:
      verification_status: verified
""",
            encoding="utf-8",
        )
        registry = _build_fact_registry(repo_root=tmp_path)
        assert "FACT-FODT-001" in registry

    def test_multiple_format_files_merged(self, tmp_path):
        """Multiple verified-facts-review.yaml files across formats are merged."""
        for fmt in ["fods", "fodt"]:
            wb = tmp_path / ".local" / "spec-cache" / fmt / "workbench"
            wb.mkdir(parents=True)
            (wb / "verified-facts-review.yaml").write_text(
                f"facts:\n  - claim_id: FACT-{fmt.upper()}-001\n    provenance:\n      verification_status: verified\n",
                encoding="utf-8",
            )
        registry = _build_fact_registry(repo_root=tmp_path)
        assert "FACT-FODS-001" in registry
        assert "FACT-FODT-001" in registry

    def test_malformed_yaml_file_skipped_gracefully(self, tmp_path):
        """Malformed YAML file is skipped without crashing."""
        workbench = tmp_path / ".local" / "spec-cache" / "bad" / "workbench"
        workbench.mkdir(parents=True)
        (workbench / "verified-facts-review.yaml").write_text(
            "this: is: not: valid: yaml: [[[[",
            encoding="utf-8",
        )
        registry = _build_fact_registry(repo_root=tmp_path)
        assert registry == {}

    def test_cache_is_populated_on_first_call(self, tmp_path):
        """get_fact_registry caches on first call."""
        workbench = tmp_path / ".local" / "spec-cache" / "fods" / "workbench"
        workbench.mkdir(parents=True)
        (workbench / "verified-facts-review.yaml").write_text(
            "facts:\n  - claim_id: FACT-FODS-001\n    provenance:\n      verification_status: verified\n",
            encoding="utf-8",
        )
        r1 = get_fact_registry(repo_root=tmp_path)
        r2 = get_fact_registry(repo_root=tmp_path)
        assert r1 is r2  # same object = cached


class TestFactExistenceEnforcementWithRegistry:
    """Tests for existence checking in check_item() when registry is populated."""

    def setup_method(self):
        reset_fact_registry_cache()

    def teardown_method(self):
        reset_fact_registry_cache()

    def _patch_registry(self, registry: dict):
        """Helper: patch get_fact_registry to return a known registry."""
        return patch(
            "validate_spec_fact_refs.get_fact_registry",
            return_value=registry,
        )

    def test_fact_in_registry_is_accepted(self):
        """Fact ID that exists in registry → accepted."""
        registry = {"FACT-FODS-001": "verified"}
        with self._patch_registry(registry):
            item = {
                "item_id": "WI-TEST-001",
                "item_type": "PRODUCT_SOURCE",
                "spec_fact_refs": ["FACT-FODS-001"],
            }
            result = check_item(item)
        assert result["compliant"]
        assert result["grade_impact"] == "none"

    def test_fact_not_in_registry_is_rejected(self):
        """Fact ID not in registry → rejected (existence check)."""
        registry = {"FACT-FODS-001": "verified"}
        with self._patch_registry(registry):
            item = {
                "item_id": "WI-TEST-002",
                "item_type": "PRODUCT_SOURCE",
                "spec_fact_refs": ["FACT-DOES-NOT-EXIST"],
            }
            result = check_item(item)
        assert not result["compliant"]
        assert result["grade_impact"] == "reject"
        assert "not found in governed fact registry" in result["violation"]
        assert "FACT-DOES-NOT-EXIST" in result["violation"]

    def test_empty_registry_skips_existence_check(self):
        """Empty registry (no registry files) → graceful degradation, format-only."""
        registry = {}  # no registry files exist
        with self._patch_registry(registry):
            item = {
                "item_id": "WI-TEST-003",
                "item_type": "PRODUCT_SOURCE",
                "spec_fact_refs": ["FACT-DOES-NOT-EXIST"],
            }
            result = check_item(item)
        # graceful degradation: format valid, registry absent → pass
        assert result["compliant"]

    def test_mixed_known_and_unknown_refs_rejected(self):
        """Mix of known and unknown refs → rejected for unknown."""
        registry = {"FACT-FODS-001": "verified"}
        with self._patch_registry(registry):
            item = {
                "item_id": "WI-TEST-004",
                "item_type": "PRODUCT_SOURCE",
                "spec_fact_refs": ["FACT-FODS-001", "FACT-GHOST-999"],
            }
            result = check_item(item)
        assert not result["compliant"]
        assert "FACT-GHOST-999" in result["violation"]

    def test_format_check_happens_before_registry_check(self):
        """Malformed fact IDs are rejected before registry lookup."""
        registry = {"FACT-FODS-001": "verified"}
        with self._patch_registry(registry):
            item = {
                "item_id": "WI-TEST-005",
                "item_type": "PRODUCT_SOURCE",
                "spec_fact_refs": ["bad-id-no-prefix"],
            }
            result = check_item(item)
        assert not result["compliant"]
        assert "Invalid spec_fact_ref format" in result["violation"]

    def test_needs_review_fact_still_accepted(self):
        """Fact with needs_review status is still accepted (verification_status doesn't block)."""
        registry = {"FACT-FODS-002": "needs_review"}
        with self._patch_registry(registry):
            item = {
                "item_id": "WI-TEST-006",
                "item_type": "PRODUCT_SOURCE",
                "spec_fact_refs": ["FACT-FODS-002"],
            }
            result = check_item(item)
        assert result["compliant"]


# ============================================================
# Lane 2 — schema_authority_available tightening tests
# ============================================================


class TestSchemaAuthorityDebtOnly:
    """schema_authority_available is debt-only: blocks READINESS and RELEASE_GATE."""

    def test_schema_authority_in_debt_only_exceptions(self):
        """schema_authority_available is in DEBT_ONLY_EXCEPTIONS."""
        assert "schema_authority_available" in DEBT_ONLY_EXCEPTIONS

    def test_schema_authority_not_in_readiness_allowed(self):
        """schema_authority_available is NOT in READINESS_ALLOWED_EXCEPTIONS."""
        assert "schema_authority_available" not in READINESS_ALLOWED_EXCEPTIONS

    def test_schema_authority_blocks_readiness(self):
        """READINESS + schema_authority_available → REJECTED."""
        item = {
            "item_id": "WI-GNUMERIC-READINESS-001",
            "item_type": "READINESS",
            "spec_fact_refs": [],
            "exception_classification": "schema_authority_available",
            "exception_rationale": "gnumeric.xsd exists.",
        }
        result = check_item(item)
        assert not result["compliant"]
        assert result["grade_impact"] == "reject"
        assert "debt/grace classification" in result["violation"]

    def test_schema_authority_blocks_release_gate(self):
        """RELEASE_GATE + schema_authority_available → REJECTED."""
        item = {
            "item_id": "WI-GNUMERIC-RELEASE-001",
            "item_type": "RELEASE_GATE",
            "spec_fact_refs": [],
            "exception_classification": "schema_authority_available",
            "exception_rationale": "gnumeric.xsd exists.",
        }
        result = check_item(item)
        assert not result["compliant"]
        assert result["grade_impact"] == "reject"

    def test_schema_authority_allows_product_source_with_debt(self):
        """PRODUCT_SOURCE + schema_authority_available → ACCEPTED with grade_impact=debt."""
        item = {
            "item_id": "WI-GNUMERIC-PRODUCT-001",
            "item_type": "PRODUCT_SOURCE",
            "spec_fact_refs": [],
            "exception_classification": "schema_authority_available",
            "exception_rationale": "gnumeric.xsd is the primary authority.",
        }
        result = check_item(item)
        assert result["compliant"]
        assert result["grade_impact"] == "debt"

    def test_schema_authority_allows_test_with_debt(self):
        """TEST + schema_authority_available → ACCEPTED with grade_impact=debt."""
        item = {
            "item_id": "WI-GNUMERIC-TEST-001",
            "item_type": "TEST",
            "spec_fact_refs": [],
            "exception_classification": "schema_authority_available",
            "exception_rationale": "gnumeric.xsd is the primary authority.",
        }
        result = check_item(item)
        assert result["compliant"]
        assert result["grade_impact"] == "debt"

    def test_schema_authority_allows_requirement_with_debt(self):
        """REQUIREMENT + schema_authority_available → ACCEPTED with grade_impact=debt."""
        item = {
            "item_id": "WI-GNUMERIC-REQ-001",
            "item_type": "REQUIREMENT",
            "spec_fact_refs": [],
            "exception_classification": "schema_authority_available",
            "exception_rationale": "gnumeric.xsd is the primary authority.",
        }
        result = check_item(item)
        assert result["compliant"]
        assert result["grade_impact"] == "debt"

    def test_real_spec_fact_refs_override_schema_limitation(self):
        """READINESS with real FACT- refs overrides any schema limitation (spec facts are authoritative)."""
        from unittest.mock import patch
        registry = {"FACT-GNUMERIC-001": "verified"}
        with patch("validate_spec_fact_refs.get_fact_registry", return_value=registry):
            item = {
                "item_id": "WI-GNUMERIC-READINESS-002",
                "item_type": "READINESS",
                "spec_fact_refs": ["FACT-GNUMERIC-001"],
                "exception_classification": "",
            }
            result = check_item(item)
        assert result["compliant"]
        assert result["grade_impact"] == "none"
