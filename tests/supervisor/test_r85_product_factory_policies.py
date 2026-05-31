"""
test_r85_product_factory_policies.py

R85 Train D/E: Verify product-factory direction policies in .supervisor/policies.yaml
and next-sprint-generator.md prompt template.

Sprint: FORMAT-FACTORY-R85
"""
from __future__ import annotations

from pathlib import Path
import yaml
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
POLICIES_FILE = PROJECT_ROOT / ".supervisor" / "policies.yaml"
NEXT_SPRINT_GENERATOR = PROJECT_ROOT / ".supervisor" / "prompts" / "next-sprint-generator.md"
POC_MATRIX_FILE = PROJECT_ROOT / "product-capability-matrix" / "poc-targets.yaml"


# ============================================================
# Test: Policies file has product-factory section
# ============================================================

class TestProductFactoryPolicies:
    """Verify .supervisor/policies.yaml has product-factory direction policies."""

    def _load_policies(self):
        assert POLICIES_FILE.exists(), f"policies.yaml not found at {POLICIES_FILE}"
        with open(POLICIES_FILE, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_product_factory_section_exists(self):
        policies = self._load_policies()
        assert "product_factory" in policies, (
            "policies.yaml must have 'product_factory' section (R85 direction)"
        )

    def test_product_factory_direction_required(self):
        policies = self._load_policies()
        pf = policies.get("product_factory", {})
        assert pf.get("product_factory_direction_required") is True, (
            "product_factory_direction_required must be true"
        )

    def test_evidence_not_finish_line(self):
        policies = self._load_policies()
        pf = policies.get("product_factory", {})
        assert pf.get("evidence_supports_product_not_finish_line") is True, (
            "evidence_supports_product_not_finish_line must be true"
        )

    def test_poc_targets_required(self):
        policies = self._load_policies()
        pf = policies.get("product_factory", {})
        assert pf.get("poc_targets_required") is True

    def test_three_commercial_products_required(self):
        policies = self._load_policies()
        pf = policies.get("product_factory", {})
        assert pf.get("commercial_net_products_required") == 3, (
            "Must require 3 commercial .NET products"
        )

    def test_three_foss_products_required(self):
        policies = self._load_policies()
        pf = policies.get("product_factory", {})
        assert pf.get("foss_reduced_products_required") == 3, (
            "Must require 3 FOSS reduced products"
        )

    def test_dogfood_export_required(self):
        policies = self._load_policies()
        pf = policies.get("product_factory", {})
        assert pf.get("dogfood_export_required") is True

    def test_installed_package_proof_required(self):
        policies = self._load_policies()
        pf = policies.get("product_factory", {})
        assert pf.get("installed_package_proof_required_for_package_claims") is True

    def test_required_next_sprint_lanes_present(self):
        policies = self._load_policies()
        pf = policies.get("product_factory", {})
        required = pf.get("required_next_sprint_lanes", [])
        expected = [
            "commercial_product_advancement",
            "foss_reduced_product_advancement",
            "dogfooding_export",
            "supervisor_loop_trigger",
        ]
        for lane in expected:
            assert lane in required, f"Required lane '{lane}' not in policies"

    def test_supervisor_loop_required_after_bundle(self):
        policies = self._load_policies()
        pf = policies.get("product_factory", {})
        assert pf.get("supervisor_loop_required_after_bundle") is True

    def test_product_factory_gates_section_exists(self):
        policies = self._load_policies()
        assert "product_factory_gates" in policies, (
            "policies.yaml must have 'product_factory_gates' section"
        )

    def test_commercial_approval_gate_defined(self):
        policies = self._load_policies()
        gates = policies.get("product_factory_gates", {})
        assert "stop_commercial_approval_required" in gates

    def test_autonomous_product_deepening_gate_defined(self):
        policies = self._load_policies()
        gates = policies.get("product_factory_gates", {})
        assert "autonomous_product_deepening_continue" in gates
        gate = gates["autonomous_product_deepening_continue"]
        assert gate.get("who_unblocks") is None, (
            "autonomous_product_deepening should not require human unblock"
        )


# ============================================================
# Test: next-sprint-generator.md has product-factory lanes
# ============================================================

class TestNextSprintGeneratorTemplate:
    """Verify next-sprint-generator.md template enforces product-factory lanes."""

    def _load_template(self) -> str:
        assert NEXT_SPRINT_GENERATOR.exists(), (
            f"next-sprint-generator.md not found at {NEXT_SPRINT_GENERATOR}"
        )
        return NEXT_SPRINT_GENERATOR.read_text(encoding="utf-8")

    def test_template_has_product_factory_section(self):
        text = self._load_template()
        assert "PRODUCT-FACTORY DIRECTION" in text.upper() or "product_factory_direction" in text, (
            "Template must have product-factory direction section"
        )

    def test_template_requires_commercial_product_lane(self):
        text = self._load_template()
        assert "commercial" in text.lower() and ("product" in text.lower() or "advancement" in text.lower()), (
            "Template must mention commercial product advancement lane"
        )

    def test_template_requires_foss_product_lane(self):
        text = self._load_template()
        assert "foss" in text.lower() or "reduced" in text.lower(), (
            "Template must mention FOSS reduced product lane"
        )

    def test_template_requires_dogfooding_lane(self):
        text = self._load_template()
        assert "dogfood" in text.lower(), (
            "Template must mention dogfooding export lane"
        )

    def test_template_requires_supervisor_loop_trigger(self):
        text = self._load_template()
        assert "supervisor_loop" in text or "run-on-latest" in text, (
            "Template must include supervisor loop trigger instruction"
        )

    def test_template_has_insufficient_sprint_classification(self):
        text = self._load_template()
        assert "insufficient" in text.lower() or "partial" in text.lower(), (
            "Template must classify evidence-only closure as insufficient/partial"
        )


# ============================================================
# Test: POC target matrix exists and has correct entries
# ============================================================

class TestPocTargetMatrix:
    """Verify product-capability-matrix/poc-targets.yaml exists and is correct."""

    def _load_matrix(self):
        assert POC_MATRIX_FILE.exists(), (
            f"poc-targets.yaml not found at {POC_MATRIX_FILE}"
        )
        with open(POC_MATRIX_FILE, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_poc_matrix_exists(self):
        assert POC_MATRIX_FILE.exists()

    def test_three_commercial_net_products(self):
        matrix = self._load_matrix()
        commercial = matrix.get("commercial_net_products", [])
        assert len(commercial) == 3, f"Expected 3 commercial .NET products, got {len(commercial)}"

    def test_three_foss_reduced_products(self):
        matrix = self._load_matrix()
        foss = matrix.get("foss_reduced_products", [])
        assert len(foss) == 3, f"Expected 3 FOSS reduced products, got {len(foss)}"

    def test_fods_is_confirmed(self):
        matrix = self._load_matrix()
        fods = next(
            (p for p in matrix.get("commercial_net_products", []) if p["format"] == "FODS"),
            None
        )
        assert fods is not None, "FODS must be in commercial_net_products"
        assert fods["classification"] == "POC_TARGET_CONFIRMED"

    def test_fodt_is_confirmed(self):
        matrix = self._load_matrix()
        fodt = next(
            (p for p in matrix.get("commercial_net_products", []) if p["format"] == "FODT"),
            None
        )
        assert fodt is not None, "FODT must be in commercial_net_products"
        assert fodt["classification"] == "POC_TARGET_CONFIRMED"

    def test_netpbm_is_commercial_confirmed(self):
        matrix = self._load_matrix()
        netpbm = next(
            (p for p in matrix.get("commercial_net_products", []) if p["format"] == "Netpbm"),
            None
        )
        assert netpbm is not None, "Netpbm must be in commercial_net_products"
        assert netpbm["classification"] == "POC_TARGET_CONFIRMED"

    def test_no_commercial_product_ready_true(self):
        matrix = self._load_matrix()
        for product in matrix.get("commercial_net_products", []):
            assert product.get("commercial_product_ready") is not True, (
                f"{product['format']}: commercial_product_ready must not be True"
            )

    def test_summary_counts_correct(self):
        matrix = self._load_matrix()
        summary = matrix.get("summary", {})
        assert summary.get("commercial_net_confirmed") == 3
        assert summary.get("foss_reduced_confirmed") == 3

    def test_summary_no_commercial_ready(self):
        matrix = self._load_matrix()
        summary = matrix.get("summary", {})
        assert summary.get("commercial_product_ready") is not True
        assert summary.get("gate_11_approved") is not True
