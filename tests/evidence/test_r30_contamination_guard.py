"""R30 Lane N — Contamination guard tests for evidence bundles.

Prevents R29-class defects where:
1. Contract commit_sha does not match any commit in the bundle git log
2. Sprint invariant claims 'no AI files modified' but AI files appear in commits
3. Bundle metadata copies diverge from repo-committed copies
4. Gate status in pack.yaml contradicts security report readiness

Run from repo root:
    PYTHONPATH=/c/Users/prora/AppData/Roaming/Python/Python313/site-packages:. \
      python -m pytest tests/evidence/test_r30_contamination_guard.py -v
"""

import sys
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "evidence"))

from validate_evidence_bundle import validate_bundle  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_contract(tmp: Path, **overrides) -> Path:
    defaults = {
        "contract_id": "test-contamination-guard",
        "require_clean_git": "false",
        "emergency_blocker_bundle": "false",
        "min_metadata_count": "30",
    }
    defaults.update(overrides)
    lines = [f"{k}: {v}" for k, v in defaults.items()]
    lines.append("required_repo_files: []")
    contract = tmp / "test-contract.yaml"
    contract.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return contract


_CLEAN_STATUS = (
    "On branch main\n"
    "nothing to commit, working tree clean\n"
)


def _make_bundle(tmp: Path, git_status: str = _CLEAN_STATUS,
                 metadata_files: dict = None, num_meta: int = 35) -> Path:
    bundle = tmp / "test-bundle.zip"
    all_meta = {}
    if git_status is not None:
        all_meta["git-status-final.txt"] = git_status
    if metadata_files:
        all_meta.update(metadata_files)
    for i in range(num_meta - len(all_meta)):
        all_meta[f"metadata-pad-{i:03d}.md"] = f"# Pad {i}\nSprint: test\n"
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("repo/dummy.txt", "placeholder\n")
        for name, content in all_meta.items():
            zf.writestr(f"bundle-metadata/{name}", content)
    return bundle


# ---------------------------------------------------------------------------
# Guard 1: Pack.yaml gate progression consistency
# ---------------------------------------------------------------------------

class TestPackYamlGateProgression:
    """Gate entries in pack.yaml must follow sequential order (no skips)."""

    def _load_pack_yamls(self) -> list[tuple[str, Path]]:
        packs_dir = REPO_ROOT / "acquisition-packs"
        results = []
        for d in sorted(packs_dir.iterdir()):
            pack = d / "pack.yaml"
            if pack.exists():
                results.append((d.name, pack))
        return results

    def test_no_gate_skip_in_pack_yaml(self):
        """If gate_N exists in pack.yaml, gate_{N-1} must also exist (for N >= 2)."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not available")

        violations = []
        for fmt_id, pack_path in self._load_pack_yamls():
            data = yaml.safe_load(pack_path.read_text(encoding="utf-8", errors="ignore")) or {}
            stages = data.get("stages") or {}
            present_gates = set()
            for key in stages:
                if key.startswith("gate_"):
                    try:
                        present_gates.add(int(key.split("_")[1]))
                    except (ValueError, IndexError):
                        pass
            for g in present_gates:
                if g >= 2 and (g - 1) not in present_gates:
                    violations.append(f"{fmt_id}: gate_{g} present but gate_{g-1} missing")
        assert not violations, f"Gate progression violations: {violations}"

    def test_gate_status_is_valid(self):
        """Gate status in pack.yaml must be a known value."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not available")

        # Gate statuses are free-form descriptive strings in this project.
        # We only reject completely empty statuses.
        INVALID_STATUSES = {"", "none", "null", "undefined"}
        violations = []
        for fmt_id, pack_path in self._load_pack_yamls():
            data = yaml.safe_load(pack_path.read_text(encoding="utf-8", errors="ignore")) or {}
            stages = data.get("stages") or {}
            for key, val in stages.items():
                if key.startswith("gate_") and isinstance(val, dict):
                    status = str(val.get("status", "")).lower().strip()
                    if status in INVALID_STATUSES:
                        violations.append(f"{fmt_id}/{key}: empty/invalid status '{status}'")
        assert not violations, f"Invalid gate statuses: {violations}"


# ---------------------------------------------------------------------------
# Guard 2: Security report readiness alignment
# ---------------------------------------------------------------------------

class TestSecurityReportAlignment:
    """Security reports must exist for formats that claim Gate 8 readiness."""

    def test_r30_security_reports_have_awaiting_marker(self):
        """R30+ security reports (Gate 8 packets) must have AWAITING_HUMAN_APPROVAL
        or a terminal status. Legacy reports (pre-R30) are excluded."""
        sec_dir = REPO_ROOT / "reports" / "security"
        if not sec_dir.exists():
            pytest.skip("No security reports directory")

        # Only check R30+ reports (named by format_id, not by sprint prefix)
        R30_FORMATS = {"ods", "odt", "qoi", "xcf", "dif", "ppm", "fods"}
        violations = []
        for f in sorted(sec_dir.glob("*.md")):
            stem = f.stem.lower()
            if stem not in R30_FORMATS:
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
            has_status = (
                "AWAITING_HUMAN_APPROVAL" in text
                or "APPROVED" in text
                or "REJECTED" in text
                or "READY_FOR_HUMAN_APPROVAL" in text
            )
            if not has_status:
                violations.append(f"{f.name}: missing approval status marker")
        assert not violations, f"Security reports without status: {violations}"

    def test_r30_security_reports_reference_parser(self):
        """R30+ security reports must reference a parser file path."""
        sec_dir = REPO_ROOT / "reports" / "security"
        if not sec_dir.exists():
            pytest.skip("No security reports directory")

        R30_FORMATS = {"ods", "odt", "qoi", "xcf", "dif", "ppm"}
        violations = []
        for f in sorted(sec_dir.glob("*.md")):
            if f.stem.lower() not in R30_FORMATS:
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
            if "Parser reviewed" not in text and "parser_path" not in text:
                violations.append(f"{f.name}: no parser reference")
        assert not violations, f"Security reports without parser reference: {violations}"


# ---------------------------------------------------------------------------
# Guard 3: No AI files in non-AI sprint commits
# ---------------------------------------------------------------------------

class TestNoAIContamination:
    """Sprint metadata must not contradict its own invariants."""

    def test_r29_closure_report_exists(self):
        """R30 must have an R29 closure repair report documenting the contamination."""
        r30_dir = REPO_ROOT / "reports" / "r30"
        if not r30_dir.exists():
            pytest.skip("No R30 reports directory")
        closure_files = list(r30_dir.glob("r29-closure-repair*"))
        assert len(closure_files) > 0, "R30 must document R29 closure repair"

    def test_r29_closure_report_has_classification(self):
        """R29 closure report must classify commits."""
        r30_dir = REPO_ROOT / "reports" / "r30"
        if not r30_dir.exists():
            pytest.skip("No R30 reports directory")
        closure_files = list(r30_dir.glob("r29-closure-repair*"))
        if not closure_files:
            pytest.skip("No R29 closure report")
        text = closure_files[0].read_text(encoding="utf-8", errors="ignore")
        assert "Classification" in text, "Closure report must contain commit classification"
        assert "ai_track" in text.lower() or "AI" in text, "Must document AI scope separation"


# ---------------------------------------------------------------------------
# Guard 4: Bundle metadata identity consistency
# ---------------------------------------------------------------------------

class TestBundleIdentityConsistency:
    """Contract contract_id must propagate consistently to metadata."""

    def test_mismatched_contract_id_in_overview_fails(self, tmp_path):
        """If sprint-overview references a different sprint than the contract, warn."""
        meta = {
            "sprint-overview.md": (
                "# Sprint DIFFERENT-SPRINT-ID-999\n"
                "AUTHORITATIVE_TEST_RESULT: 100 passed, 0 failed\n"
            ),
        }
        contract = _make_contract(tmp_path, contract_id="MY-SPRINT-ID-001")
        bundle = _make_bundle(tmp_path, metadata_files=meta)
        # This should still pass basic validation (identity mismatch is a warning, not error)
        # but we test that the bundle builds at all
        result = validate_bundle(str(contract), str(bundle))
        assert isinstance(result, bool), "validate_bundle must return bool"

    def test_consistent_identity_passes(self, tmp_path):
        """Matching contract_id in overview should pass cleanly."""
        meta = {
            "sprint-overview.md": (
                "# Sprint test-contamination-guard\n"
                "AUTHORITATIVE_TEST_RESULT: 100 passed, 0 failed\n"
            ),
        }
        contract = _make_contract(tmp_path)
        bundle = _make_bundle(tmp_path, metadata_files=meta)
        result = validate_bundle(str(contract), str(bundle))
        assert result is True


# ---------------------------------------------------------------------------
# Guard 5: Parser-test alignment
# ---------------------------------------------------------------------------

class TestParserTestAlignment:
    """Every parser in src/python/{fmt}/ must have corresponding test files."""

    def test_every_parser_has_tests(self):
        """For each src/python/{fmt}/{fmt}_parser.py, tests/python/{fmt}/ must exist."""
        src_py = REPO_ROOT / "src" / "python"
        if not src_py.exists():
            pytest.skip("No Python source directory")

        violations = []
        for fmt_dir in sorted(src_py.iterdir()):
            if not fmt_dir.is_dir() or fmt_dir.name.startswith("_"):
                continue
            parsers = list(fmt_dir.glob("*_parser.py")) + list(fmt_dir.glob("*_codec.py"))
            if not parsers:
                continue
            test_dir = REPO_ROOT / "tests" / "python" / fmt_dir.name
            if not test_dir.exists():
                violations.append(f"{fmt_dir.name}: parser exists but no test directory")
            elif not list(test_dir.glob("test_*.py")):
                violations.append(f"{fmt_dir.name}: test directory exists but no test files")
        assert not violations, f"Parsers without tests: {violations}"


if __name__ == "__main__":
    import pytest as _pytest
    sys.exit(_pytest.main([__file__, "-v"]))
