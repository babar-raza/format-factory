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
            if sg_data.get("selected_gap_count", 0) > 0:
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
            return {g.get("gap_id", "") for g in sg_data.get("selected_gaps", [])}
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
