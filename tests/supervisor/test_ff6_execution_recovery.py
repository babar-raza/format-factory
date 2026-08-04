"""
Tests for TC-FF6-EXECUTION-RECOVERY-001: Stage 1 minimal control repair.

Reproduces the four proven control defects blocking an exact, taskcard-owned
FF6 product mutation from moving through authorization, transactional claim,
attempt execution, and continuation selection:

1. product_action_guard.py relies on a hard-coded product source allowlist
   rather than the live taskcard's exact owned source/test paths.
2. action_queue.py provides no atomic claim under concurrent processes and
   no immutable attempt history.
3. autonomous_orchestrator.py stops after a fixed low cycle count instead of
   running UNTIL_BLOCKED by default.
4. run_product_source_patch_bounded's also_modify loop bypasses path
   authorization entirely for secondary targets.
"""
from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))


# ── Defect 1: taskcard-bound authorization for the six FF6 product roots ───

def _write_taskcard(taskcards_dir: Path, task_id: str, status: str, paths_block: str) -> None:
    taskcards_dir.mkdir(parents=True, exist_ok=True)
    (taskcards_dir / f"{task_id}.md").write_text(
        f"---\nstatus: {status}\n---\n\n"
        f"## Exact writable paths\n\n{paths_block}\n\n"
        f"## Forbidden paths\n\n- `src/**`\n",
        encoding="utf-8",
    )


def test_ff6_taskcard_bound_authorization_unlocks_declared_nrrd_path(tmp_path):
    from tools.supervisor import product_action_guard as pag

    taskcards_dir = tmp_path / "taskcards"
    _write_taskcard(
        taskcards_dir, "TC-FF6-NRRD-GOLDEN-SLICE-001", "READY_AFTER_STAGE_1",
        "- `src/python/nrrd/src/format_factory/nrrd/payload.py`\n"
        "- `tests/python/nrrd/test_payload_endian.py`\n",
    )
    assert pag.is_path_authorized_for_task(
        "src/python/nrrd/src/format_factory/nrrd/payload.py",
        "TC-FF6-NRRD-GOLDEN-SLICE-001",
        taskcards_dir=taskcards_dir,
    ) is True


def test_ff6_taskcard_bound_authorization_rejects_undeclared_sibling_path(tmp_path):
    from tools.supervisor import product_action_guard as pag

    taskcards_dir = tmp_path / "taskcards"
    _write_taskcard(
        taskcards_dir, "TC-FF6-NRRD-GOLDEN-SLICE-001", "READY_AFTER_STAGE_1",
        "- `src/python/nrrd/src/format_factory/nrrd/payload.py`\n",
    )
    assert pag.is_path_authorized_for_task(
        "src/python/nrrd/src/format_factory/nrrd/writer.py",
        "TC-FF6-NRRD-GOLDEN-SLICE-001",
        taskcards_dir=taskcards_dir,
    ) is False


def test_ff6_taskcard_bound_authorization_rejects_other_format(tmp_path):
    from tools.supervisor import product_action_guard as pag

    taskcards_dir = tmp_path / "taskcards"
    _write_taskcard(
        taskcards_dir, "TC-FF6-NRRD-GOLDEN-SLICE-001", "READY_AFTER_STAGE_1",
        "- `src/python/nrrd/src/format_factory/nrrd/payload.py`\n",
    )
    assert pag.is_path_authorized_for_task(
        "src/python/safetensors/src/format_factory/safetensors/header.py",
        "TC-FF6-NRRD-GOLDEN-SLICE-001",
        taskcards_dir=taskcards_dir,
    ) is False


def test_ff6_taskcard_bound_authorization_always_rejects_controller_state(tmp_path):
    """Even a taskcard that (incorrectly) declares a controller path never
    authorizes it — controller/registry/promotion paths are fail-closed."""
    from tools.supervisor import product_action_guard as pag

    taskcards_dir = tmp_path / "taskcards"
    _write_taskcard(
        taskcards_dir, "TC-EVIL-001", "READY",
        "- `plans/strategic/ff6/controller-state.yaml`\n",
    )
    assert pag.is_path_authorized_for_task(
        "plans/strategic/ff6/controller-state.yaml",
        "TC-EVIL-001",
        taskcards_dir=taskcards_dir,
    ) is False


def test_ff6_taskcard_bound_authorization_rejects_closed_taskcard(tmp_path):
    from tools.supervisor import product_action_guard as pag

    taskcards_dir = tmp_path / "taskcards"
    _write_taskcard(
        taskcards_dir, "TC-FF6-NRRD-GOLDEN-SLICE-001", "CLOSED",
        "- `src/python/nrrd/src/format_factory/nrrd/payload.py`\n",
    )
    assert pag.is_path_authorized_for_task(
        "src/python/nrrd/src/format_factory/nrrd/payload.py",
        "TC-FF6-NRRD-GOLDEN-SLICE-001",
        taskcards_dir=taskcards_dir,
    ) is False


def test_ff6_taskcard_bound_authorization_accepts_product_paths_heading(tmp_path):
    """Real product taskcards (e.g. TC-FF6-NRRD-GOLDEN-SLICE-001) head this
    section '## Exact writable product paths', not '## Exact writable paths'.
    Both must be recognized."""
    from tools.supervisor import product_action_guard as pag

    taskcards_dir = tmp_path / "taskcards"
    taskcards_dir.mkdir(parents=True)
    (taskcards_dir / "TC-FF6-NRRD-GOLDEN-SLICE-001.md").write_text(
        "---\nstatus: READY\n---\n\n"
        "## Exact writable product paths\n\n"
        "- `src/python/nrrd/src/format_factory/nrrd/codec/payload.py`\n",
        encoding="utf-8",
    )
    assert pag.is_path_authorized_for_task(
        "src/python/nrrd/src/format_factory/nrrd/codec/payload.py",
        "TC-FF6-NRRD-GOLDEN-SLICE-001",
        taskcards_dir=taskcards_dir,
    ) is True


def test_ff6_taskcard_bound_authorization_rejects_path_traversal(tmp_path):
    from tools.supervisor import product_action_guard as pag

    taskcards_dir = tmp_path / "taskcards"
    _write_taskcard(
        taskcards_dir, "TC-EVIL-002", "READY",
        "- `src/python/nrrd/../../../AGENTS.md`\n",
    )
    assert pag.is_path_authorized_for_task(
        "AGENTS.md",
        "TC-EVIL-002",
        taskcards_dir=taskcards_dir,
    ) is False


def test_check_action_unlocks_nrrd_when_task_id_present(tmp_path, monkeypatch):
    from tools.supervisor import product_action_guard as pag

    taskcards_dir = tmp_path / "taskcards"
    _write_taskcard(
        taskcards_dir, "TC-FF6-NRRD-GOLDEN-SLICE-001", "READY_AFTER_STAGE_1",
        "- `src/python/nrrd/src/format_factory/nrrd/payload.py`\n",
    )
    monkeypatch.setattr(pag, "_default_taskcards_dir", lambda: taskcards_dir)

    action = {
        "action_type": "PRODUCT_SOURCE_PATCH_BOUNDED",
        "target_path": "src/python/nrrd/src/format_factory/nrrd/payload.py",
        "task_id": "TC-FF6-NRRD-GOLDEN-SLICE-001",
        "external_gate": False,
    }
    pag.check_action(action)  # must not raise


def test_check_action_still_blocks_nrrd_without_task_id():
    """Legacy behaviour is preserved: no task_id means the hard-coded
    ALLOWED_PRODUCT_SOURCE_PATCH_PATHS list governs, and NRRD is not in it."""
    from tools.supervisor.product_action_guard import check_action, GuardViolation

    action = {
        "action_type": "PRODUCT_SOURCE_PATCH_BOUNDED",
        "target_path": "src/python/nrrd/src/format_factory/nrrd/payload.py",
        "external_gate": False,
    }
    with pytest.raises(GuardViolation):
        check_action(action)


def test_check_action_still_allows_legacy_abw_without_task_id():
    """Regression guard: pre-existing formats keep working unauthenticated."""
    from tools.supervisor.product_action_guard import check_action

    action = {
        "action_type": "PRODUCT_SOURCE_PATCH_BOUNDED",
        "target_path": "src/python/abw/abw_codec.py",
        "external_gate": False,
    }
    check_action(action)  # must not raise


# ── Defect 4: also_modify bypasses path authorization ──────────────────────

def test_also_modify_forbidden_target_is_rejected(tmp_path, monkeypatch):
    from tools.supervisor import product_action_guard as pag

    monkeypatch.setattr(pag, "_repo_root", tmp_path)

    primary = tmp_path / "src" / "python" / "abw" / "abw_codec.py"
    primary.parent.mkdir(parents=True)
    primary.write_text("# primary\n", encoding="utf-8")

    forbidden = tmp_path / "registry" / "format-registry.yaml"
    forbidden.parent.mkdir(parents=True)
    forbidden.write_text("original: true\n", encoding="utf-8")

    action = {
        "action_type": "PRODUCT_SOURCE_PATCH_BOUNDED",
        "target_path": "src/python/abw/abw_codec.py",
        "patch_type": "add_export",
        "patch_code": "X = 1",
        "external_gate": False,
        "also_modify": [
            {"target_path": "registry/format-registry.yaml", "patch_type": "add_export", "patch_code": "X = 1"},
        ],
    }
    result = pag.run_product_source_patch_bounded(action)

    assert result["status"] == "FAILED"
    assert forbidden.read_text(encoding="utf-8") == "original: true\n", (
        "also_modify wrote to a forbidden path without authorization"
    )
    assert primary.read_text(encoding="utf-8") == "# primary\n", (
        "primary target must be rolled back when also_modify is rejected"
    )


def test_also_modify_authorized_target_succeeds(tmp_path, monkeypatch):
    from tools.supervisor import product_action_guard as pag

    monkeypatch.setattr(pag, "_repo_root", tmp_path)

    primary = tmp_path / "src" / "python" / "abw" / "abw_codec.py"
    primary.parent.mkdir(parents=True)
    primary.write_text("# primary\n", encoding="utf-8")

    sibling = tmp_path / "src" / "python" / "abw" / "abw_writer.py"
    sibling.write_text("# sibling\n", encoding="utf-8")

    action = {
        "action_type": "PRODUCT_SOURCE_PATCH_BOUNDED",
        "target_path": "src/python/abw/abw_codec.py",
        "patch_type": "add_export",
        "patch_code": "X = 1",
        "external_gate": False,
        "also_modify": [
            {"target_path": "src/python/abw/abw_writer.py", "patch_type": "add_export", "patch_code": "Y = 2"},
        ],
    }
    result = pag.run_product_source_patch_bounded(action)

    assert result["status"] == "SUCCESS"
    assert "Y = 2" in sibling.read_text(encoding="utf-8")


# ── Defect 2: action_queue.py atomic claim + immutable attempt history ─────

def test_save_queue_uses_atomic_write():
    import inspect
    from tools.supervisor import action_queue as aq

    source = inspect.getsource(aq._save_queue)
    assert "atomic_write_text" in source, (
        "_save_queue must write through atomic_io.atomic_write_text, not Path.write_text"
    )


def test_concurrent_dequeue_never_double_claims(tmp_path, monkeypatch):
    """Five concurrent dequeue_next() callers against a five-item queue must
    each win exactly one distinct item — no item claimed twice."""
    from tools.supervisor import action_queue as aq

    q_path = tmp_path / "action-queue.jsonl"
    monkeypatch.setattr(aq, "QUEUE_PATH", q_path)
    monkeypatch.setattr(aq, "QUEUE_LOCK_PATH", tmp_path / "action-queue.lock")

    for i in range(5):
        aq.enqueue({"action_type": "RUN_JSON_VALIDATION", "target_path": f"f{i}.json"})

    orig_load = aq._load_queue

    def slow_load():
        items = orig_load()
        time.sleep(0.03)
        return items

    monkeypatch.setattr(aq, "_load_queue", slow_load)

    claimed: list = []
    claim_lock = threading.Lock()

    def worker():
        item = aq.dequeue_next()
        if item is not None:
            with claim_lock:
                claimed.append(item["action_id"])

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(claimed) == 5, f"expected 5 successful claims, got {len(claimed)}"
    assert len(claimed) == len(set(claimed)), "duplicate claim detected — dequeue_next is not atomic"


def test_dequeue_appends_immutable_attempt_record(tmp_path, monkeypatch):
    from tools.supervisor import action_queue as aq

    q_path = tmp_path / "action-queue.jsonl"
    attempts_path = tmp_path / "action-queue-attempts.jsonl"
    monkeypatch.setattr(aq, "QUEUE_PATH", q_path)
    monkeypatch.setattr(aq, "QUEUE_LOCK_PATH", tmp_path / "action-queue.lock")
    monkeypatch.setattr(aq, "ATTEMPTS_PATH", attempts_path)

    action_id = aq.enqueue({"action_type": "RUN_JSON_VALIDATION", "target_path": "f.json"})
    aq.dequeue_next()

    assert attempts_path.exists()
    lines = [l for l in attempts_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 1
    import json as _json
    record = _json.loads(lines[0])
    assert record["action_id"] == action_id
    assert "attempt_id" in record and record["attempt_id"]


# ── Defect 3: orchestrator UNTIL_BLOCKED default continuation ──────────────

def test_default_max_cycles_is_unbounded():
    from tools.supervisor.autonomous_orchestrator import AutonomousOrchestrator, DEFAULT_SPRINT_ID

    orch = AutonomousOrchestrator(dry_run=True, sprint_id=DEFAULT_SPRINT_ID)
    assert orch.max_cycles is None, "default max_cycles must be unbounded (UNTIL_BLOCKED), not a fixed cycle count"


def test_cli_default_max_cycles_is_none():
    from tools.supervisor.autonomous_orchestrator import _build_parser

    args = _build_parser().parse_args([])
    assert args.max_cycles is None


def test_explicit_max_cycles_still_honored():
    from tools.supervisor.autonomous_orchestrator import _build_parser

    args = _build_parser().parse_args(["--max-cycles", "7"])
    assert args.max_cycles == 7


def test_watch_flag_removed():
    """--watch was declared but never implemented; C3 requires removing
    unused continuation interfaces rather than shipping dead flags."""
    from tools.supervisor.autonomous_orchestrator import _build_parser

    with pytest.raises(SystemExit):
        _build_parser().parse_args(["--watch"])


def test_stop_after_idle_flag_removed():
    from tools.supervisor.autonomous_orchestrator import _build_parser

    with pytest.raises(SystemExit):
        _build_parser().parse_args(["--stop-after-idle", "2"])


# ── Structural finding (independent review, 2026-08-04): forbidden-action-type
# drift ── product_action_guard, action_queue, continuation_state, and
# backend_selector each independently defined their own "forbidden action
# types" set; backend_selector's had drifted to include PYPI_PUBLISH and
# NUGET_PUBLISH while the other three did not, so a publish action could sit
# in the durable queue as "safe" until reaching backend selection. All four
# now import tools.supervisor.forbidden_actions.TRUE_EXTERNAL_GATE_ACTION_TYPES.

def test_forbidden_action_types_have_a_single_canonical_source():
    from tools.supervisor.forbidden_actions import TRUE_EXTERNAL_GATE_ACTION_TYPES
    from tools.supervisor import action_queue as aq
    from tools.supervisor import continuation_state as cs
    from tools.supervisor import backend_selector as bs
    from tools.supervisor import product_action_guard as pag

    assert aq.FORBIDDEN_IN_QUEUE == TRUE_EXTERNAL_GATE_ACTION_TYPES
    assert bs.FORBIDDEN_ACTION_TYPES == TRUE_EXTERNAL_GATE_ACTION_TYPES
    assert TRUE_EXTERNAL_GATE_ACTION_TYPES <= pag.FORBIDDEN_ACTION_TYPES
    for extra in ("PYPI_PUBLISH", "NUGET_PUBLISH"):
        assert extra in TRUE_EXTERNAL_GATE_ACTION_TYPES
        safe, reason = cs.is_action_safe({"action_type": extra})
        assert safe is False, f"{extra} must be rejected by continuation_state.is_action_safe: {reason}"
        assert extra in aq.FORBIDDEN_IN_QUEUE, f"{extra} must be rejected by action_queue.enqueue"
