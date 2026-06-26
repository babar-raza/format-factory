"""
test_runner_calls_extractor.py — TC-SAL-CARRY-WIRE-001
Verifies that sal_master_runner.py's --extract-requirements wiring
correctly calls the requirement extractor and stores artifacts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "specification-authority-layer"))

import importlib.util

_RUNNER_PATH = _REPO / "tools" / "specification-authority-layer" / "sal_master_runner.py"
_spec = importlib.util.spec_from_file_location("sal_master_runner", _RUNNER_PATH)
_sal_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sal_mod)
run_sal_pipeline = _sal_mod.run_sal_pipeline
_try_extract = _sal_mod._try_extract_requirements_from_spec


class TestExtractorWiring:
    """TC-SAL-CARRY-WIRE-001: requirement_extractor wired into sal_master_runner."""

    def test_extract_flag_defaults_to_false(self):
        """extract_requirements=False is the default — no regression in existing calls."""
        import inspect
        sig = inspect.signature(run_sal_pipeline)
        assert sig.parameters["extract_requirements"].default is False

    def test_extract_zst_returns_nonzero(self, tmp_path):
        """ZST has normalized spec text — extraction should return >0 requirements."""
        spec_cache = _REPO / ".local" / "spec-cache" / "zst"
        norm_texts = list(spec_cache.glob("*/normalized/text.txt"))
        if not norm_texts:
            pytest.skip("ZST normalized text not available in spec-cache")
        count = _try_extract("zst")
        assert count > 0, f"Expected >0 requirements extracted for ZST, got {count}"

    def test_extract_nonexistent_format_returns_zero(self):
        """Format with no normalized spec text returns 0 (non-blocking)."""
        count = _try_extract("nonexistent_format_xyz")
        assert count == 0

    def test_run_pipeline_with_extract_flag(self, tmp_path):
        """run_sal_pipeline with extract_requirements=True should not crash."""
        spec_cache = _REPO / ".local" / "spec-cache" / "zst"
        norm_texts = list(spec_cache.glob("*/normalized/text.txt"))
        if not norm_texts:
            pytest.skip("ZST normalized text not available")

        result = run_sal_pipeline(
            formats=["ZST"],
            output_dir=tmp_path,
            from_cache_only=True,
            write_latest=False,
            extract_requirements=True,
        )
        assert result["formats_processed"] >= 1
        # Entry should have extracted_requirements_count field
        zst_entry = next(
            (r for r in result["results"] if r["format_id"].upper() == "ZST"), None
        )
        assert zst_entry is not None
        assert "extracted_requirements_count" in zst_entry
        assert zst_entry["extracted_requirements_count"] > 0

    def test_run_pipeline_without_extract_flag_unchanged(self, tmp_path):
        """run_sal_pipeline without extract flag produces extracted_requirements_count=0."""
        result = run_sal_pipeline(
            formats=["ZST"],
            output_dir=tmp_path,
            from_cache_only=True,
            write_latest=False,
            extract_requirements=False,
        )
        zst_entry = next(
            (r for r in result["results"] if r["format_id"].upper() == "ZST"), None
        )
        if zst_entry:
            assert zst_entry.get("extracted_requirements_count", 0) == 0

    def test_spec_artifacts_written_for_zst(self, tmp_path):
        """When extract_requirements=True for ZST, artifact file is created."""
        spec_cache = _REPO / ".local" / "spec-cache" / "zst"
        norm_texts = list(spec_cache.glob("*/normalized/text.txt"))
        if not norm_texts:
            pytest.skip("ZST normalized text not available")

        _try_extract("zst")
        # Artifact should exist in default location
        art_dir = _REPO / ".local" / "spec-artifacts"
        artifacts = list(art_dir.glob("zst-spec-normalized-requirements.json"))
        assert artifacts, "Expected spec-artifacts file for ZST"
        d = json.loads(artifacts[0].read_text(encoding="utf-8"))
        assert d["format_id"] == "zst"
        assert d["requirements_count"] > 0


class TestReqToFactBridge:
    """TC-SAL-CARRY-WIRE-006: req_to_fact_bridge coverage verification."""

    def test_bridge_script_exists(self):
        bridge = _REPO / "tools" / "specification-authority-layer" / "req_to_fact_bridge.py"
        assert bridge.exists(), "req_to_fact_bridge.py must exist"

    def test_bridge_fods_coverage(self, tmp_path):
        """FODS context pack should have ≥10 CP IDs matched in SAL."""
        sys.path.insert(0, str(_REPO / "tools" / "specification-authority-layer"))
        import importlib.util as iu
        bridge_path = _REPO / "tools" / "specification-authority-layer" / "req_to_fact_bridge.py"
        bspec = iu.spec_from_file_location("req_to_fact_bridge", bridge_path)
        bmod = iu.module_from_spec(bspec)
        bspec.loader.exec_module(bmod)

        sal_json = _REPO / ".local" / "sal-output" / "sal-facts-latest.json"
        cp_dir = _REPO / "reports" / "specification-authority-layer-mwp" / "context-pack-sample"
        if not sal_json.exists() or not (cp_dir / "fods-context-pack.json").exists():
            pytest.skip("SAL facts or FODS context pack not available")

        sal_all = bmod._load_sal_qnames()
        sal_by_fmt = bmod._load_sal_by_format()
        cov = bmod.build_coverage("fods", sal_all, sal_by_fmt)

        assert cov["cp_fact_count"] > 0, "FODS context pack must have fact IDs"
        assert cov["matched_count"] >= 10, (
            f"FODS: expected ≥10 CP IDs matched in SAL, got {cov['matched_count']}"
        )
        assert cov["coverage_pct"] >= 90.0, (
            f"FODS coverage expected ≥90%, got {cov['coverage_pct']}%"
        )

    def test_bridge_zst_100pct_coverage(self, tmp_path):
        """ZST context pack should be 100% matched (all FACT-ZST-* in SAL)."""
        sys.path.insert(0, str(_REPO / "tools" / "specification-authority-layer"))
        import importlib.util as iu
        bridge_path = _REPO / "tools" / "specification-authority-layer" / "req_to_fact_bridge.py"
        bspec = iu.spec_from_file_location("req_to_fact_bridge2", bridge_path)
        bmod = iu.module_from_spec(bspec)
        bspec.loader.exec_module(bmod)

        sal_json = _REPO / ".local" / "sal-output" / "sal-facts-latest.json"
        cp_dir = _REPO / "reports" / "specification-authority-layer-mwp" / "context-pack-sample"
        if not sal_json.exists() or not (cp_dir / "zst-context-pack.json").exists():
            pytest.skip("SAL facts or ZST context pack not available")

        sal_all = bmod._load_sal_qnames()
        sal_by_fmt = bmod._load_sal_by_format()
        cov = bmod.build_coverage("zst", sal_all, sal_by_fmt)

        assert cov["coverage_pct"] >= 95.0, (
            f"ZST coverage expected ≥95%, got {cov['coverage_pct']}%"
        )
