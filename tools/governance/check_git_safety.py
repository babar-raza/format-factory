#!/usr/bin/env python3
"""Read-only Git safety preflight for agent execution sprints."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
IDENTITY_FILES = [
    "verdict.md",
    "final-state-summary.yaml",
    "final-bundle-validation-proof.txt",
    "evidence-contract-validation-report.md",
    "sprint-summary.md",
]
METADATA_SENTINELS = set(IDENTITY_FILES + [
    "git-status-final.txt",
    "git-log.txt",
    "validation-command-log.txt",
    "bundle-manifest.yaml",
])
FORBIDDEN_COMMAND_PATTERNS = [
    r"\bgit\s+add\s+\.",
    r"\bgit\s+add\s+-A\b",
]
DIRTY_FLAG_RE = re.compile(r"^[a-zS]")


def run_git(args: list[str], repo_root: Path) -> tuple[int, str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, (result.stdout + result.stderr)


def extract_identity(text: str) -> set[str]:
    """Extract likely primary sprint IDs from metadata text."""
    ids: set[str] = set()
    patterns = [
        r"\bsprint_id:\s*['\"]?([A-Za-z0-9_.-]+)",
        r"\bSprint:\s*([A-Za-z0-9_.-]+)",
        r"\bcontract_id:\s*['\"]?([A-Za-z0-9_.-]+)",
        r"\bContract:\s*.*?([A-Za-z0-9_.-]+\.ya?ml)",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = match.group(1).strip().strip("'\"")
            if value.endswith((".yaml", ".yml")):
                value = Path(value).stem
            if value and value.lower() not in {"true", "false", "null"}:
                ids.add(value)
    return ids


def check_metadata_identity(metadata_dir: Path) -> tuple[bool, list[str], list[str]]:
    """Return (ok, identities, messages) for identity-critical metadata files."""
    identities: set[str] = set()
    messages: list[str] = []
    present = []
    for name in IDENTITY_FILES:
        path = metadata_dir / name
        if not path.exists():
            continue
        present.append(name)
        file_ids = extract_identity(path.read_text(encoding="utf-8", errors="replace"))
        identities.update(file_ids)
        if file_ids:
            messages.append(f"{name}: {', '.join(sorted(file_ids))}")
    if not present:
        return False, [], ["No identity-critical metadata files found."]
    if len(identities) > 1:
        return False, sorted(identities), messages
    if len(identities) == 0:
        return False, [], messages + ["Identity files present but no sprint identity found."]
    return True, sorted(identities), messages


def root_bundle_metadata_contaminated(repo_root: Path) -> tuple[bool, list[str]]:
    root_meta = repo_root / "bundle-metadata"
    if not root_meta.exists():
        return False, []
    hits = [p.name for p in root_meta.iterdir() if p.is_file() and p.name in METADATA_SENTINELS]
    return bool(hits), sorted(hits)


def forbidden_commands_in_text(text: str) -> list[str]:
    hits = []
    for pattern in FORBIDDEN_COMMAND_PATTERNS:
        if re.search(pattern, text):
            hits.append(pattern)
    return hits


def scan_command_logs(metadata_dir: Path) -> list[str]:
    hits = []
    for path in metadata_dir.rglob("*command-log*.txt"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in forbidden_commands_in_text(text):
            hits.append(f"{path}: {pattern}")
    return hits


def check_index_flags(ls_files_v: str) -> list[str]:
    hits = []
    for line in ls_files_v.splitlines():
        if DIRTY_FLAG_RE.match(line):
            path = line[2:].strip()
            if not path.startswith((".local/", "bundle-metadata/")):
                hits.append(line)
    return hits


def build_report(args: argparse.Namespace) -> tuple[dict, int]:
    repo_root = Path(args.repo_root).resolve()
    report = {"errors": [], "warnings": [], "info": {}}

    rc, branch = run_git(["branch", "--show-current"], repo_root)
    report["info"]["branch"] = branch.strip() if rc == 0 else ""
    rc, head = run_git(["rev-parse", "HEAD"], repo_root)
    report["info"]["head"] = head.strip() if rc == 0 else ""
    _, status = run_git(["status", "--short"], repo_root)
    dirty_lines = [line for line in status.splitlines() if line.strip()]
    report["info"]["dirty_files"] = dirty_lines

    if args.strict and dirty_lines and not args.classification_file:
        report["errors"].append("Dirty files present but --classification-file was not supplied.")
    if args.classification_file and not Path(args.classification_file).exists():
        report["errors"].append(f"Classification file not found: {args.classification_file}")

    contaminated, sentinels = root_bundle_metadata_contaminated(repo_root)
    if contaminated:
        report["errors"].append(
            "Root bundle-metadata/ contains sprint metadata files: " + ", ".join(sentinels)
        )

    lost_found = repo_root / ".git" / "lost-found"
    if lost_found.exists() and any(lost_found.rglob("*")):
        report["warnings"].append(".git/lost-found contains pointers from prior recovery/investigation.")

    _, stash_list = run_git(["stash", "list"], repo_root)
    if stash_list.strip():
        report["warnings"].append("git stash list is non-empty.")
    report["info"]["stash_list"] = stash_list.strip()

    _, reflog = run_git(["reflog", "--date=iso", "-50"], repo_root)
    if "reset: moving to HEAD" in reflog:
        report["warnings"].append("Recent reflog contains 'reset: moving to HEAD'.")

    _, ls_files_v = run_git(["ls-files", "-v"], repo_root)
    flag_hits = check_index_flags(ls_files_v)
    if flag_hits:
        report["errors"].append("skip-worktree/assume-unchanged flags found: " + "; ".join(flag_hits[:10]))

    if args.metadata_dir:
        metadata_dir = Path(args.metadata_dir)
        if not metadata_dir.exists():
            report["errors"].append(f"Metadata directory not found: {metadata_dir}")
        else:
            command_hits = scan_command_logs(metadata_dir)
            if command_hits:
                report["errors"].append("Forbidden broad staging command found: " + "; ".join(command_hits))
            ok, identities, messages = check_metadata_identity(metadata_dir)
            report["info"]["metadata_identities"] = identities
            report["info"]["metadata_identity_messages"] = messages
            if not ok:
                report["errors"].append("Metadata identity check failed: " + "; ".join(messages))

    exit_code = 1 if report["errors"] else 0
    return report, exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Git safety checker.")
    parser.add_argument("--metadata-dir", default=None)
    parser.add_argument("--classification-file", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json-output", default=None)
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args()

    report, exit_code = build_report(args)
    print("GIT_SAFETY_CHECK")
    print(f"Branch: {report['info'].get('branch', '')}")
    print(f"HEAD: {report['info'].get('head', '')}")
    print(f"Dirty files: {len(report['info'].get('dirty_files', []))}")
    for warning in report["warnings"]:
        print(f"WARN: {warning}")
    for error in report["errors"]:
        print(f"ERROR: {error}")
    print("GIT_SAFETY_CHECK: " + ("PASS" if exit_code == 0 else "FAIL"))

    if args.json_output:
        Path(args.json_output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
