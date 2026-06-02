"""
supervisor_loop.py — Format Factory Local Supervisor Control Plane

CANONICAL commands (declaration-driven evidence directory):
  validate-declaration  — validate evidence-declaration.yaml
  inspect-declared      — inspect declared evidence directory
  grade-declared        — grade declared work items
  plan-next             — generate next worker prompt from review
  autonomous-cycle      — full declaration-driven cycle
  generate-manifest     — generate evidence-manifest.yaml from declaration
  validate-manifest     — validate existing evidence-manifest.yaml
  create-sample-declaration — create template declaration
  list-unreviewed-declarations — find unreviewed declarations

LEGACY commands (ZIP/watcher-based, convenience only):
  discover          — find latest evidence bundle (legacy)
  review            — validate bundle and extract facts (legacy)
  next              — generate next-sprint artifacts (legacy)
  run-on-latest     — full legacy pipeline (legacy)
  export-taskmaster — export next-sprint-taskmaster.json (legacy)
  export-ruflo      — export next-ruflo-lanes.json (legacy)

Exit codes:
  0 — success
  1 — no bundle/declaration found
  2 — validation failed
  3 — critical rework/contradiction
  9 — unexpected error
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
STATE_DIR = REPO_ROOT / ".supervisor" / "state"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports" / "supervisor"


def run_script(script_name: str, extra_args: list[str], repo_root: Path) -> subprocess.CompletedProcess:
    """Run a supervisor sub-script as subprocess."""
    script_path = SCRIPT_DIR / script_name
    cmd = [sys.executable, str(script_path)] + extra_args
    result = subprocess.run(
        cmd,
        capture_output=False,  # Let output stream to terminal
        text=True,
        cwd=str(repo_root),
        timeout=120,
    )
    return result


def run_script_capture(script_name: str, extra_args: list[str], repo_root: Path) -> tuple[int, str, str]:
    """Run a supervisor sub-script capturing output."""
    script_path = SCRIPT_DIR / script_name
    cmd = [sys.executable, str(script_path)] + extra_args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        timeout=120,
    )
    return result.returncode, result.stdout, result.stderr


def load_current_run() -> dict:
    """Load .supervisor/state/current-run.json if it exists."""
    state_file = STATE_DIR / "current-run.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_run_state(state: dict) -> None:
    """Save run state to .supervisor/state/current-run.json."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_file = STATE_DIR / "current-run.json"
    existing = load_current_run()
    existing.update(state)
    state_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def cmd_discover(args) -> int:
    """Discover latest evidence bundle."""
    print("=== SUPERVISOR: DISCOVER ===")
    extra = ["--repo-root", str(REPO_ROOT), "--output-dir", str(args.output_dir)]
    if args.bundle:
        extra += ["--path", str(args.bundle)]

    rc, stdout, stderr = run_script_capture(
        "discover_latest_evidence.py", extra, REPO_ROOT
    )

    print(stdout, end="")
    if stderr:
        print(stderr, end="", file=sys.stderr)

    # Read and persist discovery result
    state = load_current_run()
    if "last_discovery" in state:
        disc = state["last_discovery"]
        bundle_path = disc.get("bundle_path", "")
        sprint_id = disc.get("sprint_id", "unknown")
        save_run_state({
            "discover_exit_code": rc,
            "bundle_path": bundle_path,
            "sprint_id": sprint_id,
            "discover_timestamp": datetime.now().isoformat(),
        })
        if rc == 0:
            print("  -> Bundle path saved to .supervisor/state/current-run.json")

    return rc


def cmd_review(args) -> int:
    """Validate bundle and extract facts."""
    print("=== SUPERVISOR: REVIEW ===")

    bundle = args.bundle
    if not bundle:
        # Try to get from state
        state = load_current_run()
        bundle = state.get("bundle_path")
        if not bundle:
            print("ERROR: No bundle path. Run 'discover' first or provide --bundle.", file=sys.stderr)
            return 1

    extra = [
        "--bundle", str(bundle),
        "--output-dir", str(args.output_dir),
        "--repo-root", str(REPO_ROOT),
    ]
    rc = run_script("validate_evidence_for_supervisor.py", extra, REPO_ROOT).returncode

    if rc != 0:
        print(f"ERROR: Evidence validation failed (exit {rc})")
        return rc

    # Run contradiction detection
    print()
    print("=== SUPERVISOR: CONTRADICTION DETECTION ===")
    review_json = args.output_dir / "evidence-review.json"
    if review_json.exists():
        extra2 = [
            "--review", str(review_json),
            "--output-dir", str(args.output_dir),
            "--repo-root", str(REPO_ROOT),
        ]
        rc2 = run_script("compare_goal_to_evidence.py", extra2, REPO_ROOT).returncode

        # Check if critical contradictions were found
        contradictions_json = args.output_dir / "contradictions.json"
        if contradictions_json.exists():
            try:
                contra = json.loads(contradictions_json.read_text(encoding="utf-8"))
                save_run_state({
                    "review_exit_code": rc,
                    "contradiction_exit_code": rc2,
                    "critical_contradictions": contra.get("critical_count", 0),
                    "autonomous_continue": contra.get("autonomous_continue", True),
                    "review_timestamp": datetime.now().isoformat(),
                })
                if contra.get("critical_count", 0) > 0:
                    print(f"\n⚠ CRITICAL CONTRADICTIONS: {contra['critical_count']} — autonomous loop paused")
                    return 3
            except Exception:
                pass

    return rc


def cmd_next(args) -> int:
    """Generate next-sprint artifacts."""
    print("=== SUPERVISOR: NEXT SPRINT GENERATION ===")
    extra = [
        "--review", str(args.output_dir / "evidence-review.json"),
        "--contradictions", str(args.output_dir / "contradictions.json"),
        "--output-dir", str(args.output_dir),
        "--repo-root", str(REPO_ROOT),
    ]
    rc = run_script("generate_supervisor_packet.py", extra, REPO_ROOT).returncode

    save_run_state({
        "next_exit_code": rc,
        "next_timestamp": datetime.now().isoformat(),
    })
    return rc


def cmd_memory_sync(args) -> int:
    """Sync memory."""
    print("=== SUPERVISOR: MEMORY SYNC ===")
    extra = [
        "--review", str(args.output_dir / "evidence-review.json"),
        "--output-dir", str(args.output_dir),
        "--repo-root", str(REPO_ROOT),
    ]
    rc = run_script("sync_local_memory.py", extra, REPO_ROOT).returncode
    save_run_state({
        "memory_sync_exit_code": rc,
        "memory_sync_timestamp": datetime.now().isoformat(),
    })
    return rc


def cmd_run_on_latest(args) -> int:
    """Full pipeline: discover → review → next → export → memory-sync."""
    print("WARNING: run-on-latest is legacy. Use 'autonomous-cycle --declaration <path>' instead.",
          file=sys.stderr)
    print("=" * 60)
    print("SUPERVISOR LOOP: RUN-ON-LATEST (LEGACY)")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    save_run_state({"run_start": datetime.now().isoformat(), "sprint_id": "in-progress"})

    # Step 1: Discover
    rc = cmd_discover(args)
    if rc == 1:
        print("\nSUPERVISOR RESULT: NO_BUNDLE_FOUND")
        print("  Run with a real evidence bundle in .local/evidence/")
        save_run_state({"final_exit_code": 1, "run_end": datetime.now().isoformat()})
        return 1
    if rc == 2:
        print("\nSUPERVISOR RESULT: MALFORMED_BUNDLE")
        save_run_state({"final_exit_code": 2, "run_end": datetime.now().isoformat()})
        return 2

    # Update args.bundle from state if not set
    if not args.bundle:
        state = load_current_run()
        bundle_path = state.get("bundle_path")
        if bundle_path:
            args.bundle = Path(bundle_path)

    # Step 2: Review + contradiction detection
    print()
    rc = cmd_review(args)
    if rc == 3:
        print("\nSUPERVISOR RESULT: CRITICAL_CONTRADICTIONS — human review required")
        # Still generate next-sprint (focused on repair)
        cmd_next(args)
        cmd_memory_sync(args)
        save_run_state({"final_exit_code": 3, "run_end": datetime.now().isoformat()})
        return 3
    # D86-SUP-03 fix: Track validation failure — rc=2 means bundle validation failed
    review_rc = rc
    if rc == 2:
        print("\nWARNING: Evidence validation failed (rc=2) — continuing to generate next-sprint for repair guidance")

    # Step 3: Generate next-sprint artifacts
    print()
    rc_next = cmd_next(args)

    # Step 4: Memory sync
    print()
    cmd_memory_sync(args)

    # D86-SUP-04 fix: Final exit code incorporates validation state
    # If validation failed (rc=2), propagate that as the final exit code
    if review_rc == 2:
        final_rc = 2
    elif rc_next != 0:
        final_rc = rc_next
    else:
        final_rc = 0
    save_run_state({
        "final_exit_code": final_rc,
        "run_end": datetime.now().isoformat(),
    })

    print()
    print("=" * 60)
    print(f"SUPERVISOR LOOP: COMPLETE (exit {final_rc})")
    print(f"Ended: {datetime.now().isoformat()}")
    print(f"Outputs: {args.output_dir}")
    print("=" * 60)

    return final_rc


def cmd_export_taskmaster(args) -> int:
    """Export next-sprint-taskmaster.json."""
    tm_path = args.output_dir / "next-sprint-taskmaster.json"
    if tm_path.exists():
        print(f"EXPORT_TASKMASTER: {tm_path}")
        print(f"  Size: {tm_path.stat().st_size} bytes")
        return 0
    print("ERROR: next-sprint-taskmaster.json not found. Run 'run-on-latest' first.", file=sys.stderr)
    return 1


def cmd_export_ruflo(args) -> int:
    """Export next-ruflo-lanes.json."""
    ruflo_path = args.output_dir / "next-ruflo-lanes.json"
    if ruflo_path.exists():
        print(f"EXPORT_RUFLO: {ruflo_path}")
        print(f"  Size: {ruflo_path.stat().st_size} bytes")
        return 0
    print("ERROR: next-ruflo-lanes.json not found. Run 'run-on-latest' first.", file=sys.stderr)
    return 1


def cmd_validate_declaration(args) -> int:
    """Validate an evidence-declaration.yaml (canonical command)."""
    print("=== SUPERVISOR: VALIDATE-DECLARATION ===")
    extra = ["--declaration", str(args.declaration), "--repo-root", str(REPO_ROOT)]
    if args.json:
        extra.append("--json")
    return run_script("evidence_declaration.py", extra, REPO_ROOT).returncode


def cmd_inspect_declared(args) -> int:
    """Inspect declared evidence directory (canonical command)."""
    print("=== SUPERVISOR: INSPECT-DECLARED ===")
    output = args.output_dir / "inspection.json"
    extra = ["--declaration", str(args.declaration), "--repo-root", str(REPO_ROOT), "--output", str(output)]
    return run_script("inspect_declared_evidence.py", extra, REPO_ROOT).returncode


def cmd_grade_declared(args) -> int:
    """Grade declared work items (canonical command)."""
    print("=== SUPERVISOR: GRADE-DECLARED ===")
    inspection_path = args.output_dir / "inspection.json"
    if not inspection_path.exists():
        print("ERROR: Run inspect-declared first.", file=sys.stderr)
        return 1
    extra = [
        "--inspection", str(inspection_path),
        "--declaration", str(args.declaration),
        "--output-dir", str(args.output_dir),
    ]
    return run_script("grade_declared_work.py", extra, REPO_ROOT).returncode


def cmd_plan_next(args) -> int:
    """Generate next worker prompt from review (canonical command)."""
    print("=== SUPERVISOR: PLAN-NEXT ===")
    review_path = args.review if hasattr(args, "review") and args.review else args.output_dir / "supervisor-review.json"
    if not review_path.exists():
        print("ERROR: Run grade-declared first (need supervisor-review.json).", file=sys.stderr)
        return 1
    extra = ["--review", str(review_path), "--output-dir", str(args.output_dir)]
    return run_script("generate_next_worker_prompt.py", extra, REPO_ROOT).returncode


def cmd_autonomous_cycle(args) -> int:
    """Full declaration-driven autonomous supervisor cycle (canonical command).

    After the cycle completes, calls generate_supervisor_packet.py to produce
    session-resume.md, approval-gates.md, and next-sprint.md from the bridged
    evidence-review.json + contradictions.json.

    D92-01 fix: This command is DECLARATION-MODE ONLY. It does NOT call
    validate_evidence_for_supervisor.py (legacy bundle-validator). The legacy
    bundle-validator validated declaration-review-package.zip as a bundle and
    overwrote the correctly-bridged evidence-review.json. This is prevented here
    by explicitly calling autonomous_cycle.py then generate_supervisor_packet.py —
    never cmd_review() which calls the legacy bundle-validator.

    Also: rebuild context-pack before generating the packet, so enrichment in
    generate_supervisor_packet.py has fresh data.
    """
    print("=== SUPERVISOR: AUTONOMOUS-CYCLE ===")
    extra = ["--declaration", str(args.declaration), "--repo-root", str(REPO_ROOT)]
    rc = run_script("autonomous_cycle.py", extra, REPO_ROOT).returncode

    # D92-01 fix: Rebuild context-pack BEFORE generating packet so enrichment is current
    print("\n=== SUPERVISOR: REBUILDING CONTEXT-PACK ===")
    cp_script = SCRIPT_DIR / "build_context_pack.py"
    if cp_script.exists():
        cp_extra = ["--repo-root", str(REPO_ROOT), "--output-dir", str(args.output_dir)]
        cp_rc = run_script("build_context_pack.py", cp_extra, REPO_ROOT).returncode
        if cp_rc != 0:
            print(f"  WARNING: Context-pack rebuild returned {cp_rc}", file=sys.stderr)
    else:
        print("  INFO: build_context_pack.py not found — skipping context-pack rebuild")

    # Bridge: generate session-resume/approval-gates/next-sprint from bridged JSON
    # NOTE: autonomous-cycle writes evidence-review.json via bridge_to_legacy_format
    # inside autonomous_cycle.py. Do NOT call cmd_review() here — it would run the
    # legacy bundle-validator and overwrite evidence-review.json. (D92-01 fix)
    if rc in (0, 3):
        print("\n=== SUPERVISOR: GENERATING SESSION-RESUME + APPROVAL-GATES + NEXT-SPRINT ===")
        next_rc = cmd_next(args)
        if next_rc != 0:
            print(f"  WARNING: Packet generation returned {next_rc}", file=sys.stderr)

    return rc


def cmd_create_sample_declaration(args) -> int:
    """Create a sample evidence-declaration.yaml template."""
    print("=== SUPERVISOR: CREATE-SAMPLE-DECLARATION ===")
    out_path = args.out if hasattr(args, "out") and args.out else Path(".local/evidences/sample/evidence-declaration.yaml")
    extra = ["--create-sample", str(out_path)]
    return run_script("evidence_declaration.py", extra, REPO_ROOT).returncode


def cmd_generate_manifest(args) -> int:
    """Generate evidence-manifest.yaml from a declaration (canonical command)."""
    print("=== SUPERVISOR: GENERATE-MANIFEST ===")
    extra = ["generate", "--declaration", str(args.declaration)]
    if hasattr(args, "out") and args.out:
        extra += ["--out", str(args.out)]
    extra += ["--repo-root", str(REPO_ROOT)]
    return run_script("evidence_manifest.py", extra, REPO_ROOT).returncode


def cmd_validate_manifest(args) -> int:
    """Validate an existing evidence-manifest.yaml (canonical command)."""
    print("=== SUPERVISOR: VALIDATE-MANIFEST ===")
    manifest_path = args.declaration.parent / "evidence-manifest.yaml" if args.declaration else args.out
    if not manifest_path or not manifest_path.exists():
        print("ERROR: Provide --declaration (manifest inferred) or --out pointing to manifest.", file=sys.stderr)
        return 1
    extra = ["validate", "--manifest", str(manifest_path), "--repo-root", str(REPO_ROOT)]
    return run_script("evidence_manifest.py", extra, REPO_ROOT).returncode


def cmd_list_unreviewed(args) -> int:
    """List evidence declarations that have not been reviewed yet."""
    print("=== SUPERVISOR: LIST-UNREVIEWED-DECLARATIONS ===")
    evidences_dir = REPO_ROOT / ".local" / "evidences"
    if not evidences_dir.is_dir():
        print("No .local/evidences/ directory found.")
        return 0

    reviewed = set()
    reviews_dir = REPO_ROOT / ".local" / "supervisor" / "reviews"
    if reviews_dir.is_dir():
        for rd in reviews_dir.iterdir():
            if rd.is_dir():
                reviewed.add(rd.name)

    count = 0
    for d in sorted(evidences_dir.iterdir()):
        if d.is_dir():
            decl = d / "evidence-declaration.yaml"
            if decl.exists():
                status = "REVIEWED" if d.name in reviewed else "UNREVIEWED"
                if status == "UNREVIEWED":
                    count += 1
                print(f"  [{status}] {decl}")

    print(f"\nTotal unreviewed: {count}")
    return 0


CANONICAL_COMMANDS = [
    "validate-declaration", "inspect-declared", "grade-declared",
    "plan-next", "autonomous-cycle",
    "generate-manifest", "validate-manifest",
    "create-sample-declaration", "list-unreviewed-declarations",
]

LEGACY_COMMANDS = [
    "discover", "review", "next", "run-on-latest",
    "export-taskmaster", "export-ruflo",
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Format Factory Local Supervisor Control Plane"
    )
    parser.add_argument(
        "command",
        choices=CANONICAL_COMMANDS + LEGACY_COMMANDS,
        help="Sub-command to run",
    )
    parser.add_argument("--bundle", type=Path, help="Evidence bundle path (legacy)")
    parser.add_argument("--declaration", type=Path, help="Evidence declaration path (canonical)")
    parser.add_argument("--review", type=Path, help="Review JSON path for plan-next")
    parser.add_argument("--out", type=Path, help="Output path for create-sample-declaration")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for supervisor artifacts",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root (default: auto-detected)",
    )
    parser.add_argument("--json", action="store_true", help="JSON output mode")

    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    command_map = {
        # Canonical declaration-driven commands
        "validate-declaration": cmd_validate_declaration,
        "inspect-declared": cmd_inspect_declared,
        "grade-declared": cmd_grade_declared,
        "plan-next": cmd_plan_next,
        "autonomous-cycle": cmd_autonomous_cycle,
        "generate-manifest": cmd_generate_manifest,
        "validate-manifest": cmd_validate_manifest,
        "create-sample-declaration": cmd_create_sample_declaration,
        "list-unreviewed-declarations": cmd_list_unreviewed,
        # Legacy ZIP/watcher commands
        "discover": cmd_discover,
        "review": cmd_review,
        "next": cmd_next,
        "run-on-latest": cmd_run_on_latest,
        "export-taskmaster": cmd_export_taskmaster,
        "export-ruflo": cmd_export_ruflo,
    }

    # Warn about declaration requirement for canonical commands
    if args.command in ("validate-declaration", "inspect-declared", "grade-declared", "autonomous-cycle", "generate-manifest"):
        if not args.declaration:
            print(f"ERROR: --declaration is required for {args.command}", file=sys.stderr)
            return 1

    try:
        return command_map[args.command](args)
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        return 9
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 9


if __name__ == "__main__":
    sys.exit(main())
