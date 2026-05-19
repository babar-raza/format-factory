"""
Cross-format Gate 4 prototype harness.

Verifies every authorized Gate 4 prototype records required metadata
and does not overclaim production or commercial readiness.
"""

import sys
from pathlib import Path

import yaml

_src = Path(__file__).resolve().parents[2] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

REPO_ROOT = Path(__file__).resolve().parents[2]


# Gate 4 prototype formats and their expected modules
GATE4_PROTOTYPES = {
    "ods": {
        "module": "ods.ods_parser",
        "parse_fn": "parse_ods",
        "probe_fn": "probe_ods",
        "strict_fn": "parse_ods_strict",
        "sample_dir": "samples/by-format/ods/valid",
        "pack_yaml": "acquisition-packs/ods/pack.yaml",
    },
    "odt": {
        "module": "odt.odt_parser",
        "parse_fn": "parse_odt",
        "probe_fn": "probe_odt",
        "strict_fn": "parse_odt_strict",
        "sample_dir": "samples/by-format/odt/valid",
        "pack_yaml": "acquisition-packs/odt/pack.yaml",
    },
    "qoi": {
        "module": "qoi.qoi_parser",
        "parse_fn": "parse_qoi",
        "probe_fn": "probe_qoi",
        "strict_fn": "parse_qoi_strict",
        "sample_dir": "samples/by-format/qoi/valid",
        "pack_yaml": "acquisition-packs/qoi/pack.yaml",
    },
}


class TestGate4PrototypeMetadata:
    """Verify each prototype has correct __init__.py metadata."""

    def test_ods_package_metadata(self):
        from ods import __version__, __track__, __commercial_ready__, __capability_level__
        assert __version__ == "0.1.0.dev0"
        assert __track__ == "python-foss"
        assert __commercial_ready__ is False
        assert __capability_level__ == "alpha-foss-preview"

    def test_odt_package_metadata(self):
        from odt import __version__, __track__, __commercial_ready__, __capability_level__
        assert __version__ == "0.1.0.dev0"
        assert __track__ == "python-foss"
        assert __commercial_ready__ is False
        assert __capability_level__ == "alpha-foss-preview"

    def test_qoi_package_metadata(self):
        from qoi import __version__, __track__, __commercial_ready__, __capability_level__
        assert __version__ == "0.1.0.dev0"
        assert __track__ == "python-foss"
        assert __commercial_ready__ is False
        assert __capability_level__ == "alpha-foss-preview"


class TestGate4PackYamlConsistency:
    """Verify pack.yaml gate_4 status matches actual prototype state."""

    def _load_pack(self, fmt: str) -> dict:
        pack_path = REPO_ROOT / GATE4_PROTOTYPES[fmt]["pack_yaml"]
        with open(pack_path) as f:
            # pack.yaml has YAML front matter mixed with comments
            # Read and strip comment lines starting with #
            lines = []
            for line in f:
                if not line.strip().startswith("#"):
                    lines.append(line)
            content = "\n".join(lines)
        return yaml.safe_load(content)

    def test_ods_pack_gate4_status(self):
        pack = self._load_pack("ods")
        gate4 = pack["stages"]["gate_4"]
        assert gate4["status"] == "prototype_complete"
        assert gate4["commercial_product_ready"] is False
        assert gate4["production_source_authorized"] is True

    def test_odt_pack_gate4_status(self):
        pack = self._load_pack("odt")
        gate4 = pack["stages"]["gate_4"]
        assert gate4["status"] == "prototype_complete"
        assert gate4["commercial_product_ready"] is False
        assert gate4["production_source_authorized"] is True

    def test_qoi_pack_gate4_status(self):
        pack = self._load_pack("qoi")
        gate4 = pack["stages"]["gate_4"]
        assert gate4["status"] == "prototype_complete"
        assert gate4["commercial_product_ready"] is False
        assert gate4["production_source_authorized"] is True


class TestGate5SafetyGuards:
    """Verify no Gate 6+ claims exist in pack.yaml (Gate 5 is now complete)."""

    def _load_pack(self, fmt: str) -> dict:
        pack_path = REPO_ROOT / GATE4_PROTOTYPES[fmt]["pack_yaml"]
        with open(pack_path) as f:
            lines = [line for line in f if not line.strip().startswith("#")]
        return yaml.safe_load("\n".join(lines))

    def test_gate5_exists_ods(self):
        pack = self._load_pack("ods")
        assert "gate_5" in pack.get("stages", {})
        assert pack["stages"]["gate_5"]["commercial_product_ready"] is False

    def test_gate5_exists_odt(self):
        pack = self._load_pack("odt")
        assert "gate_5" in pack.get("stages", {})
        assert pack["stages"]["gate_5"]["commercial_product_ready"] is False

    def test_gate5_exists_qoi(self):
        pack = self._load_pack("qoi")
        assert "gate_5" in pack.get("stages", {})
        assert pack["stages"]["gate_5"]["commercial_product_ready"] is False

    def test_no_gate6_ods(self):
        pack = self._load_pack("ods")
        assert "gate_6" not in pack.get("stages", {})

    def test_no_gate6_odt(self):
        pack = self._load_pack("odt")
        assert "gate_6" not in pack.get("stages", {})

    def test_no_gate6_qoi(self):
        pack = self._load_pack("qoi")
        assert "gate_6" not in pack.get("stages", {})

    def test_commercial_product_ready_false_ods(self):
        pack = self._load_pack("ods")
        assert pack.get("commercial_product_ready") is False

    def test_commercial_product_ready_false_odt(self):
        pack = self._load_pack("odt")
        assert pack.get("commercial_product_ready") is False

    def test_commercial_product_ready_false_qoi(self):
        pack = self._load_pack("qoi")
        assert pack.get("commercial_product_ready") is False


class TestGate4PrototypeParseFunctions:
    """Verify each prototype's parse function works on its valid samples."""

    def test_ods_parses_any_valid_sample(self):
        from ods.ods_parser import parse_ods
        sample_dir = REPO_ROOT / "samples" / "by-format" / "ods" / "valid"
        for f in sample_dir.glob("*.ods"):
            result = parse_ods(f)
            assert result["ok"] is True, f"Failed on {f.name}: {result.get('error')}"

    def test_odt_parses_any_valid_sample(self):
        from odt.odt_parser import parse_odt
        sample_dir = REPO_ROOT / "samples" / "by-format" / "odt" / "valid"
        for f in sample_dir.glob("*.odt"):
            result = parse_odt(f)
            assert result["ok"] is True, f"Failed on {f.name}: {result.get('error')}"

    def test_qoi_parses_any_valid_sample(self):
        from qoi.qoi_parser import parse_qoi
        sample_dir = REPO_ROOT / "samples" / "by-format" / "qoi" / "valid"
        for f in sample_dir.glob("*.qoi"):
            result = parse_qoi(f)
            assert result["ok"] is True, f"Failed on {f.name}: {result.get('error')}"
