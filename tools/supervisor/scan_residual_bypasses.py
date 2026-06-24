"""
scan_residual_bypasses.py — Skill 12

Scan git log (last 20 commits) for src/ file mutations, cross-reference against
.local/transcripts/ to find mutations that have no corresponding skill transcript;
report as UNGOVERNED_MUTATION.

Output: .supervisor/residual-bypass-report.yaml
LOC budget: <90 lines
"""
import argparse
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


def load_governed_commits(transcripts_root: Path) -> set[str]:
    """Return set of commit SHAs that have skill execution transcripts."""
    governed = set()
    if not transcripts_root.exists():
        return governed
    for f in transcripts_root.glob("*.json"):
        try:
            import json
            data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            sha = data.get("git_head") or data.get("commit_sha") or data.get("head")
            if sha:
                governed.add(sha[:40])
        except Exception:
            pass
    return governed


def main(output_path: str | None = None) -> None:
    mutations = get_src_mutations(_REPO)
    transcripts_root = _REPO / ".local" / "transcripts"
    governed_commits = load_governed_commits(transcripts_root)

    entries = []
    ungoverned_count = 0
    for sha, paths in mutations.items():
        has_transcript = sha in governed_commits
        verdict = "GOVERNED" if has_transcript else "UNGOVERNED_MUTATION"
        if verdict == "UNGOVERNED_MUTATION":
            ungoverned_count += 1
        entries.append({
            "commit_sha": sha,
            "src_paths_changed": paths,
            "has_skill_transcript": has_transcript,
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
