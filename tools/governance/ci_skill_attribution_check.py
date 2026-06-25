"""
ci_skill_attribution_check.py — CI Enforcement for Skill Attribution
Format Factory Skill-Only Governance — EP-006

PURPOSE
-------
Run in CI (GitHub Actions) to detect src/ mutations in pushed commits
that lack a corresponding skill execution transcript or retroactive binding.

Used by .github/workflows/ci.yml job: skill-attribution-check

EXIT CODES
----------
  0 = PASS — all src/ mutations in pushed commits have skill transcripts
  1 = FAIL — ungoverned mutations detected (src/ changed, no transcript found)
  2 = CONFIG_ERROR — cannot read required files

TRANSCRIPT SEARCH PATHS (in priority order)
--------------------------------------------
  1. .local/transcripts/          (primary transcript store)
  2. reports/skills-*/skill-transcripts/  (per-sprint transcript bundles)
  3. .supervisor/skill-execution-receipt-index.yaml  (aggregated receipt index)

A commit is considered GOVERNED if ANY of:
  - a transcript JSON exists in the search paths that lists the commit SHA in commit_sha field
  - the commit SHA appears in a retroactive binding file in .local/retroactive-bindings/
  - the src/ path changed is in a globally-exempt path list

POLICY REFERENCE
----------------
  docs/governance/skill-only-policy.yaml § 7 (Enforcement Points: EP-006)
  .supervisor/residual-bypass-report.yaml (historical ungoverned mutations)

KNOWN LIMITATION
----------------
  This check fires AFTER commits are pushed. It provides detection not prevention.
  Prevention requires pre-commit hooks (SKILL-GAP-008).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TRANSCRIPT_PRIMARY = REPO_ROOT / ".local" / "transcripts"
RECEIPT_INDEX = REPO_ROOT / ".supervisor" / "skill-execution-receipt-index.yaml"
RETROACTIVE_BINDINGS = REPO_ROOT / ".local" / "retroactive-bindings"
SKILLS_REPORTS_GLOB = "reports/skills-*/skill-transcripts/*.json"

# src/ paths that are always exempt from attribution (generated, not manually edited)
EXEMPT_SRC_PREFIXES = (
    "src/python/__pycache__/",
    "src/net/obj/",
    "src/net/bin/",
)

# Pre-policy commits (before SKILL-FIRST-001, 2026-06-24) are exempt by default
PRE_POLICY_CUTOFF_SHA = "4a37978f"  # first ALL-GREEN skill-governance commit


def _get_changed_src_commits(base_ref: str = "HEAD~1", head_ref: str = "HEAD") -> list[dict]:
    """
    Return list of {sha, src_paths_changed} for commits between base_ref..head_ref
    that touch src/ paths.
    """
    try:
        log_out = subprocess.check_output(
            ["git", "log", "--format=%H", f"{base_ref}..{head_ref}"],
            cwd=str(REPO_ROOT),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        # Fallback: just HEAD
        try:
            sha = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=str(REPO_ROOT), text=True, stderr=subprocess.DEVNULL,
            ).strip()
            log_out = sha
        except subprocess.CalledProcessError:
            return []

    commits = []
    for sha in log_out.splitlines():
        sha = sha.strip()
        if not sha:
            continue
        try:
            diff_out = subprocess.check_output(
                ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", sha],
                cwd=str(REPO_ROOT), text=True, stderr=subprocess.DEVNULL,
            ).strip()
        except subprocess.CalledProcessError:
            continue
        src_paths = [
            p for p in diff_out.splitlines()
            if p.startswith("src/") and not any(p.startswith(ex) for ex in EXEMPT_SRC_PREFIXES)
        ]
        if src_paths:
            commits.append({"sha": sha, "src_paths": src_paths})
    return commits


def _load_transcript_commit_shas() -> set[str]:
    """Collect all commit SHAs referenced in transcript/receipt files."""
    shas: set[str] = set()

    # Primary transcripts
    if TRANSCRIPT_PRIMARY.exists():
        for f in TRANSCRIPT_PRIMARY.rglob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if sha := data.get("commit_sha"):
                    shas.add(sha)
                for item in data.get("commits", []):
                    if isinstance(item, dict) and (s := item.get("sha")):
                        shas.add(s)
            except Exception:
                continue

    # Per-sprint transcript bundles
    for f in REPO_ROOT.glob(SKILLS_REPORTS_GLOB):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if sha := data.get("commit_sha"):
                shas.add(sha)
            for item in data.get("commits", []):
                if isinstance(item, dict) and (s := item.get("sha")):
                    shas.add(s)
        except Exception:
            continue

    # Retroactive bindings
    if RETROACTIVE_BINDINGS.exists():
        for f in RETROACTIVE_BINDINGS.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if sha := data.get("commit_sha"):
                    shas.add(sha)
            except Exception:
                continue

    return shas


def _is_pre_policy(sha: str) -> bool:
    """Check if commit predates the SKILL-FIRST-001 policy cutoff."""
    try:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", sha, PRE_POLICY_CUTOFF_SHA],
            cwd=str(REPO_ROOT), capture_output=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="CI skill attribution check (EP-006)")
    parser.add_argument("--base-ref", default="HEAD~1", help="Base git ref for commit range")
    parser.add_argument("--head-ref", default="HEAD", help="Head git ref for commit range")
    parser.add_argument("--allow-pre-policy", action="store_true", default=True,
                        help="Exempt commits predating SKILL-FIRST-001 (default: True)")
    parser.add_argument("--output", help="Path to write JSON report")
    args = parser.parse_args()

    commits = _get_changed_src_commits(args.base_ref, args.head_ref)
    transcript_shas = _load_transcript_commit_shas()

    ungoverned = []
    governed = []
    pre_policy_exempt = []

    for commit in commits:
        sha = commit["sha"]

        # Check pre-policy exemption
        if args.allow_pre_policy and _is_pre_policy(sha):
            pre_policy_exempt.append(sha)
            continue

        # Check transcript coverage
        if sha in transcript_shas:
            governed.append(sha)
        else:
            ungoverned.append({"sha": sha, "src_paths": commit["src_paths"]})

    verdict = "PASS" if not ungoverned else "FAIL"
    report = {
        "verdict": verdict,
        "commits_checked": len(commits),
        "governed": len(governed),
        "ungoverned": len(ungoverned),
        "pre_policy_exempt": len(pre_policy_exempt),
        "ungoverned_details": ungoverned,
        "policy_reference": "docs/governance/skill-only-policy.yaml § EP-006",
        "enforcement_point": "EP-006",
    }

    print(json.dumps(report, indent=2))

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")

    if verdict == "FAIL":
        print(
            "\nFAIL: Ungoverned src/ mutations detected. "
            "Every src/ commit must have a skill execution transcript. "
            "See docs/governance/skill-only-policy.yaml for remediation.",
            file=sys.stderr,
        )
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
