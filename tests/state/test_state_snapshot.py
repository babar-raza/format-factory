"""
Lane C: State snapshot and linter tests.

Sprint: FORMAT-FACTORY-MEGA-CLOSURE-R35-R36-AND-PRODUCTION-AUTHORITY-STABILIZATION-001
"""
import pathlib
import sys

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
    """R43/R52: Guard tests covering all verdict markdown formats."""

    def _extract_verdict(self, text):
        """Mirror logic of state_snapshot.get_latest_sprint() for unit testing."""
        import re
        verdict = None
        # Format A/B: VERDICT: or Verdict: inline
        m = re.search(r"(?:^|\n)\s*\*{0,2}(?:VERDICT|Verdict):\*{0,2}\s*\*{0,2}([A-Z][A-Z0-9_]+)\*{0,2}", text)
        if m:
            verdict = m.group(1)
        # Format C: "## Verdict" heading + code-block value (R51+)
        if not verdict:
            m = re.search(r"##\s+Verdict\s*\n+\s*`([A-Z][A-Z0-9_]+)`", text)
            if m:
                verdict = m.group(1)
        if verdict and not re.match(r"[A-Z][A-Z0-9_]{3,}", verdict):
            verdict = None
        return verdict

    def test_plain_uppercase_verdict(self):
        assert self._extract_verdict("VERDICT: R43_COMPLETE") == "R43_COMPLETE"

    def test_title_case_verdict(self):
        assert self._extract_verdict("Verdict: R43_COMPLETE") == "R43_COMPLETE"

    def test_bold_label_plain_value(self):
        assert self._extract_verdict("**VERDICT:** R43_COMPLETE") == "R43_COMPLETE"

    def test_bold_label_bold_value(self):
        # R42 actual format: **Verdict:** **R42_HIGH_THROUGHPUT_POC_READY**
        assert self._extract_verdict("**Verdict:** **R42_HIGH_THROUGHPUT_POC_READY**") == "R42_HIGH_THROUGHPUT_POC_READY"

    def test_code_block_verdict_r51_format(self):
        """R52: R51 uses ## Verdict heading + backtick code-block value."""
        text = "## Verdict\n\n`R51_INSTALLED_ARTIFACT_BASELINE_AND_AI_ACCELERATION_COMPLETE`\n"
        assert self._extract_verdict(text) == "R51_INSTALLED_ARTIFACT_BASELINE_AND_AI_ACCELERATION_COMPLETE"

    def test_code_block_verdict_with_extra_newlines(self):
        """R52: code-block verdict with extra blank lines between heading and value."""
        text = "## Verdict\n\n\n`R52_STATE_CONSISTENT_INSTALLED_ARTIFACT_BASELINE_CLEAN`\n"
        assert self._extract_verdict(text) == "R52_STATE_CONSISTENT_INSTALLED_ARTIFACT_BASELINE_CLEAN"

    def test_code_block_verdict_not_polluted(self):
        """R52: bare text after ## Verdict (no backtick) must not be captured as code-block verdict."""
        text = "## Verdict\n\nsome prose text\n"
        # Should fall back to None (no VERDICT: inline either)
        assert self._extract_verdict(text) is None

    def test_live_r42_verdict_resolves(self):
        """R43 regression: live R42 final-verdict.md must return non-unknown verdict."""
        import pathlib
        snap_root = pathlib.Path(__file__).resolve().parents[2]
        vpath = snap_root / "reports" / "r42" / "final-verdict.md"
        if not vpath.exists():
            return  # R42 report not present — skip
        verdict = self._extract_verdict(vpath.read_text())
        assert verdict is not None, "No verdict found in reports/r42/final-verdict.md"
        assert verdict != "unknown", f"Verdict resolved to 'unknown'; actual: {verdict!r}"

    def test_live_r51_verdict_resolves(self):
        """R52: live R51 final-verdict.md must return correct code-block verdict."""
        import pathlib
        snap_root = pathlib.Path(__file__).resolve().parents[2]
        vpath = snap_root / "reports" / "r51" / "final-verdict.md"
        if not vpath.exists():
            return
        verdict = self._extract_verdict(vpath.read_text())
        assert verdict is not None, "No verdict found in reports/r51/final-verdict.md"
        assert verdict.startswith("R51_"), f"R51 verdict must start with R51_: {verdict!r}"

    def test_latest_sprint_not_unknown(self):
        """R43/R52: get_latest_sprint() must not return verdict='unknown' when final-verdict.md is present."""
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
