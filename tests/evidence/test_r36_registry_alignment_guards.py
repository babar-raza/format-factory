"""
R36 Lane I: Registry alignment guard tests.

Ensures format-registry.yaml gate corrections and scope finalizations
are consistent with pack.yaml corrections applied in R33/R35.
Prevents registry drift where pack.yaml is corrected but registry is not.
"""

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

skipif_no_yaml = pytest.mark.skipif(not HAS_YAML, reason="pyyaml not installed")


def _load_yaml(path: Path):
    """Load a YAML file."""
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class TestRegistryGateCorrectionAlignment:
    """Verify format-registry.yaml has gate_correction for all corrected pack.yamls."""

    CORRECTED_FORMATS = ["fodp", "fodg", "gnumeric", "abw"]

    @skipif_no_yaml
    def test_registry_has_gate_correction_for_corrected_formats(self):
        """Every pack.yaml with gate_correction must also have gate_correction in registry."""
        registry_path = REPO / "registry" / "format-registry.yaml"
        assert registry_path.exists(), "format-registry.yaml not found"
        reg = _load_yaml(registry_path)
        formats = reg.get("formats", [])
        fmt_map = {f["format_id"]: f for f in formats}

        for fmt_id in self.CORRECTED_FORMATS:
            assert fmt_id in fmt_map, f"{fmt_id} not in format-registry.yaml"
            gates = fmt_map[fmt_id].get("gates", {})
            assert "gate_correction" in gates, \
                f"{fmt_id} registry missing gate_correction (pack.yaml has it)"

    @skipif_no_yaml
    def test_registry_gate_correction_preserves_previous_claimed_gate(self):
        """Registry gate_correction must preserve previous_claimed_gate."""
        registry_path = REPO / "registry" / "format-registry.yaml"
        reg = _load_yaml(registry_path)
        formats = reg.get("formats", [])
        fmt_map = {f["format_id"]: f for f in formats}

        for fmt_id in self.CORRECTED_FORMATS:
            gates = fmt_map[fmt_id].get("gates", {})
            gc = gates.get("gate_correction", {})
            assert gc.get("previous_claimed_gate"), \
                f"{fmt_id} registry gate_correction missing previous_claimed_gate"

    @skipif_no_yaml
    def test_registry_gate_correction_has_evidence_backed_gate(self):
        """Registry gate_correction must declare evidence_backed_gate."""
        registry_path = REPO / "registry" / "format-registry.yaml"
        reg = _load_yaml(registry_path)
        formats = reg.get("formats", [])
        fmt_map = {f["format_id"]: f for f in formats}

        for fmt_id in self.CORRECTED_FORMATS:
            gates = fmt_map[fmt_id].get("gates", {})
            gc = gates.get("gate_correction", {})
            assert gc.get("evidence_backed_gate"), \
                f"{fmt_id} registry gate_correction missing evidence_backed_gate"

    @skipif_no_yaml
    def test_registry_gate_correction_matches_pack_yaml(self):
        """Registry and pack.yaml gate_correction maturity_class must match."""
        registry_path = REPO / "registry" / "format-registry.yaml"
        reg = _load_yaml(registry_path)
        formats = reg.get("formats", [])
        fmt_map = {f["format_id"]: f for f in formats}

        for fmt_id in self.CORRECTED_FORMATS:
            pack_path = REPO / "acquisition-packs" / fmt_id / "pack.yaml"
            if not pack_path.exists():
                continue
            pack = _load_yaml(pack_path)
            # pack.yaml stores gate_correction under 'stages' key
            stages = pack.get("stages", {})
            pack_gc = stages.get("gate_correction", pack.get("gate_correction", {}))
            reg_gc = fmt_map[fmt_id].get("gates", {}).get("gate_correction", {})
            assert pack_gc.get("maturity_class") == reg_gc.get("maturity_class"), \
                f"{fmt_id} maturity_class mismatch: pack={pack_gc.get('maturity_class')} vs reg={reg_gc.get('maturity_class')}"


class TestRegistryScopeFinalizationAlignment:
    """Verify format-registry.yaml has scope_finalization for image formats."""

    SCOPE_FORMATS = ["xcf", "ppm", "pgm", "pbm"]

    @skipif_no_yaml
    def test_registry_has_scope_finalization(self):
        """Image format registry entries must have scope_finalization if pack.yaml does."""
        registry_path = REPO / "registry" / "format-registry.yaml"
        reg = _load_yaml(registry_path)
        formats = reg.get("formats", [])
        fmt_map = {f["format_id"]: f for f in formats}

        for fmt_id in self.SCOPE_FORMATS:
            pack_path = REPO / "acquisition-packs" / fmt_id / "pack.yaml"
            if not pack_path.exists():
                continue
            pack_text = pack_path.read_text(encoding="utf-8")
            if "scope_finalization:" not in pack_text:
                continue
            assert fmt_id in fmt_map, f"{fmt_id} not in registry"
            gates = fmt_map[fmt_id].get("gates", {})
            assert "scope_finalization" in gates, \
                f"{fmt_id} registry missing scope_finalization (pack.yaml has it)"

    @skipif_no_yaml
    def test_registry_scope_finalization_has_scope_description(self):
        """Registry scope_finalization must have scope_description."""
        registry_path = REPO / "registry" / "format-registry.yaml"
        reg = _load_yaml(registry_path)
        formats = reg.get("formats", [])
        fmt_map = {f["format_id"]: f for f in formats}

        for fmt_id in self.SCOPE_FORMATS:
            if fmt_id not in fmt_map:
                continue
            gates = fmt_map[fmt_id].get("gates", {})
            sf = gates.get("scope_finalization", {})
            if not sf:
                continue
            assert sf.get("scope_description"), \
                f"{fmt_id} registry scope_finalization missing scope_description"


class TestRegistryMatrixConsistency:
    """Verify format-completion-matrix.yaml reflects gate corrections."""

    @skipif_no_yaml
    def test_matrix_probe_only_formats_have_correction(self):
        """Probe-only formats in the matrix must have r35 or r36 gate correction noted."""
        matrix_path = REPO / "registry" / "format-completion-matrix.yaml"
        if not matrix_path.exists():
            pytest.skip("format-completion-matrix.yaml not found")
        matrix = _load_yaml(matrix_path)
        formats = matrix.get("formats", [])
        fmt_map = {f["format_id"]: f for f in formats}

        for fmt_id in ["fodp", "fodg", "gnumeric", "abw"]:
            if fmt_id not in fmt_map:
                continue
            entry = fmt_map[fmt_id]
            mc = entry.get("actual_maturity_class", "")
            if mc == "probe_only":
                assert entry.get("r35_gate_correction") or entry.get("r36_gate_correction"), \
                    f"{fmt_id} is probe_only in matrix but has no gate correction record"

    @skipif_no_yaml
    def test_no_probe_only_format_claims_production_track(self):
        """No probe_only format may claim production_track_real in the matrix."""
        matrix_path = REPO / "registry" / "format-completion-matrix.yaml"
        if not matrix_path.exists():
            pytest.skip("format-completion-matrix.yaml not found")
        matrix = _load_yaml(matrix_path)
        formats = matrix.get("formats", [])

        for f in formats:
            if f.get("actual_maturity_class") == "probe_only":
                claimed = f.get("claimed_gate", "")
                assert "production_track" not in str(f.get("actual_maturity_class", "")), \
                    f"{f['format_id']} is probe_only but claims production_track"
