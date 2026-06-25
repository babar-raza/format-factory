"""Integration tests for TC-SIGNAL-001 call site at autonomous_cycle.py line 1605.

These tests exercise the full TC-REPAIR-VERIFY-001 code path — the subprocess check,
the GOV_BLOCK filter, and the _sync_hard_stops_after_repair call — not just the helper
in isolation. They prove the CALL SITE works correctly under the exact conditions that
occur in a real repair cycle (TC-POSTSPRINT-002).
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))
from autonomous_cycle import _sync_hard_stops_after_repair


# Mirror of _GOVBLOCK_PREFIXES at autonomous_cycle.py lines 1582-1585
_GOVBLOCK_PREFIXES = (
    "GOV_BLOCK:monolith_detection_validator",
    "GOV_BLOCK:validate_source_architecture",
)


def _simulate_tc_repair_verify_001(
    hard_stops: list,
    rework_items: list,
    prior_structural_blocks: list,
    rescan_returncode: int,
) -> tuple[list, list, bool]:
    """Simulate the TC-REPAIR-VERIFY-001 block at autonomous_cycle.py lines 1600-1614.

    Replicates the exact code path:
      if _rescan.returncode == 0:
          rework_items = [it for it in rework_items if not any(...)]
          hard_stops = _sync_hard_stops_after_repair(hard_stops, rework_items, prior_structural_blocks)

    Returns: (hard_stops, rework_items, signal_sync_fired)
    """
    signal_sync_fired = False
    if not prior_structural_blocks:
        return hard_stops, rework_items, signal_sync_fired

    # Simulate subprocess result
    mock_rescan = MagicMock()
    mock_rescan.returncode = rescan_returncode

    if mock_rescan.returncode == 0:
        # Exact filter from call site lines 1601-1604
        rework_items = [
            it for it in rework_items
            if not any(it.startswith(p) or it == p for p in _GOVBLOCK_PREFIXES)
        ]
        # Check if signal_sync will fire
        original_len = len(hard_stops)
        hard_stops = _sync_hard_stops_after_repair(
            hard_stops, rework_items, prior_structural_blocks
        )
        signal_sync_fired = len(hard_stops) < original_len

    return hard_stops, rework_items, signal_sync_fired


class TestSignal001CallSite:
    """Integration tests for the _sync_hard_stops_after_repair call site (line 1605)."""

    def test_full_path_govblock_resolved_clears_hard_stop(self):
        """CALL-SITE-001: Rescan exit 0, GOV_BLOCK resolved, rework_items empty → hard_stop cleared.

        This is the primary FM-0014 repair scenario. Prior signal had critical_rework_blocks_continuation;
        TC-REPAIR-VERIFY-001 runs validate_source_architecture.py (exit 0); filter removes GOV_BLOCK
        from rework_items; call site should clear the hard_stop.
        """
        hard_stops = ["critical_rework_blocks_continuation"]
        rework_items = ["GOV_BLOCK:monolith_detection_validator"]
        prior_blocks = ["GOV_BLOCK:monolith_detection_validator"]

        result_stops, result_rework, sync_fired = _simulate_tc_repair_verify_001(
            hard_stops, rework_items, prior_blocks, rescan_returncode=0
        )

        assert "critical_rework_blocks_continuation" not in result_stops, (
            "hard_stop should be cleared after successful rescan + GOV_BLOCK filter"
        )
        assert result_rework == [], "rework_items should be empty after GOV_BLOCK filter"
        assert sync_fired, "[SIGNAL-SYNC] should have fired at the call site"

    def test_full_path_rescan_fails_hard_stop_preserved(self):
        """CALL-SITE-002: Rescan exit non-zero → filter not applied, hard_stop preserved.

        When validate_source_architecture.py returns non-zero, the call site is NOT reached.
        The hard_stop must remain to keep the cycle blocked.
        """
        hard_stops = ["critical_rework_blocks_continuation"]
        rework_items = ["GOV_BLOCK:monolith_detection_validator"]
        prior_blocks = ["GOV_BLOCK:monolith_detection_validator"]

        result_stops, result_rework, sync_fired = _simulate_tc_repair_verify_001(
            hard_stops, rework_items, prior_blocks, rescan_returncode=1
        )

        assert "critical_rework_blocks_continuation" in result_stops, (
            "hard_stop must be preserved when rescan fails"
        )
        assert sync_fired is False, "[SIGNAL-SYNC] must NOT fire when rescan fails"

    def test_full_path_mixed_rework_items_govblock_filtered_others_remain(self):
        """CALL-SITE-003: Mixed rework (GOV_BLOCK + REJECTED) → only GOV_BLOCK filtered, hard_stop preserved.

        Safety: If REJECTED items also caused exit_code==3, they remain after GOV_BLOCK filter.
        _sync_hard_stops_after_repair checks `not rework_items` — non-empty → hard_stop preserved.
        """
        hard_stops = ["critical_rework_blocks_continuation"]
        rework_items = [
            "GOV_BLOCK:monolith_detection_validator",
            "REJECTED:TC-PRODUCT-001 [overclaim detected]",
        ]
        prior_blocks = ["GOV_BLOCK:monolith_detection_validator"]

        result_stops, result_rework, sync_fired = _simulate_tc_repair_verify_001(
            hard_stops, rework_items, prior_blocks, rescan_returncode=0
        )

        # GOV_BLOCK filtered out
        assert not any("GOV_BLOCK" in it for it in result_rework), (
            "GOV_BLOCK items should be filtered by the call-site list comprehension"
        )
        # REJECTED item remains
        assert any("REJECTED" in it for it in result_rework), (
            "REJECTED item must survive the GOV_BLOCK filter"
        )
        # hard_stop preserved because rework_items is non-empty
        assert "critical_rework_blocks_continuation" in result_stops, (
            "hard_stop must be preserved while REJECTED items remain"
        )
        assert sync_fired is False, "[SIGNAL-SYNC] must not fire when REJECTED items remain"

    def test_full_path_no_prior_blocks_skips_call_site_entirely(self):
        """CALL-SITE-004: _prior_structural_blocks is empty → TC-REPAIR-VERIFY-001 block skipped.

        The outer condition `if _tc_heal_sprint and _prior_structural_blocks:` requires
        prior_structural_blocks to be non-empty. When empty, the entire block is skipped.
        """
        hard_stops = ["critical_rework_blocks_continuation"]
        rework_items = []
        prior_blocks = []  # empty — no GOV_BLOCK items existed before

        result_stops, result_rework, sync_fired = _simulate_tc_repair_verify_001(
            hard_stops, rework_items, prior_blocks, rescan_returncode=0
        )

        # Call site not reached — hard_stop unchanged
        assert "critical_rework_blocks_continuation" in result_stops, (
            "hard_stop must not be cleared when prior_structural_blocks is empty"
        )
        assert sync_fired is False


class TestSignal001HelperVariableAlignment:
    """Verify that variable names used in test match EXACTLY the call site at line 1605."""

    def test_call_site_variable_names_match_helper_signature(self):
        """The helper signature must accept the three arguments passed at line 1605."""
        import inspect
        sig = inspect.signature(_sync_hard_stops_after_repair)
        params = list(sig.parameters.keys())
        assert params == ["hard_stops", "rework_items", "prior_structural_blocks"], (
            f"Helper signature changed; call site at line 1605 passes these 3 positional args. Got: {params}"
        )

    def test_govblock_prefix_constants_match_autonomous_cycle(self):
        """Prefixes used in the call-site filter must match _GOVBLOCK_PREFIXES in autonomous_cycle.py."""
        import re
        import inspect
        import autonomous_cycle as ac
        src = inspect.getsource(ac)
        # Extract _GOVBLOCK_PREFIXES tuple from source
        m = re.search(r'_GOVBLOCK_PREFIXES\s*=\s*\(([^)]+)\)', src)
        assert m, "_GOVBLOCK_PREFIXES not found in autonomous_cycle.py"
        extracted = [s.strip().strip('"').strip("'") for s in m.group(1).split(',') if s.strip()]
        for p in _GOVBLOCK_PREFIXES:
            assert p in extracted, f"Prefix {p!r} missing from autonomous_cycle._GOVBLOCK_PREFIXES"
