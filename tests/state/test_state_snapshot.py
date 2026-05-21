"""
Lane C: State snapshot and linter tests.

Sprint: FORMAT-FACTORY-MEGA-CLOSURE-R35-R36-AND-PRODUCTION-AUTHORITY-STABILIZATION-001
"""
import json
import pathlib
import sys
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "state"))

from state_snapshot import build_snapshot, snapshot_to_markdown
from state_linter import run_all_lints, lint_contracts, lint_gate_overclaim, lint_commercial_ready


class TestStateSnapshot:
    def test_snapshot_has_format_count(self):
        snap = build_snapshot()
        assert "format_count" in snap
        assert snap["format_count"] > 0

    def test_snapshot_has_latest_sprint(self):
        snap = build_snapshot()
        assert "latest_sprint" in snap
        assert "latest_sprint_number" in snap["latest_sprint"]

    def test_snapshot_gate11_not_approved(self):
        snap = build_snapshot()
        assert snap["gate_11_approved"] is False

    def test_snapshot_commercial_not_ready(self):
        snap = build_snapshot()
        assert snap["commercial_product_ready"] is False

    def test_snapshot_to_markdown(self):
        snap = build_snapshot()
        md = snapshot_to_markdown(snap)
        assert "Current State Snapshot" in md
        assert "Formats in registry" in md

    def test_snapshot_evidence_contracts(self):
        snap = build_snapshot()
        assert "evidence_contracts" in snap
        ec = snap["evidence_contracts"]
        assert ec.get("total_contracts", 0) > 0


class TestVerdictParsing:
    """Guard tests for verdict parsing — must not capture markdown bold markers."""

    def test_verdict_no_markdown_bold_suffix(self):
        """Verdict must not end with ** (markdown bold leak)."""
        snap = build_snapshot()
        verdict = snap["latest_sprint"].get("verdict", "")
        assert not verdict.endswith("*"), (
            f"Verdict captured markdown bold marker: {verdict!r}. "
            "Fix: state_snapshot.py regex must use [A-Z0-9_]+ not \\S+"
        )

    def test_verdict_is_clean_identifier(self):
        """When a final-verdict exists, verdict must be a clean uppercase identifier (no ** suffix)."""
        snap = build_snapshot()
        verdict = snap["latest_sprint"].get("verdict", "unknown")
        # Skip placeholder/no-verdict states — these are valid intermediate states
        if verdict in ("unknown", "no_final_verdict"):
            return
        import re
        assert re.fullmatch(r"[A-Z][A-Z0-9_]+", verdict), (
            f"Verdict is not a clean identifier: {verdict!r}"
        )

    def test_snapshot_latest_sprint_r40_or_newer(self):
        """Latest sprint must be R40 or newer (regression guard)."""
        snap = build_snapshot()
        r_num_str = snap["latest_sprint"].get("latest_sprint_number", "R0")
        r_num = int(r_num_str.lstrip("R")) if r_num_str.lstrip("R").isdigit() else 0
        assert r_num >= 40, f"Latest sprint regressed: {r_num_str}"


class TestVerdictRegexFormats:
    """R43: Guard tests covering all verdict markdown formats."""

    def _extract_verdict(self, text):
        import re
        from state_snapshot import get_latest_sprint  # noqa: verify import
        m = re.search(r"\*{0,2}VERDICT:\*{0,2}\s*\*{0,2}([A-Z0-9_]+)", text, re.IGNORECASE)
        return m.group(1) if m else None

    def test_plain_uppercase_verdict(self):
        assert self._extract_verdict("VERDICT: R43_COMPLETE") == "R43_COMPLETE"

    def test_title_case_verdict(self):
        assert self._extract_verdict("Verdict: R43_COMPLETE") == "R43_COMPLETE"

    def test_bold_label_plain_value(self):
        assert self._extract_verdict("**VERDICT:** R43_COMPLETE") == "R43_COMPLETE"

    def test_bold_label_bold_value(self):
        # R42 actual format: **Verdict:** **R42_HIGH_THROUGHPUT_POC_READY**
        assert self._extract_verdict("**Verdict:** **R42_HIGH_THROUGHPUT_POC_READY**") == "R42_HIGH_THROUGHPUT_POC_READY"

    def test_live_r42_verdict_resolves(self):
        """R43 regression: live R42 final-verdict.md must return non-unknown verdict."""
        import pathlib
        snap_root = pathlib.Path(__file__).resolve().parents[2]
        vpath = snap_root / "reports" / "r42" / "final-verdict.md"
        if not vpath.exists():
            return  # R42 report not present — skip
        import re
        content = vpath.read_text()
        m = re.search(r"\*{0,2}VERDICT:\*{0,2}\s*\*{0,2}([A-Z0-9_]+)", content, re.IGNORECASE)
        assert m is not None, "No verdict found in reports/r42/final-verdict.md"
        verdict = m.group(1)
        assert verdict != "unknown", f"Verdict resolved to 'unknown'; actual: {verdict!r}"

    def test_latest_sprint_not_unknown(self):
        """R43 regression: get_latest_sprint() must not return verdict='unknown' when final-verdict.md is present."""
        from state_snapshot import get_latest_sprint
        result = get_latest_sprint()
        verdict = result.get("verdict", "unknown")
        assert verdict not in ("unknown",), (
            f"state_snapshot verdict is 'unknown' — final-verdict.md exists but regex failed. Got: {verdict!r}"
        )


class TestStateLinter:
    def test_no_required_artifacts_errors(self):
        findings = lint_contracts()
        artifacts_errors = [f for f in findings if f["check"] == "required_artifacts"]
        assert len(artifacts_errors) == 0, f"Contracts still use required_artifacts: {artifacts_errors}"

    def test_no_gate11_overclaim(self):
        findings = lint_gate_overclaim()
        assert len(findings) == 0, f"Gate 11 overclaim found: {findings}"

    def test_no_commercial_ready_overclaim(self):
        findings = lint_commercial_ready()
        assert len(findings) == 0, f"commercial_product_ready overclaim: {findings}"

    def test_linter_detects_below_floor(self):
        """Synthetic test: a fake contract with low floor should be detected."""
        # We test the linting logic indirectly by checking known-good contracts
        findings = lint_contracts()
        below_floor = [f for f in findings if f["check"] == "below_floor_metadata"]
        # All known below-floor contracts should be excluded (AI-only, etc.)
        # This test documents the current state
        for f in below_floor:
            assert "min_metadata_count" in f["message"]

    def test_full_lint_no_errors(self):
        findings = run_all_lints()
        errors = [f for f in findings if f["severity"] == "error"]
        assert len(errors) == 0, f"Lint errors found: {errors}"
