"""
sprint_executor.py — Autonomous Loop Actuator for format-factory

Provides the missing "actuator" layer: check_continuation.py and autonomous_cycle.py
produce signals but nothing re-invokes Claude for the next sprint. This tool closes that
gap with a run-loop subcommand that calls `claude --print --dangerously-skip-permissions`
as a subprocess (same pattern as aspose.org sprint_loop.py).

Subcommands:
  inject-declaration <sprint_id>   Pre-create skeleton evidence-declaration.yaml
  run-sprint <sprint_id>           Invoke claude --print headlessly, capture output
  run-loop [--max-cycles N]        Full autonomous cycle loop (check → sprint → closeout → repeat)
  build-review-package             Wrapper for build_declaration_review_package.py
  status                           Print current continuation signal as JSON

Exit codes:
  0  — success / loop completed normally
  1  — hard stop or external gate
  2  — claude CLI not found (run-sprint/run-loop only)
  9  — unexpected error

Usage:
  python tools/supervisor/sprint_executor.py inject-declaration sprint-20260616-abc1234
  python tools/supervisor/sprint_executor.py status
  python tools/supervisor/sprint_executor.py run-loop --max-cycles 3
  python tools/supervisor/sprint_executor.py build-review-package --declaration .local/evidences/.../evidence-declaration.yaml
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent

# Coordination plane integration (TC-SWB-004)
try:
    import sys as _sys_cw
    _sys_cw.path.insert(0, str(_HERE))
    from coordination.coordinated_io import coordinated_write as _coordinated_write
except ImportError:
    from contextlib import contextmanager as _cm_fallback
    @_cm_fallback
    def _coordinated_write(path, **kw):
        yield

# Required fields from evidence-declaration.schema.json
_REQUIRED_FIELDS = [
    "run_id", "sprint_id", "evidence_root",
    "start_time", "end_time",
    "git_head_start", "git_head_end", "git_status_final",
    "declared_scope",
    "planned_work_items", "completed_work_items", "incomplete_work_items",
    "changed_files", "tests_run", "test_results",
    "evidence_artifacts", "reports_created",
    "worker_self_verdict", "worker_self_grade",
    "next_recommended_work",
]

_TRUE_EXTERNAL_GATES = {
    "EXTERNAL_GATE",
    "NO_EXTERNAL_GATE",
    "GATE_11_APPROVAL",
    "GIT_PUSH_CREDENTIALS",
    "PUBLICATION_CREDENTIALS",
}

# TC-EXT-010-02: Structural GOV_BLOCK stops are NOT TRUE_EXTERNAL_GATEs (the agent
# CAN resolve them by running the analytics-separation sprint — see CLAUDE.md's
# "GOV_BLOCK Exception" section) — but they are still NON-OVERRIDABLE by the
# Supreme Directive's generic "log exit 3 and continue" rule. Before this set
# existed, _is_external_gate() returned False for this reason and the loop fell
# through to the generic override branch below, silently proceeding past a
# structural failure. See tools/supervisor/governance_block_registry.py and
# check_continuation.py's "Check 8" for the detection logic this halts on.
_NON_OVERRIDABLE_STRUCTURAL_STOPS = {
    "STRUCTURAL_GOVBLOCK_MUST_BE_RESOLVED_FIRST",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _git(args: list[str], *, cwd: Path = _REPO) -> str:
    """Run a git command and return stdout stripped. Returns '' on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write(path: Path, text: str) -> None:
    """Write atomically: tmp → fsync → os.replace()."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        data = text.encode("utf-8")
        with open(tmp, "wb") as tmp_fd:
            tmp_fd.write(data)
            try:
                os.fsync(tmp_fd.fileno())
            except OSError:
                pass  # fsync best-effort on Windows
        os.replace(str(tmp), str(path))
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _db_path() -> Path:
    """Return absolute path to control-index.db."""
    return _REPO / ".local" / "supervisor" / "control-index.db"


def _get_session_id() -> str:
    """Return current session identity."""
    try:
        sys.path.insert(0, str(_HERE))
        from continuation_identity import get_or_create_session_identity  # type: ignore[import]
        return get_or_create_session_identity(_REPO)["session_id"]
    except Exception:
        import socket
        return f"{socket.gethostname()}-{os.getpid()}"


def _load_continuation_signal(repo_root: Path) -> dict | None:
    p = repo_root / ".local" / "supervisor" / "continuation-signal.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _check_continuation(repo_root: Path) -> dict:
    """Run check_continuation.py and return parsed output dict."""
    result = subprocess.run(
        [sys.executable,
         str(repo_root / "tools" / "supervisor" / "check_continuation.py"),
         "--repo-root", str(repo_root)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    try:
        data = json.loads(result.stdout)
    except Exception:
        data = {
            "verdict": "STOP",
            "reason": "PARSE_ERROR",
            "detail": result.stdout[:500] or result.stderr[:500],
        }
    data["_exit_code"] = result.returncode
    return data


def _is_external_gate(stop_reason: str) -> bool:
    """Return True if stop_reason represents a TRUE_EXTERNAL_GATE."""
    if not stop_reason:
        return False
    upper = stop_reason.upper()
    if any(gate in upper for gate in _TRUE_EXTERNAL_GATES):
        return True
    # Git push and package pub blockers are external gates
    external_markers = ["GIT_PUSH", "PUSH_CREDENTIALS", "PYPI", "NUGET", "GATE_11"]
    return any(m in upper for m in external_markers)


def _is_structural_govblock_stop(stop_reason: str) -> bool:
    """Return True if stop_reason is the non-overridable structural GOV_BLOCK stop.

    TC-EXT-010-02: Unlike _is_external_gate(), this is NOT a TRUE_EXTERNAL_GATE —
    the agent CAN resolve it autonomously by running the analytics-separation
    sprint (CLAUDE.md's "GOV_BLOCK Exception"). But sprint_executor.py's run-loop
    has no logic to autonomously select and execute that separation sprint, so it
    must halt here rather than silently overriding and reading next-sprint.md as
    if this were an ordinary advisory stop.
    """
    if not stop_reason:
        return False
    return stop_reason.strip().upper() in _NON_OVERRIDABLE_STRUCTURAL_STOPS


# ---------------------------------------------------------------------------
# inject-declaration
# ---------------------------------------------------------------------------

def cmd_inject_declaration(sprint_id: str, repo_root: Path) -> Path:
    """
    Pre-create a skeleton evidence-declaration.yaml for the given sprint_id.
    All 21 required fields are present with empty/default values.
    The worker (Claude) fills in the specifics after completing the sprint.

    Returns the path to the created skeleton file.
    """
    git_head = _git(["rev-parse", "HEAD"], cwd=repo_root) or "unknown"
    short_sha = git_head[:7] if git_head != "unknown" else "unknown"
    git_status = _git(["status", "--short"], cwd=repo_root) or ""
    now = _now_iso()

    run_id = f"{sprint_id}-{short_sha}"
    evidence_root = f".local/evidences/{run_id}/"
    evidence_dir = repo_root / ".local" / "evidences" / run_id
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Read next-sprint.md to extract scope hint
    next_sprint_path = repo_root / "reports" / "supervisor" / "next-sprint.md"
    declared_scope = "Execute next sprint from reports/supervisor/next-sprint.md"
    if next_sprint_path.exists():
        first_lines = next_sprint_path.read_text(encoding="utf-8")[:400].strip()
        # Use first non-empty heading or first line
        for line in first_lines.splitlines():
            line = line.strip().lstrip("#").strip()
            if line:
                declared_scope = line[:200]
                break

    skeleton = {
        "run_id": run_id,
        "sprint_id": sprint_id,
        "evidence_root": evidence_root,
        "start_time": now,
        "end_time": now,  # worker updates this at end
        "git_head_start": git_head,
        "git_head_end": git_head,  # worker updates after work
        "git_status_final": git_status,
        "declared_scope": declared_scope,
        "planned_work_items": [],     # worker fills these in
        "completed_work_items": [],   # list of item_id strings
        "incomplete_work_items": [],
        "changed_files": [],
        "tests_run": 0,
        "test_results": {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
        },
        "evidence_artifacts": [],
        "reports_created": [],
        "worker_self_verdict": "PENDING — fill in after sprint execution",
        "worker_self_grade": "PASS",
        "next_recommended_work": [],
        # Optional but commonly used
        "known_limitations": [],
        "external_gates": [],
    }

    declaration_path = evidence_dir / "evidence-declaration.yaml"
    with _coordinated_write(declaration_path, op="inject_declaration", source="sprint_executor"):
        _atomic_write(declaration_path, yaml.dump(skeleton, default_flow_style=False, sort_keys=False))

    abs_path = declaration_path.resolve()
    print(f"Skeleton declaration created: {abs_path}")
    print(f"Run ID: {run_id}")
    print(f"Evidence root: {evidence_dir.resolve()}")
    print()
    print("Next steps:")
    print("  1. Execute the sprint tasks from reports/supervisor/next-sprint.md")
    print("  2. Edit the declaration to record what you did")
    print(f"  3. Run: python tools/supervisor/autonomous_cycle.py --declaration {abs_path}")
    return declaration_path


# ---------------------------------------------------------------------------
# build-review-package
# ---------------------------------------------------------------------------

def cmd_build_review_package(declaration_path: Path, repo_root: Path) -> int:
    """Wrapper around build_declaration_review_package.py. Prints abs path + SHA-256."""
    builder = repo_root / "tools" / "supervisor" / "build_declaration_review_package.py"
    if not builder.exists():
        print(f"ERROR: build_declaration_review_package.py not found at {builder}", file=sys.stderr)
        return 9

    result = subprocess.run(
        [sys.executable, str(builder), "--declaration", str(declaration_path.resolve()),
         "--repo-root", str(repo_root)],
        capture_output=False,  # let stdout/stderr pass through
        timeout=120,
    )

    # Compute SHA-256 of the output ZIP if we can find it
    try:
        with open(declaration_path, encoding="utf-8") as f:
            decl = yaml.safe_load(f)
        run_id = decl.get("run_id", "unknown")
        zip_path = repo_root / ".local" / "supervisor" / "reviews" / run_id / "declaration-review-package.zip"
        if zip_path.exists():
            sha = _sha256(zip_path)
            abs_zip = zip_path.resolve()
            print(f"\nAbsolute path: {abs_zip}")
            print(f"SHA-256: {sha}")
    except Exception:
        pass

    return result.returncode


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

def cmd_status(repo_root: Path) -> int:
    signal = _load_continuation_signal(repo_root)
    if signal is None:
        print(json.dumps({"error": "continuation-signal.json not found"}, indent=2))
        return 1

    # Enrich with check_continuation verdict
    cont = _check_continuation(repo_root)
    output = {
        "continuation_signal": signal,
        "check_continuation": cont,
        "verdict": cont.get("verdict", "UNKNOWN"),
    }
    print(json.dumps(output, indent=2))
    return 0  # status is a read-only reporter; verdict is in the JSON output


# ---------------------------------------------------------------------------
# run-sprint (headless)
# ---------------------------------------------------------------------------

# SFC-GAP-E (2026-07-17): conservative, BOUNDED fallback path scope when no
# specific skill resolves for a sprint's free-text prompt. Deliberately NOT
# unbounded ("**") -- still excludes runtime/build/vcs internals implicitly
# (they are not repo-tracked source lanes) -- but honest about being a
# fallback, not a precisely-scoped grant. Tightening this via
# next-work-items.json's own lane/path structure is a named follow-up
# (tracked in skill-only-policy.yaml known_gaps), not a silently accepted gap.
_FALLBACK_LANE_PATHS = [
    "src/", "tools/", "tests/", "docs/", "registry/", "reports/",
    ".supervisor/", "plans/",
]


def _resolve_sprint_scope(prompt_text: str, repo_root: Path):
    """Best-effort skill resolution for a run-loop sprint's prompt text.

    Returns (selected_skill_ids, allowed_paths, resolution_decision, rationale).

    Honest limitation: next-sprint.md is free-form prose, not a structured
    operation description, so the derived operation string (first non-blank
    line, truncated) is a heuristic -- it can under- or over-resolve relative
    to a hand-authored operation description. When no specific skill resolves
    (or the resolved skill declares no paths of its own), this binds the
    manifest to `autonomous-loop` -- the skill that legitimately governs "an
    autonomous sprint is being executed," not a loosely-related pick -- with
    the conservative fallback scope above, explicitly tagged as a fallback so
    it is never mistaken for a precise grant.
    """
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from tools.governance.skills_first import resolve as sfc_resolve
    from tools.governance.skills_first.registries import load_skills

    first_line = next(
        (ln.strip() for ln in prompt_text.splitlines() if ln.strip()), "")
    operation = first_line[:200]

    try:
        res = sfc_resolve.resolve(operation)
    except Exception:
        res = {"verdict": "MISSING_SKILL_CAPABILITY"}

    if res.get("verdict") == "RESOLVED" and res.get("selected_skill_id"):
        skills = {s.skill_id: s for s in load_skills()}
        sid = res["selected_skill_id"]
        s = skills.get(sid)
        paths = (list(s.allowed_paths) + list(s.implementation_paths)) if s else []
        if paths:
            return ([sid], paths, res.get("resolution_decision", "REUSE_EXACT_MATCH"),
                    f"resolved from sprint prompt heading: {res.get('rationale', '')}")

    return (
        ["autonomous-loop"], list(_FALLBACK_LANE_PATHS), "REUSE_EXACT_MATCH",
        "FALLBACK: no specific skill resolved for this sprint's free-text "
        "prompt (or the resolved skill declared no paths); bound to "
        "autonomous-loop (the skill that legitimately governs autonomous "
        "sprint execution) with a conservative, bounded lane-wide scope. "
        "Tightening this via next-work-items.json's own lane structure is a "
        "tracked follow-up (skill-only-policy.yaml known_gaps), not a "
        "silent gap.",
    )


def _expand_scope_paths(repo_root: Path, patterns: list) -> list:
    """Expand allowed_paths patterns (literal dirs/files or globs) to a list
    of actual on-disk file Paths, scoped ONLY to these patterns -- never the
    whole repo. This narrow scoping is what makes a before/after hash diff
    sound under concurrency (unlike a git-diff over a 30-minute window across
    a tree 44+ other agents are simultaneously mutating): the compared
    surface is exactly the small set of paths this sprint was authorized to
    touch, not everything anyone touched anywhere in the interval."""
    files = []
    for pat in patterns:
        norm = pat.rstrip("/")
        if any(c in pat for c in "*?["):
            files.extend(p for p in repo_root.glob(pat) if p.is_file())
            continue
        p = repo_root / norm
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files.extend(q for q in p.rglob("*") if q.is_file())
    return files


def _hash_snapshot(repo_root: Path, patterns: list) -> dict:
    """sha256 of every file currently within `patterns` (see
    _expand_scope_paths). Unlike a git-commit-range diff, this sees
    uncommitted working-tree changes directly -- the sprint's own edits don't
    need to be committed to be detected."""
    out = {}
    for f in _expand_scope_paths(repo_root, patterns):
        try:
            out[f.relative_to(repo_root).as_posix()] = hashlib.sha256(
                f.read_bytes()).hexdigest()
        except OSError:
            continue
    return out


def _diff_snapshots(before: dict, after: dict) -> list:
    changed = set(before) ^ set(after)  # added or removed
    changed |= {k for k in before if k in after and before[k] != after[k]}
    return sorted(changed)


def cmd_run_sprint(sprint_id: str, repo_root: Path, *, dry_run: bool = False) -> dict:
    """
    Invoke `claude --print --dangerously-skip-permissions` with next-sprint.md as the prompt.
    Captures output to evidence dir.

    Returns dict with keys: exit_code, declaration_path, output_path
    """
    # 1. Inject skeleton declaration
    declaration_path = cmd_inject_declaration(sprint_id, repo_root)

    # 2. Read next-sprint.md
    next_sprint_path = repo_root / "reports" / "supervisor" / "next-sprint.md"
    if not next_sprint_path.exists():
        print(f"ERROR: next-sprint.md not found at {next_sprint_path}", file=sys.stderr)
        return {"exit_code": 9, "declaration_path": str(declaration_path)}

    prompt_text = next_sprint_path.read_text(encoding="utf-8")

    # 3. Append declaration path hint to prompt so Claude knows where to write evidence
    abs_decl = declaration_path.resolve()
    prompt_text += (
        f"\n\n---\n"
        f"DECLARATION SKELETON PRE-CREATED: {abs_decl}\n"
        f"Fill this file in after executing the sprint. "
        f"Then run: python tools/supervisor/autonomous_cycle.py --declaration {abs_decl}\n"
    )

    # Write prompt to temp file so we can pass it via @file syntax
    with open(declaration_path.parent / "sprint-prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt_text)

    output_path = declaration_path.parent / "sprint-output.txt"

    if dry_run:
        print("[DRY RUN] Would invoke: claude --print --dangerously-skip-permissions -p <next-sprint.md>")
        print(f"Declaration skeleton: {abs_decl}")
        print(f"Output would be written to: {output_path.resolve()}")
        return {"exit_code": 0, "declaration_path": str(abs_decl), "dry_run": True}

    # SFC-GAP-E (2026-07-17): bind an execution manifest to this sprint
    # BEFORE spawning the skip-permissions child. The orchestrator (this
    # trusted process) resolves scope on the untrusted child's behalf -- the
    # child is never trusted to self-govern. A manifest-creation failure is
    # logged and non-blocking (the sprint still runs; it simply proceeds
    # without SFC governance for this run, exactly as it did before this
    # change -- never worse than today, only sometimes not-yet-better).
    manifest_execution_id = None
    allowed_paths: list = []
    pre_snapshot: dict = {}
    try:
        from tools.governance.skills_first.manifest import create_manifest
        skill_ids, allowed_paths, decision, rationale = _resolve_sprint_scope(
            prompt_text, repo_root)
        sfc_manifest = create_manifest(
            task_id=sprint_id, agent_type="LOCAL_AUTOMATION",
            requested_operation=f"autonomous sprint: {sprint_id}",
            selected_skill_ids=skill_ids, allowed_paths=allowed_paths,
            resolution_decision=decision, resolution_rationale=rationale,
            mission_id="AUTONOMOUS_LOOP", sprint_id=sprint_id, write=True)
        manifest_execution_id = sfc_manifest["execution_id"]
        (declaration_path.parent / "sfc-manifest-id.txt").write_text(
            manifest_execution_id, encoding="utf-8")
        pre_snapshot = _hash_snapshot(repo_root, allowed_paths)
        print(f"  SFC manifest: {manifest_execution_id} "
              f"(skills={skill_ids}, scope={len(allowed_paths)} path(s))")
    except Exception as exc:
        print(f"WARNING: SFC manifest creation failed (non-blocking; sprint "
              f"proceeds without governance for this run): {exc}",
              file=sys.stderr)

    # 4. Invoke claude
    print(f"Invoking claude CLI for sprint: {sprint_id}")
    print(f"Output: {output_path.resolve()}")
    try:
        result = subprocess.run(
            ["claude", "--print", "--dangerously-skip-permissions", "-p", prompt_text],
            capture_output=True,
            text=True,
            timeout=1800,  # 30 min max per sprint
            cwd=str(repo_root),
        )
    except FileNotFoundError:
        print(
            "ERROR: 'claude' CLI not found in PATH.\n"
            "Install it with: npm install -g @anthropic-ai/claude-code\n"
            "Or run /autonomous-loop in VSCode instead.",
            file=sys.stderr,
        )
        return {"exit_code": 2, "declaration_path": str(abs_decl)}
    except subprocess.TimeoutExpired:
        print("ERROR: claude CLI timed out after 30 minutes", file=sys.stderr)
        return {"exit_code": 9, "declaration_path": str(abs_decl)}

    # 5. Save output
    _atomic_write(output_path, result.stdout + "\n\n--- STDERR ---\n" + result.stderr)
    print(f"Claude exit code: {result.returncode}")
    print(f"Output saved to: {output_path.resolve()}")

    # SFC-GAP-E: independently-computed changed-files list, scoped ONLY to
    # this manifest's own allowed_paths -- never the whole repo -- so
    # concurrent unrelated agents' writes elsewhere in the shared tree cannot
    # pollute this sprint's own change set (the flaw a git-diff-over-30-
    # minutes approach would have had). Sees uncommitted edits directly.
    if manifest_execution_id is not None:
        try:
            post_snapshot = _hash_snapshot(repo_root, allowed_paths)
            changed_files = _diff_snapshots(pre_snapshot, post_snapshot)
            (declaration_path.parent / "sfc-changed-files.json").write_text(
                json.dumps(changed_files), encoding="utf-8")
            print(f"  SFC changed-files (scoped, independent): "
                  f"{len(changed_files)} file(s)")
        except Exception as exc:
            print(f"WARNING: SFC post-run snapshot failed (non-blocking): "
                  f"{exc}", file=sys.stderr)

    return {
        "exit_code": result.returncode,
        "declaration_path": str(abs_decl),
        "output_path": str(output_path.resolve()),
        "sfc_manifest_execution_id": manifest_execution_id,
    }


# ---------------------------------------------------------------------------
# run-loop
# ---------------------------------------------------------------------------

def cmd_run_loop(repo_root: Path, *, max_cycles: int = 12, dry_run: bool = False) -> int:
    """
    Full autonomous loop:
      1. check_continuation → if STOP & external gate → exit 1
      2. inject-declaration
      3. run-sprint (claude --print) — skipped if dry_run
      4. run autonomous_cycle.py closeout
      5. Repeat until STOP or max_cycles

    CLAUDE.md Supreme Directive: max_cycles is NOT a hard stop —
    when reached, log it and continue (governed rollover, matching autonomous_cycle.py behaviour).
    """
    # ── MISSION LOCK: acquire before any work begins (TC-CONC-007) ────────
    MISSION_ID = "format-factory-main"
    _lock_cm = None
    try:
        from concurrency.mission_lock import MissionLock  # type: ignore[import]
        from concurrency.errors import MissionLockConflict  # type: ignore[import]
        try:
            _branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])
        except Exception:
            _branch = "unknown"
        _session_id = _get_session_id()
        _ml = MissionLock(db_path=_db_path())
        _lock_cm = _ml.locked(
            mission_id=MISSION_ID,
            controller_type="headless",
            session_id=_session_id,
            branch=_branch,
        )
        _lock_cm.__enter__()
    except Exception as _lock_err:
        if "MissionLockConflict" in type(_lock_err).__name__:
            import sys as _sys
            print(
                f"\nBLOCKED: Mission '{MISSION_ID}' is locked by another controller.\n"
                f"Cannot start headless run-loop while another controller is active.\n"
                f"Run 'python tools/supervisor/sprint_executor.py status' for details.",
                file=_sys.stderr,
            )
            return 1
        # TC-COORD-008: non-conflict lock errors are FATAL by default. The
        # prior fail-open here is how two controllers ended up sharing one
        # working tree (R1227). FF_COORDINATION_SOFT=1 restores the old
        # behaviour for degraded environments -- the softening is explicit
        # and visible, never silent.
        import os as _os
        if _os.environ.get("FF_COORDINATION_SOFT") == "1":
            print(f"[MissionLock] Warning: lock not acquired ({_lock_err})."
                  f" Proceeding without lock (FF_COORDINATION_SOFT=1).")
            _lock_cm = None
        else:
            import sys as _sys
            print(
                f"\nBLOCKED: mission lock could not be acquired ({_lock_err}).\n"
                f"Refusing to run unlocked (two controllers on one tree lost"
                f" work before -- GAP-MA-006).\n"
                f"Set FF_COORDINATION_SOFT=1 to override explicitly.",
                file=_sys.stderr,
            )
            return 1
    # ──────────────────────────────────────────────────────────────────────

    cycle = 0
    autonomous_cycle = repo_root / "tools" / "supervisor" / "autonomous_cycle.py"

    try:
      while True:
        cycle += 1
        print(f"\n{'='*60}")
        print(f"AUTONOMOUS LOOP — Cycle {cycle}")
        print(f"{'='*60}")

        # --- Step 1: Check continuation ---
        print("\n[Step 1] Checking continuation signal...")
        cont = _check_continuation(repo_root)
        verdict = cont.get("verdict", "STOP")
        print(json.dumps(cont, indent=2))

        if verdict == "STOP":
            reason = cont.get("reason", "")
            if _is_external_gate(reason):
                print(f"\nHARD STOP: TRUE_EXTERNAL_GATE — {reason}")
                print("This requires human action. Stopping.")
                return 1
            elif _is_structural_govblock_stop(reason):
                # TC-EXT-010-02: non-overridable structural GOV_BLOCK. Not a
                # TRUE_EXTERNAL_GATE, but the generic "log exit 3 and continue"
                # Supreme Directive override does NOT apply — see CLAUDE.md's
                # "GOV_BLOCK Exception" section.
                print(f"\nHARD STOP: structural GOV_BLOCK — {reason}")
                print("This is NOT a TRUE_EXTERNAL_GATE, but it IS non-overridable per")
                print("CLAUDE.md's 'GOV_BLOCK Exception' section. The Supreme Directive's")
                print("generic override does not apply to structural GOV_BLOCKs.")
                print("The NEXT sprint must be the analytics-separation refactor for the")
                print("blocking format (docs/code-quality/production-library-standard-v2.md")
                print("§8.1) before product deepening may resume. Stopping this loop.")
                return 1
            else:
                # Supreme Directive: non-external-gate stops are overridden
                print(f"\nNOTE: check_continuation returned STOP ({reason}) — not an external gate.")
                print("Supreme Directive: overriding, reading next-sprint.md directly.")
                next_sprint_path = repo_root / "reports" / "supervisor" / "next-sprint.md"
                if not next_sprint_path.exists():
                    print("ERROR: next-sprint.md not found and no continuation signal. Cannot proceed.")
                    return 1

        # Max cycles: governed rollover (not a hard stop)
        iteration = cont.get("iteration", 0)
        max_iterations = cont.get("max_iterations", 12)
        if cycle > max_cycles:
            print(f"\nNOTE: cycle {cycle} > max_cycles {max_cycles} — governed rollover, continuing.")
            # Reset signal iteration if possible
            sig_path = repo_root / ".local" / "supervisor" / "continuation-signal.json"
            if sig_path.exists():
                try:
                    sig = json.loads(sig_path.read_text(encoding="utf-8"))
                    sig["iteration"] = 0
                    with _coordinated_write(sig_path, op="signal_reset", source="sprint_executor"):
                        _atomic_write(sig_path, json.dumps(sig, indent=2))
                    print("Iteration counter reset to 0.")
                except Exception as e:
                    print(f"Could not reset iteration: {e}")

        # --- Step 2+3: Run sprint ---
        now = datetime.now(timezone.utc)
        sprint_id = f"autonomous-loop-{now.strftime('%Y%m%d-%H%M%S')}"
        print(f"\n[Step 2+3] Running sprint: {sprint_id}")
        sprint_result = cmd_run_sprint(sprint_id, repo_root, dry_run=dry_run)

        if sprint_result.get("exit_code", 9) == 2:
            print("\nClaude CLI not available. Cannot run headlessly.")
            print("Use /autonomous-loop in VSCode for interactive execution.")
            return 2

        if dry_run:
            print("\n[DRY RUN] Skipping closeout step.")
            print("Run without --dry-run to execute the full loop.")
            return 0

        # --- Step 4: Closeout via autonomous_cycle.py ---
        declaration_path = sprint_result.get("declaration_path")
        if declaration_path and Path(declaration_path).exists():
            print("\n[Step 4] Running closeout: autonomous_cycle.py")
            closeout = subprocess.run(
                [sys.executable, str(autonomous_cycle),
                 "--declaration", declaration_path,
                 "--repo-root", str(repo_root)],
                capture_output=False,
                timeout=300,
                cwd=str(repo_root),
            )
            closeout_exit = closeout.returncode
            print(f"Closeout exit code: {closeout_exit}")

            if closeout_exit not in (0, 3):
                print(f"NOTE: Closeout returned {closeout_exit} — logging and continuing (Supreme Directive).")

            # Build review package (best-effort)
            try:
                cmd_build_review_package(Path(declaration_path), repo_root)
            except Exception as e:
                print(f"Review package build failed (non-blocking): {e}")
        else:
            print("\nNOTE: No declaration path from run-sprint. Closeout skipped.")

        # ── PRE-SPRINT CHECKPOINT (TC-CONC-007) ──────────────────────────
        sprint_ckpt_id = f"autonomous-loop-{now.strftime('%Y%m%d-%H%M%S')}"
        try:
            from concurrency.checkpoint import CheckpointManager  # type: ignore[import]
            _ckpt = CheckpointManager(db_path=_db_path(), repo_root=repo_root)
            _cid = _ckpt.create(
                task_id=sprint_ckpt_id,
                worker_id="sprint_executor_headless",
                description="pre-sprint working-tree snapshot",
            )
            print(f"[Checkpoint] Working-tree state saved: {_cid}")
        except Exception as _ckpt_err:
            print(f"[Checkpoint] Warning: checkpoint creation failed (non-blocking): {_ckpt_err}")
        # ─────────────────────────────────────────────────────────────────

        print(f"\nCycle {cycle} complete.")
    finally:
        if _lock_cm is not None:
            try:
                _lock_cm.__exit__(None, None, None)
            except Exception:
                pass

    # Unreachable — loop exits via return statements above
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Autonomous loop actuator — the missing run-loop for format-factory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--repo-root", type=Path, default=_REPO,
                        help="Repository root (default: auto-detected)")

    sub = parser.add_subparsers(dest="command", required=True)

    # inject-declaration
    p_inj = sub.add_parser("inject-declaration",
                            help="Pre-create skeleton evidence-declaration.yaml")
    p_inj.add_argument("sprint_id", help="Sprint ID (e.g. product-deepening-sprint12-20260616)")

    # status
    sub.add_parser("status", help="Print current continuation signal")

    # build-review-package
    p_pkg = sub.add_parser("build-review-package",
                            help="Build declaration review ZIP (wrapper)")
    p_pkg.add_argument("--declaration", type=Path, required=True,
                       help="Path to evidence-declaration.yaml")

    # run-sprint
    p_run = sub.add_parser("run-sprint",
                            help="Invoke claude --print headlessly for one sprint")
    p_run.add_argument("sprint_id", help="Sprint ID")
    p_run.add_argument("--dry-run", action="store_true",
                       help="Show what would happen without invoking claude")

    # run-loop
    p_loop = sub.add_parser("run-loop",
                             help="Full autonomous loop (check → sprint → closeout → repeat)")
    p_loop.add_argument("--max-cycles", type=int, default=12,
                        help="Max loop cycles before governed rollover (default: 12)")
    p_loop.add_argument("--dry-run", action="store_true",
                        help="Run checks and inject-declaration without invoking claude")

    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    if args.command == "inject-declaration":
        cmd_inject_declaration(args.sprint_id, repo_root)
        return 0

    elif args.command == "status":
        return cmd_status(repo_root)

    elif args.command == "build-review-package":
        decl = args.declaration
        if not decl.is_absolute():
            decl = Path.cwd() / decl
        return cmd_build_review_package(decl, repo_root)

    elif args.command == "run-sprint":
        result = cmd_run_sprint(args.sprint_id, repo_root, dry_run=args.dry_run)
        return result.get("exit_code", 0)

    elif args.command == "run-loop":
        return cmd_run_loop(repo_root, max_cycles=args.max_cycles, dry_run=args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
