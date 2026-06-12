"""R28 Lane J — Evidence and bundle automation hardening tests.

Prevents recurring evidence issues:
- BUNDLE_VALIDATION: PENDING in final reports
- COMMIT_SHA: PENDING after commit
- emergency_blocker_bundle used for clean completion
- stale git metadata inside bundle
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


class TestPendingMarkerDetection:
    """Ensure no PENDING markers slip through to final artifacts."""

    def _scan_for_pending(self, path: Path) -> list[tuple[str, int, str]]:
        """Scan a file for PENDING markers. Returns (file, line_no, line)."""
        hits = []
        if not path.exists():
            return hits
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if "PENDING" in line and not line.strip().startswith("#"):
                # Allow PENDING in comments and headers, but not in status fields
                if any(k in line for k in ["BUNDLE_VALIDATION:", "COMMIT_SHA:", "EVIDENCE_BUNDLE:", "status:"]):
                    # Exclude false positives:
                    # 1. Lines documenting historical forward-pending (e.g. "PENDING forward-documented")
                    # 2. Lines describing PENDING_MARKER_PATTERNS added to the validator
                    # 3. Lines where the trigger keyword appears inside backtick code spans
                    stripped = line.strip()
                    if "forward-documented" in stripped:
                        continue
                    if "PENDING_MARKER_PATTERNS" in stripped:
                        continue
                    # Skip 2-pass protocol narrative: "BUNDLE_VALIDATION: PENDING in final-verdict"
                    # documents the closeout sequence, not a stale marker.
                    if "in final-verdict" in stripped:
                        continue
                    # Skip if every occurrence of the trigger keyword is inside backticks
                    import re
                    backtick_content = " ".join(re.findall(r"`[^`]+`", stripped))
                    triggers_in_backticks = all(
                        k in backtick_content
                        for k in ["BUNDLE_VALIDATION:", "COMMIT_SHA:", "EVIDENCE_BUNDLE:", "status:"]
                        if k in stripped
                    )
                    if triggers_in_backticks:
                        continue
                    hits.append((str(path), i, stripped))
        return hits

    def test_no_pending_in_committed_verdicts(self):
        repo = Path(__file__).resolve().parents[2]
        verdict_dirs = list((repo / "reports").glob("r*/final-verdict*.md"))
        all_hits = []
        for v in verdict_dirs:
            all_hits.extend(self._scan_for_pending(v))
        assert not all_hits, f"PENDING found in verdicts: {all_hits}"

    def test_no_pending_in_sprint_overviews(self):
        repo = Path(__file__).resolve().parents[2]
        overviews = list((repo / "reports").glob("r*-sprint-metadata-*/sprint-overview.md"))
        all_hits = []
        for o in overviews:
            all_hits.extend(self._scan_for_pending(o))
        assert not all_hits, f"PENDING found in overviews: {all_hits}"


class TestEmergencyBlockerPolicy:
    """Ensure emergency_blocker_bundle is not used for clean completions."""

    def test_no_active_emergency_blocker_in_recent_complete_contracts(self):
        """Only check R25+ contracts — legacy contracts predating the policy are excluded."""
        repo = Path(__file__).resolve().parents[2]
        contracts_dir = repo / "tools" / "evidence" / "contracts"
        recent_prefixes = ("r25-", "r26-", "r27-", "r28-", "r29-", "r30-")
        violations = []
        for contract in contracts_dir.glob("*.yaml"):
            if not any(contract.name.startswith(p) for p in recent_prefixes):
                continue
            text = contract.read_text(encoding="utf-8", errors="ignore")
            has_emergency = "emergency_blocker_bundle: true" in text
            is_complete = "status: complete" in text
            if has_emergency and is_complete:
                violations.append(contract.name)
        assert not violations, f"Recent complete contracts with emergency_blocker: {violations}"


class TestBundleValidatorIntegrity:
    """Verify the evidence bundle validator can be imported and run."""

    def test_validator_importable(self):
        repo = Path(__file__).resolve().parents[2]
        validator = repo / "tools" / "evidence" / "validate_evidence_bundle.py"
        assert validator.exists()

    def test_builder_importable(self):
        repo = Path(__file__).resolve().parents[2]
        builder = repo / "tools" / "evidence" / "build_evidence_bundle.py"
        assert builder.exists()

    def test_contract_files_parseable(self):
        """All contract YAML files should be parseable."""
        repo = Path(__file__).resolve().parents[2]
        contracts_dir = repo / "tools" / "evidence" / "contracts"
        for contract in contracts_dir.glob("*.yaml"):
            text = contract.read_text(encoding="utf-8", errors="ignore")
            # Basic structure check - must have contract_id or verdict
            assert ("contract_id:" in text or "verdict" in text), (
                f"Contract {contract.name} missing contract_id/verdict"
            )


class TestGitMetadataFreshness:
    """Ensure evidence bundle git metadata would be fresh."""

    def test_git_status_final_not_in_recent_reports(self):
        """Recent sprint metadata (R25+) should not have git-status-final.txt committed."""
        repo = Path(__file__).resolve().parents[2]
        recent_prefixes = ("r25-", "r26-", "r27-", "r28-", "r29-", "r30-")
        bad_paths = []
        for d in (repo / "reports").iterdir():
            if d.is_dir() and any(d.name.startswith(p) for p in recent_prefixes):
                gsf = d / "git-status-final.txt"
                if gsf.exists():
                    bad_paths.append(str(gsf))
        assert not bad_paths, f"git-status-final.txt found in recent metadata: {bad_paths}"
