"""
before_after_evidence.py — Before/after proof comparison (TC-FG-005).

Compares assertion strength of test files before and after a sprint.
Uses git-show to retrieve the baseline version of files.

Fallback: if git show fails (new file, no baseline, git unavailable), sets
baseline_revision="NO_BASELINE" and verdict="NEW_FILE".

Entry point: build_before_after_proof(...)
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

_SUPERVISOR = Path(__file__).resolve().parent
if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))

from proof_adequacy_contract import BeforeAfterProof, assess_proof_level


def _get_baseline_content(git_sha: str, rel_path: str, repo_root: str) -> Optional[str]:
    """Retrieve file content at a specific git SHA. Returns None on failure."""
    try:
        result = subprocess.run(
            ["git", "show", f"{git_sha}:{rel_path}"],
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=15,
        )
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass
    return None


def build_before_after_proof(
    requirement_id: str,
    baseline_git_sha: str,
    final_git_sha: str,
    test_paths: list,
    evidence_root: str,
    repo_root: str,
) -> BeforeAfterProof:
    """
    Generate a BeforeAfterProof by comparing test assertions before vs after sprint.

    Args:
        requirement_id: The work item ID being evaluated
        baseline_git_sha: Git SHA at sprint start ("UNKNOWN" or "NO_BASELINE" = new file)
        final_git_sha: Git SHA at sprint end ("UNKNOWN" = current HEAD)
        test_paths: List of test file paths (may be absolute or relative to repo_root)
        evidence_root: Directory for writing any output artifacts
        repo_root: Repository root path

    Returns:
        BeforeAfterProof with verdict:
        - "NEW_FILE": file didn't exist at baseline (always improvement)
        - "IMPROVEMENT": proof level increased
        - "REGRESSION": proof level decreased
        - "UNCHANGED": proof level same
    """
    _repo = Path(repo_root)
    after_assessments = []
    before_assessments = []
    resolved_paths = []

    for tp in test_paths:
        tp_path = Path(tp)
        if not tp_path.is_absolute():
            tp_path = _repo / tp
        if tp_path.exists():
            resolved_paths.append(str(tp_path))

    # --- AFTER state ---
    for rp in resolved_paths:
        assessment = assess_proof_level(rp)
        after_assessments.append(assessment)

    # --- BEFORE state ---
    can_use_baseline = (
        baseline_git_sha
        and baseline_git_sha not in ("UNKNOWN", "NO_BASELINE", "")
    )

    if can_use_baseline:
        for rp in resolved_paths:
            try:
                # Compute relative path from repo root
                abs_path = Path(rp)
                try:
                    rel_path = abs_path.relative_to(_repo)
                except ValueError:
                    rel_path = abs_path

                content = _get_baseline_content(baseline_git_sha, str(rel_path), str(_repo))
                if content is None:
                    # File didn't exist at baseline
                    baseline_git_sha = "NO_BASELINE"
                    break

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix="_baseline_test.py", delete=False, encoding="utf-8"
                ) as tf:
                    tf.write(content)
                    tmp_path = tf.name

                before_assessment = assess_proof_level(tmp_path)
                before_assessments.append(before_assessment)
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                baseline_git_sha = "NO_BASELINE"
                before_assessments = []
                break

    # --- Compute verdict ---
    if baseline_git_sha in ("NO_BASELINE", "UNKNOWN", "") or not before_assessments:
        verdict = "NEW_FILE"
    else:
        after_level = max((a.get("level", 0) for a in after_assessments), default=0)
        before_level = max((a.get("level", 0) for a in before_assessments), default=0)

        if after_level > before_level:
            verdict = "IMPROVEMENT"
        elif after_level < before_level:
            verdict = "REGRESSION"
        else:
            # Same level — check if weak test count improved
            after_weak = sum(len(a.get("weak_tests", [])) for a in after_assessments)
            before_weak = sum(len(a.get("weak_tests", [])) for a in before_assessments)
            if after_weak < before_weak:
                verdict = "IMPROVEMENT"
            else:
                verdict = "UNCHANGED"

    # Build output
    before_behaviors = []
    for a in before_assessments:
        before_behaviors.extend(t["name"] for t in a.get("strong_tests", []))

    after_behaviors = []
    for a in after_assessments:
        after_behaviors.extend(t["name"] for t in a.get("strong_tests", []))

    improvements = []
    regressions = []
    unchanged_weaknesses = []

    if verdict == "IMPROVEMENT":
        new_strong = set(after_behaviors) - set(before_behaviors)
        improvements = list(new_strong)
    elif verdict == "REGRESSION":
        lost_strong = set(before_behaviors) - set(after_behaviors)
        regressions = list(lost_strong)

    # Weak tests that persist after sprint
    for a in after_assessments:
        for wt in a.get("weak_tests", []):
            unchanged_weaknesses.append(wt["name"])

    return BeforeAfterProof(
        requirement_id=requirement_id,
        baseline_revision=baseline_git_sha,
        final_revision=final_git_sha,
        before_tests=resolved_paths,
        before_behaviors_proven=before_behaviors,
        before_faults_detected=[],
        after_tests=resolved_paths,
        after_behaviors_proven=after_behaviors,
        after_faults_detected=[],
        improvements=improvements,
        unchanged_weaknesses=unchanged_weaknesses,
        regressions=regressions,
        new_findings=[],
        verdict=verdict,
    )
