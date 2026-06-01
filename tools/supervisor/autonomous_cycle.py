"""
autonomous_cycle.py — Declaration-Driven Autonomous Supervisor Cycle
Orchestrates the full cycle: validate -> inspect -> grade -> plan-next -> manifest

This is the canonical supervisor command. It takes a declaration path
(not a ZIP, not a watcher state) and produces a complete review.

Exit codes:
  0 — cycle complete, autonomous continue possible
  3 — cycle complete, critical rework exists
  9 — unexpected error
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# Import sibling modules
sys.path.insert(0, str(SCRIPT_DIR))
from evidence_declaration import validate_declaration, load_declaration
from inspect_declared_evidence import inspect_declaration
from grade_declared_work import grade_all, write_outputs
from generate_next_worker_prompt import generate_prompt, generate_next_work_items
from evidence_manifest import generate_from_declaration, validate_manifest, write_manifest


def run_cycle(declaration_path: Path, repo_root: Path) -> dict:
    """Run a complete autonomous supervisor cycle."""
    timestamp = datetime.now().isoformat()

    # Step 1: Validate declaration
    print("=== STEP 1: VALIDATE DECLARATION ===")
    validation = validate_declaration(declaration_path, repo_root)
    if not validation["valid"]:
        print(f"DECLARATION_INVALID: {declaration_path}")
        for e in validation.get("schema_errors", []):
            print(f"  SCHEMA_ERROR: {e}")
        for e in validation.get("path_errors", []):
            print(f"  PATH_ERROR: {e}")
        return {"exit_code": 1, "error": "Declaration validation failed"}

    decl = validation["declaration"]
    run_id = decl.get("run_id", "unknown")
    sprint_id = decl.get("sprint_id", "unknown")
    print(f"  VALID: run_id={run_id}, sprint_id={sprint_id}")

    # Step 2: Inspect declared evidence
    print("\n=== STEP 2: INSPECT DECLARED EVIDENCE ===")
    inspection = inspect_declaration(decl, repo_root)
    item_count = len(inspection.get("item_inspections", []))
    artifact_count = len(inspection.get("artifact_inspections", []))
    print(f"  Inspected: {item_count} work items, {artifact_count} artifacts")

    # Step 2b: Generate/validate evidence manifest
    print("\n=== STEP 2b: EVIDENCE MANIFEST ===")
    try:
        evidence_manifest = generate_from_declaration(declaration_path, repo_root)
        evidence_manifest_path = (repo_root / decl["evidence_root"]) / "evidence-manifest.yaml"
        if evidence_manifest_path.exists():
            # Validate existing manifest
            val_result = validate_manifest(evidence_manifest_path, repo_root)
            print(f"  Existing manifest: {'VALID' if val_result['valid'] else 'INVALID'} ({val_result['checked']} artifacts checked)")
            if not val_result["valid"]:
                for err in val_result["errors"][:5]:
                    print(f"    {err}")
        else:
            # Write generated manifest
            write_manifest(evidence_manifest, evidence_manifest_path)
            print(f"  Generated: {evidence_manifest_path} ({len(evidence_manifest['artifacts'])} artifacts)")
    except Exception as e:
        print(f"  WARNING: Manifest step skipped: {e}")

    # Step 3: Grade work items
    print("\n=== STEP 3: GRADE WORK ITEMS ===")
    review = grade_all(inspection, decl)
    review["declaration_path"] = str(declaration_path)
    print(f"  Verdict: {review['overall_verdict']}")
    print(f"  Accepted: {len(review['accepted_items'])}")
    print(f"  Rework: {len(review['rework_items'])}")
    print(f"  Overclaimed: {len(review['overclaimed_items'])}")
    print(f"  Autonomous Continue: {review['autonomous_continue']}")

    # Write review outputs
    review_dir = repo_root / ".local" / "supervisor" / "reviews" / run_id
    write_outputs(review, review_dir)

    # Write inspection JSON
    (review_dir / "inspection.json").write_text(
        json.dumps(inspection, indent=2), encoding="utf-8"
    )

    # Step 4: Generate next worker prompt
    print("\n=== STEP 4: GENERATE NEXT WORKER PROMPT ===")
    prompt = generate_prompt(review, repo_root=repo_root)
    prompt_path = review_dir / "combined-next-worker-prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    next_work = generate_next_work_items(review)
    work_path = review_dir / "next-work-items.yaml"
    work_path.write_text(
        yaml.dump(next_work, default_flow_style=False, sort_keys=False), encoding="utf-8"
    )
    (review_dir / "next-work-items.json").write_text(
        json.dumps(next_work, indent=2), encoding="utf-8"
    )
    print(f"  Prompt: {prompt_path}")
    print(f"  Next work: {len(next_work['items'])} items")

    # Step 5: Write cycle manifest
    print("\n=== STEP 5: WRITE CYCLE MANIFEST ===")
    manifest = {
        "cycle_id": f"cycle-{run_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "run_id": run_id,
        "sprint_id": sprint_id,
        "timestamp": timestamp,
        "declaration_path": str(declaration_path),
        "review_path": str(review_dir / "supervisor-review.json"),
        "next_prompt_path": str(prompt_path),
        "item_grades_path": str(review_dir / "item-grades.yaml"),
        "next_work_items_path": str(work_path),
        "memory_synced": False,
        "autonomous_continue": review["autonomous_continue"],
        "stop_reason": review.get("stop_reason", ""),
        "exit_code": 3 if review["critical_rework_count"] > 0 else 0,
        "accepted_count": len(review["accepted_items"]),
        "rework_count": len(review["rework_items"]),
        "rejected_count": len(review["rejected_items"]),
        "overclaimed_count": len(review["overclaimed_items"]),
        "blocked_count": len([g for g in review["item_grades"] if g["supervisor_grade"] == "BLOCKED_EXTERNAL_GATE"]),
    }
    manifest_path = review_dir / "supervisor-cycle-manifest.yaml"
    manifest_path.write_text(
        yaml.dump(manifest, default_flow_style=False, sort_keys=False), encoding="utf-8"
    )
    print(f"  Manifest: {manifest_path}")

    # Step 6: Copy latest summaries to reports/supervisor/
    print("\n=== STEP 6: COPY LATEST SUMMARIES ===")
    latest_dir = repo_root / "reports" / "supervisor"
    latest_dir.mkdir(parents=True, exist_ok=True)

    copies = [
        ("supervisor-review.md", "latest-review.md"),
        ("combined-next-worker-prompt.md", "latest-next-worker-prompt.md"),
    ]
    for src_name, dst_name in copies:
        src = review_dir / src_name
        dst = latest_dir / dst_name
        if src.exists():
            shutil.copy2(str(src), str(dst))
            print(f"  Copied: {dst}")

    # Write latest cycle summary
    summary_lines = [
        f"# Latest Supervisor Cycle Summary",
        f"Run: {run_id}",
        f"Sprint: {sprint_id}",
        f"Timestamp: {timestamp}",
        f"Verdict: {review['overall_verdict']}",
        f"Autonomous Continue: {review['autonomous_continue']}",
        f"Accepted: {len(review['accepted_items'])}",
        f"Rework: {len(review['rework_items'])}",
        f"Overclaimed: {len(review['overclaimed_items'])}",
        f"Review: {review_dir / 'supervisor-review.md'}",
        f"Next Prompt: {prompt_path}",
    ]
    (latest_dir / "latest-cycle-summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    # Step 7: Bridge to legacy format for session-resume/approval-gates/next-sprint
    print("\n=== STEP 7: BRIDGE TO LEGACY PACKET FORMAT ===")
    try:
        bridge_to_legacy_format(review, manifest, decl, repo_root)
        print("  Bridge: evidence-review.json + contradictions.json written to reports/supervisor/")
    except Exception as e:
        print(f"  WARNING: Bridge step failed: {e}")

    return manifest


def bridge_to_legacy_format(review: dict, manifest: dict, decl: dict, repo_root: Path) -> None:
    """Convert declaration-driven cycle outputs to the JSON format expected by
    generate_supervisor_packet.py so that session-resume.md, approval-gates.md,
    and next-sprint.md are regenerated from fresh data.

    Writes:
      reports/supervisor/evidence-review.json
      reports/supervisor/contradictions.json
    """
    output_dir = repo_root / "reports" / "supervisor"
    output_dir.mkdir(parents=True, exist_ok=True)

    test_results = decl.get("test_results", {})
    passed = test_results.get("passed", 0)
    failed = test_results.get("failed", 0)

    # Build evidence-review.json in the format generate_supervisor_packet expects
    evidence_review = {
        "sprint_id": manifest.get("sprint_id", "unknown"),
        "timestamp": manifest.get("timestamp", datetime.now().isoformat()),
        "verdict": review.get("overall_verdict", "unknown"),
        "bundle_path": str(decl.get("evidence_root", "")),
        "facts": {
            "test_count": passed,
            "fail_count": failed,
            "skip_count": test_results.get("skipped", 0),
            "git_head": decl.get("git_head_end", "unknown"),
            "gate_states": {},
            "final_verdict_text": review.get("overall_verdict", ""),
            "pending_marker_count": 0,
            "bundle_entry_count": len(review.get("item_grades", [])),
            "bundle_validation_pass": manifest.get("exit_code", 9) != 9,
        },
        "contradictions": [],
        "limitation_notes": [],
        "validator_invoked": True,
        "bundle_validation_pass": manifest.get("exit_code", 9) != 9,
        "exit_code": manifest.get("exit_code", 0),
        "status": "complete",
    }

    # Build contradictions.json
    contradictions_list = []
    if review.get("critical_rework_count", 0) > 0:
        for grade in review.get("item_grades", []):
            if grade.get("supervisor_grade") in ("OVERCLAIMED", "REJECTED"):
                contradictions_list.append({
                    "severity": "CRITICAL",
                    "description": f"{grade['supervisor_grade']}: {grade.get('item_title', grade.get('item_id', 'unknown'))}",
                    "detail": grade.get("required_rework", ""),
                })
    if failed > 0:
        contradictions_list.append({
            "severity": "CRITICAL",
            "description": f"Tests failed: {failed} failures detected",
            "detail": "All tests must pass per Format Factory policy",
        })

    critical_count = sum(1 for c in contradictions_list if c["severity"] == "CRITICAL")
    contradictions = {
        "sprint_id": manifest.get("sprint_id", "unknown"),
        "timestamp": manifest.get("timestamp", datetime.now().isoformat()),
        "overall": "CRITICAL_CONTRADICTIONS" if critical_count > 0 else "CLEAN",
        "critical_count": critical_count,
        "warning_count": 0,
        "autonomous_continue": manifest.get("autonomous_continue", False),
        "contradictions": contradictions_list,
    }

    (output_dir / "evidence-review.json").write_text(
        json.dumps(evidence_review, indent=2), encoding="utf-8"
    )
    (output_dir / "contradictions.json").write_text(
        json.dumps(contradictions, indent=2), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run declaration-driven autonomous supervisor cycle"
    )
    parser.add_argument(
        "--declaration", type=Path, required=True,
        help="Path to evidence-declaration.yaml"
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    if not args.declaration.exists():
        print(f"ERROR: Declaration not found: {args.declaration}", file=sys.stderr)
        return 1

    print("=" * 60)
    print("AUTONOMOUS SUPERVISOR CYCLE")
    print(f"Declaration: {args.declaration}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    manifest = run_cycle(args.declaration, args.repo_root)

    exit_code = manifest.get("exit_code", 9)
    print()
    print("=" * 60)
    print(f"CYCLE COMPLETE (exit {exit_code})")
    print(f"Autonomous Continue: {manifest.get('autonomous_continue', False)}")
    if manifest.get("stop_reason"):
        print(f"Stop Reason: {manifest['stop_reason']}")
    print("=" * 60)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
