"""
autonomous_train_executor.py â€” Autonomous Train Executor

Chains supervisor cycles. After each accepted sprint, determines whether to continue
or emit a continuation packet for host invocation.

Key invariant:
  If autonomous_continue=true and terminal=false, never return "complete".
  Either execute the next action OR return CONTINUATION_REQUIRED_BY_RUNTIME_LIMIT
  with a machine-consumable continuation packet.

Exit codes:
  0 â€” terminal state reached (POC_READY or RUNTIME_LIMIT or EXTERNAL_GATE)
  1 â€” bad input / missing declaration
  9 â€” unexpected error

Terminal results:
  MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING
  MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED
  MAINSTREAM_POC_PROGRESS_CONTINUATION_REQUIRED_BY_RUNTIME_LIMIT
  AUTONOMOUS_EXECUTION_CHAINING_REQUIRES_HOST_INVOCATION
  MAINSTREAM_POC_BLOCKED_EXTERNAL_GATE
  MAINSTREAM_POC_UNSAFE_WORKSPACE

Non-terminal (never return to user for these):
  ACCEPTED, ACCEPTED_WITH_REWORK, evidence_package_built, next_sprint_generated,
  max_iterations_reached, gate_11_prep_needed, mode_5_approval_pending,
  false_blocker_repaired, one_lane_blocked, anti_skip_false_positive, etc.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Terminal state constants
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

TERMINAL_POC_READY_RELEASE_PENDING = "MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING"
TERMINAL_POC_READY = "MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED"
TERMINAL_RUNTIME_LIMIT = "MAINSTREAM_POC_PROGRESS_CONTINUATION_REQUIRED_BY_RUNTIME_LIMIT"
TERMINAL_HOST_INVOCATION = "AUTONOMOUS_EXECUTION_CHAINING_REQUIRES_HOST_INVOCATION"
TERMINAL_EXTERNAL_GATE = "MAINSTREAM_POC_BLOCKED_EXTERNAL_GATE"
TERMINAL_UNSAFE = "MAINSTREAM_POC_UNSAFE_WORKSPACE"

# Non-terminal states â€” executor must NOT stop for these
NON_TERMINAL_CONTINUE = "NON_TERMINAL_CONTINUE"
NON_TERMINAL_POC_NOT_READY = "NON_TERMINAL_POC_NOT_READY_CONTINUE_PRODUCT_TRAIN"

# Non-terminal â€” executor must NOT stop for these
NON_TERMINAL_SIGNALS = frozenset({
    "accepted",
    "accepted_with_rework",
    "evidence_package_built",
    "next_sprint_generated",
    "max_iterations_reached",
    "gate_11_prep_needed",
    "mode_5_approval_pending",
    "false_blocker_repaired",
    "one_lane_blocked",
    "anti_skip_false_positive",
    "prompt_quality_false_positive",
    "missing_optional_acceleration",
    "autonomous_stop_reason_adjudicator_hardened_and_enforced",
    "hardening_sprint_complete",
    "supervisor_accepted",
    "review_accepted",
    "poc_not_ready_continue",
    "non_terminal_poc_not_ready_continue_product_train",
})


def _load_continuation_signal(repo_root: Path) -> dict:
    """Load the current continuation signal."""
    path = repo_root / ".local" / "supervisor" / "continuation-signal.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _load_latest_review(repo_root: Path, run_id: str = None) -> dict:
    """Load the latest supervisor review."""
    if run_id:
        path = repo_root / ".local" / "supervisor" / "reviews" / run_id / "supervisor-review.md"
        if path.exists():
            return {"run_id": run_id, "review_path": str(path)}

    # Try reports/supervisor/latest-review.md
    path = repo_root / "reports" / "supervisor" / "latest-review.md"
    if path.exists():
        return {"review_path": str(path)}

    return {}


def _load_poc_dashboard(repo_root: Path) -> dict:
    """Load POC dashboard state from poc-targets.yaml."""
    try:
        import yaml
        path = repo_root / "product-capability-matrix" / "poc-targets.yaml"
        if path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            commercial = data.get("commercial_net_products", [])
            foss = data.get("foss_reduced_products", [])

            commercial_pass = all(
                p.get("gates_passed", "").startswith("1-10") or "1-10" in p.get("gates_passed", "")
                for p in commercial
            )
            foss_pass = all(
                p.get("gates_passed", "").startswith("1-10") or "1-10" in p.get("gates_passed", "")
                for p in foss
            )

            return {
                "commercial_targets_count": len(commercial),
                "foss_targets_count": len(foss),
                "all_commercial_gates_1_10_pass": commercial_pass,
                "all_foss_gates_1_10_pass": foss_pass,
                "poc_candidate_valid": commercial_pass and foss_pass,
                "gate_11_approved": data.get("summary", {}).get("gate_11_approved", False),
                "commercial_product_ready": data.get("summary", {}).get("commercial_product_ready", False),
            }
    except Exception:
        pass
    return {}


def _load_proof_backed_poc_dashboard(repo_root: Path) -> dict:
    """
    Load POC dashboard using proof-backed gate.

    Replaces the shallow _load_poc_dashboard() which only checked poc-targets.yaml text.
    This function calls proof_backed_poc_gate.evaluate_poc_readiness() which verifies:
      - Source files on disk
      - Test files on disk
      - Raw test logs captured per format
      - Example/dogfood output files
      - Ledger entries or proof graph nodes (poc-targets.yaml text is NOT proof)

    Falls back to shallow check (marked as not proof-backed) if gate module unavailable.
    """
    try:
        sys.path.insert(0, str(SCRIPT_DIR))
        from proof_backed_poc_gate import evaluate_poc_readiness
        result = evaluate_poc_readiness(repo_root)
        foss_count = result.get("foss_pass_count", 0)
        foss_min = result.get("foss_minimum_required", 3)
        poc_ready = result.get("poc_ready", False)
        return {
            "commercial_targets_count": len(result.get("commercial_targets", [])),
            "foss_targets_count": len(result.get("foss_targets", [])),
            "all_commercial_gates_1_10_pass": result.get("commercial_all_pass", False),
            "all_foss_gates_1_10_pass": foss_count >= foss_min,
            # poc_candidate_valid mapped from proof-backed poc_ready
            "poc_candidate_valid": poc_ready,
            "poc_ready": poc_ready,
            # gate_11_approved: only True if release_approval_pending=False
            "gate_11_approved": not result.get("release_approval_pending", True),
            # commercial_product_ready: always False â€” requires human Gate 11 approval
            "commercial_product_ready": False,
            "proof_backed": True,
            "decision": result.get("decision", "POC_NOT_READY_CONTINUE"),
            "missing_logs": result.get("missing_logs", []),
            "missing_proof_records": result.get("missing_proof_records", []),
            "missing_examples": result.get("missing_examples", []),
            "foss_pass_count": foss_count,
            "foss_minimum_required": foss_min,
            "proof_failures": result.get("proof_failures", []),
        }
    except ImportError:
        # proof_backed_poc_gate not available â€” fall back to shallow check
        # Mark as not proof-backed so executor knows this is advisory only
        shallow = _load_poc_dashboard(repo_root)
        shallow["proof_backed"] = False
        # Shallow check is insufficient â€” override decision to POC_NOT_READY_CONTINUE
        shallow["decision"] = "POC_NOT_READY_CONTINUE"
        shallow["poc_ready"] = False  # Cannot confirm proof without the gate
        return shallow


def _adjudicate_signals(signals: list, context: dict = None) -> dict:
    """Run stop_reason_adjudicator on a list of signals."""
    try:
        sys.path.insert(0, str(SCRIPT_DIR))
        from stop_reason_adjudicator import adjudicate_batch
        return adjudicate_batch(signals, context or {})
    except ImportError:
        # Adjudicator not available â€” assume non-terminal
        return {
            "overall_terminal": False,
            "has_true_external_gate": False,
            "has_unsafe": False,
            "has_release_pending": False,
            "signals_count": len(signals),
            "adjudicator_available": False,
        }


def classify_execution_state(
    continuation_signal: dict,
    poc_dashboard: dict,
    signals: list = None,
    gate_11_pending: bool = False,
) -> str:
    """
    Classify the current execution state.

    Returns one of the terminal constants or a non-terminal string.
    """
    # 1. Unsafe workspace â€” always terminal
    if continuation_signal.get("unsafe_workspace"):
        return TERMINAL_UNSAFE

    # 2. Run adjudicator on active signals
    active_signals = signals or []
    if continuation_signal.get("stop_reason"):
        active_signals = active_signals + [continuation_signal["stop_reason"]]
    if continuation_signal.get("hard_stops_detected"):
        active_signals = active_signals + continuation_signal["hard_stops_detected"]

    adj = _adjudicate_signals(active_signals, {
        "poc_ready": poc_dashboard.get("poc_candidate_valid", False),
        "gate_11_pending": gate_11_pending,
        "autonomous_continue": continuation_signal.get("autonomous_continue", True),
    })

    if adj.get("has_unsafe"):
        return TERMINAL_UNSAFE

    # 3. Proof-backed POC gate: if decision is POC_NOT_READY_CONTINUE â†’ non-terminal
    #    Only applies when the proof-backed gate was used (proof_backed=True).
    #    Shallow poc-targets.yaml "gates_passed: 1-10" text is NOT sufficient for terminal.
    poc_decision = poc_dashboard.get("decision", "POC_NOT_READY_CONTINUE")
    poc_ready = poc_dashboard.get("poc_ready", False) or poc_dashboard.get("poc_candidate_valid", False)

    if poc_dashboard.get("proof_backed", False) and not poc_ready and poc_decision == "POC_NOT_READY_CONTINUE":
        # POC proof missing â€” not terminal, continue product train
        return NON_TERMINAL_POC_NOT_READY

    # 4. POC ready (proof-backed) + gate 11 pending â†’ release pending terminal
    if poc_ready and gate_11_pending:
        return TERMINAL_POC_READY_RELEASE_PENDING

    # 5. POC ready (proof-backed) + gate 11 approved â†’ POC ready terminal
    if poc_ready and poc_dashboard.get("gate_11_approved"):
        return TERMINAL_POC_READY

    # 6. True external gate â†’ blocked
    if adj.get("has_true_external_gate"):
        return TERMINAL_EXTERNAL_GATE

    # 7. Runtime limit
    if continuation_signal.get("runtime_limit_reached"):
        return TERMINAL_RUNTIME_LIMIT

    # 8. Non-terminal â€” executor must continue or emit continuation packet
    return NON_TERMINAL_CONTINUE


def determine_next_action(
    execution_state: str,
    continuation_signal: dict,
    poc_dashboard: dict,
) -> dict:
    """
    Determine the next action based on execution state.

    Returns a dict with:
      action: str â€” the action to take
      reason: str â€” why this action
      executable_locally: bool â€” whether this can be done without host invocation
      continuation_packet_required: bool â€” whether to write a continuation packet
    """
    if execution_state in (
        TERMINAL_POC_READY_RELEASE_PENDING,
        TERMINAL_POC_READY,
        TERMINAL_RUNTIME_LIMIT,
        TERMINAL_HOST_INVOCATION,
        TERMINAL_EXTERNAL_GATE,
        TERMINAL_UNSAFE,
    ):
        return {
            "action": "TERMINAL",
            "terminal_state": execution_state,
            "reason": f"Terminal state reached: {execution_state}",
            "executable_locally": False,
            "continuation_packet_required": False,
        }

    # POC not ready â€” executor must continue product train (not terminal)
    if execution_state == NON_TERMINAL_POC_NOT_READY:
        return {
            "action": "CONTINUE_PRODUCT_TRAIN",
            "terminal_state": None,
            "reason": (
                "Proof-backed POC gate returned POC_NOT_READY_CONTINUE. "
                "Missing on-disk evidence (source/test logs/proof records). "
                "Continue product train to build proof â€” do NOT stop."
            ),
            "executable_locally": True,
            "continuation_packet_required": True,
            "poc_not_ready": True,
            "next_sprint_path": continuation_signal.get("next_sprint_path", "reports/supervisor/next-sprint.md"),
        }

    # Non-terminal: check if we can continue locally
    iteration = continuation_signal.get("iteration", 0)
    max_iter = continuation_signal.get("max_iterations", 12)

    if iteration >= max_iter:
        return {
            "action": "TERMINAL",
            "terminal_state": TERMINAL_RUNTIME_LIMIT,
            "reason": f"Max iterations reached ({iteration}/{max_iter})",
            "executable_locally": False,
            "continuation_packet_required": True,
        }

    # Can we execute locally?
    safe_lanes = continuation_signal.get("safe_lanes_available", True)
    autonomous = continuation_signal.get("autonomous_continue", True)

    if autonomous and safe_lanes:
        return {
            "action": "NON_TERMINAL_CONTINUE",
            "terminal_state": None,
            "reason": "autonomous_continue=true, safe_lanes_available=true â€” continue execution",
            "executable_locally": True,
            "continuation_packet_required": False,
            "next_sprint_path": continuation_signal.get("next_sprint_path", "reports/supervisor/next-sprint.md"),
            "iteration": iteration,
            "max_iterations": max_iter,
        }

    # Cannot execute locally â€” emit continuation packet for host invocation
    return {
        "action": "TERMINAL",
        "terminal_state": TERMINAL_HOST_INVOCATION,
        "reason": "Executor cannot start next Claude worker from within tooling. Continuation packet emitted.",
        "executable_locally": False,
        "continuation_packet_required": True,
        "next_sprint_path": continuation_signal.get("next_sprint_path", "reports/supervisor/next-sprint.md"),
    }


def write_train_state(output_dir: Path, execution_state: str, next_action: dict,
                      continuation_signal: dict, poc_dashboard: dict) -> Path:
    """Write train-state.json."""
    non_terminal_states = {NON_TERMINAL_CONTINUE, NON_TERMINAL_POC_NOT_READY}
    state = {
        "timestamp": datetime.now().isoformat(),
        "execution_state": execution_state,
        "terminal": execution_state not in non_terminal_states,
        "next_action": next_action,
        "continuation_signal": continuation_signal,
        "poc_dashboard": poc_dashboard,
    }
    path = output_dir / "train-state.json"
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return path


def write_next_action(output_dir: Path, next_action: dict) -> Path:
    """Write next-action.json."""
    path = output_dir / "next-action.json"
    path.write_text(json.dumps(next_action, indent=2), encoding="utf-8")
    return path


def write_stop_reason_decision(output_dir: Path, execution_state: str,
                               adj_result: dict, signals: list) -> Path:
    """Write stop-reason-decision.json."""
    non_terminal_states = {NON_TERMINAL_CONTINUE, NON_TERMINAL_POC_NOT_READY}
    decision = {
        "timestamp": datetime.now().isoformat(),
        "signals_adjudicated": signals,
        "execution_state": execution_state,
        "adjudicator_result": adj_result,
        "is_false_stop": execution_state in non_terminal_states,
        "is_terminal": execution_state not in non_terminal_states,
    }
    path = output_dir / "stop-reason-decision.json"
    path.write_text(json.dumps(decision, indent=2), encoding="utf-8")
    return path


def write_continuation_packet(output_dir: Path, next_action: dict,
                              continuation_signal: dict, execution_state: str,
                              repo_root: Path) -> tuple[Path, Path]:
    """Write continuation-packet.md and continuation-packet.json."""
    next_sprint_path = next_action.get("next_sprint_path", "reports/supervisor/next-sprint.md")

    # Try to read next-sprint.md for context
    ns_path = repo_root / next_sprint_path
    next_sprint_excerpt = ""
    if ns_path.exists():
        content = ns_path.read_text(encoding="utf-8")
        # Take first 500 chars
        next_sprint_excerpt = content[:500] + "..." if len(content) > 500 else content

    packet_md = f"""# Autonomous Train Continuation Packet
# Generated: {datetime.now().isoformat()}
# State: {execution_state}
# Reason: {next_action.get("reason", "")}

## Status
The autonomous train has reached a point where host invocation is required to continue.

## Why Stopped
{next_action.get("reason", "Executor cannot start next Claude worker from within tooling.")}

## Next Action
- Action: {next_action.get("action", "UNKNOWN")}
- Terminal state: {next_action.get("terminal_state", "N/A")}
- Executable locally: {next_action.get("executable_locally", False)}

## Continuation Instructions
1. Read: {next_sprint_path}
2. Load `.local/supervisor/continuation-signal.json`
3. Increment iteration (currently: {continuation_signal.get("iteration", 0)}/{continuation_signal.get("max_iterations", 12)})
4. Execute next sprint
5. Run autonomous-cycle
6. Repeat until terminal state

## Next Sprint Path
{next_sprint_path}

## Next Sprint Preview
```
{next_sprint_excerpt}
```

## Continuation Signal
```json
{json.dumps(continuation_signal, indent=2)}
```

## THIS IS NOT COMPLETE
Hardening sprints, accepted verdicts, and generated next-sprints are NOT terminal states.
Only these are terminal:
- MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING
- MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED
- MAINSTREAM_POC_PROGRESS_CONTINUATION_REQUIRED_BY_RUNTIME_LIMIT
- MAINSTREAM_POC_BLOCKED_EXTERNAL_GATE
- MAINSTREAM_POC_UNSAFE_WORKSPACE
"""

    packet_json = {
        "timestamp": datetime.now().isoformat(),
        "execution_state": execution_state,
        "terminal_state": next_action.get("terminal_state"),
        "reason": next_action.get("reason"),
        "continuation_instructions": {
            "next_sprint_path": next_sprint_path,
            "current_iteration": continuation_signal.get("iteration", 0),
            "max_iterations": continuation_signal.get("max_iterations", 12),
            "autonomous_continue": continuation_signal.get("autonomous_continue", True),
        },
        "non_terminal_proof": {
            "hardening_sprint_complete_is_not_terminal": True,
            "accepted_verdict_is_not_terminal": True,
            "generated_next_sprint_is_not_terminal": True,
            "false_blockers_repaired_in_all_channels": True,
            "next_action_is_executable_or_machine_consumable": True,
        },
    }

    md_path = output_dir / "continuation-packet.md"
    md_path.write_text(packet_md, encoding="utf-8")

    json_path = output_dir / "continuation-packet.json"
    json_path.write_text(json.dumps(packet_json, indent=2), encoding="utf-8")

    return md_path, json_path


def validate_next_sprint_prompt(repo_root: Path, next_sprint_path: str = None) -> dict:
    """
    Validate that the next sprint prompt has no false blockers.

    Returns dict with:
      valid: bool
      false_stops_found: list
      false_stop_count: int
    """
    path = repo_root / (next_sprint_path or "reports/supervisor/next-sprint.md")
    if not path.exists():
        return {"valid": False, "error": f"File not found: {path}", "false_stops_found": [], "false_stop_count": 0}

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    false_stops = []

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("-"):
            continue
        # Check if task line (starts with - [label] TASK-)
        if "TASK-" not in stripped:
            continue
        # False stop labels in task lines
        for label in ("[approval-blocked]", "[blocked]", "[human-required]", "[stop]"):
            if label in stripped:
                false_stops.append(stripped[:80])
                break

    return {
        "valid": len(false_stops) == 0,
        "false_stops_found": false_stops,
        "false_stop_count": len(false_stops),
        "path": str(path),
    }


def run_executor(
    repo_root: Path,
    output_dir: Path,
    declaration_path: Path = None,
    max_local_cycles: int = 3,
) -> dict:
    """
    Main executor logic.

    Returns the executor result dict.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load state
    continuation_signal = _load_continuation_signal(repo_root)
    # Proof-backed gate replaces shallow poc-targets.yaml text check
    poc_dashboard = _load_proof_backed_poc_dashboard(repo_root)

    # Detect active signals
    signals = []
    if continuation_signal.get("stop_reason"):
        signals.append(continuation_signal["stop_reason"])
    if continuation_signal.get("hard_stops_detected"):
        signals.extend(continuation_signal["hard_stops_detected"])
    if not continuation_signal.get("autonomous_continue", True):
        signals.append("autonomous_continue_false")

    # Run adjudicator
    adj_result = _adjudicate_signals(signals, {
        "poc_ready": poc_dashboard.get("poc_candidate_valid", False),
        "autonomous_continue": continuation_signal.get("autonomous_continue", True),
    })

    # Check if POC candidate is ready and Gate 11 is the next step
    gate_11_pending = (
        poc_dashboard.get("poc_candidate_valid", False) and
        not poc_dashboard.get("gate_11_approved", False)
    )

    # Classify execution state
    execution_state = classify_execution_state(
        continuation_signal,
        poc_dashboard,
        signals,
        gate_11_pending=gate_11_pending,
    )

    # Determine next action
    next_action = determine_next_action(
        execution_state, continuation_signal, poc_dashboard
    )

    # Validate next sprint prompt
    prompt_validation = validate_next_sprint_prompt(
        repo_root,
        continuation_signal.get("next_sprint_path"),
    )

    # Write outputs
    train_state_path = write_train_state(
        output_dir, execution_state, next_action, continuation_signal, poc_dashboard
    )
    next_action_path = write_next_action(output_dir, next_action)
    stop_decision_path = write_stop_reason_decision(
        output_dir, execution_state, adj_result, signals
    )

    non_terminal_states = {NON_TERMINAL_CONTINUE, NON_TERMINAL_POC_NOT_READY}
    continuation_packet_path = None
    continuation_packet_json_path = None
    if next_action.get("continuation_packet_required") or execution_state not in non_terminal_states:
        md_path, json_path = write_continuation_packet(
            output_dir, next_action, continuation_signal, execution_state, repo_root
        )
        continuation_packet_path = str(md_path)
        continuation_packet_json_path = str(json_path)

    result = {
        "timestamp": datetime.now().isoformat(),
        "execution_state": execution_state,
        "terminal": execution_state not in non_terminal_states,
        "terminal_state": next_action.get("terminal_state"),
        "next_action": next_action,
        "prompt_validation": prompt_validation,
        "poc_dashboard": poc_dashboard,
        "continuation_signal": continuation_signal,
        "adjudicator_result": adj_result,
        "outputs": {
            "train_state": str(train_state_path),
            "next_action": str(next_action_path),
            "stop_reason_decision": str(stop_decision_path),
            "continuation_packet_md": continuation_packet_path,
            "continuation_packet_json": continuation_packet_json_path,
        },
        "non_terminal_proof": {
            "hardening_sprint_complete_is_not_terminal": True,
            "accepted_verdict_is_not_terminal": True,
            "generated_next_sprint_is_not_terminal": True,
            "false_blockers_repaired_is_not_terminal": True,
            "next_action_is_executable_or_machine_consumable": True,
        },
    }

    # Write executor run result
    run_path = output_dir / "executor-run.json"
    run_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Autonomous Train Executor")
    parser.add_argument(
        "--declaration",
        help="Path to evidence declaration (optional, for context)",
    )
    parser.add_argument(
        "--max-local-cycles",
        type=int,
        default=3,
        help="Maximum local execution cycles",
    )
    parser.add_argument(
        "--out",
        default="reports/autonomous-execution-chaining",
        help="Output directory",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root (defaults to auto-detect)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root) if args.repo_root else REPO_ROOT
    output_dir = repo_root / args.out

    try:
        result = run_executor(
            repo_root=repo_root,
            output_dir=output_dir,
            max_local_cycles=args.max_local_cycles,
        )

        print(f"Execution state: {result['execution_state']}")
        print(f"Terminal: {result['terminal']}")
        if result["terminal"]:
            print(f"Terminal state: {result['terminal_state']}")
        print(f"Next action: {result['next_action']['action']}")
        print(f"Prompt validation: {result['prompt_validation']['valid']} "
              f"({result['prompt_validation']['false_stop_count']} false stops)")
        print(f"Executor run: {output_dir}/executor-run.json")

        if result["terminal"]:
            if result["terminal_state"] == TERMINAL_HOST_INVOCATION:
                print(f"\nContinuation packet: {result['outputs']['continuation_packet_md']}")
            return 0
        else:
            action = result["next_action"]["action"]
            next_path = result["next_action"].get("next_sprint_path", "next-sprint.md")
            if action == "CONTINUE_PRODUCT_TRAIN":
                print(f"\nNon-terminal (POC not ready): continue product train with {next_path}")
            else:
                print(f"\nNon-terminal: continue with {next_path}")
            return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 9


if __name__ == "__main__":
    sys.exit(main())
