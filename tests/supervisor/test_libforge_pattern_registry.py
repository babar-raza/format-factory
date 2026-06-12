"""
test_libforge_pattern_registry.py — Tests for LibForge pattern registry.

Sprint: FF-LIBFORGE-REFOCUS-INTEGRATION-001
Verifies pattern source mapping, adoption mode classification,
unsafe coupling detection, and JSON serialization.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from tools.supervisor.libforge_pattern_registry import (
    AdoptionMode,
    PatternCategory,
    PatternSource,
    get_all_patterns,
    get_ff_missing_gaps,
    get_pattern,
    get_patterns_by_adoption_mode,
    get_patterns_by_category,
    get_patterns_by_source,
    is_safe_to_import,
    to_dict_list,
)


class TestRegistryBasics:
    def test_registry_not_empty(self):
        patterns = get_all_patterns()
        assert len(patterns) >= 6

    def test_all_sources_represented(self):
        patterns = get_all_patterns()
        sources = {p.source for p in patterns}
        assert PatternSource.APIDEV in sources
        assert PatternSource.REFDEV in sources
        assert PatternSource.SPECDEV in sources

    def test_get_pattern_by_id(self):
        rec = get_pattern("APIDEV-CAP-VERIFY")
        assert rec is not None
        assert rec.pattern_id == "APIDEV-CAP-VERIFY"

    def test_get_pattern_unknown_returns_none(self):
        rec = get_pattern("DOES_NOT_EXIST_XYZ")
        assert rec is None


class TestPatternSourceMapping:
    def test_apidev_capability_verifier_maps_to_ff(self):
        """apidev capability verifier pattern maps to existing CapabilityVerifier."""
        rec = get_pattern("APIDEV-CAP-VERIFY")
        assert rec is not None
        assert rec.ff_mapping is not None
        assert "CapabilityVerifier" in rec.ff_mapping.component
        assert "capability_verifier.py" in rec.ff_mapping.path

    def test_refdev_compose_verify_maps_to_ff(self):
        """refdev compose/verify maps to existing ComposeVerifyLoop + missing product mutation gate."""
        rec = get_pattern("REFDEV-COMPOSE-VERIFY-LOOP")
        assert rec is not None
        assert rec.ff_mapping is not None
        assert "ComposeVerifyLoop" in rec.ff_mapping.component
        assert "compose_verify_loop.py" in rec.ff_mapping.path
        assert rec.ff_mapping.status == "partial"
        assert "mutation gate" in rec.ff_mapping.notes.lower()

    def test_specdev_freeze_gate_maps_to_ff(self):
        """specdev freeze gate maps to existing FreezeGateRunner + missing multi-format gates."""
        rec = get_pattern("SPECDEV-FREEZE-GATE")
        assert rec is not None
        assert rec.ff_mapping is not None
        assert "FreezeGateRunner" in rec.ff_mapping.component
        assert rec.ff_mapping.status == "partial"
        assert "multi-format" in rec.ff_mapping.notes.lower()

    def test_apidev_source_patterns_present(self):
        apidev_patterns = get_patterns_by_source(PatternSource.APIDEV)
        assert len(apidev_patterns) >= 2

    def test_refdev_source_patterns_present(self):
        refdev_patterns = get_patterns_by_source(PatternSource.REFDEV)
        assert len(refdev_patterns) >= 2

    def test_specdev_source_patterns_present(self):
        specdev_patterns = get_patterns_by_source(PatternSource.SPECDEV)
        assert len(specdev_patterns) >= 2


class TestUnsafeCouplingDetection:
    def test_unsafe_direct_import_rejected_for_dotnet_pieces(self):
        """Patterns with .NET/Roslyn/clang coupling are not safe to import directly."""
        rec = get_pattern("APIDEV-CAP-VERIFY")
        assert rec is not None
        # apidev requires Roslyn — must reimplement FF-natively, not direct import
        assert rec.requires_ff_native is True

    def test_freeze_gate_has_unsafe_coupling(self):
        rec = get_pattern("SPECDEV-FREEZE-GATE")
        assert rec is not None
        assert len(rec.unsafe_coupling) > 0
        # clang/g++/dotnet coupling should be listed
        coupling_str = " ".join(rec.unsafe_coupling).lower()
        assert any(kw in coupling_str for kw in ["clang", "dotnet", "build"])

    def test_compose_verify_has_unsafe_coupling(self):
        rec = get_pattern("REFDEV-COMPOSE-VERIFY-LOOP")
        assert rec is not None
        assert len(rec.unsafe_coupling) > 0

    def test_soft_skip_pattern_is_safe_to_wrap(self):
        """The soft-skip pattern has no unsafe coupling and is safe to wrap."""
        rec = get_pattern("REFDEV-SOFT-SKIP-TOOLCHAIN")
        assert rec is not None
        assert len(rec.unsafe_coupling) == 0


class TestAdoptionModes:
    def test_ff_native_reimplementation_count(self):
        ff_native = get_patterns_by_adoption_mode(AdoptionMode.FF_NATIVE_REIMPLEMENTATION)
        assert len(ff_native) >= 4

    def test_isolated_job_runner_is_missing(self):
        rec = get_pattern("SPECDEV-ISOLATED-JOB-EXECUTION")
        assert rec is not None
        assert rec.ff_mapping is not None
        assert rec.ff_mapping.status == "missing"

    def test_high_priority_gaps_not_empty(self):
        gaps = get_ff_missing_gaps()
        assert len(gaps) >= 1

    def test_all_records_have_valid_adoption_mode(self):
        for rec in get_all_patterns():
            assert rec.adoption_mode in AdoptionMode


class TestSerialization:
    def test_to_dict_list_is_json_serializable(self):
        data = to_dict_list()
        json_str = json.dumps(data)
        assert len(json_str) > 100

    def test_to_dict_list_all_keys_present(self):
        data = to_dict_list()
        required_keys = {
            "pattern_id", "source", "category", "adoption_mode",
            "description", "source_path", "unsafe_coupling",
            "integration_notes", "requires_ff_native", "priority",
        }
        for item in data:
            assert required_keys.issubset(item.keys())

    def test_to_dict_list_count_matches_registry(self):
        data = to_dict_list()
        all_patterns = get_all_patterns()
        assert len(data) == len(all_patterns)
