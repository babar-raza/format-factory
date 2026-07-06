"""
autonomous_cycle_extensions.py — TC-SH helper blocks for autonomous_cycle.py

Extracted to keep autonomous_cycle.py under its baseline_loc_cap.
All functions are non-blocking helpers called from specific steps in autonomous_cycle.py.
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_sprint_learnings_prepass(repo_root: Path) -> None:
    """Step 0a-prepass (TC-SH-005): Sprint learnings pre-pass.

    Reads prior sprint learnings via learning_consumer.py, writes advisory
    pre-pass-advisory.json. Completely non-blocking.
    """
    print("=== STEP 0a-prepass: SPRINT LEARNINGS PRE-PASS ===")
    try:
        from learning_consumer import LearningConsumer
        lc = LearningConsumer(repo_root)
        lc_count = lc.scan_all_learnings()
        if lc_count > 0:
            lc.aggregate()
            proposals = lc.generate_proposals(threshold=2)
            prepass_path = repo_root / ".local" / "supervisor" / "pre-pass-advisory.json"
            prepass_path.parent.mkdir(parents=True, exist_ok=True)
            prepass_data = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "authority_state": "ai_advisory",
                "non_authoritative": True,
                "total_learnings_scanned": lc_count,
                "unique_patterns": len(lc.aggregated),
                "proposals_count": len(proposals),
                "top_recurring": sorted(
                    lc.aggregated.values(),
                    key=lambda x: x["occurrence_count"],
                    reverse=True,
                )[:5],
                "proposals": proposals,
            }
            prepass_path.write_text(
                json.dumps(prepass_data, indent=2, default=str),
                encoding="utf-8",
            )
            print(f"  Scanned {lc_count} learnings, {len(proposals)} proposals "
                  f"-> {prepass_path}")
        else:
            print("  No sprint learnings found — skipping pre-pass")
    except Exception as exc:
        print(f"  WARNING: Sprint learnings pre-pass skipped (non-blocking): {exc}")


def run_stale_lock_reaper(repo_root: Path, timestamp: str) -> int:
    """Step 0a3 (TC-SH-011): Stale plan lock reaper.

    Scans plan-locks/ for IN_PROGRESS locks older than 48h. If the plan file
    is TERMINAL_CLOSED or missing, marks the lock COMPLETE.
    Returns number of reaped locks.
    """
    print("=== STEP 0a3: STALE PLAN LOCK REAPER ===")
    reaped = 0
    try:
        reaper_dir = repo_root / ".local" / "supervisor" / "plan-locks"
        if reaper_dir.is_dir():
            import time
            now_ts = time.time()
            for lf in sorted(reaper_dir.glob("*.json")):
                try:
                    lock_age_h = (now_ts - lf.stat().st_mtime) / 3600
                    if lock_age_h < 48:
                        continue
                    lock_data = json.loads(lf.read_text(encoding="utf-8"))
                    if lock_data.get("status") != "IN_PROGRESS":
                        continue
                    plan_path_str = lock_data.get("plan_path", "")
                    plan_file = repo_root / plan_path_str if plan_path_str else None
                    should_reap = False
                    if plan_file and not plan_file.exists():
                        should_reap = True
                    elif plan_file and plan_file.exists():
                        plan_text = plan_file.read_text(encoding="utf-8", errors="replace")
                        if "TERMINAL_CLOSED" in plan_text or "status: COMPLETE" in plan_text:
                            should_reap = True
                    if should_reap:
                        lock_data["status"] = "COMPLETE"
                        lock_data["reaped_by"] = "TC-SH-011_stale_lock_reaper"
                        lock_data["reaped_at"] = timestamp
                        lf.write_text(json.dumps(lock_data, indent=2), encoding="utf-8")
                        reaped += 1
                        print(f"  Reaped stale lock: {lf.name} (age={lock_age_h:.0f}h)")
                except Exception:
                    continue
        print(f"  Stale locks reaped: {reaped}")
    except Exception as err:
        print(f"  WARNING: Stale lock reaper failed (non-blocking): {err}")
    return reaped


def classify_rework_items(rework_items: list, sprint_id: str, timestamp: str,
                          review_dir: Path, repo_root: Path) -> None:
    """Step 3c2 (TC-SH-007): Rework item root cause classification.

    Pattern-matches rework items against known failure categories.
    Writes rework-classification.json.
    """
    if not rework_items:
        return
    print("\n=== STEP 3c2: REWORK CLASSIFICATION ===")
    try:
        import shutil
        patterns = {
            "GOV_BLOCK": "governance_violation",
            "SKILL_GATE": "skill_attribution_missing",
            "LANE_ENFORCEMENT": "lane_violation",
            "TC-GUARD": "guard_violation",
            "PROMPT_QUALITY": "prompt_quality",
            "PROMPT_INCOMPLETE": "prompt_incomplete",
            "test_failure": "test_failure",
            "evidence_missing": "evidence_gap",
            "OVERCLAIM": "overclaim",
        }
        classifications = []
        for rw_item in rework_items:
            rw_str = str(rw_item)
            category = "UNCLASSIFIED"
            for pattern, cat in patterns.items():
                if pattern in rw_str:
                    category = cat
                    break
            classifications.append({"item": rw_str[:200], "category": category})
        rw_class_path = review_dir / "rework-classification.json"
        rw_class_path.write_text(json.dumps({
            "sprint_id": sprint_id,
            "classified_at": timestamp,
            "total_rework_items": len(rework_items),
            "classifications": classifications,
        }, indent=2), encoding="utf-8")
        persist_path = repo_root / ".local" / "supervisor" / "rework-classification.json"
        persist_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(rw_class_path), str(persist_path))
        print(f"  Classified {len(classifications)} rework items -> {rw_class_path}")
    except Exception as err:
        print(f"  WARNING: Rework classification failed (non-blocking): {err}")


def append_maturity_trend(repo_root: Path) -> None:
    """Step 7d (TC-SH-012): Maturity trend appended to session-resume.md.

    Calls maturity_trend.py and appends a ## Maturity Trend section.
    Non-blocking: skips silently on failure.
    """
    print("\n=== STEP 7d: MATURITY TREND ===")
    try:
        import subprocess
        maturity_script = repo_root / "tools" / "supervisor" / "maturity_trend.py"
        if maturity_script.exists():
            result = subprocess.run(
                [sys.executable, str(maturity_script)],
                cwd=str(repo_root),
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                sr_path = repo_root / "reports" / "supervisor" / "session-resume.md"
                if sr_path.exists():
                    sr_text = sr_path.read_text(encoding="utf-8")
                    if "## Maturity Trend" not in sr_text:
                        sr_text += "\n\n## Maturity Trend\n\n"
                        sr_text += result.stdout.strip()[:500]
                        sr_text += "\n"
                        sr_path.write_text(sr_text, encoding="utf-8")
                        print("  Maturity trend appended to session-resume.md")
                    else:
                        print("  Maturity trend already present in session-resume.md")
                else:
                    print("  session-resume.md not found — skipping trend append")
            else:
                print(f"  maturity_trend.py: exit {result.returncode} — skipping")
        else:
            print("  maturity_trend.py not found — skipping")
    except Exception as err:
        print(f"  WARNING: Maturity trend failed (non-blocking): {err}")


def load_selected_gap_ids(repo_root: Path) -> set:
    """TC-MACH-CAP-002: Load selected product gap IDs for priority boosting.

    Runs capability compiler to refresh selected-product-gaps.json if stale
    (>1 hour old or empty). Returns set of selected gap_id strings.
    """
    selected_gaps_path = repo_root / ".local" / "supervisor" / "selected-product-gaps.json"
    try:
        needs_refresh = True
        if selected_gaps_path.exists():
            sg_data = json.loads(selected_gaps_path.read_text(encoding="utf-8"))
            if isinstance(sg_data, dict) and sg_data.get("selected_gap_count", 0) > 0:
                gen_at = sg_data.get("generated_at", "")
                if gen_at:
                    try:
                        gen_time = datetime.fromisoformat(gen_at)
                        age = (datetime.now(timezone.utc) - gen_time).total_seconds()
                        if age < 3600:
                            needs_refresh = False
                    except Exception:
                        pass
        if needs_refresh:
            try:
                from capability_compiler import select_and_write_gaps
                select_and_write_gaps(output_path=selected_gaps_path)
            except Exception:
                pass
        if selected_gaps_path.exists():
            sg_data = json.loads(selected_gaps_path.read_text(encoding="utf-8"))
            gaps_list = sg_data.get("selected_gaps", []) if isinstance(sg_data, dict) else sg_data
            return {g.get("gap_id", "") for g in gaps_list if isinstance(g, dict)}
    except Exception:
        pass
    return set()


def enrich_goals_with_compiled_taskcards(all_goals: list, repo_root: Path) -> None:
    """TC-SH-003: Enrich gap-ledger goals with compiled taskcard metadata.

    Reads compiled-gap-taskcards.json and adds compiled_taskcard_id/path
    to matching goals by gap_id. Best-effort: errors are silently ignored.
    """
    try:
        compiled_path = repo_root / ".local" / "supervisor" / "compiled-gap-taskcards.json"
        if not compiled_path.exists():
            return
        cgd = json.loads(compiled_path.read_text(encoding="utf-8"))
        if not isinstance(cgd, dict):
            return
        index = {}
        for cg in cgd.get("compiled", []):
            gid = cg.get("gap_id", "")
            if gid and cg.get("status") == "compiled":
                index[gid] = cg
        for goal in all_goals:
            gid = goal.get("gap_id", "")
            if gid in index:
                goal["compiled_taskcard_id"] = index[gid].get("taskcard_id")
                goal["compiled_taskcard_path"] = index[gid].get("taskcard_path")
                goal["gap_ledger_ref"] = gid  # TC-GUARD-001 requires this field
    except Exception:
        pass


def write_govblock_directive(structural_blocks: list, sprint_id: str,
                             timestamp: str, signal_dir: Path) -> None:
    """TC-SH-006: GOV_BLOCK auto-repair directive writer.

    When current rework_items contain structural GOV_BLOCK items, writes
    govblock-auto-repair-directive.json.
    """
    if not structural_blocks:
        return
    try:
        from atomic_io import atomic_write_json
        directive_path = signal_dir / "govblock-auto-repair-directive.json"
        blocking_formats = set()
        fmt_candidates = (
            "zst", "xcf", "fodg", "fods", "fodt", "ndjson", "csv",
            "tsv", "sylk", "abw", "dif", "gnumeric", "ods", "odt",
            "pbm", "pgm", "ppm", "qoi", "toml",
        )
        for gb_item in structural_blocks:
            for fmt in fmt_candidates:
                if fmt in gb_item.lower():
                    blocking_formats.add(fmt.upper())
        directive = {
            "generated_at": timestamp,
            "source_sprint_id": sprint_id,
            "govblock_items": structural_blocks,
            "blocking_formats": sorted(blocking_formats) if blocking_formats else ["UNKNOWN"],
            "recommended_sprint_type": "analytics_separation",
            "recommended_taskcard_pattern": "TC-HEAL-PY-{FORMAT}-001",
            "auto_apply_wired": True,
            "authority": "TC-SH-006",
        }
        atomic_write_json(directive_path, directive)
        print(f"  TC-SH-006: GOV_BLOCK auto-repair directive written -> {directive_path}")
        print(f"    Blocking formats: {directive['blocking_formats']}")
    except Exception as err:
        print(f"  WARNING: TC-SH-006 directive write failed (non-blocking): {err}")


# ---------------------------------------------------------------------------
# TC-MACH-LANE-001: Lane conflict guard (extracted for testability)
# ---------------------------------------------------------------------------


def check_lane_conflicts(
    declared_lane: str,
    changed_files: list,
    policies_path: "Path | None" = None,
) -> list:
    """Check for cross-lane file changes and return hard_stop strings.

    Returns empty list if no conflicts, or list of LANE_CONFLICT strings.
    Grace period is checked via policies.yaml ``lanes_grace_period_until``.
    """
    hard_stops: list = []
    _declared_lane = (declared_lane or "").upper()
    _lane_violations: list = []

    if _declared_lane == "MACHINERY":
        for cf in changed_files:
            if isinstance(cf, str) and (cf.startswith("src/python/") or cf.startswith("src/net/")):
                _lane_violations.append(f"MACHINERY sprint touched product source: {cf}")
    elif _declared_lane == "PRODUCT":
        for cf in changed_files:
            if isinstance(cf, str) and cf.startswith("tools/supervisor/") and not cf.endswith("_test.py"):
                _lane_violations.append(f"PRODUCT sprint touched machinery: {cf}")

    if _lane_violations:
        _grace_active = False
        if policies_path is not None:
            try:
                import yaml as _yaml_lc
                _pol = _yaml_lc.safe_load(policies_path.read_text(encoding="utf-8"))
                _grace_until = (_pol or {}).get("lanes_grace_period_until", "")
                if _grace_until:
                    if datetime.now().isoformat() < str(_grace_until):
                        _grace_active = True
            except Exception:
                pass
        if not _grace_active:
            hard_stops.append(
                f"LANE_CONFLICT: {_declared_lane} sprint has cross-lane file changes"
            )
    return hard_stops


# ---------------------------------------------------------------------------
# TC-MACH-SAL-001: SAL staleness escalation (extracted for testability)
# ---------------------------------------------------------------------------


def check_sal_staleness(sal_is_stale: bool, sprint_type: str) -> list:
    """Return hard_stop strings when SAL is stale and sprint is product-type.

    MACHINERY and SAL_REPAIR sprints are exempt from the block.
    Returns empty list if not stale or sprint type is exempt.
    """
    hard_stops: list = []
    if sal_is_stale:
        _sprint_type = (sprint_type or "").upper()
        if "SAL_REPAIR" not in _sprint_type and "MACHINERY" not in _sprint_type:
            hard_stops.append(
                "SAL_STALE: sal-facts-latest.json is >7 days old. "
                "Run SAL refresh before product sprints. "
                "Override: set sprint_type to MACHINERY:sal_repair"
            )
    return hard_stops


# ---------------------------------------------------------------------------
# TC-SGOV-008: Steps 3d+3e+3f extraction (SAL recompute, capability map,
# capability queue consumer, authority integration fabric)
# ---------------------------------------------------------------------------


def run_sal_capmap_recompute(decl, repo_root, review):
    """Steps 3d+3e+3f: SAL recompute, capability map, queue consumer, fabric.

    Returns (sal_result, capmap_result, consumer_result, fabric_result).
    All non-blocking — failures are logged but do not stop the cycle.
    """
    print("\n=== STEP 3d: SAL + CAPABILITY MAP RECOMPUTE ===")
    sal_result = {"status": "skipped"}
    capmap_result = {"status": "skipped"}

    changed_files = decl.get("changed_files", [])
    product_src_changed = any(f.startswith("src/") for f in changed_files)
    if product_src_changed:
        try:
            sal_runner_path = repo_root / "tools" / "specification-authority-layer" / "sal_master_runner.py"
            if sal_runner_path.exists():
                sal_proc = subprocess.run(
                    [sys.executable, str(sal_runner_path), "--all", "--output-dir",
                     str(repo_root / ".local" / "sal-output")],
                    capture_output=True, text=True, timeout=120, cwd=str(repo_root)
                )
                sal_result = {
                    "status": "completed" if sal_proc.returncode == 0 else "failed",
                    "returncode": sal_proc.returncode,
                    "trigger": "product_src_changed",
                }
                print(f"  SAL recompute: {'OK' if sal_proc.returncode == 0 else 'FAILED'} "
                      f"(exit {sal_proc.returncode})")
            else:
                sal_result = {"status": "not_found", "path": str(sal_runner_path)}
                print("  SAL recompute: sal_master_runner.py not found — skipped")
        except Exception as sal_err:
            sal_result = {"status": "error", "error": str(sal_err)}
            print(f"  WARNING: SAL recompute failed: {sal_err}")

        try:
            capmap_gen_path = repo_root / "tools" / "capability_layer" / "capability_map_generator.py"
            if capmap_gen_path.exists():
                capmap_proc = subprocess.run(
                    [sys.executable, str(capmap_gen_path)],
                    capture_output=True, text=True, timeout=120, cwd=str(repo_root)
                )
                capmap_result = {
                    "status": "completed" if capmap_proc.returncode == 0 else "failed",
                    "returncode": capmap_proc.returncode,
                    "trigger": "sal_recompute_completed",
                }
                print(f"  Capability map recompute: {'OK' if capmap_proc.returncode == 0 else 'FAILED'} "
                      f"(exit {capmap_proc.returncode})")
            else:
                capmap_result = {"status": "not_found", "path": str(capmap_gen_path)}
                print("  Capability map recompute: capability_map_generator.py not found — skipped")
        except Exception as cap_err:
            capmap_result = {"status": "error", "error": str(cap_err)}
            print(f"  WARNING: Capability map recompute failed: {cap_err}")
    else:
        print("  No product source changes detected — recompute skipped")

    # Step 3e: Capability Queue Consumer (TC-WIRE-001)
    print("\n=== STEP 3e: CAPABILITY QUEUE CONSUMER ===")
    consumer_result = {"status": "skipped"}
    consumer_path = repo_root / "tools" / "supervisor" / "capability_queue_consumer.py"
    if consumer_path.exists():
        try:
            consumer_proc = subprocess.run(
                [sys.executable, str(consumer_path), "--max-gaps", "5"],
                capture_output=True, text=True, timeout=60, cwd=str(repo_root)
            )
            consumer_result = {
                "status": "completed" if consumer_proc.returncode == 0 else "failed",
                "returncode": consumer_proc.returncode,
                "trigger": "post_capmap_recompute",
                "stdout_tail": consumer_proc.stdout.strip().splitlines()[-3:] if consumer_proc.stdout else [],
            }
            print(f"  Capability queue consumer: {'OK' if consumer_proc.returncode == 0 else 'FAILED'} "
                  f"(exit {consumer_proc.returncode})")
            if consumer_proc.stdout:
                for line in consumer_proc.stdout.strip().splitlines()[-3:]:
                    print(f"    {line}")
        except Exception as consumer_err:
            consumer_result = {"status": "error", "error": str(consumer_err)}
            print(f"  WARNING: Capability queue consumer failed: {consumer_err}")
    else:
        consumer_result = {"status": "not_found", "path": str(consumer_path)}
        print("  Capability queue consumer: not found — skipped")

    # Step 3f: Authority Integration Fabric (TC-FABRIC-001)
    print("\n=== STEP 3f: AUTHORITY INTEGRATION FABRIC ===")
    fabric_result = {"status": "skipped"}
    fabric_script = repo_root / "tools" / "supervisor" / "authority_integration_fabric.py"
    if fabric_script.exists():
        try:
            fabric_proc = subprocess.run(
                [sys.executable, str(fabric_script)],
                capture_output=True, text=True, timeout=120, cwd=str(repo_root)
            )
            fabric_result = {
                "status": "completed" if fabric_proc.returncode == 0 else "failed",
                "returncode": fabric_proc.returncode,
                "stdout_lines": fabric_proc.stdout.strip().splitlines()[-5:] if fabric_proc.stdout else [],
                "stderr_lines": fabric_proc.stderr.strip().splitlines()[-5:] if fabric_proc.stderr else [],
            }
            if fabric_proc.returncode == 0:
                print("  Authority integration fabric: OK")
            else:
                print(f"  Authority integration fabric: non-zero exit {fabric_proc.returncode} (non-blocking)")
        except Exception as fabric_err:
            fabric_result = {"status": "error", "error": str(fabric_err)}
            print(f"  Authority integration fabric error (non-blocking): {fabric_err}")

    return sal_result, capmap_result, consumer_result, fabric_result


# ---------------------------------------------------------------------------
# TC-SGOV-008: Step 6 extraction (copy latest summaries)
# ---------------------------------------------------------------------------


def copy_cycle_summaries(review, review_dir, repo_root,
                         detected_stream, run_id, sprint_id,
                         timestamp, track, prompt_path):
    """Step 6: Copy latest summaries to reports/supervisor/ and stream dirs."""
    print("\n=== STEP 6: COPY LATEST SUMMARIES ===")
    latest_dir = repo_root / "reports" / "supervisor"
    latest_dir.mkdir(parents=True, exist_ok=True)

    copies = [
        ("supervisor-review.md", "latest-review.md"),
        ("combined-next-worker-prompt.md", "latest-next-worker-prompt.md"),
        ("item-grades.json", "work-item-grades.json"),
        ("item-grades.yaml", "work-item-grades.yaml"),
    ]
    for src_name, dst_name in copies:
        src = review_dir / src_name
        dst = latest_dir / dst_name
        if src.exists():
            shutil.copy2(str(src), str(dst))
            print(f"  Copied: {dst}")

    stream_dir = repo_root / "reports" / "supervisor-streams" / detected_stream
    stream_dir.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name in copies:
        src = review_dir / src_name
        dst = stream_dir / dst_name
        if src.exists():
            shutil.copy2(str(src), str(dst))
    print(f"  Stream dir: {stream_dir}")

    _supervisor_dir = repo_root / ".local" / "supervisor"
    if track == "product":
        _track_supervisor_dir = _supervisor_dir / "product"
    elif track == "machinery":
        _track_supervisor_dir = _supervisor_dir / "machinery"
    else:
        _track_supervisor_dir = _supervisor_dir
    canonical_work_items = _track_supervisor_dir / "next-work-items.json"
    canonical_work_items.parent.mkdir(parents=True, exist_ok=True)
    legacy_work_items = _supervisor_dir / "next-work-items.json"
    legacy_work_items.parent.mkdir(parents=True, exist_ok=True)
    src_work = review_dir / "next-work-items.json"
    if src_work.exists():
        shutil.copy2(str(src_work), str(canonical_work_items))
        if track:
            shutil.copy2(str(src_work), str(legacy_work_items))
        print(f"  Canonical work items: {canonical_work_items}")

    authority_map = {
        "stream": detected_stream, "run_id": run_id,
        "sprint_id": sprint_id, "timestamp": timestamp,
        "stream_local_dir": str(stream_dir), "global_dir": str(latest_dir),
        "authority": "STREAM_LOCAL", "global_status": "ADVISORY_REFERENCE",
        "stream_local_files": {
            "evidence_review": str(stream_dir / "evidence-review.json"),
            "contradictions": str(stream_dir / "contradictions.json"),
            "next_prompt": str(stream_dir / "latest-next-worker-prompt.md"),
            "work_item_grades": str(stream_dir / "work-item-grades.json"),
            "continuation_signal": str(
                repo_root / ".local" / "supervisor" / "streams" / detected_stream / "continuation-signal.json"
            ),
        },
    }
    (stream_dir / "authority-map.json").write_text(
        json.dumps(authority_map, indent=2), encoding="utf-8"
    )
    print(f"  Authority map: {stream_dir / 'authority-map.json'}")

    grades = review.get("item_grades", [])
    if grades:
        wg_lines = [
            "# Work Item Grades", f"Sprint: {sprint_id}",
            f"Generated: {timestamp}",
            f"Global Status: {review.get('overall_verdict', 'UNKNOWN')}",
            "", "| Item ID | Grade | Rework Required |",
            "|---------|-------|-----------------|",
        ]
        for g in grades:
            rework = (g.get("required_rework") or "")[:80]
            wg_lines.append(f"| {g['item_id']} | {g['supervisor_grade']} | {rework} |")
        wg_lines += [
            "", "## Summary",
            f"- Accepted: {len(review['accepted_items'])}",
            f"- Rework: {len(review['rework_items'])}",
            f"- Overclaimed: {len(review['overclaimed_items'])}",
            f"- Autonomous Continue: {review['autonomous_continue']}",
        ]
        (latest_dir / "work-item-grades.md").write_text("\n".join(wg_lines) + "\n", encoding="utf-8")
        print(f"  Written: {latest_dir / 'work-item-grades.md'}")

    summary_lines = [
        "# Latest Supervisor Cycle Summary", f"Run: {run_id}",
        f"Sprint: {sprint_id}", f"Timestamp: {timestamp}",
        f"Verdict: {review['overall_verdict']}",
        f"Autonomous Continue: {review['autonomous_continue']}",
        f"Accepted: {len(review['accepted_items'])}",
        f"Rework: {len(review['rework_items'])}",
        f"Overclaimed: {len(review['overclaimed_items'])}",
        f"Review: {review_dir / 'supervisor-review.md'}",
        f"Next Prompt: {prompt_path}",
    ]
    (latest_dir / "latest-cycle-summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")


def run_post_grading_anti_skip(review, decl, sprint_id, review_dir, repo_root, detected_stream):
    """Step 3b: Post-grading anti-skip checks (R107: hard gates with severity).

    Extracted from autonomous_cycle.py (TC-SGOV-008).
    """
    import json
    from anti_skip_checks import run_anti_skip_checks
    from validate_package_identity import _extract_stream_from_sprint

    print("\n=== STEP 3b: ANTI-SKIP QUALITY CHECKS ===")
    evidence_root = repo_root / decl.get("evidence_root", "")
    target_stream = _extract_stream_from_sprint(sprint_id)
    sample_outputs_dir = evidence_root / "sample-outputs"

    # Load gaps if available
    gaps_data = None
    gaps_path = evidence_root / f"selected-gaps-{review.get('run_id', '')}.json"
    if gaps_path.exists():
        try:
            gaps_data = json.loads(gaps_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Load generated prompt if available
    prompt_text = ""
    prompt_path = review_dir / "combined-next-worker-prompt.md"
    if prompt_path.exists():
        prompt_text = prompt_path.read_text(encoding="utf-8")

    # R111: Load global next-sprint.md for stream-output authority check
    global_next_sprint_text = ""
    global_ns_path = repo_root / "reports" / "supervisor" / "next-sprint.md"
    if global_ns_path.exists():
        try:
            global_next_sprint_text = global_ns_path.read_text(encoding="utf-8")
        except Exception:
            pass

    # Extract declared item types for stream-aware anti-skip exemptions
    _declared_item_types = list({
        item.get("item_type", "")
        for item in decl.get("planned_work_items", [])
        if item.get("item_type")
    }) if decl else None

    anti_skip_result = run_anti_skip_checks(
        prompt_text=prompt_text,
        gaps_data=gaps_data,
        expected_sprint=sprint_id,
        evidence_root=evidence_root,
        declaration=decl,
        grades=review.get("item_grades", []),
        target_stream=target_stream,
        repo_root=repo_root,
        sample_outputs_dir=sample_outputs_dir if sample_outputs_dir.exists() else None,
        next_sprint_text=global_next_sprint_text,
        declared_scope=_declared_item_types,
    )
    # Write anti-skip results
    (review_dir / "anti-skip-check-result.json").write_text(
        json.dumps(anti_skip_result, indent=2), encoding="utf-8"
    )
    anti_skip_impact = anti_skip_result.get("impact", {})
    print(f"  Anti-skip: {anti_skip_result['total_checks']} checks, "
          f"{anti_skip_result['violations']} violations")
    if anti_skip_impact:
        if anti_skip_impact.get("block"):
            print(f"  HARD GATE BLOCK: {anti_skip_impact['block_items']}")
        if anti_skip_impact.get("downgrade"):
            print(f"  DOWNGRADE: {anti_skip_impact['downgrade_items']}")
        if anti_skip_impact.get("caveats"):
            print(f"  CAVEATS: {anti_skip_impact['caveats']}")
    if anti_skip_result["violations"] > 0:
        for check in anti_skip_result["checks"]:
            if check.get("is_violation"):
                sev = check.get("severity", "medium")
                print(f"    [{sev.upper()}] {check['check']} — {check.get('recommendation', '')[:100]}")

    # R107: Apply hard gate enforcement to review
    if anti_skip_impact and anti_skip_impact.get("block"):
        review["autonomous_continue"] = False
        review["stop_reason"] = f"Anti-skip critical block: {anti_skip_impact['block_items']}"
        review["critical_rework_count"] = max(review["critical_rework_count"], 1)
        print("  >>> CONTINUATION BLOCKED by anti-skip critical violations")
    elif anti_skip_impact and anti_skip_impact.get("downgrade"):
        # High-severity violations downgrade the overall verdict
        if review["overall_verdict"] == "ACCEPTED":
            review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
        review["anti_skip_downgrade_reasons"] = anti_skip_impact["downgrade_items"]
        print("  >>> VERDICT DOWNGRADED by anti-skip high-severity violations")

    return anti_skip_result, anti_skip_impact


def validate_prompt_and_work_items(review, prompt_path, next_work, detected_stream,
                                    sprint_id, review_dir, repo_root):
    """Steps 4b+4c: Prompt quality validation, zero-task circuit breaker, completeness.

    Extracted from autonomous_cycle.py (TC-SGOV-008).
    """
    import json

    # Step 4b: Prompt quality validation (R108: moved after prompt generation)
    print("\n=== STEP 4b: PROMPT QUALITY VALIDATION ===")
    try:
        from validate_prompt_quality import validate_prompt_quality
        target_stream = detected_stream
        if prompt_path.exists():
            prompt_text = prompt_path.read_text(encoding="utf-8")
            has_repairs = len(review.get("rework_items", [])) > 0
            pq_result = validate_prompt_quality(
                prompt_text, target_stream,
                has_repairs=has_repairs, has_advancement=True,
            )
            (review_dir / "prompt-quality-result.json").write_text(
                json.dumps(pq_result, indent=2), encoding="utf-8"
            )
            if pq_result["valid"]:
                print(f"  Prompt quality: PASS ({pq_result['passed']}/{pq_result['total_checks']} checks)")
            else:
                failed_checks = [c["check"] for c in pq_result["checks"] if not c["pass"]]
                print(f"  Prompt quality: FAIL ({pq_result['failed']} failures: {failed_checks})")
                # R108: Prompt quality failures — hard-stop only for truly unrecoverable issues
                hard_prompt_failures = {"stream_identity", "not_generic"}
                soft_prompt_failures = {"no_wrong_stream", "advancement_lane"}
                failed_set = set(failed_checks)
                has_hard = bool(hard_prompt_failures & failed_set)
                has_soft_only = bool(soft_prompt_failures & failed_set) and not has_hard
                if has_hard:
                    review["autonomous_continue"] = False
                    review["stop_reason"] = f"Prompt quality gate: {failed_checks}"
                    review["prompt_quality_failure"] = True
                    print("  >>> CONTINUATION BLOCKED by prompt quality failures")
                elif has_soft_only:
                    # Soft failures become rework items — safe lanes can continue
                    review.setdefault("rework_items", [])
                    review["rework_items"].append(f"PROMPT_QUALITY_REWORK:{','.join(failed_checks)}")
                    print(f"  Prompt quality: soft failure {failed_checks} → rework (not hard stop)")
        else:
            print("  No prompt file to validate")
    except Exception as e:
        print(f"  WARNING: Prompt quality check skipped: {e}")
    print(f"  Next work: {len(next_work['items'])} items (stream={detected_stream})")

    # SUP-RECT-005: Circuit breaker for zero-task loops
    if len(next_work.get("items", [])) == 0:
        zero_task_counter_path = repo_root / ".local" / "supervisor" / "zero-task-counter.json"
        ztc = {"count": 0, "sprints": []}
        try:
            if zero_task_counter_path.exists():
                ztc = json.loads(zero_task_counter_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
        ztc["count"] = ztc.get("count", 0) + 1
        ztc.setdefault("sprints", []).append(sprint_id)
        zero_task_counter_path.parent.mkdir(parents=True, exist_ok=True)
        zero_task_counter_path.write_text(json.dumps(ztc, indent=2), encoding="utf-8")
        if ztc["count"] >= 3:
            print(f"  CIRCUIT BREAKER: {ztc['count']} consecutive zero-task cycles detected!")
            review["stop_reason"] = (
                review.get("stop_reason", "") +
                f" CIRCUIT_BREAKER: {ztc['count']} zero-task cycles ({ztc['sprints'][-3:]})"
            ).strip()
            review["autonomous_continue"] = False
        else:
            print(f"  Zero-task warning: {ztc['count']}/3 before circuit breaker triggers")
    else:
        # Reset counter on successful task generation
        ztc_path = repo_root / ".local" / "supervisor" / "zero-task-counter.json"
        if ztc_path.exists():
            ztc_path.write_text(json.dumps({"count": 0, "sprints": []}, indent=2), encoding="utf-8")

    # Step 4b: Validate next-work-items stream correctness (R108)
    try:
        from validate_prompt_quality import validate_next_work_items
        nwi_result = validate_next_work_items(next_work, detected_stream)
        (review_dir / "next-work-items-quality.json").write_text(
            json.dumps(nwi_result, indent=2), encoding="utf-8"
        )
        if nwi_result["valid"]:
            print(f"  Next-work-items quality: PASS ({nwi_result['passed']}/{nwi_result['total_checks']})")
        else:
            failed = [c["check"] for c in nwi_result["checks"] if not c["pass"]]
            print(f"  Next-work-items quality: FAIL ({failed})")
            if "no_wrong_stream_items" in failed or "stream_field_match" in failed:
                review["autonomous_continue"] = False
                review["stop_reason"] = f"Next-work-items stream violation: {failed}"
    except Exception as e:
        print(f"  WARNING: Next-work-items validation skipped: {e}")

    # Step 4c: Validate generated prompt has required sections
    print("\n=== STEP 4c: PROMPT COMPLETENESS VALIDATION ===")
    try:
        if prompt_path.exists():
            prompt_text = prompt_path.read_text(encoding="utf-8")
            required_sections = ["## Sprint", "## Mandatory Evidence", "## Hard Prohibitions"]
            found = [s for s in required_sections if s in prompt_text]
            missing = [s for s in required_sections if s not in prompt_text]
            has_tasks = "TASK-" in prompt_text or "## Group G" in prompt_text or "## Section 1" in prompt_text
            classification = {
                "classification": "STRUCTURED_PROMPT" if not missing and has_tasks else "INCOMPLETE_PROMPT",
                "required_sections_found": found,
                "required_sections_missing": missing,
                "has_task_items": has_tasks,
                "line_count": len(prompt_text.splitlines()),
            }
            (review_dir / "output-classification.json").write_text(
                json.dumps(classification, indent=2), encoding="utf-8"
            )
            if missing or not has_tasks:
                review.setdefault("rework_items", [])
                review["rework_items"].append(f"PROMPT_INCOMPLETE:missing={missing},tasks={has_tasks}")
                print(f"  Prompt completeness: INCOMPLETE (missing={missing}, tasks={has_tasks})")
            else:
                print(f"  Prompt completeness: PASS ({len(found)} sections, tasks=True, {classification['line_count']} lines)")
        else:
            print("  No prompt file to validate")
            review["autonomous_continue"] = False
            review["stop_reason"] = "No generated prompt file"
    except Exception as e:
        print(f"  WARNING: Prompt completeness check skipped: {e}")


# ---------------------------------------------------------------------------
# TC-TCF-005: Autonomous reopening helpers
# ---------------------------------------------------------------------------

_TERMINAL_TASK_STATUSES = frozenset({"CLOSED", "SUPERSEDED", "EXCLUDED"})


def find_next_eligible_task_in_plan(plan_path: str) -> dict | None:
    """TC-TCF-005: Find the first open (non-terminal) taskcard in a plan.

    Returns {"tc_id": ..., "plan_path": ..., "status": ...} or None.
    Uses lifecycle_audit.parse_plan_taskcards which already knows the taskcard
    status patterns (OPEN, IN_PROGRESS, PENDING, CLOSED, etc.).
    """
    try:
        import sys as _sys
        from pathlib import Path as _Path
        _sys.path.insert(0, str(_Path(__file__).resolve().parent))
        from lifecycle_audit import parse_plan_taskcards  # type: ignore[import]
        tcs = parse_plan_taskcards(plan_path)
        for tc in tcs:
            if tc.get("status", "OPEN") not in _TERMINAL_TASK_STATUSES:
                return {
                    "tc_id": tc.get("tc_id") or tc.get("id", "UNKNOWN"),
                    "plan_path": plan_path,
                    "status": tc.get("status", "OPEN"),
                }
        return None
    except Exception as exc:
        print(f"  [TCF-005] find_next_eligible_task_in_plan error: {exc}")
        return None


def scan_closed_plan_test_regression(repo_root: "Path | None" = None) -> list[dict]:
    """TC-TCF-005: Detect test regressions in TERMINAL_CLOSED plans.

    Reads the most recent evidence-review.json and checks whether any
    previously-PASS test item is now failing. Returns a (possibly empty) list
    of regression dicts. Never raises — returns [] on any error.
    """
    import json as _json
    from pathlib import Path as _Path

    if repo_root is None:
        repo_root = _Path(__file__).resolve().parent.parent.parent
    else:
        repo_root = _Path(repo_root)

    result: list[dict] = []
    try:
        review_path = repo_root / "reports" / "supervisor" / "evidence-review.json"
        if not review_path.exists():
            return result
        review = _json.loads(review_path.read_text(encoding="utf-8", errors="replace"))
        items = review if isinstance(review, list) else review.get("items", [])
        for item in items:
            if not isinstance(item, dict):
                continue
            grade = str(item.get("grade", "")).upper()
            prev_grade = str(item.get("previous_grade", grade)).upper()
            if prev_grade == "PASS" and grade in ("FAIL", "NEEDS_REWORK"):
                result.append({
                    "item_id": item.get("id") or item.get("work_item_id"),
                    "format": item.get("format"),
                    "grade": grade,
                    "previous_grade": prev_grade,
                    "description": str(item.get("description", ""))[:120],
                })
    except Exception as exc:
        print(f"  [TCF-005] scan_closed_plan_test_regression warning: {exc}")
    return result


def scan_closure_evidence_invalidation(repo_root: "Path | None" = None) -> list[dict]:
    """TC-TCF-005: Find terminal closure records whose evidence is now missing.

    Scans .local/evidences/plan-closures/ for terminal_closure_record.json files
    and checks if the cited plan file still exists. Returns a (possibly empty)
    list of dicts. Never raises — returns [] on any error.
    """
    import json as _json
    from pathlib import Path as _Path

    if repo_root is None:
        repo_root = _Path(__file__).resolve().parent.parent.parent
    else:
        repo_root = _Path(repo_root)

    result: list[dict] = []
    try:
        closures_dir = repo_root / ".local" / "evidences" / "plan-closures"
        if not closures_dir.exists():
            return result
        for record_file in closures_dir.rglob("terminal_closure_record.json"):
            try:
                record = _json.loads(record_file.read_text(encoding="utf-8", errors="replace"))
                plan_path = record.get("plan_path", "")
                plan_exists = _Path(plan_path).exists() if plan_path else False
                open_tcs = record.get("open_taskcards", [])
                if not plan_exists or open_tcs:
                    result.append({
                        "record_file": str(record_file),
                        "plan_path": plan_path,
                        "plan_file_exists": plan_exists,
                        "open_taskcards_in_record": open_tcs,
                        "invalidation_reason": (
                            "plan_file_missing" if not plan_exists
                            else "open_taskcards_in_record"
                        ),
                    })
            except Exception:
                continue
    except Exception as exc:
        print(f"  [TCF-005] scan_closure_evidence_invalidation warning: {exc}")
    return result


def run_sal_audit_checks(repo_root: "Path", continuation_warnings: list) -> None:
    """Run Step 0a-sal and 0a-gap-sal audit checks (extracted from autonomous_cycle.py).

    TC-PGI-045: Extracted to reduce autonomous_cycle.py LOC below baseline_loc_cap.
    Non-blocking — any exception is caught and logged.
    Mutates continuation_warnings in-place when regressions are detected.
    """
    import json as _json
    import re as _re
    import subprocess as _sub
    import sys as _sys

    # Step 0a-sal (FF-DEFERRED-RESOLVE-20260624 TC-D3): SAL-to-QName cross-reference check.
    print("=== STEP 0a-sal: SAL-TO-QNAME CROSS-REFERENCE CHECK ===")
    try:
        _sal_tool = repo_root / "tools" / "audit_sal_to_qname.py"
        _sal_baseline_path = repo_root / "reports" / "sal-qname-baseline.json"
        if _sal_tool.exists():
            _sal_result = _sub.run(
                [_sys.executable, str(_sal_tool)],
                capture_output=True, text=True, timeout=60, cwd=str(repo_root),
            )
            _sal_high_match = _re.search(r"High severity:\s+(\d+)", _sal_result.stdout)
            _sal_high = int(_sal_high_match.group(1)) if _sal_high_match else 0
            _sal_bl_high = 28  # default baseline
            if _sal_baseline_path.exists():
                try:
                    _sal_bl_data = _json.loads(_sal_baseline_path.read_text(encoding="utf-8"))
                    _sal_bl_high = int(_sal_bl_data.get("high_severity_count", 28))
                except Exception:
                    pass
            if _sal_high > _sal_bl_high:
                continuation_warnings.append(
                    f"SAL_QNAME_DANGLING_REFS: {_sal_high} HIGH gaps (baseline {_sal_bl_high})"
                )
                print(f"  WARNING: SAL-QName HIGH gaps increased: {_sal_high} > baseline {_sal_bl_high}")
            else:
                print(f"  SAL-QName audit: {_sal_high} HIGH gaps (baseline: {_sal_bl_high}) — OK")
        else:
            print("  SKIP: tools/audit_sal_to_qname.py not found")
    except Exception as _sal_err:
        print(f"  WARNING: SAL-QName check skipped (non-blocking): {_sal_err}")

    # Step 0a-gap-sal (FF-DEFERRED-RESOLVE-20260624 TC-D4): Gap-ledger SAL traceability check.
    print("=== STEP 0a-gap-sal: GAP-LEDGER SAL TRACEABILITY CHECK ===")
    try:
        _gsal_tool = repo_root / "tools" / "audit_gap_ledger_sal_refs.py"
        _gsal_baseline_path = repo_root / "reports" / "gap-ledger-sal-baseline.json"
        if _gsal_tool.exists():
            _gsal_result = _sub.run(
                [_sys.executable, str(_gsal_tool)],
                capture_output=True, text=True, timeout=60, cwd=str(repo_root),
            )
            _gsal_high_match = _re.search(r"High severity:\s+(\d+)", _gsal_result.stdout)
            _gsal_high = int(_gsal_high_match.group(1)) if _gsal_high_match else 0
            _gsal_bl_high = 0  # default baseline
            if _gsal_baseline_path.exists():
                try:
                    _gsal_bl_data = _json.loads(_gsal_baseline_path.read_text(encoding="utf-8"))
                    _gsal_bl_high = int(_gsal_bl_data.get("high_severity_count", 0))
                except Exception:
                    pass
            if _gsal_high > _gsal_bl_high:
                continuation_warnings.append(
                    f"GAP_LEDGER_SAL_TRACEABILITY: {_gsal_high} HIGH gaps (baseline {_gsal_bl_high})"
                )
                print(f"  WARNING: Gap-ledger SAL HIGH gaps increased: {_gsal_high} > baseline {_gsal_bl_high}")
            else:
                print(f"  Gap-ledger SAL audit: {_gsal_high} HIGH gaps (baseline: {_gsal_bl_high}) — OK")
        else:
            print("  SKIP: tools/audit_gap_ledger_sal_refs.py not found")
    except Exception as _gsal_err:
        print(f"  WARNING: Gap-ledger SAL check skipped (non-blocking): {_gsal_err}")


def run_output_invariant_and_parity_checks(
    declaration_path: "Path | str",
    repo_root: "Path",
) -> list:
    """Run Step 0d (OIC) and 0e (CPF) checks (extracted from autonomous_cycle.py).

    TC-PGI-045: Extracted to reduce autonomous_cycle.py LOC below baseline_loc_cap.
    Non-blocking — any exception is caught and logged.
    Returns a list of rework entry strings (may be empty).
    """
    import json as _json
    from pathlib import Path as _Path

    _OIC_EXPORT_SIGS = [
        "ToJson", "ExportToJson", "ExportToNdjson",
        "ToHtml", "ExportToHtml", "ExportToXml",
        "to_json", "export_json", "to_html", "export_html",
    ]
    _oic_rework_entries: list = []

    # Step 0d (TC-B2): Output Invariant Check (OIC)
    print("=== STEP 0d: OUTPUT INVARIANT CHECK (OIC) ===")
    try:
        import sys as _oic_sys
        _oic_tools = str(_Path(__file__).resolve().parent.parent / "assurance")
        if _oic_tools not in _oic_sys.path:
            _oic_sys.path.insert(0, _oic_tools)
        from output_invariant_checker import OutputInvariantChecker as _OIC  # type: ignore[import]

        _oic_decl_path = _Path(declaration_path)
        _oic_diff = ""
        _oic_decl_raw: dict = {}
        if _oic_decl_path.exists():
            try:
                _oic_decl_raw = _json.loads(_oic_decl_path.read_text(encoding="utf-8"))
                _oic_diff = _oic_decl_raw.get("diff_content", "") or ""
            except Exception:
                pass

        _oic_triggered = any(sig in _oic_diff for sig in _OIC_EXPORT_SIGS)
        if not _oic_triggered:
            print("  [OIC] No JSON/HTML/XML export method changes detected — skipping")
        else:
            print("  [OIC] Export signature detected in diff — running invariant checks")
            _oic = _OIC()
            _oic_results: list = []
            _oic_failures: list = []

            _oic_fixtures_dir = repo_root / "tests" / "assurance" / "fixtures"
            if _oic_fixtures_dir.exists():
                for _oic_fix in sorted(_oic_fixtures_dir.iterdir()):
                    try:
                        _oic_content = _oic_fix.read_text(encoding="utf-8", errors="replace")
                        _oic_ctx = f"fixture:{_oic_fix.name}"
                        if _oic_fix.suffix in (".json", ".ndjson"):
                            for _ln in _oic_content.splitlines():
                                _ln = _ln.strip()
                                if _ln:
                                    _r = _oic.check_json(_ln, _oic_ctx)
                                    _oic_results.append({"context": _oic_ctx, "check": "json", "pass": _r.passed, "detail": _r.error})
                                    if not _r.passed:
                                        _oic_failures.append(f"{_oic_ctx}: {_r.error}")
                        elif _oic_fix.suffix in (".html",):
                            _r = _oic.check_html_cell_safety(_oic_content, _oic_ctx)
                            _oic_results.append({"context": _oic_ctx, "check": "html", "pass": _r.passed, "detail": _r.error})
                            if not _r.passed:
                                _oic_failures.append(f"{_oic_ctx}: {_r.error}")
                        elif _oic_fix.suffix in (".xml", ".fods", ".fodt", ".fodp", ".fodg"):
                            _r = _oic.check_xml(_oic_content, _oic_ctx)
                            _oic_results.append({"context": _oic_ctx, "check": "xml", "pass": _r.passed, "detail": _r.error})
                            if not _r.passed:
                                _oic_failures.append(f"{_oic_ctx}: {_r.error}")
                    except Exception as _oic_fix_err:
                        print(f"  [OIC] WARNING: fixture {_oic_fix.name} error: {_oic_fix_err}")
            else:
                print("  [OIC] No fixtures directory — invariant check skipped")

            import datetime as _oic_dt
            _oic_run_id = _oic_decl_raw.get("run_id", "unknown")
            _oic_report_dir = repo_root / "reports" / "assurance"
            _oic_report_dir.mkdir(parents=True, exist_ok=True)
            _oic_report_path = _oic_report_dir / f"oic-{_oic_run_id}.json"
            _oic_report_path.write_text(
                _json.dumps({
                    "run_id": _oic_run_id,
                    "timestamp": _oic_dt.datetime.utcnow().isoformat() + "Z",
                    "triggered_by": [s for s in _OIC_EXPORT_SIGS if s in _oic_diff],
                    "results": _oic_results,
                    "failures": _oic_failures,
                    "pass": len(_oic_failures) == 0,
                }, indent=2),
                encoding="utf-8",
            )

            if _oic_failures:
                print(f"  [OIC] {len(_oic_failures)} invariant failure(s) — adding to rework_items (non-blocking)")
                for _f in _oic_failures:
                    print(f"    FAIL: {_f}")
                _oic_rework_entries = [f"OIC_INVARIANT_FAIL:{_f}" for _f in _oic_failures]
            else:
                print(f"  [OIC] All {len(_oic_results)} invariant checks PASS")
            print(f"  [OIC] Report: {_oic_report_path}")
    except ImportError:
        print("  [OIC] output_invariant_checker not available — skipping (non-blocking)")
    except Exception as _oic_err:
        print(f"  [OIC] WARNING: OIC step failed ({_oic_err}) — skipping (non-blocking)")

    # Step 0e (TC-C2): Cross-Platform Parity Check
    print("=== STEP 0e: CROSS-PLATFORM PARITY CHECK ===")
    _CPF_TRIGGER_PATHS = ("src/net/csv/", "src/python/csv/")
    try:
        _cpf_decl_path = _Path(declaration_path)
        _cpf_changed: list = []
        if _cpf_decl_path.exists():
            try:
                _cpf_decl = _json.loads(_cpf_decl_path.read_text(encoding="utf-8"))
                _cpf_changed = _cpf_decl.get("changed_files", []) or []
            except Exception:
                pass

        _cpf_triggered = any(
            any(trigger in str(f).replace("\\", "/") for trigger in _CPF_TRIGGER_PATHS)
            for f in _cpf_changed
        )
        if not _cpf_triggered:
            print("  [CPF] No CSV source changes detected — skipping")
        else:
            import sys as _cpf_sys
            _cpf_tools = str(_Path(__file__).resolve().parent.parent / "assurance")
            if _cpf_tools not in _cpf_sys.path:
                _cpf_sys.path.insert(0, _cpf_tools)
            from cross_platform_parity_runner import CrossPlatformParityRunner as _CPF  # type: ignore[import]

            _cpf_fixtures_path = repo_root / "tests" / "cross-platform" / "csv" / "parity-fixtures.yaml"
            if not _cpf_fixtures_path.exists():
                print("  [CPF] No parity fixtures found — skipping")
            else:
                _cpf = _CPF()
                _cpf_fixtures = _cpf.load_fixtures(_cpf_fixtures_path)
                _cpf_results = _cpf.run_all(_cpf_fixtures)
                _cpf_summary = _cpf.summary(_cpf_results)
                print(f"  [CPF] {_cpf_summary['passed']}/{_cpf_summary['total']} fixtures PASS")

                _cpf_report_dir = repo_root / "reports" / "assurance"
                _cpf_report_dir.mkdir(parents=True, exist_ok=True)
                _cpf_run_id = (
                    _json.loads(_cpf_decl_path.read_text(encoding="utf-8")).get("run_id", "unknown")
                    if _cpf_decl_path.exists() else "unknown"
                )
                _cpf_report_path = _cpf_report_dir / f"cross-platform-parity-{_cpf_run_id}.json"
                _cpf_report_path.write_text(
                    _json.dumps({"run_id": _cpf_run_id, "summary": _cpf_summary,
                                 "results": [r.to_dict() for r in _cpf_results]}, indent=2),
                    encoding="utf-8",
                )

                if _cpf_summary["failures"]:
                    print(f"  [CPF] {len(_cpf_summary['failures'])} parity failure(s) — adding to rework_items (non-blocking)")
                    for _cpf_f in _cpf_summary["failures"]:
                        print(f"    FAIL: {_cpf_f['fixture_id']}: {_cpf_f.get('error', '')}")
                    _oic_rework_entries.extend([
                        f"CPF_PARITY_FAIL:{f['fixture_id']}" for f in _cpf_summary["failures"]
                    ])
                print(f"  [CPF] Report: {_cpf_report_path}")
    except ImportError:
        print("  [CPF] cross_platform_parity_runner not available — skipping (non-blocking)")
    except Exception as _cpf_err:
        print(f"  [CPF] WARNING: parity check failed ({_cpf_err}) — skipping (non-blocking)")

    return _oic_rework_entries
