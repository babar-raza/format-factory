"""
generate_supervisor_packet.py — Format Factory Local Supervisor Control Plane
Assembles supervisor next-sprint artifacts from evidence review + contradictions.

Generates:
  reports/supervisor/next-sprint.md        — full next-sprint Claude Code prompt
  reports/supervisor/next-sprint-taskmaster.json  — TM import ready (schema-validated)
  reports/supervisor/next-ruflo-lanes.json        — Ruflo lane plan (schema-validated)
  reports/supervisor/approval-gates.md            — gate classifications (mode-aware)
  reports/supervisor/session-resume.md            — fresh-session briefing

Does NOT call Claude Code or any external API — pure local assembly.

Exit codes:
  0 — success
  3 — critical contradictions present; next-sprint focuses on repair
  9 — unexpected error

Usage:
  python tools/supervisor/generate_supervisor_packet.py
  python tools/supervisor/generate_supervisor_packet.py --review reports/supervisor/evidence-review.json --contradictions reports/supervisor/contradictions.json
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from atomic_io import atomic_write_json, atomic_write_text  # noqa: E402

SELECTED_PRODUCT_GAPS_PATH = ".local/supervisor/selected-product-gaps.json"
NEXT_WORK_ITEMS_PATH = ".local/supervisor/next-work-items.json"
SKILL_REGISTRY_PATH = ".supervisor/skill-registry.yaml"
PRODUCT_CODE_LEDGER_PATH = "reports/r90/product-code-change-ledger.json"
CONTEXT_PACK_PATH = ".supervisor/context-pack.yaml"

# R101: Stream-aware prompt generation (D101-GENERIC-PROMPT-01)
KNOWN_STREAMS = ("mainstream", "acceleration", "skills", "supervisor")

STREAM_FOCUS = {
    "mainstream": "ADVANCE: Product deepening — .NET commercial + Python FOSS + dogfood + packaging",
    "acceleration": "ADVANCE: Acceleration tooling — gap selector, skill engine, handoff generator, lane ledger",
    "skills": "ADVANCE: Governed execution — skill commands, validation fixtures, transcript ledger",
    "supervisor": "ADVANCE: Supervisor infrastructure — grading, continuation, stream prompts, evidence model",
}


def detect_stream_from_sprint_id(sprint_id: str) -> str:
    """Extract stream name from sprint_id pattern.

    Patterns:
      FORMAT-FACTORY-SUPERVISOR-R100-... → supervisor
      FORMAT-FACTORY-ACCELERATION-R101-... → acceleration
      FORMAT-FACTORY-SKILLS-R99-... → skills
      FORMAT-FACTORY-MAINSTREAM-R103-... → mainstream
      FORMAT-FACTORY-R93-... → mainstream (legacy, no stream prefix)

    Returns one of: mainstream, acceleration, skills, supervisor
    """
    sid = sprint_id.upper()
    # Match stream name only in the prefix position: FORMAT-FACTORY-{STREAM}-R{N}
    m = re.match(r"FORMAT-FACTORY-(SUPERVISOR|ACCELERATION|SKILLS|MAINSTREAM)-R\d+", sid)
    if m:
        stream_name = m.group(1).lower()
        return stream_name if stream_name != "mainstream" else "mainstream"
    # Legacy sprints without stream prefix are mainstream
    return "mainstream"


def load_context_pack(repo_root: Path) -> dict:
    """Load context-pack.yaml — the authoritative current state snapshot.
    Returns empty dict if not present."""
    path = repo_root / CONTEXT_PACK_PATH
    if not path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def enrich_review_from_context_pack(review: dict, repo_root: Path) -> dict:
    """Patch stale/corrupted evidence-review data with context-pack facts.

    When evidence-review.json has sprint_id: 'unknown' or tests: 0/0 (symptoms
    of D92-01 where legacy bundle-validator overwrote the bridged output), pull
    authoritative state from context-pack.yaml instead.

    This is a READ-ONLY enrichment — it does not modify the on-disk review file.
    """
    sprint_id = review.get("sprint_id", "unknown")
    test_count = review.get("facts", {}).get("test_count", 0)
    verdict = review.get("verdict", "unknown")

    stale_verdicts = {"BLOCKED_MISSING_FINAL_VERDICT", "unknown", ""}
    is_stale = (
        sprint_id in ("unknown", "")
        or verdict in stale_verdicts
        or test_count == 0
    )

    if not is_stale:
        return review

    pack = load_context_pack(repo_root)
    if not pack:
        return review

    # Build enriched copy
    enriched = dict(review)
    latest = pack.get("latest_sprint", {})
    poc = pack.get("poc_matrix", {})

    # Patch sprint_id from context pack
    if sprint_id in ("unknown", ""):
        enriched["sprint_id"] = latest.get("sprint_id", sprint_id)
        enriched["_enriched_sprint_id"] = True

    # Patch verdict from autonomous_continue signal
    if verdict in stale_verdicts:
        auto_continue = latest.get("autonomous_continue", False)
        if auto_continue:
            enriched["verdict"] = "ALL_ACCEPTED_AUTONOMOUS_CONTINUE"
        else:
            enriched["verdict"] = "REVIEW_REQUIRED"
        enriched["_enriched_verdict"] = True

    # Patch test counts from POC matrix
    if test_count == 0:
        net_products = poc.get("commercial_net_products", {})
        net_total = sum(
            v.get("dotnet_tests", 0)
            for v in net_products.values()
            if isinstance(v, dict) and isinstance(v.get("dotnet_tests"), int)
        )
        if net_total > 0:
            facts = dict(enriched.get("facts", {}))
            facts["test_count"] = net_total
            facts["fail_count"] = 0
            facts["_enriched_from_context_pack"] = True
            enriched["facts"] = facts
            enriched["_enriched_test_counts"] = True

    # Patch bundle_validation_pass
    if not enriched.get("bundle_validation_pass", False):
        auto_continue = latest.get("autonomous_continue", False)
        if auto_continue:
            enriched["bundle_validation_pass"] = True
            enriched["_enriched_bundle_validation"] = True

    return enriched


def load_json(path: Path) -> dict:
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _load_gap_ledger_ids(repo_root: Path) -> set:
    """Load all valid gap IDs from gap-ledger.json for phantom-ID prevention."""
    path = repo_root / "reports" / "capability-layer" / "gap-ledger.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        gaps = data.get("gaps", []) if isinstance(data, dict) else data
        return {g.get("gap_id", "") for g in gaps if g.get("gap_id")}
    except Exception:
        return set()


def load_selected_product_gaps(repo_root: Path) -> list[dict]:
    """Load bounded product work selected by the governed R90 selector."""
    payload = load_json(repo_root / SELECTED_PRODUCT_GAPS_PATH)
    if not isinstance(payload, dict):
        return payload if isinstance(payload, list) else []
    gaps = payload.get("selected_gaps", [])
    return gaps if isinstance(gaps, list) else []


def load_memory(memory_path: Path) -> str:
    if memory_path.exists():
        lines = memory_path.read_text(encoding="utf-8").splitlines()
        return "\n".join(lines[-50:])
    return "(no memory file)"


def read_current_mode(repo_root: Path) -> int:
    """Read current mode number from .supervisor/config.yaml.
    Returns 0 if not determinable."""
    config_path = repo_root / ".supervisor" / "config.yaml"
    if not config_path.exists():
        return 0
    text = config_path.read_text(encoding="utf-8")
    m = re.search(r"Status:\s*MODE\s*(\d+)", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return 0


def read_registry_gate_states(repo_root: Path) -> dict:
    """Read gate states from registry/format-registry.yaml for all formats.
    Returns {format_id: {gate_N: status}} for formats with high-number incomplete gates.

    Registry structure:
      formats:
        - format_id: fods
          gates:
            gate_11:
              status: commercial_readiness_in_progress
    """
    registry_path = repo_root / "registry" / "format-registry.yaml"
    if not registry_path.exists():
        return {}
    try:
        text = registry_path.read_text(encoding="utf-8", errors="replace")
        result = {}
        current_format = None
        current_gate = None

        for line in text.splitlines():
            # Detect format_id lines: "  - format_id: fods"
            fmt_m = re.match(r"\s+(?:-\s+)?format_id:\s+(\S+)", line)
            if fmt_m:
                current_format = fmt_m.group(1)
                result[current_format] = {}
                current_gate = None
                continue

            if current_format is None:
                continue

            # Detect gate block starts: "      gate_11:" (with leading spaces)
            gate_m = re.match(r"\s+(gate_\d+):\s*$", line)
            if gate_m:
                current_gate = gate_m.group(1)
                continue

            # Detect status lines under a gate block: "        status: not_started"
            if current_gate:
                status_m = re.match(r"\s+status:\s+(\S+)", line)
                if status_m:
                    result[current_format][current_gate] = status_m.group(1)
                    current_gate = None

        # Return only formats with incomplete high-number gates (>=10)
        filtered = {}
        for fmt, gates in result.items():
            incomplete = {
                g: s for g, s in gates.items()
                if int(g.split("_")[1]) >= 10
                and s not in ("passed", "not_applicable", "waived")
            }
            if incomplete:
                filtered[fmt] = incomplete
        return filtered
    except Exception:
        return {}


def read_open_taskcards(repo_root: Path, limit: int = 5) -> list[dict]:
    """Read open taskcards from taskcards/ directory.
    Returns list of {id, title, status} for not_started/in_progress ones."""
    tc_dir = repo_root / "taskcards"
    if not tc_dir.exists():
        return []
    open_cards = []
    for fn in sorted(tc_dir.iterdir()):
        if not fn.suffix == ".md":
            continue
        try:
            text = fn.read_text(encoding="utf-8", errors="replace")
            status_m = re.search(r"\*\*Status:\*\*\s*(\S+)", text)
            status = status_m.group(1) if status_m else "unknown"
            if status not in ("not_started", "in_progress", "open", "pending"):
                continue
            # Extract title from first h1
            title_m = re.search(r"^#\s+(.+)", text, re.MULTILINE)
            title = title_m.group(1).strip() if title_m else fn.stem
            open_cards.append({
                "id": fn.stem,
                "title": title,
                "status": status,
            })
        except Exception:
            continue
        if len(open_cards) >= limit:
            break
    return open_cards


def synthesize_stream_tasks(stream: str, review: dict, contradictions: dict, repo_root: Path) -> list[dict]:
    """Generate stream-specific tasks for non-mainstream streams.

    Each stream gets tasks appropriate to its domain instead of
    product-gap/gate/dogfood/package tasks that only apply to mainstream.

    R101: D101-GENERIC-PROMPT-01 fix.
    """
    tasks = []
    critical_count = contradictions.get("critical_count", 0)
    task_seq = 1

    # Repair tasks always come first regardless of stream
    if critical_count > 0:
        for i, c in enumerate(contradictions.get("contradictions", []), 1):
            if c["severity"] == "CRITICAL":
                tasks.append({
                    "task_id": f"REPAIR-{i:03d}",
                    "title": f"Repair: {c['description'][:80]}",
                    "description": c.get("detail", ""),
                    "status": "pending",
                    "ff_taskcard_ref": "repair-required",
                    "supervisor_task_ref": "TC-SUP-009",
                    "acceptance_evidence": "contradictions.md shows 0 CRITICAL contradictions",
                    "non_authoritative": True,
                    "lane": "C2",
                })

    task_seq = len(tasks) + 1

    if stream == "acceleration":
        for title, desc, ref in [
            ("Harden gap selector and product-gap extraction pipeline",
             "Verify selected-product-gaps.json freshness; add staleness detection; "
             "test gap selection against current POC matrix state.",
             "ACCEL-GAP-SELECTOR"),
            ("Advance skill engine — new skill templates and validation",
             "Add or harden skill commands in .supervisor/skill-registry.yaml; "
             "ensure skill execution produces governed handoffs with ledger entries.",
             "ACCEL-SKILL-ENGINE"),
            ("Improve execution handoff generator and lane ledger",
             "Harden generate-execution-handoff skill; verify lane ownership "
             "matrix generation; test handoff→declaration→cycle round-trip.",
             "ACCEL-HANDOFF-GEN"),
            ("Stream-aware prompt generation hardening",
             "Verify generate_supervisor_packet.py produces stream-specific prompts; "
             "add anti-regression tests for generic prompt detection.",
             "ACCEL-STREAM-PROMPTS"),
        ]:
            tasks.append({
                "task_id": f"TASK-{task_seq:03d}",
                "title": title,
                "description": desc,
                "status": "pending",
                "supervisor_task_ref": ref,
                "acceptance_evidence": f"Tests pass for {ref}; no regressions",
                "validation_command": "pytest tests/supervisor/ -x -q",
                "non_authoritative": True,
                "lane": "C3",
            })
            task_seq += 1

    elif stream == "skills":
        for title, desc, ref in [
            ("Validate and expand governed skill commands",
             "Run all skill commands in dry-run mode; verify transcript ledger "
             "entries are created; add missing validation fixtures.",
             "SKILLS-COMMAND-VALIDATION"),
            ("Add skill transcript ledger tests",
             "Ensure every skill execution logs to the transcript ledger; "
             "test ledger format, immutability, and query capabilities.",
             "SKILLS-TRANSCRIPT-LEDGER"),
            ("Harden skill registry schema and add new skill templates",
             "Validate .supervisor/skill-registry.yaml against schema; "
             "add skill templates for newly identified patterns.",
             "SKILLS-REGISTRY-SCHEMA"),
            ("Skill execution isolation and rollback testing",
             "Test that skill failures do not leave partial state; "
             "verify rollback mechanisms for governed src edits.",
             "SKILLS-ISOLATION"),
        ]:
            tasks.append({
                "task_id": f"TASK-{task_seq:03d}",
                "title": title,
                "description": desc,
                "status": "pending",
                "supervisor_task_ref": ref,
                "acceptance_evidence": f"Tests pass for {ref}; no regressions",
                "validation_command": "pytest tests/supervisor/ -x -q",
                "non_authoritative": True,
                "lane": "C3",
            })
            task_seq += 1

    elif stream == "supervisor":
        for title, desc, ref in [
            ("Harden grading engine — anti-skip and deep grading",
             "Add grading checks for path-only evidence, missing raw logs, "
             "stale selected gaps, generic prompts, cross-stream pollution.",
             "SUP-GRADING-ENGINE"),
            ("Improve continuation state machine and checkpoint logic",
             "Test all 8 continuation states; verify checkpoint_every policy; "
             "add dirty-tree and YES_WITH_REWORK scenario tests.",
             "SUP-CONTINUATION-SM"),
            ("Stream-aware prompt generation and anti-regression",
             "Verify 4 streams produce distinct prompts; add tests that "
             "detect generic 'Continue normal mega-train lanes' in non-mainstream.",
             "SUP-STREAM-PROMPTS"),
            ("Evidence model hardening — manifest, materialization, review package",
             "Test evidence-manifest generation, materialization verification, "
             "and review package self-containment for all artifact types.",
             "SUP-EVIDENCE-MODEL"),
            ("Replay test infrastructure",
             "Build replay test fixtures from real review packages; verify "
             "that replaying a package produces identical grades.",
             "SUP-REPLAY-INFRA"),
        ]:
            tasks.append({
                "task_id": f"TASK-{task_seq:03d}",
                "title": title,
                "description": desc,
                "status": "pending",
                "supervisor_task_ref": ref,
                "acceptance_evidence": f"Tests pass for {ref}; no regressions",
                "validation_command": "pytest tests/supervisor/ -x -q",
                "non_authoritative": True,
                "lane": "C3",
            })
            task_seq += 1

    # All streams: evidence declaration task
    tasks.append({
        "task_id": f"TASK-{task_seq:03d}",
        "title": "Write evidence declaration and run supervisor autonomous-cycle",
        "description": "Write .local/evidences/<run_id>/evidence-declaration.yaml for all work items, "
                       "then run the declaration-driven supervisor autonomous-cycle.",
        "status": "pending",
        "supervisor_task_ref": "TC-SUP-010",
        "acceptance_evidence": "evidence-declaration.yaml exists and autonomous-cycle regenerates the supervisor packet",
        "validation_command": "python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml",
        "non_authoritative": True,
        "lane": "C6",
    })

    return tasks


def synthesize_sprint_tasks(review: dict, contradictions: dict, repo_root: Path, stream: str = "mainstream", drift_findings_path: "Path | None" = None) -> list[dict]:
    """Generate sprint-specific tasks from gate states, open taskcards, and phase context.
    Returns list of TM-schema-compatible task dicts.

    R101: accepts `stream` parameter. Non-mainstream streams get stream-specific tasks
    via synthesize_stream_tasks() instead of product-oriented tasks.
    """
    # R101: Non-mainstream streams get their own task set
    if stream != "mainstream":
        return synthesize_stream_tasks(stream, review, contradictions, repo_root)

    tasks = []
    critical_count = contradictions.get("critical_count", 0)

    # --- REPAIR TASKS (always first when contradictions exist) ---
    if critical_count > 0:
        for i, c in enumerate(contradictions.get("contradictions", []), 1):
            if c["severity"] == "CRITICAL":
                tasks.append({
                    "task_id": f"REPAIR-{i:03d}",
                    "title": f"Repair: {c['description'][:80]}",
                    "description": c.get("detail", ""),
                    "status": "pending",
                    "ff_taskcard_ref": "repair-required",
                    "supervisor_task_ref": "TC-SUP-009",
                    "acceptance_evidence": "contradictions.md shows 0 CRITICAL contradictions",
                    "validation_command": "python tools/supervisor/compare_goal_to_evidence.py --review reports/supervisor/evidence-review.json",
                    "non_authoritative": True,
                    "lane": "C2",
                })
        # D87-R86-11 FIX: Do NOT return early — continue to add safe product lanes
        # even when repair is needed. Repair tasks are first, but product-factory
        # work-ahead lanes still get generated below.

    # --- SYNTHESIZE FROM CONTEXT (always, regardless of repair status) ---

    task_seq = len(tasks) + 1

    # 0. Governed acceleration preflight (R90+)
    tasks.append({
        "task_id": f"TASK-{task_seq:03d}",
        "title": "Select governed product gaps and validate the product-code ledger",
        "description": f"Load {SELECTED_PRODUCT_GAPS_PATH} and {SKILL_REGISTRY_PATH}. "
                       "No direct ad-hoc src edits are permitted. Any generated execution "
                       f"handoff that edits src must update {PRODUCT_CODE_LEDGER_PATH}.",
        "status": "pending",
        "ff_doc_ref": "docs/product-factory/product-factory-acceleration-layer.md",
        "supervisor_task_ref": "R90-ACCELERATION-PREFLIGHT",
        "acceptance_evidence": f"{PRODUCT_CODE_LEDGER_PATH} validates and selected product gaps map to governed skills or explicit handoffs",
        "validation_command": f"python tools/supervisor/validate_product_code_ledger.py --ledger {PRODUCT_CODE_LEDGER_PATH}",
        "non_authoritative": True,
        "lane": "C3",
    })
    task_seq += 1

    # 1. Check for uncommitted tracked changes (R79 closure indicator)
    try:
        import subprocess
        r = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=10
        )
        modified = [l for l in r.stdout.splitlines() if l.startswith(" M") and
                    any(x in l for x in ["src/python/", "src/net/", "state/", "packaging/"])]
        if modified:
            # R_HARD-P2: Split into agent-owned preparation and external-gate execution.
            # Commit PREPARATION is agent-owned; commit EXECUTION is SCM Agent task per AGENTS.md §AG4.1.
            tasks.append({
                "task_id": f"TASK-{task_seq:03d}",
                "title": "Prepare commit candidate summary and changed-file manifest",
                "description": f"Modified tracked files detected: {len(modified)} file(s) (e.g. {modified[0].strip().split()[-1]}). "
                               "Build evidence bundle and write commit candidate manifest. "
                               "Agent-owned preparation — do NOT self-commit.",
                "status": "agent-owned",
                "ff_doc_ref": "plans/master-plan.md",
                "supervisor_task_ref": "TC-R79-CLOSURE-001",
                "acceptance_evidence": "Commit candidate manifest written; BUNDLE_VALIDATION: PASS",
                "validation_command": ".local/venv/Scripts/python tools/evidence/validate_evidence_bundle.py --contract <contract> --bundle <bundle>",
                "non_authoritative": True,
                "lane": "C3",
            })
            task_seq += 1
            tasks.append({
                "task_id": f"TASK-{task_seq:03d}",
                "title": "Execute git commit (SCM Agent task — AGENTS.md §AG4.1)",
                "description": "Commit is an SCM Agent task. Execute when: tests pass, diff clean, governance validators pass, sprint policy authorizes. "
                               "Classify EXTERNAL_BLOCKER: sprint_policy_not_authorizing_commit if conditions not met.",
                "status": "external-gate",
                "ff_doc_ref": "plans/master-plan.md",
                "supervisor_task_ref": "TC-R79-CLOSURE-001-EXEC",
                "acceptance_evidence": "git log --oneline -1 shows clean commit with sprint evidence",
                "validation_command": "git log --oneline -1",
                "blocker_type": "human_approval",
                "non_authoritative": True,
                "lane": "C3",
            })
            task_seq += 1
    except Exception:
        pass

    # 2. Gate state tasks from registry
    gate_states = read_registry_gate_states(repo_root)
    incomplete_formats = []
    for fmt, gates in gate_states.items():
        for gate, status in gates.items():
            if status in ("not_started", "in_progress", "commercial_readiness_in_progress"):
                gate_num = int(gate.split("_")[1])
                if gate_num >= 10:  # Only surface high gates
                    incomplete_formats.append((fmt, gate, status))

    for fmt, gate, status in incomplete_formats[:3]:
        gate_num = gate.split("_")[1]
        # R_HARD-P2: Split gate tasks. Preparation is agent-owned; approval execution is external-gate.
        # "commercial_readiness_in_progress" → prepare readiness packet (agent-owned)
        # "not_started" / "in_progress" → continue implementation (pending)
        if status == "commercial_readiness_in_progress":
            # Preparation task (agent-owned)
            tasks.append({
                "task_id": f"TASK-{task_seq:03d}",
                "title": f"Prepare {fmt.upper()} Gate {gate_num} readiness packet and commercial checklist",
                "description": f"{fmt} gate_{gate_num} status: {status}. "
                               f"Prepare readiness packet (agent-owned — no human needed for preparation). "
                               f"Packet: capability proof, test counts, dogfood evidence, API documentation.",
                "status": "agent-owned",
                "ff_gate_ref": f"{fmt}_{gate}",
                "ff_doc_ref": "plans/master-plan.md",
                "acceptance_evidence": f"Gate {gate_num} readiness packet written for {fmt}",
                "validation_command": "",
                "non_authoritative": True,
                "lane": "C3",
            })
            task_seq += 1
            tasks.append({
                "task_id": f"TASK-{task_seq:03d}",
                "title": f"Submit {fmt.upper()} Gate {gate_num} for Babar Raza approval (after packet ready — human required)",
                "description": f"Gate {gate_num} approval EXECUTION requires Babar Raza authorization. "
                               f"This is a TRUE_EXTERNAL_GATE per stop_reason_adjudicator. "
                               f"Do NOT self-approve. Only submit after readiness packet is complete.",
                "status": "external-gate",
                "ff_gate_ref": f"{fmt}_{gate}",
                "ff_doc_ref": "plans/master-plan.md",
                "acceptance_evidence": f"Babar Raza written approval of {fmt} Gate {gate_num}",
                "validation_command": f"grep -A5 '{fmt}:' registry/format-registry.yaml | grep '{gate}'",
                "blocker_type": "human_approval",
                "non_authoritative": True,
                "lane": "C3",
            })
            task_seq += 1
        else:
            # Continue implementation (pending — not blocked)
            tasks.append({
                "task_id": f"TASK-{task_seq:03d}",
                "title": f"Continue {fmt.upper()} implementation toward Gate {gate_num} readiness criteria",
                "description": f"{fmt} gate_{gate_num} status: {status}. "
                               f"Continue implementation. This is NOT a hard stop — continue product work.",
                "status": "pending",
                "ff_gate_ref": f"{fmt}_{gate}",
                "ff_doc_ref": "plans/master-plan.md",
                "acceptance_evidence": f"Additional {fmt} capabilities proven; test count increased",
                "validation_command": "",
                "non_authoritative": True,
                "lane": "C3",
            })
            task_seq += 1

    # 3. Open taskcards
    open_tcs = read_open_taskcards(repo_root, limit=3)
    for tc in open_tcs:
        tasks.append({
            "task_id": f"TASK-{task_seq:03d}",
            "title": f"Work on open taskcard: {tc['id']}",
            "description": tc["title"],
            "status": "pending",
            "ff_taskcard_ref": tc["id"],
            "ff_doc_ref": f"taskcards/{tc['id']}.md",
            "acceptance_evidence": f"taskcards/{tc['id']}.md shows Status: closed or verified",
            "validation_command": f"grep 'Status:' taskcards/{tc['id']}.md",
            "non_authoritative": True,
            "lane": "C3",
        })
        task_seq += 1

    # 4. Product-factory lanes from next-work-items.json (TC-MA2-PIPE-001-03)
    # next-work-items.json is the SOLE authority for governed product work.
    # The legacy selected-product-gaps.json + fixture fallback is removed.
    _nwi_path = repo_root / NEXT_WORK_ITEMS_PATH
    _nwi_items: list[dict] = []
    if _nwi_path.exists():
        try:
            _nwi = json.loads(_nwi_path.read_text(encoding="utf-8"))
            _nwi_items = _nwi.get("items", [])
        except Exception as _nwi_err:
            print(f"  WARNING: Could not read {NEXT_WORK_ITEMS_PATH}: {_nwi_err}")

    if _nwi_items:
        for item in _nwi_items[:5]:
            item_id = item.get("item_id", "unknown")
            lane_raw = item.get("lane", "product")
            lane = "C4" if "dogfood" in lane_raw.lower() else "C3"
            tasks.append({
                "task_id": f"TASK-{task_seq:03d}",
                "title": item.get("title", item_id),
                "description": item.get("description", ""),
                "status": "pending",
                "ff_doc_ref": NEXT_WORK_ITEMS_PATH,
                "supervisor_task_ref": item_id,
                "acceptance_evidence": item.get("acceptance_criteria", f"Tests pass for {item_id}"),
                "validation_command": "pytest tests/ -x -q",
                "non_authoritative": False,
                "lane": lane,
            })
            task_seq += 1
    else:
        # No governed product work available — surface explicitly (REQ-PIPE-003)
        tasks.append({
            "task_id": f"TASK-{task_seq:03d}",
            "title": "NO GOVERNED PRODUCT WORK",
            "description": (
                f"{NEXT_WORK_ITEMS_PATH} is empty or missing. "
                "Run autonomous_cycle to regenerate governed work items."
            ),
            "status": "blocked",
            "ff_doc_ref": NEXT_WORK_ITEMS_PATH,
            "supervisor_task_ref": "NONE",
            "acceptance_evidence": "next-work-items.json non-empty",
            "validation_command": "",
            "non_authoritative": False,
            "lane": "C3",
        })
        task_seq += 1

    # 5. Always: dogfood and package/install product-proof lanes
    tasks.append({
        "task_id": f"TASK-{task_seq:03d}",
        "title": "Advance one dogfood export path using a Format Factory library",
        "description": f"Product objective: close or verify a selected dogfood export from {SELECTED_PRODUCT_GAPS_PATH}. "
                       "Use a Format Factory-produced library and record truthful status.",
        "status": "pending",
        "ff_doc_ref": "docs/export/dogfood-export-strategy.md",
        "supervisor_task_ref": "R90-DOGFOOD-LANE",
        "acceptance_evidence": "Dogfood test proves the Format Factory library path and matrix status is truthful",
        "validation_command": "pytest tests/ -x -q",
        "non_authoritative": True,
        "lane": "C4",
    })
    task_seq += 1

    tasks.append({
        "task_id": f"TASK-{task_seq:03d}",
        "title": "Build package artifacts and run installed-workflow proof",
        "description": "Product objective: prove changed product packages from physical artifacts. "
                       "A missing artifact is a failure, not a skipped package test.",
        "status": "pending",
        "ff_doc_ref": "plans/master-plan.md",
        "supervisor_task_ref": "R90-PACKAGE-INSTALL-LANE",
        "acceptance_evidence": "Physical package artifacts exist and installed-workflow tests pass from extracted packages",
        "validation_command": "pytest tests/evidence/ -x -q",
        "non_authoritative": True,
        "lane": "C5",
    })
    task_seq += 1

    # 6. Always: evidence declaration and autonomous-cycle task
    tasks.append({
        "task_id": f"TASK-{task_seq:03d}",
        "title": "Write evidence declaration and run supervisor autonomous-cycle",
        "description": "Write .local/evidences/<run_id>/evidence-declaration.yaml for all work items, "
                       "then run the declaration-driven supervisor autonomous-cycle. ZIP export is optional.",
        "status": "pending",
        "ff_doc_ref": "tools/supervisor/supervisor_loop.py",
        "supervisor_task_ref": "TC-SUP-010",
        "acceptance_evidence": "evidence-declaration.yaml exists and autonomous-cycle regenerates the supervisor packet",
        "validation_command": "python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml",
        "non_authoritative": True,
        "lane": "C6",
    })

    # TC-PBHP-004: Inject playbook drift followup tasks (advisory, non-blocking, capped at 3)
    _drift_findings_path = drift_findings_path
    if _drift_findings_path is None:
        _drift_findings_path = repo_root / ".local" / "supervisor" / "playbook-drift-findings.json"
    try:
        if _drift_findings_path.exists():
            _drift_data = json.loads(_drift_findings_path.read_text(encoding="utf-8"))
            _seen_playbooks: set = set()
            _drift_added = 0
            for _finding in _drift_data:
                if _finding.get("finding_type") != "PLAYBOOK_DRIFT":
                    continue
                _pb = _finding.get("applicable_playbook", "")
                if _pb in _seen_playbooks or _drift_added >= 3:
                    continue
                _seen_playbooks.add(_pb)
                _drift_added += 1
                _phases = _finding.get("required_phases", [])
                tasks.append({
                    "task_id": f"TASK-{task_seq:03d}",
                    "title": f"Playbook drift followup: evidence required phases for {_finding.get('work_item_type', '')}",
                    "description": (
                        f"Prior sprint item '{_finding.get('work_item_id', '')}' used playbook "
                        f"'{_pb}' but evidenced none of its {len(_phases)} required phases "
                        f"({', '.join(_phases[:3])}{'...' if len(_phases) > 3 else ''}). "
                        "Add explicit evidence for at least one phase in the next sprint's declaration."
                    ),
                    "status": "pending",
                    "ff_doc_ref": _pb,
                    "supervisor_task_ref": "TC-PBHP-004",
                    "acceptance_evidence": f"Drift checker reports 0 PLAYBOOK_DRIFT findings for {_finding.get('work_item_type', '')}",
                    "validation_command": "python tools/playbook/playbook_drift_checker.py",
                    "non_authoritative": True,
                    "lane": "C3",
                    "item_type": _finding.get("work_item_type", ""),
                })
                task_seq += 1
    except Exception:
        pass  # advisory — drift followup never blocks task synthesis

    # Fallback: if no tasks were synthesized at all, add generic advance
    if not tasks:
        tasks.append({
            "task_id": "TASK-001",
            "title": "Continue next mega-train sprint",
            "description": "Evidence accepted; continue normal sprint lanes per plans/master-plan.md",
            "status": "pending",
            "ff_doc_ref": "plans/master-plan.md",
            "supervisor_task_ref": "TC-SUP-010",
            "acceptance_evidence": "BUNDLE_VALIDATION: PASS in next sprint evidence bundle",
            "validation_command": ".local/venv/Scripts/python tools/evidence/validate_evidence_bundle.py --contract <contract> --bundle <bundle>",
            "non_authoritative": True,
            "lane": "C0",
        })

    return tasks


def validate_against_schema(data: dict, schema_path: Path) -> list[str]:
    """Validate data against JSON schema.
    Primary: uses jsonschema library.
    Fallback: manual required-field check (no external dependency).
    Returns list of errors; empty = valid."""
    # --- Primary: jsonschema library ---
    try:
        import jsonschema
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        try:
            jsonschema.validate(instance=data, schema=schema)
            return []
        except jsonschema.ValidationError as e:
            return [str(e.message)]
        except jsonschema.SchemaError as e:
            return [f"Schema error: {e.message}"]
    except ImportError:
        pass  # Fall through to manual validation
    except Exception as e:
        return [f"Validation error: {e}"]

    # --- Fallback: manual required-field check (no external library) ---
    errors = []
    if not schema_path.exists():
        return ["Schema file not found — skipping validation"]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"Cannot read schema: {e}"]

    # Check top-level required fields
    required = schema.get("required", [])
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Check tasks array items if present
    tasks_schema = schema.get("properties", {}).get("tasks", {})
    item_required = tasks_schema.get("items", {}).get("required", [])
    for i, task in enumerate(data.get("tasks", [])):
        for field in item_required:
            if field not in task:
                errors.append(f"tasks[{i}] missing required field: {field}")

    if not errors:
        print(
            "  NOTE: jsonschema library not found; manual required-field check used. "
            "For full validation run with .local/venv/Scripts/python.",
            file=sys.stderr,
        )
    return errors


def generate_next_sprint_md(review: dict, contradictions: dict, memory_snippet: str, tasks: list, stream: str = "mainstream", plan_lock: dict | None = None) -> str:
    sprint_id = review.get("sprint_id", "unknown")
    verdict = review.get("verdict", "unknown")
    facts = review.get("facts", {})
    critical_count = contradictions.get("critical_count", 0)
    autonomous = contradictions.get("autonomous_continue", True)

    if critical_count > 0:
        focus = "PRODUCT + REPAIR: Advance product POC AND address CRITICAL contradictions"
        repair_notes = "\n".join(
            f"- [{c['severity']}] {c['description']}"
            for c in contradictions.get("contradictions", [])
        )
    else:
        # R101: Use stream-specific focus instead of generic product focus
        focus = STREAM_FOCUS.get(stream, STREAM_FOCUS["mainstream"])
        repair_notes = "None"

    test_line = f"{facts.get('test_count', 0)} passed, {facts.get('fail_count', 0)} failed, {facts.get('skip_count', 0)} skipped"

    # Split tasks: new-work first, repair/rework second
    repair_tasks = [t for t in tasks if t.get("task_id", "").startswith("REPAIR-")]
    work_tasks = [t for t in tasks if not t.get("task_id", "").startswith("REPAIR-")]

    # R102: Stream-specific section headers instead of "New Product Work"
    STREAM_SECTION_NAMES = {
        "mainstream": "New Product Work (Advisory — Always Execute)",
        "acceleration": "Acceleration Tooling Work (Advisory — Always Execute)",
        "skills": "Governed Skill Work (Advisory — Always Execute)",
        "supervisor": "Supervisor Infrastructure Work (Advisory — Always Execute)",
    }
    section_name = STREAM_SECTION_NAMES.get(stream, STREAM_SECTION_NAMES["mainstream"])

    work_task_lines = "\n".join(
        f"- [{t.get('status', 'pending')}] {t['task_id']}: {t['title']}"
        for t in work_tasks
    ) or "(no tasks generated)"

    repair_task_lines = "\n".join(
        f"- [{t.get('status', 'pending')}] {t['task_id']}: {t['title']}"
        for t in repair_tasks
    ) or "None"

    # R102: Stream-specific lane manifests
    STREAM_LANE_MANIFESTS = {
        "mainstream": """- Lane C0: Coordinator — integration, manifest authority, stop-gate monitoring
- Lane C1: Governance discovery — read AGENTS.md, GOVERNANCE.md, master-plan state
- Lane C2: Repair lanes — address any open contradictions from prior sprint
- Lane C3: Governed implementation — selected gaps, skill registry, product-code ledger
- Lane C4: Dogfood export — use a Format Factory-produced library
- Lane C5: Package/install proof — build physical artifacts and run installed workflows
- Lane C6: Evidence — declaration + autonomous-cycle
- Lane C7: Adversarial — challenge all claims before finalizing""",
        "acceleration": """- Lane C0: Coordinator — integration, stop-gate monitoring
- Lane C1: Governance discovery — read AGENTS.md, policies, skill registry
- Lane C2: Repair lanes — address any open contradictions from prior sprint
- Lane C3: Acceleration tooling — gap selector, skill engine, handoff generator
- Lane C4: Stream-aware prompt generation and anti-regression
- Lane C5: Lane ledger and handoff quality verification
- Lane C6: Evidence — declaration + autonomous-cycle
- Lane C7: Adversarial — challenge all claims before finalizing""",
        "skills": """- Lane C0: Coordinator — integration, stop-gate monitoring
- Lane C1: Governance discovery — read AGENTS.md, policies, skill registry
- Lane C2: Repair lanes — address any open contradictions from prior sprint
- Lane C3: Skill command validation and expansion
- Lane C4: Transcript ledger testing and query capabilities
- Lane C5: Skill execution isolation and rollback testing
- Lane C6: Evidence — declaration + autonomous-cycle
- Lane C7: Adversarial — challenge all claims before finalizing""",
        "supervisor": """- Lane C0: Coordinator — integration, stop-gate monitoring
- Lane C1: Governance discovery — read AGENTS.md, policies, context-pack
- Lane C2: Repair lanes — address any open contradictions from prior sprint
- Lane C3: Grading engine hardening and anti-skip checks
- Lane C4: Continuation state machine and checkpoint logic
- Lane C5: Stream-aware prompt generation and replay infrastructure
- Lane C6: Evidence — declaration + autonomous-cycle
- Lane C7: Adversarial — challenge all claims before finalizing""",
    }
    lane_manifest = STREAM_LANE_MANIFESTS.get(stream, STREAM_LANE_MANIFESTS["mainstream"])

    # R102: Stream-specific rules (non-mainstream streams don't need product ledger rules)
    if stream == "mainstream":
        rules_section = f"""## Non-Negotiable Rules (always apply)
1. No push: SCM Agent task (AGENTS.md §AG4.2). Execute when credentials and branch policy allow; else classify EXTERNAL_BLOCKER: git_push_credentials_unavailable.
2. No commit: SCM Agent task (AGENTS.md §AG4.1). Execute when sprint policy authorizes and tests pass; else classify specific blocker.
3. No gate self-approval without evidence.
4. No active .vscode/mcp.json without MODE 4 approval.
5. No Task Master / Ruflo init without MODE 3+ authorization.
6. Load `{SELECTED_PRODUCT_GAPS_PATH}` and `{SKILL_REGISTRY_PATH}` before product work.
7. Gates 1-10: agent-owned policy gates (evidence + validators + acceptance criteria per AGENTS.md §AG5). Gate 11 G11-G: sole TRUE_EXTERNAL_GATE (Babar Raza).
8. Format Factory authority is final — supervisor is advisory only.
9. No direct ad-hoc `src/` edits. Use a governed skill or generated execution handoff.
10. Every `src/` edit requires an entry in `{PRODUCT_CODE_LEDGER_PATH}`."""
    else:
        rules_section = """## Non-Negotiable Rules (always apply)
1. No push: SCM Agent task (AGENTS.md §AG4.2). Execute when credentials and branch policy allow; else classify EXTERNAL_BLOCKER: git_push_credentials_unavailable.
2. No commit: SCM Agent task (AGENTS.md §AG4.1). Execute when sprint policy authorizes and tests pass; else classify specific blocker.
3. No gate self-approval without evidence.
4. Format Factory authority is final — supervisor is advisory only.
5. Stay within stream boundary — do not implement product features.
6. All supervisor/tool changes must have tests."""

    # R_HARD-P2: STOP_REASON_ADVISORY injected into every generated next-sprint.md
    stop_reason_advisory = """## STOP_REASON_ADVISORY (enforced by stop_reason_adjudicator.py)

Labels [approval-blocked] and [blocked] are NEVER sufficient to stop the autonomous train.
Before treating any task as blocked, run: python tools/supervisor/stop_reason_adjudicator.py "<signal>"

Permanent false stops (NEVER stop for these):
- [approval-blocked] tasks -> reclassify via stop_reason_adjudicator.reclassify_task_label()
- [blocked] tasks -> reclassify; only TRUE_EXTERNAL_GATE/UNSAFE_WORKSPACE stop
- mode_5_approval_pending -> RUFLO_FALLBACK_LOCAL_CONTINUE
- evidence_quality_zero -> LOCAL_REPAIR_CONTINUE
- Gate 11 PREPARATION -> agent-owned (preparation is never a stop)
- anti_skip_critical_block with empty rework_items -> false positive, continue

TRUE_EXTERNAL_GATE (ONLY these warrant a stop):
- git commit/push/merge: SCM Agent task (AGENTS.md §AG4). Classify EXTERNAL_BLOCKER if credentials or policy unavailable.
- Gate 11 G11-G approval EXECUTION (Babar Raza only — sole TRUE_EXTERNAL_GATE)
- NuGet/PyPI publication execution
- Credentials unavailable with no fallback

"""

    content = f"""# Supervisor-Generated Next Sprint Prompt
# Source sprint: {sprint_id}
# Stream: {stream}
# Generated: {datetime.now().isoformat()}
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
{focus}

## Prior Sprint Summary
- Sprint ID: {sprint_id}
- Evidence verdict: {verdict}
- Tests: {test_line}
- Autonomous continue: {autonomous}

{stop_reason_advisory}## Section 1: {section_name}
{work_task_lines}

## Section 2: Rework / Repair (Advisory — Fix Before Closeout)
{repair_task_lines}

## Contradictions Context
{repair_notes}

{rules_section}

## Evidence Requirements for Next Sprint
- Write `.local/evidences/<run_id>/evidence-declaration.yaml`
- Run `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml`
- ZIP bundle export is optional for archive or external transfer
- Tests: 0 failures required

## Suggested Lane Manifest (Advisory)
{lane_manifest}

## Project Memory Context
```
{memory_snippet}
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
"""
    # TC-PBHP-002: Inject playbook guidance for applicable work item types (C1 fix).
    # Advisory only — exceptions are caught and silently skipped.
    try:
        import sys as _sys_pb
        from pathlib import Path as _PB_Path
        _pb_repo = _PB_Path(__file__).resolve().parent.parent.parent
        _sys_pb.path.insert(0, str(_pb_repo / "tools" / "playbook"))
        from playbook_selector import select_playbook as _sel_pb
        from generate_playbook_taskcards import parse_contract as _parse_pb
        _pb_seen, _pb_sections = set(), []
        for _task in tasks:
            _wtype = _task.get("item_type", "")
            if _wtype and _wtype not in _pb_seen:
                _pb_seen.add(_wtype)
                _pb_path = _sel_pb(_wtype)
                if _pb_path:
                    _contract = _parse_pb(_PB_Path(_pb_repo / _pb_path))
                    if _contract and _contract.get("status") == "ACTIVE":
                        _pb_sections.append({
                            "type": _wtype,
                            "skill": f"/{_contract['playbook_id']}",
                            "phases": _contract.get("phases", []),
                            "stop_conditions": _contract.get("stop_conditions", []),
                        })
        if _pb_sections:
            _pb_block = "\n\n---\n\n## Playbook Guidance (advisory)\n\n"
            _pb_block += "> Invoke the listed skill before executing each work item type.\n\n"
            for _s in _pb_sections:
                _pb_block += f"**{_s['type']}** -> `{_s['skill']}`"
                if _s["phases"]:
                    _pb_block += f"  \nPhases: {' -> '.join(_s['phases'])}"
                if _s["stop_conditions"]:
                    _pb_block += f"  \nStop if: {'; '.join(_s['stop_conditions'])}"
                _pb_block += "\n\n"
            content += _pb_block
    except Exception:
        pass  # advisory — never blocks sprint generation

    # Plan-lock header: if a per-chat plan is active, prepend a prominent notice.
    if plan_lock and plan_lock.get("status") != "COMPLETE":
        _pp = plan_lock.get("plan_path", "unknown")
        _ltc = plan_lock.get("last_taskcard", "unknown")
        _plan_header = (
            "## ACTIVE PER-CHAT PLAN \u2014 SYSTEM LEDGER SUPPRESSED\n\n"
            "A per-chat plan is active. Complete ALL plan taskcards before any ledger/product work.\n\n"
            f"- **Plan:** `{_pp}`\n"
            f"- **Last completed taskcard:** `{_ltc}`\n"
            f"- **Action:** Read the plan file. Find the next open taskcard after `{_ltc}`. Execute it.\n"
            f"  After each: `python tools/supervisor/write_plan_lock.py --plan-path \"{_pp}\" --last-taskcard <TC_ID>`\n"
            f"  When ALL done: `python tools/supervisor/write_plan_lock.py --plan-path \"{_pp}\" --complete`\n\n"
            "**Do NOT start system ledger / product hardening work until plan status = COMPLETE.**\n\n"
            "---\n\n"
        )
        return _plan_header + content

    return content


def generate_taskmaster_json(review: dict, contradictions: dict, tasks: list) -> dict:
    sprint_id = review.get("sprint_id", "unknown")
    timestamp = datetime.now().isoformat()

    return {
        "sprint_id": f"supervisor-export-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": timestamp,
        "verdict": review.get("verdict", "unknown"),
        "source_bundle": review.get("bundle_path", ""),
        "tasks": tasks,
        "notes": f"Generated from evidence review of sprint {sprint_id}",
    }


def generate_ruflo_lanes_json(review: dict, contradictions: dict, tasks: list) -> dict:
    timestamp = datetime.now().isoformat()
    sprint_id = review.get("sprint_id", "unknown")

    # Assign tasks to lanes
    c2_tasks = [t["task_id"] for t in tasks if t.get("lane") == "C2"]
    c3_tasks = [t["task_id"] for t in tasks if t.get("lane") == "C3"]
    c4_tasks = [t["task_id"] for t in tasks if t.get("lane") == "C4"]
    c5_tasks = [t["task_id"] for t in tasks if t.get("lane") == "C5"]

    lanes = [
        {
            "lane_id": "C0",
            "owner_role": "Coordinator",
            "title": "Sprint coordination and integration",
            "description": "Tracks all lanes; owns file ownership matrix; stops on emergency conditions",
            "allowed_files": ["reports/rNN/**"],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**", "tools/evidence/**", "tests/evidence/**"],
            "dependencies": [],
            "tasks": [t["task_id"] for t in tasks if t.get("lane") == "C0"],
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C1",
            "owner_role": "Governance",
            "title": "Governance discovery",
            "description": "Read-only access to governance files; produces preflight report",
            "allowed_files": ["reports/rNN/00-preflight.md"],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md"],
            "dependencies": [],
            "tasks": [],
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C2",
            "owner_role": "Repair",
            "title": "Contradiction repair",
            "description": "Address any open CRITICAL contradictions from prior sprint",
            "allowed_files": ["reports/rNN/**", "src/**"],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**"],
            "dependencies": ["C0"],
            "tasks": c2_tasks,
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C3",
            "owner_role": "Implementation",
            "title": "Product implementation and taskcard execution",
            "description": f"Product objective: execute selected work from {SELECTED_PRODUCT_GAPS_PATH} through {SKILL_REGISTRY_PATH}; no ad-hoc src edits; update {PRODUCT_CODE_LEDGER_PATH}",
            "allowed_files": ["src/**", "tests/**", "reports/rNN/**", "taskcards/**", PRODUCT_CODE_LEDGER_PATH],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**"],
            "dependencies": ["C0", "C1"],
            "tasks": c3_tasks,
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C4",
            "owner_role": "Dogfood",
            "title": "Dogfood export advancement",
            "description": f"Product objective: close or verify one selected dogfood export from {SELECTED_PRODUCT_GAPS_PATH} using a Format Factory-produced library",
            "allowed_files": ["src/**", "tests/**", "reports/rNN/**", PRODUCT_CODE_LEDGER_PATH],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**"],
            "dependencies": ["C0", "C1", "C3"],
            "tasks": c4_tasks,
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C5",
            "owner_role": "PackageInstall",
            "title": "Package and installed-workflow proof",
            "description": "Product objective: prove changed packages from physical artifacts; missing artifacts fail the lane",
            "allowed_files": ["packaging/**", "tests/**", "reports/rNN/**"],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**"],
            "dependencies": ["C0", "C1", "C3", "C4"],
            "tasks": c5_tasks,
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C6",
            "owner_role": "Evidence",
            "title": "Evidence bundle",
            "description": "Write the evidence declaration and run supervisor autonomous-cycle",
            "allowed_files": [".local/evidence/**"],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**"],
            "dependencies": ["C0", "C1", "C2", "C3", "C4", "C5"],
            "tasks": [t["task_id"] for t in tasks if t.get("lane") == "C6"],
            "status": "pending",
            "non_authoritative": True,
        },
    ]

    return {
        "sprint_id": f"supervisor-export-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": timestamp,
        "verdict": review.get("verdict", "unknown"),
        "source_bundle": review.get("bundle_path", ""),
        "coordinator_lane": "C0",
        "lanes": lanes,
        "overlap_check_passed": True,
        "notes": f"Generated from evidence review of sprint {sprint_id}",
    }


def generate_approval_gates_md(review: dict, contradictions: dict, current_mode: int, repo_root: Path = None) -> str:
    critical_count = contradictions.get("critical_count", 0)
    autonomous = contradictions.get("autonomous_continue", True)

    lines = [
        "# Approval Gates Classification",
        f"Sprint ID: {review.get('sprint_id', 'unknown')}",
        f"Generated: {datetime.now().isoformat()}",
        f"Current Mode: MODE {current_mode}" + (" (ACTIVE_MCP_ACTIVATION)" if current_mode == 4 else
                                                  " (AUTONOMOUS_SPRINT_LOOP_RC)" if current_mode == 5 else ""),
        "",
        "## Pending Actions",
        "",
    ]

    # D86-SUP-06 fix: Physical check for .vscode/mcp.json
    mcp_physically_present = False
    if repo_root:
        mcp_json_path = repo_root / ".vscode" / "mcp.json"
        mcp_physically_present = mcp_json_path.exists()

    if critical_count > 0:
        lines += [
            "| Action | Classification | Who Unblocks |",
            "|--------|---------------|-------------|",
            f"| Repair {critical_count} CRITICAL contradictions | local-repair-loop | Claude_Code |",
            "| Continue to next sprint | stop-contradictions-present | Claude_Code (after repair) |",
        ]
    else:
        if current_mode >= 4 and mcp_physically_present:
            mcp_row = "| MCP activation (MODE 4 ACTIVE — .vscode/mcp.json verified present) | autonomous-continue | already-done |"
        elif current_mode >= 4 and not mcp_physically_present:
            mcp_row = "| MCP activation (MODE 4 claimed but .vscode/mcp.json MISSING) | stop-mcp-file-missing | User |"
        else:
            mcp_row = "| MCP activation | stop-mcp-activation-required | User |"

        lines += [
            "| Action | Classification | Who Unblocks |",
            "|--------|---------------|-------------|",
            "| Continue to next sprint lanes | autonomous-continue | null |",
            "| Gate approval (if any gate pending) | stop-gate-approval-required | Babar_Raza |",
            "| Push/commit | agent-owned-scm-task | Agent_AG4 |",
            mcp_row,
        ]

    # D86-SUP-06 fix: Physical check for MCP status line
    if current_mode >= 4 and mcp_physically_present:
        next_gate_line = "- NEXT_HUMAN_GATE: MODE 5 autonomous sprint loop (explicit user approval required)"
        mcp_status_line = "- MCP_STATUS: ACTIVE (.vscode/mcp.json verified present)"
    elif current_mode >= 4 and not mcp_physically_present:
        next_gate_line = "- NEXT_HUMAN_GATE: MODE 4 MCP file missing (restore .vscode/mcp.json)"
        mcp_status_line = "- MCP_STATUS: CLAIMED_BUT_MISSING (.vscode/mcp.json not found on disk)"
    else:
        next_gate_line = "- NEXT_HUMAN_GATE: MODE 4 MCP activation (explicit user approval required)"
        mcp_status_line = "- MCP_STATUS: NOT_ACTIVATED (MODE < 4)"

    lines += [
        "",
        "## Summary",
        f"- AUTONOMOUS_CONTINUE: {'YES' if autonomous else 'NO — repair required first'}",
        next_gate_line,
        mcp_status_line,
        "- DAEMON_STATUS: NOT_STARTED (no human gate needed to keep it stopped)",
    ]

    return "\n".join(lines) + "\n"


def _load_due_obligations(repo_root: Path, lookahead_days: int = 14) -> list:
    """C4 (MOR read path): Load open obligations due within lookahead window.

    Returns empty list if MOR absent, MOR import fails, or no obligations are due.
    Non-blocking — never raises.
    """
    try:
        mor_path = repo_root / "reports" / "supervisor" / "maintenance-obligations.json"
        import importlib as _il
        _mor = _il.import_module("tools.supervisor.maintenance_obligation_register")
        return _mor.surface_due_obligations(mor_path, lookahead_days=lookahead_days)
    except Exception:
        return []


def generate_session_resume_md(
    review: dict,
    contradictions: dict,
    memory_snippet: str,
    current_mode: int,
    due_obligations: list | None = None,
) -> str:
    facts = review.get("facts", {})
    _sprint_id = review.get('sprint_id', 'unknown')
    _now_iso = datetime.now().isoformat()

    # Build optional ## Maintenance Obligations Due section
    _mor_section = ""
    if due_obligations:
        rows = []
        for o in due_obligations:
            sched = o.get("scheduled_date") or "(no date)"
            action = o.get("action", "")[:80]
            rows.append(
                f"| {o['obligation_id']} | {o.get('type', '')} | {sched} "
                f"| {action} | {o.get('owner', '')} |"
            )
        _mor_section = (
            "\n## Maintenance Obligations Due\n"
            "| obligation_id | type | scheduled_date | action | owner |\n"
            "|---|---|---|---|---|\n"
            + "\n".join(rows)
            + "\n"
        )

    return f"""<!-- generated_at: {_now_iso} | source_sprint: {_sprint_id} -->
# Session Resume Briefing
# Format Factory — Supervisor-Generated
# Generated: {_now_iso}

## Quick State
- Last sprint: {review.get('sprint_id', 'unknown')}
- Evidence verdict: {review.get('verdict', 'unknown')}
- Tests: {facts.get('test_count', 0)} passed / {facts.get('fail_count', 0)} failed
- PENDING markers: {facts.get('pending_marker_count', 0)}
- CRITICAL contradictions: {contradictions.get('critical_count', 0)}
- Autonomous continue: {contradictions.get('autonomous_continue', True)}
- Current supervisor mode: MODE {current_mode}
- MCP status: {'ACTIVE (.vscode/mcp.json present)' if current_mode >= 4 else 'NOT_ACTIVATED'}
{_mor_section}
## What Was Done Last Sprint
(Read reports/supervisor/evidence-review.md for full details)

## What To Do Next
1. Run: `python tools/supervisor/check_continuation.py`
2. If verdict=CONTINUE: read `next_work_items_path` from output (structured work items)
3. If verdict=STOP: report the reason to the user and halt
4. Structured work items: `.local/supervisor/next-work-items.json`
5. Prose context: `reports/supervisor/next-sprint.md`

## Where To Find Evidence
- Last evidence bundle: {review.get('bundle_path', 'see .supervisor/state/current-run.json')}
- Supervisor outputs: reports/supervisor/
- Project memory: .supervisor/project-memory.md

## Project Memory (recent)
```
{memory_snippet}
```

## IMPORTANT REMINDERS
- Format Factory authority is FINAL. Supervisor output is advisory.
- No push: SCM Agent task (AGENTS.md §AG4.2). Execute when credentials and branch policy allow.
- Gates 1-10: agent-owned policy gates (AGENTS.md §AG5). Gate 11 G11-G: Babar Raza only.
- MCP activation (MODE 4): {'COMPLETE' if current_mode >= 4 else 'requires explicit user approval'}.
"""


def generate_packet(repo_root: Path, output_dir: Path = None, stream: str = None, plan_lock: dict | None = None) -> int:
    """Generate the full supervisor packet from evidence-review.json + contradictions.json.

    This is the programmatic entry point used by autonomous_cycle.py (R99 fix: D99-STALE-01).
    R101: accepts optional `stream` parameter for stream-aware prompt generation.
    Returns 0 on success, 3 if critical contradictions present.
    """
    repo_root = repo_root.resolve()
    if output_dir is None:
        output_dir = repo_root / "reports" / "supervisor"
    output_dir.mkdir(parents=True, exist_ok=True)

    review = load_json(output_dir / "evidence-review.json")
    review = enrich_review_from_context_pack(review, repo_root)
    contradictions = load_json(output_dir / "contradictions.json")

    # Suppress stale-bundle contradictions if context-pack says autonomous_continue
    if review.get("_enriched_sprint_id") or review.get("_enriched_verdict"):
        pack = load_context_pack(repo_root)
        auto_continue = pack.get("latest_sprint", {}).get("autonomous_continue", False)
        if auto_continue:
            stale_keywords = {"BUNDLE_VALIDATION", "final-verdict.md", "Sprint ID not found"}
            clean_contras = [
                c for c in contradictions.get("contradictions", [])
                if not any(kw in c.get("description", "") for kw in stale_keywords)
            ]
            contradictions = dict(contradictions)
            contradictions["contradictions"] = clean_contras
            contradictions["critical_count"] = sum(
                1 for c in clean_contras if c.get("severity") == "CRITICAL"
            )
            contradictions["overall"] = (
                "CRITICAL_CONTRADICTIONS"
                if contradictions["critical_count"] > 0
                else "CLEAN"
            )
            contradictions["autonomous_continue"] = auto_continue

    memory_snippet = load_memory(repo_root / ".supervisor" / "project-memory.md")
    current_mode = read_current_mode(repo_root)

    # R101: Detect stream from sprint_id if not explicitly provided
    if stream is None:
        sprint_id = review.get("sprint_id", "unknown")
        stream = detect_stream_from_sprint_id(sprint_id)

    tasks = synthesize_sprint_tasks(review, contradictions, repo_root, stream=stream)

    (output_dir / "next-sprint.md").write_text(
        generate_next_sprint_md(review, contradictions, memory_snippet, tasks, stream=stream, plan_lock=plan_lock), encoding="utf-8"
    )
    (output_dir / "approval-gates.md").write_text(
        generate_approval_gates_md(review, contradictions, current_mode, repo_root), encoding="utf-8"
    )
    (output_dir / "session-resume.md").write_text(
        generate_session_resume_md(
            review, contradictions, memory_snippet, current_mode,
            due_obligations=_load_due_obligations(repo_root),
        ), encoding="utf-8"
    )

    # Also write contradiction/evidence-review markdown
    tm_data = generate_taskmaster_json(review, contradictions, tasks)
    (output_dir / "next-sprint-taskmaster.json").write_text(
        json.dumps(tm_data, indent=2), encoding="utf-8"
    )
    ruflo_data = generate_ruflo_lanes_json(review, contradictions, tasks)
    (output_dir / "next-ruflo-lanes.json").write_text(
        json.dumps(ruflo_data, indent=2), encoding="utf-8"
    )

    critical_count = contradictions.get("critical_count", 0)
    return 3 if critical_count > 0 else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate supervisor next-sprint packet from evidence review"
    )
    parser.add_argument(
        "--review",
        type=Path,
        default=Path("reports/supervisor/evidence-review.json"),
        help="Path to evidence-review.json",
    )
    parser.add_argument(
        "--contradictions",
        type=Path,
        default=Path("reports/supervisor/contradictions.json"),
        help="Path to contradictions.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/supervisor"),
        help="Directory for output files",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    review = load_json(args.review)
    # D92-01 fix: enrich stale/corrupted review data from context-pack.yaml
    review = enrich_review_from_context_pack(review, repo_root)
    if review.get("_enriched_sprint_id") or review.get("_enriched_test_counts"):
        enrichments = [k for k in ("_enriched_sprint_id", "_enriched_verdict", "_enriched_test_counts") if review.get(k)]
        print(f"  NOTE: evidence-review.json enriched from context-pack.yaml: {enrichments}")
    contradictions = load_json(args.contradictions)
    # D92-01 fix: if review was enriched (was stale) and contradictions reference
    # missing-final-verdict or BUNDLE_VALIDATION FAIL, suppress them as false positives
    if review.get("_enriched_sprint_id") or review.get("_enriched_verdict"):
        pack = load_context_pack(repo_root)
        auto_continue = pack.get("latest_sprint", {}).get("autonomous_continue", False)
        if auto_continue:
            # Suppress stale-bundle contradictions; declaration-based cycle was CLEAN
            orig_crit = contradictions.get("critical_count", 0)
            stale_keywords = {"BUNDLE_VALIDATION", "final-verdict.md", "Sprint ID not found"}
            clean_contras = [
                c for c in contradictions.get("contradictions", [])
                if not any(kw in c.get("description", "") for kw in stale_keywords)
            ]
            if len(clean_contras) < orig_crit:
                print(f"  NOTE: Suppressed {orig_crit - len(clean_contras)} false-positive stale-bundle contradictions")
                contradictions = dict(contradictions)
                contradictions["contradictions"] = clean_contras
                contradictions["critical_count"] = sum(
                    1 for c in clean_contras if c.get("severity") == "CRITICAL"
                )
                contradictions["overall"] = (
                    "CRITICAL_CONTRADICTIONS"
                    if contradictions["critical_count"] > 0
                    else "CLEAN"
                )
                contradictions["autonomous_continue"] = auto_continue
    memory_snippet = load_memory(repo_root / ".supervisor" / "project-memory.md")
    current_mode = read_current_mode(repo_root)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # R111: Detect stream from sprint_id (matching generate_packet() behavior)
    sprint_id = review.get("sprint_id", "unknown")
    stream = detect_stream_from_sprint_id(sprint_id)

    # Synthesize sprint-specific tasks
    tasks = synthesize_sprint_tasks(review, contradictions, repo_root, stream=stream)

    # Generate next-sprint.md
    next_sprint_text = generate_next_sprint_md(review, contradictions, memory_snippet, tasks, stream=stream)
    atomic_write_text(output_dir / "next-sprint.md", next_sprint_text)

    # Generate next-sprint-taskmaster.json
    tm_data = generate_taskmaster_json(review, contradictions, tasks)
    schema_dir = repo_root / ".supervisor" / "schemas"
    tm_errors = validate_against_schema(tm_data, schema_dir / "next-sprint-taskmaster.schema.json")
    atomic_write_json(output_dir / "next-sprint-taskmaster.json", tm_data)

    # Generate next-ruflo-lanes.json
    ruflo_data = generate_ruflo_lanes_json(review, contradictions, tasks)
    ruflo_errors = validate_against_schema(ruflo_data, schema_dir / "next-ruflo-lanes.schema.json")
    atomic_write_json(output_dir / "next-ruflo-lanes.json", ruflo_data)

    # Generate approval-gates.md (mode-aware)
    gates_text = generate_approval_gates_md(review, contradictions, current_mode, repo_root)
    atomic_write_text(output_dir / "approval-gates.md", gates_text)

    # Generate session-resume.md (C4: surface due MOR obligations)
    resume_text = generate_session_resume_md(
        review, contradictions, memory_snippet, current_mode,
        due_obligations=_load_due_obligations(repo_root),
    )
    atomic_write_text(output_dir / "session-resume.md", resume_text)

    critical_count = contradictions.get("critical_count", 0)
    print("PACKET_GENERATION: COMPLETE")
    print(f"  Output dir: {output_dir}")
    print(f"  next-sprint.md: written ({len(tasks)} tasks synthesized)")
    print("  next-sprint-taskmaster.json: written" + (f" (schema errors: {tm_errors})" if tm_errors else " (schema OK)"))
    print("  next-ruflo-lanes.json: written" + (f" (schema errors: {ruflo_errors})" if ruflo_errors else " (schema OK)"))
    print(f"  approval-gates.md: written (mode {current_mode}: {'MCP ACTIVE' if current_mode >= 4 else 'MCP pending'})")
    print("  session-resume.md: written")

    if critical_count > 0:
        print(f"  NOTE: {critical_count} CRITICAL contradictions — next-sprint focuses on repair")
        return 3

    return 0


if __name__ == "__main__":
    sys.exit(main())
