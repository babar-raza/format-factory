"""
scan_residual_bypasses.py — Skill 12

Scan git log (last 20 commits) for src/ file mutations, cross-reference against
skill transcripts to find mutations that have no corresponding skill transcript;
report as UNGOVERNED_MUTATION.

Transcripts are scanned from:
  - reports/**/skill-transcripts/*.json  (primary — sprint-level transcripts)
  - .local/transcripts/*.json            (legacy fallback)

SHA field names checked: git_head, commit_sha, head, commit
Path-based fallback: if no SHA match, checks changed_files/actual_files_changed coverage.

Output: .supervisor/residual-bypass-report.yaml
"""
import argparse
import json
import subprocess
from pathlib import Path
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent


def get_src_mutations(repo: Path, n_commits: int = 20) -> dict[str, list[str]]:
    """Return {commit_sha: [src/ paths changed]} for last n_commits."""
    result = subprocess.run(
        ["git", "log", f"-{n_commits}", "--name-only", "--format=%H"],
        capture_output=True, text=True, cwd=str(repo)
    )
    mutations: dict[str, list[str]] = {}
    current_sha = None
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if len(line) == 40 and all(c in "0123456789abcdef" for c in line):
            current_sha = line
        elif current_sha and line.startswith("src/"):
            mutations.setdefault(current_sha, []).append(line)
    return mutations


def load_governed_commits(repo: Path) -> tuple[set[str], set[str]]:
    """Return (sha_set, path_set) from all skill transcript directories."""
    governed_shas: set[str] = set()
    governed_paths: set[str] = set()

    # Scan all skill-transcripts dirs under reports/ and legacy .local/transcripts/
    search_patterns = [
        repo.glob("reports/**/skill-transcripts/*.json"),
        (repo / ".local" / "transcripts").glob("*.json") if (repo / ".local" / "transcripts").exists() else iter([]),
    ]
    for pattern in search_patterns:
        for f in pattern:
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
                sha = (data.get("git_head") or data.get("commit_sha")
                       or data.get("head") or data.get("commit"))
                if sha:
                    governed_shas.add(sha[:40])
                for field in ("changed_files", "actual_files_changed", "allowed_files"):
                    for p in data.get(field) or []:
                        governed_paths.add(str(p))
            except Exception:
                pass
    return governed_shas, governed_paths


def main(output_path: str | None = None) -> None:
    mutations = get_src_mutations(_REPO)
    governed_shas, governed_paths = load_governed_commits(_REPO)

    entries = []
    ungoverned_count = 0
    for sha, paths in mutations.items():
        sha_match = sha in governed_shas
        # Path-based fallback: all src/ paths in this commit appear in some transcript
        paths_covered = bool(paths) and all(p in governed_paths for p in paths)
        has_transcript = sha_match or paths_covered
        match_type = "sha_match" if sha_match else ("path_covered" if paths_covered else "none")
        verdict = "GOVERNED" if has_transcript else "UNGOVERNED_MUTATION"
        if verdict == "UNGOVERNED_MUTATION":
            ungoverned_count += 1
        entries.append({
            "commit_sha": sha,
            "src_paths_changed": paths,
            "has_skill_transcript": has_transcript,
            "match_type": match_type,
            "verdict": verdict,
        })

    out = {
        "generated_by": "scan_residual_bypasses.py",
        "mission_id": "SKILL-FIRST-001",
        "commits_scanned": len(mutations),
        "ungoverned_mutation_count": ungoverned_count,
        "note": (
            "UNGOVERNED_MUTATION = src/ changed in this commit but no skill transcript found. "
            "This is expected for commits predating the skill-first policy."
        ),
        "entries": entries,
    }
    dest = output_path or str(_REPO / ".supervisor" / "residual-bypass-report.yaml")
    p = Path(dest)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.dump(out, default_flow_style=False, allow_unicode=True), encoding="utf-8")
    print(f"Scanned {len(mutations)} commits: {ungoverned_count} UNGOVERNED_MUTATION -> {dest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan for ungoverned src/ mutations")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    main(args.output)
