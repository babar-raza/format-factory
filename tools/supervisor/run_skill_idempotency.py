"""
run_skill_idempotency.py — Skill 10

For a given Python-backed tool path, run it twice against the same fixture
and produce an idempotency verdict.

SCOPE LIMITATION: Applies ONLY to Python-backed tools in tools/supervisor/
that produce deterministic file outputs. NOT for prompt-backed .md skills.

Output: .supervisor/skill-idempotency-proof.yaml
LOC budget: <90 lines
"""
import argparse
import subprocess
import sys
from pathlib import Path
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent


def run_tool(tool_path: str, args: list[str], output_path: str) -> tuple[int, str]:
    cmd = [sys.executable, tool_path] + args + ["--output", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(_REPO))
    return result.returncode, result.stdout + result.stderr


def read_output(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prove skill idempotency")
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--tool-path", required=True)
    parser.add_argument("--args", nargs="*", default=[])
    parser.add_argument("--output-path", required=True, help="Path where skill writes its output")
    parser.add_argument("--run1-path", required=True, help="Copy run1 output here for comparison")
    parser.add_argument("--run2-path", required=True, help="Copy run2 output here for comparison")
    args = parser.parse_args()

    run1_code, run1_log = run_tool(args.tool_path, args.args, args.run1_path)
    run1_content = read_output(args.run1_path)

    run2_code, run2_log = run_tool(args.tool_path, args.args, args.run2_path)
    run2_content = read_output(args.run2_path)

    identical = run1_content == run2_content
    verdict = "IDEMPOTENT_VERIFIED" if identical and run1_code == 0 and run2_code == 0 \
        else "NON_IDEMPOTENT_REPAIR_REQUIRED"

    out = {
        "generated_by": "run_skill_idempotency.py",
        "mission_id": "SKILL-FIRST-001",
        "skill_id": args.skill_id,
        "tool_path": args.tool_path,
        "scope_limitation": "Python-backed deterministic tools only; not for prompt-backed .md skills",
        "run1_exit_code": run1_code,
        "run2_exit_code": run2_code,
        "outputs_identical": identical,
        "idempotency_verdict": verdict,
        "run1_log": run1_log[:500],
        "run2_log": run2_log[:500],
    }
    dest = str(_REPO / ".supervisor" / "skill-idempotency-proof.yaml")
    p = Path(dest)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.dump(out, default_flow_style=False, allow_unicode=True), encoding="utf-8")
    print(f"Idempotency verdict: {verdict} -> {dest}")
    if verdict == "NON_IDEMPOTENT_REPAIR_REQUIRED":
        sys.exit(1)


if __name__ == "__main__":
    main()
