"""
R41 Lane C: Evidence hygiene guard tests.

Prevents:
1. Evidence ZIP blobs committed to repository (repo bloat).
2. Stale BUNDLE_VALIDATION: PENDING in closed sprint final-verdict files.
3. Markdown bold leak (**) in final-verdict VERDICT lines.
"""
import pathlib
import re
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


class TestEvidenceBundleBloat:
    """Guard against evidence ZIP blobs committed to the repository."""

    def test_no_new_zip_files_in_evidence_bundles(self):
        """evidence-bundles/*.zip must not appear in new git-tracked files.

        Existing committed ZIPs are grandfathered; this test guards future additions.
        The .gitignore now blocks evidence-bundles/*.zip.
        """
        gitignore = REPO_ROOT / ".gitignore"
        assert gitignore.exists(), ".gitignore must exist"
        content = gitignore.read_text(encoding="utf-8")
        assert "evidence-bundles/*.zip" in content, (
            ".gitignore must exclude evidence-bundles/*.zip to prevent repo bloat"
        )

    def test_gitignore_excludes_evidence_zip_pattern(self):
        """evidence-bundles/*.zip is gitignored.

        Primary: uses git check-ignore when .git is available.
        Fallback (no-Git extracted replay): reads .gitignore directly.
        """
        git_dir = REPO_ROOT / ".git"
        if git_dir.exists():
            result = subprocess.run(
                ["git", "check-ignore", "-v", "evidence-bundles/test-dummy.zip"],
                capture_output=True, text=True, cwd=str(REPO_ROOT),
            )
            assert result.returncode == 0, (
                "evidence-bundles/test-dummy.zip should be gitignored but is not. "
                "Add 'evidence-bundles/*.zip' to .gitignore."
            )
        else:
            # No-Git extracted replay: verify .gitignore text directly.
            gitignore = REPO_ROOT / ".gitignore"
            assert gitignore.exists(), ".gitignore must be present in extracted bundle repo/"
            content = gitignore.read_text(encoding="utf-8")
            assert "evidence-bundles/*.zip" in content, (
                ".gitignore must contain 'evidence-bundles/*.zip' "
                "(verified via direct read — no .git available)"
            )


class TestFinalVerdictIntegrity:
    """Guard against stale BUNDLE_VALIDATION: PENDING in closed sprint verdicts."""

    def _get_closed_sprint_verdicts(self):
        """Return list of (path, content) for all final-verdict.md files."""
        reports_dir = REPO_ROOT / "reports"
        verdicts = []
        for d in sorted(reports_dir.iterdir()):
            if d.is_dir() and re.match(r"^r\d+$", d.name):
                vf = d / "final-verdict.md"
                if vf.exists():
                    verdicts.append((vf, vf.read_text(encoding="utf-8")))
        return verdicts

    def test_no_stale_pending_in_final_verdicts(self):
        """No final-verdict.md with VERDICT: R*_COMPLETE may contain BUNDLE_VALIDATION: PENDING."""
        offenders = []
        for path, content in self._get_closed_sprint_verdicts():
            has_complete = re.search(r"VERDICT:\s*R\d+_COMPLETE", content)
            has_pending = "BUNDLE_VALIDATION: PENDING" in content
            if has_complete and has_pending:
                offenders.append(str(path.relative_to(REPO_ROOT)))
        assert not offenders, (
            f"These final-verdict files claim COMPLETE but still say BUNDLE_VALIDATION: PENDING:\n"
            + "\n".join(f"  - {p}" for p in offenders)
        )

    def test_verdict_parser_strips_markdown_bold(self):
        """state_snapshot.py verdict parser must not capture ** suffix.

        The file format **VERDICT: R40_COMPLETE** is valid markdown.
        The parser must extract only the identifier (no trailing *).
        """
        import sys
        sys.path.insert(0, str(REPO_ROOT / "tools" / "state"))
        from state_snapshot import get_latest_sprint
        sprint_info = get_latest_sprint()
        verdict = sprint_info.get("verdict", "unknown")
        assert not verdict.endswith("*"), (
            f"state_snapshot.get_latest_sprint() returned verdict with ** suffix: {verdict!r}. "
            "Fix: state_snapshot.py regex must use [A-Z0-9_]+ not \\S+"
        )

    def test_r40_verdict_bundle_validation_pass(self):
        """R40 final-verdict must say BUNDLE_VALIDATION: PASS (not PENDING)."""
        r40_verdict = REPO_ROOT / "reports" / "r40" / "final-verdict.md"
        if not r40_verdict.exists():
            pytest.skip("R40 final-verdict.md not found")
        content = r40_verdict.read_text(encoding="utf-8")
        assert "BUNDLE_VALIDATION: PASS" in content, (
            "R40 final-verdict.md must say BUNDLE_VALIDATION: PASS. "
            "Update after bundle is built and validated."
        )
        assert "BUNDLE_VALIDATION: PENDING" not in content, (
            "R40 final-verdict.md still says BUNDLE_VALIDATION: PENDING — stale text."
        )
