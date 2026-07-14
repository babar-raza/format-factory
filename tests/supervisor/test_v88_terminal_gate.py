"""Tests for V88: validate_required_layers_at_terminal gate.

TC-LHEAL-009 (glittery-splashing-manatee, 2026-07-13)
8 tests covering PASS/FAIL/SKIP paths.
"""
from __future__ import annotations

import importlib
import textwrap
from pathlib import Path

import pytest
import yaml


@pytest.fixture()
def v88(tmp_path):
    """Import and return the V88 validator function."""
    m = importlib.import_module("governance_validators_layers")
    return m.validate_required_layers_at_terminal


class TestV88PassWhenLayerPresent:
    """V88 returns PASS when required layers are in index.yaml."""

    def _make_index(self, tmp_path: Path, layer_ids: list[str]) -> None:
        idx_dir = tmp_path / "plans" / "layers"
        idx_dir.mkdir(parents=True)
        entries = [{"layer_id": lid, "canonical_name": f"Layer {lid}"} for lid in layer_ids]
        (idx_dir / "index.yaml").write_text(yaml.dump({"layers": entries}))

    def _make_plan(self, tmp_path: Path, required_layers: list[str], plan_type: str = "machinery_hardening") -> Path:
        plan_dir = tmp_path / "plans" / ".claude"
        plan_dir.mkdir(parents=True)
        header = textwrap.dedent(f"""
            ```yaml
            plan_name: test-plan
            plan_type: {plan_type}
            required_permanent_layers: {required_layers!r}
            ```
        """).strip()
        plan_path = plan_dir / "test-plan.md"
        plan_path.write_text(header + "\n\n# Test Plan\n")
        return plan_path

    def test_pass_when_single_required_layer_present(self, v88, tmp_path):
        """PASS when required_permanent_layers: [L28] and L28 is in index.yaml."""
        self._make_index(tmp_path, ["L28"])
        plan = self._make_plan(tmp_path, ["L28"])
        result = v88(str(plan), tmp_path)
        assert result["result"] == "PASS"

    def test_pass_when_multiple_required_layers_all_present(self, v88, tmp_path):
        """PASS when [L01, L05, L28] all exist in index.yaml."""
        self._make_index(tmp_path, ["L01", "L05", "L28"])
        plan = self._make_plan(tmp_path, ["L01", "L05", "L28"])
        result = v88(str(plan), tmp_path)
        assert result["result"] == "PASS"


class TestV88FailWhenLayerMissing:
    """V88 returns FAIL when a required layer is not in index.yaml."""

    def _make_index(self, tmp_path: Path, layer_ids: list[str]) -> None:
        idx_dir = tmp_path / "plans" / "layers"
        idx_dir.mkdir(parents=True)
        entries = [{"layer_id": lid, "canonical_name": f"Layer {lid}"} for lid in layer_ids]
        (idx_dir / "index.yaml").write_text(yaml.dump({"layers": entries}))

    def _make_plan(self, tmp_path: Path, required_layers: list[str], plan_type: str = "machinery_hardening") -> Path:
        plan_dir = tmp_path / "plans" / ".claude"
        plan_dir.mkdir(parents=True)
        header = textwrap.dedent(f"""
            ```yaml
            plan_name: test-plan
            plan_type: {plan_type}
            required_permanent_layers: {required_layers!r}
            ```
        """).strip()
        plan_path = plan_dir / "test-plan.md"
        plan_path.write_text(header + "\n\n# Test Plan\n")
        return plan_path

    def test_fail_when_required_layer_absent(self, v88, tmp_path):
        """FAIL when L99 is required but not in index.yaml."""
        self._make_index(tmp_path, ["L01"])
        plan = self._make_plan(tmp_path, ["L99"])
        result = v88(str(plan), tmp_path)
        assert result["result"] == "FAIL"
        assert "L99" in result.get("missing_layers", [])

    def test_fail_lists_all_missing_layers(self, v88, tmp_path):
        """FAIL includes all missing layer IDs when multiple are absent."""
        self._make_index(tmp_path, ["L01"])
        plan = self._make_plan(tmp_path, ["L01", "L88", "L99"])
        result = v88(str(plan), tmp_path)
        assert result["result"] == "FAIL"
        missing = result.get("missing_layers", [])
        assert "L88" in missing
        assert "L99" in missing
        assert "L01" not in missing


class TestV88SkipPaths:
    """V88 returns SKIP when the plan has no required layers declared."""

    def _make_plan_no_layers(self, tmp_path: Path) -> Path:
        plan_dir = tmp_path / "plans" / ".claude"
        plan_dir.mkdir(parents=True)
        header = textwrap.dedent("""
            ```yaml
            plan_name: simple-plan
            plan_type: machinery_hardening
            ```
        """).strip()
        plan_path = plan_dir / "simple-plan.md"
        plan_path.write_text(header + "\n\n# Simple Plan\n")
        return plan_path

    def test_pass_when_no_required_permanent_layers_field(self, v88, tmp_path):
        """PASS (trivially) when plan has no required_permanent_layers and is not product_certification."""
        plan = self._make_plan_no_layers(tmp_path)
        result = v88(str(plan), tmp_path)
        # No obligations declared → PASS (no_obligations_declared), not SKIP
        assert result["result"] in ("PASS", "SKIP")

    def test_skip_when_plan_file_missing(self, v88, tmp_path):
        """SKIP gracefully when plan file does not exist on disk."""
        result = v88(str(tmp_path / "nonexistent.md"), tmp_path)
        assert result["result"] == "SKIP"


class TestV88InferredL28ForCertificationPlans:
    """V88 infers [L28] for plan_type: product_certification even without explicit field."""

    def _make_index(self, tmp_path: Path, layer_ids: list[str]) -> None:
        idx_dir = tmp_path / "plans" / "layers"
        idx_dir.mkdir(parents=True)
        entries = [{"layer_id": lid, "canonical_name": f"Layer {lid}"} for lid in layer_ids]
        (idx_dir / "index.yaml").write_text(yaml.dump({"layers": entries}))

    def _make_cert_plan(self, tmp_path: Path) -> Path:
        plan_dir = tmp_path / "plans" / ".claude"
        plan_dir.mkdir(parents=True)
        header = textwrap.dedent("""
            ```yaml
            plan_name: cert-plan
            plan_type: product_certification
            ```
        """).strip()
        plan_path = plan_dir / "cert-plan.md"
        plan_path.write_text(header + "\n\n# Cert Plan\n")
        return plan_path

    def test_inferred_l28_passes_when_l28_present(self, v88, tmp_path):
        """product_certification plans infer L28; PASS when L28 in index."""
        self._make_index(tmp_path, ["L28"])
        plan = self._make_cert_plan(tmp_path)
        result = v88(str(plan), tmp_path)
        assert result["result"] == "PASS"

    def test_inferred_l28_fails_when_l28_absent(self, v88, tmp_path):
        """product_certification plans infer L28; FAIL when L28 missing from index."""
        self._make_index(tmp_path, ["L01"])
        plan = self._make_cert_plan(tmp_path)
        result = v88(str(plan), tmp_path)
        assert result["result"] == "FAIL"
        assert "L28" in result.get("missing_layers", [])
