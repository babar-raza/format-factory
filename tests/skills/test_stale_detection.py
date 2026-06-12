"""
tests/skills/test_stale_detection.py

Tests for stale_detection.py — Lane A CONWAY-R7R8.

Validates:
  1. Live state detection for FODS and FODT returns FRESH or REVIEW_REQUIRED
  2. Stale verdicts are deterministic and JSON-serializable
  3. STALE_BLOCKED is triggered correctly for synthetic stale states
  4. Resolver surfaces stale field
  5. Lane selector respects STALE_BLOCKED
  6. Prompt generator blocks on STALE_BLOCKED
  7. Stale fixtures produce expected outcomes
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from stale_detection import detect_stale_state, _parse_timestamp


# ===========================================================================
# TestTimestampParser
# ===========================================================================

class TestTimestampParser:
    def test_iso_datetime_parses(self):
        ts = _parse_timestamp("2026-05-13T00:00:00Z")
        assert ts is not None
        assert ts.year == 2026

    def test_date_only_parses(self):
        ts = _parse_timestamp("2026-05-13")
        assert ts is not None
        assert ts.month == 5

    def test_none_returns_none(self):
        assert _parse_timestamp(None) is None

    def test_garbage_returns_none(self):
        assert _parse_timestamp("not-a-date") is None

    def test_datetime_with_microseconds_parses(self):
        ts = _parse_timestamp("2026-05-13T10:30:00.123456")
        assert ts is not None


# ===========================================================================
# TestLiveStaleDetection (FODS + FODT)
# ===========================================================================

class TestLiveStaleDetection:
    def test_fods_returns_dict(self):
        result = detect_stale_state("fods")
        assert isinstance(result, dict)

    def test_fodt_returns_dict(self):
        result = detect_stale_state("fodt")
        assert isinstance(result, dict)

    def test_fods_verdict_is_valid(self):
        result = detect_stale_state("fods")
        assert result["verdict"] in ("FRESH", "REVIEW_REQUIRED", "STALE_BLOCKED", "INDETERMINATE")

    def test_fodt_verdict_is_valid(self):
        result = detect_stale_state("fodt")
        assert result["verdict"] in ("FRESH", "REVIEW_REQUIRED", "STALE_BLOCKED", "INDETERMINATE")

    def test_fods_not_stale_blocked_live(self):
        """Live FODS requirements chain should not be STALE_BLOCKED."""
        result = detect_stale_state("fods")
        assert result["verdict"] != "STALE_BLOCKED", (
            f"FODS is unexpectedly STALE_BLOCKED. Reasons: {result['reasons']}"
        )

    def test_fodt_not_stale_blocked_live(self):
        """Live FODT requirements chain should not be STALE_BLOCKED."""
        result = detect_stale_state("fodt")
        assert result["verdict"] != "STALE_BLOCKED", (
            f"FODT is unexpectedly STALE_BLOCKED. Reasons: {result['reasons']}"
        )

    def test_fods_checks_dict_present(self):
        result = detect_stale_state("fods")
        assert "checks" in result
        assert isinstance(result["checks"], dict)

    def test_fodt_checks_dict_present(self):
        result = detect_stale_state("fodt")
        assert "checks" in result

    def test_fods_directory_exists_check_pass(self):
        result = detect_stale_state("fods")
        assert result["checks"].get("directory_exists") == "PASS"

    def test_fodt_directory_exists_check_pass(self):
        result = detect_stale_state("fodt")
        assert result["checks"].get("directory_exists") == "PASS"

    def test_fods_reasons_is_list(self):
        result = detect_stale_state("fods")
        assert isinstance(result["reasons"], list)

    def test_fods_blocker_count_is_int(self):
        result = detect_stale_state("fods")
        assert isinstance(result["blocker_count"], int)

    def test_result_json_serializable(self):
        import json
        result = detect_stale_state("fods")
        # Should not raise
        json.dumps(result)


# ===========================================================================
# TestMissingFormat
# ===========================================================================

class TestMissingFormat:
    def test_missing_format_returns_stale_blocked(self):
        result = detect_stale_state("nonexistent_format_xyz")
        assert result["verdict"] == "STALE_BLOCKED"
        assert result["blocker_count"] >= 1

    def test_missing_format_directory_check_fail(self):
        result = detect_stale_state("nonexistent_format_xyz")
        assert result["checks"].get("directory_exists") == "FAIL"


# ===========================================================================
# TestSyntheticStaleStates
# ===========================================================================

class TestSyntheticStaleStates:
    def test_verifier_older_than_generation_triggers_blocker(self, tmp_path):
        """When verifier review timestamp < requirements generation timestamp, expect STALE_BLOCKED."""
        import yaml
        # Create a synthetic requirements dir
        fmt_dir = tmp_path / "synfmt"
        fmt_dir.mkdir()

        # Requirements file: newer timestamp
        cr_content = {
            "format": "synfmt",
            "generation_timestamp": "2026-06-01T00:00:00Z",
            "requirements": [],
        }
        for fname in ["commercial-requirements.yaml", "object-model-requirements.yaml",
                       "save-edit-requirements.yaml", "conversion-requirements.yaml",
                       "traceability-map.yaml"]:
            (fmt_dir / fname).write_text(yaml.dump(cr_content), encoding="utf-8")

        # Verifier review: older timestamp
        vr_content = {
            "format": "synfmt",
            "review_timestamp": "2026-05-01T00:00:00Z",  # OLDER than requirements
            "verifier_verdict": {"result": "LANE_R5_PASS"},
        }
        (fmt_dir / "verifier-review.yaml").write_text(yaml.dump(vr_content), encoding="utf-8")

        from stale_detection import detect_stale_state as _det
        with patch("stale_detection.REQS_DIR", tmp_path):
            result = _det("synfmt")

        assert result["checks"].get("verifier_after_generation") == "FAIL"
        assert result["blocker_count"] >= 1
        assert result["verdict"] == "STALE_BLOCKED"

    def test_accepted_count_mismatch_triggers_blocker(self, tmp_path):
        """When registry accepted_count != file count, expect STALE_BLOCKED."""
        import yaml
        fmt_dir = tmp_path / "synfmt2"
        fmt_dir.mkdir()

        # Requirements files with 2 accepted requirements
        cr_content = {
            "format": "synfmt2",
            "generation_timestamp": "2026-05-13T00:00:00Z",
            "requirements": [
                {"requirement_id": "SYN-001", "status": "ACCEPTED_FOR_VERTICAL_SLICE"},
                {"requirement_id": "SYN-002", "status": "ACCEPTED_FOR_VERTICAL_SLICE"},
            ],
        }
        for fname in ["commercial-requirements.yaml", "object-model-requirements.yaml",
                       "save-edit-requirements.yaml", "conversion-requirements.yaml",
                       "traceability-map.yaml"]:
            (fmt_dir / fname).write_text(yaml.dump(cr_content), encoding="utf-8")

        vr_content = {
            "format": "synfmt2",
            "review_timestamp": "2026-05-13T00:00:00Z",
            "verifier_verdict": {"result": "LANE_R5_PASS"},
        }
        (fmt_dir / "verifier-review.yaml").write_text(yaml.dump(vr_content), encoding="utf-8")

        # Patch registry to return accepted_count=99 (mismatch with actual=2)
        mock_registry = {
            "formats": [{
                "format_id": "synfmt2",
                "generated_requirements": {
                    "iv_status": "ESTABLISHED",
                    "iv_date": "2026-05-13",
                    "accepted_count": 99,  # Mismatch!
                }
            }]
        }
        import yaml as _yaml
        from stale_detection import detect_stale_state as _det

        with patch("stale_detection.REQS_DIR", tmp_path), \
             patch("stale_detection.REGISTRY_PATH") as mock_rp:
            mock_rp.exists.return_value = True
            mock_rp.read_text.return_value = _yaml.dump(mock_registry)
            result = _det("synfmt2")

        assert result["checks"].get("accepted_count_consistent") == "FAIL"
        assert result["blocker_count"] >= 1
        assert result["verdict"] == "STALE_BLOCKED"


# ===========================================================================
# TestResolverIntegration
# ===========================================================================

class TestResolverIntegration:
    def test_fods_resolver_stale_field_present(self):
        from format_context_resolver import resolve_format_context
        ctx = resolve_format_context("fods")
        stale = ctx["requirements_state"].get("stale")
        assert stale is not None

    def test_fodt_resolver_stale_field_present(self):
        from format_context_resolver import resolve_format_context
        ctx = resolve_format_context("fodt")
        stale = ctx["requirements_state"].get("stale")
        assert stale is not None

    def test_fods_stale_field_has_verdict(self):
        from format_context_resolver import resolve_format_context
        ctx = resolve_format_context("fods")
        stale = ctx["requirements_state"]["stale"]
        assert isinstance(stale, dict)
        assert "verdict" in stale

    def test_resolver_stale_not_stale_blocked_live(self):
        from format_context_resolver import resolve_format_context
        for fmt in ("fods", "fodt"):
            ctx = resolve_format_context(fmt)
            stale = ctx["requirements_state"]["stale"]
            assert stale["verdict"] != "STALE_BLOCKED", (
                f"{fmt} resolver unexpectedly surfaced STALE_BLOCKED: {stale['reasons']}"
            )


# ===========================================================================
# TestLaneSelectorStaleIntegration
# ===========================================================================

class TestLaneSelectorStaleIntegration:
    def _make_authoritative_ctx(self, stale_verdict: str) -> dict:
        """Build a minimal authoritative context with controllable stale verdict."""
        return {
            "format_id": "testfmt",
            "requirements_state": {
                "status": "REQUIREMENTS_AUTHORITATIVE",
                "iv_status": "PASS",
                "verifier_result": "LANE_R5_PASS",
                "accepted_count": 20,
                "missing_files": [],
                "stale": {"verdict": stale_verdict, "reasons": ["synthetic"], "checks": {}, "blocker_count": 1 if stale_verdict == "STALE_BLOCKED" else 0},
                "blocker_reason": None,
            },
            "gate_state": {
                "gates_passed": 10,
                "commercial_product_ready": False,
                "gate_11_status": "commercial_readiness_in_progress",
                "blocker": None,
            },
            "known_constraints": [],
            "governance": {
                "commercial_product_ready": False,
                "gate_self_approval_allowed": False,
                "autonomous_implementation_allowed": False,
            },
        }

    def test_stale_blocked_blocks_implementation_lanes(self):
        from lane_selector import select_lanes, IMPLEMENTATION_LANES
        ctx = self._make_authoritative_ctx("STALE_BLOCKED")
        result = select_lanes(ctx)
        for il in IMPLEMENTATION_LANES:
            assert il in result["blocked_lanes"], f"{il} should be blocked when STALE_BLOCKED"

    def test_stale_blocked_selects_lane_r5(self):
        from lane_selector import select_lanes
        ctx = self._make_authoritative_ctx("STALE_BLOCKED")
        result = select_lanes(ctx)
        assert "LANE-R5" in result["selected_lanes"]

    def test_fresh_allows_implementation_lanes(self):
        from lane_selector import select_lanes, IMPLEMENTATION_LANES
        ctx = self._make_authoritative_ctx("FRESH")
        result = select_lanes(ctx)
        for il in IMPLEMENTATION_LANES:
            assert il in result["selected_lanes"], f"{il} should be selected when FRESH"

    def test_review_required_allows_implementation_lanes(self):
        """REVIEW_REQUIRED is a soft warning — implementation lanes should still be selected."""
        from lane_selector import select_lanes, IMPLEMENTATION_LANES
        ctx = self._make_authoritative_ctx("REVIEW_REQUIRED")
        result = select_lanes(ctx)
        for il in IMPLEMENTATION_LANES:
            assert il in result["selected_lanes"], f"{il} should be selected when REVIEW_REQUIRED"


# ===========================================================================
# TestPromptGeneratorStaleBlock
# ===========================================================================

class TestPromptGeneratorStaleBlock:
    def test_stale_blocked_prevents_prompt_generation(self):
        from swarm_prompt_generator import generate_prompt
        from unittest.mock import patch

        def fake_resolve(fmt, verbose=False):
            return {
                "format_id": fmt,
                "requirements_state": {
                    "status": "REQUIREMENTS_AUTHORITATIVE",
                    "stale": {"verdict": "STALE_BLOCKED", "reasons": ["synthetic stale"], "blocker_count": 1},
                    "accepted_count": 20,
                    "iv_status": "PASS",
                    "verifier_result": "LANE_R5_PASS",
                    "missing_files": [],
                    "blocker_reason": None,
                },
                "gate_state": {"gates_passed": 10, "commercial_product_ready": False, "gate_11_status": None, "blocker": None},
                "known_constraints": [],
                "governance": {"commercial_product_ready": False, "gate_self_approval_allowed": False, "autonomous_implementation_allowed": False},
            }

        def fake_select(ctx):
            return {"selected_lanes": [], "blocked_lanes": [], "lane_details": {}}

        with patch("format_context_resolver.resolve_format_context", fake_resolve), \
             patch("lane_selector.select_lanes", fake_select):
            result = generate_prompt("fods", "TEST-SPRINT-001", "test mission")

        assert result["prompt"] is None
        assert "BLOCKED_STALE" in result["generator_status"]

    def test_fresh_state_allows_prompt_generation(self):
        """When stale verdict is FRESH, prompt generation should not be blocked by stale check."""
        from swarm_prompt_generator import generate_prompt
        # Use live data — FODS is FRESH
        result = generate_prompt("fods", "CONWAY-R7R8-TEST-001", "Test mission.")
        # Should generate (or be blocked only by non-authoritative, not by stale)
        if result["prompt"] is not None:
            assert "BLOCKED_STALE" not in result["generator_status"]
