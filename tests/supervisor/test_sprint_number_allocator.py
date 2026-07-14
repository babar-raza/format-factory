"""Tests for sprint_number_allocator.py.

TC-SRB-022: Idempotency and correctness tests
TC-SRB-023: Concurrent allocation safety pilot
TC-SRB-024: Interrupted allocation recovery test

Covers:
  TC-SRB-022-01  same alias → same number (ALREADY_ALLOCATED, exit 2)
  TC-SRB-022-02  different alias → next number (ALLOCATED, incremented)
  TC-SRB-022-03  ledger entry count increments correctly
  TC-SRB-022-04  no stale .tmp file remains after successful allocation
  TC-SRB-023     concurrent allocations are monotonic, no duplicates
  TC-SRB-024     orphaned .tmp file is recovered correctly
"""
from __future__ import annotations

import json
import sys
import threading
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from sprint_number_allocator import (
    allocate_sprint_number,
    find_existing_allocation,
    find_highest_number,
    load_ledger,
    recover_sprint,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ledger(tmp_path: Path) -> Path:
    """Return ledger path inside tmp_path."""
    lp = tmp_path / ".local" / "supervisor" / "sprint-ledger.json"
    lp.parent.mkdir(parents=True, exist_ok=True)
    return lp


def _receipts(tmp_path: Path) -> Path:
    rd = tmp_path / ".local" / "supervisor" / "sprint-receipts"
    rd.mkdir(parents=True, exist_ok=True)
    return rd


# ---------------------------------------------------------------------------
# TC-SRB-022-01  Same alias → same number (idempotency)
# ---------------------------------------------------------------------------


def test_same_alias_returns_already_allocated(tmp_path: Path) -> None:
    """TC-SRB-022-01: Calling allocate twice with same alias → ALREADY_ALLOCATED."""
    lp = _ledger(tmp_path)
    rd = _receipts(tmp_path)

    r1 = allocate_sprint_number("alpha-scout", ledger_path=lp, receipts_dir=rd)
    r2 = allocate_sprint_number("alpha-scout", ledger_path=lp, receipts_dir=rd)

    assert r1["verdict"] == "ALLOCATED"
    assert r2["verdict"] == "ALREADY_ALLOCATED"
    assert r1["sprint_number"] == r2["sprint_number"], "must return same number on repeat call"
    assert r1["sprint_id"] == r2["sprint_id"]


# ---------------------------------------------------------------------------
# TC-SRB-022-02  Different alias → next number
# ---------------------------------------------------------------------------


def test_different_alias_gets_next_number(tmp_path: Path) -> None:
    """TC-SRB-022-02: A different alias allocates the next sequential number."""
    lp = _ledger(tmp_path)
    rd = _receipts(tmp_path)

    r1 = allocate_sprint_number("first-alias", ledger_path=lp, receipts_dir=rd)
    r2 = allocate_sprint_number("second-alias", ledger_path=lp, receipts_dir=rd)

    assert r1["verdict"] == "ALLOCATED"
    assert r2["verdict"] == "ALLOCATED"
    assert r2["sprint_number"] == r1["sprint_number"] + 1, "must be strictly monotonic"
    assert r2["sprint_id"] == f"SPRINT-{r2['sprint_number']:05d}"


# ---------------------------------------------------------------------------
# TC-SRB-022-03  Ledger entry count increments correctly
# ---------------------------------------------------------------------------


def test_ledger_entry_count_increments(tmp_path: Path) -> None:
    """TC-SRB-022-03: Each unique alias adds exactly one entry to the ledger."""
    lp = _ledger(tmp_path)
    rd = _receipts(tmp_path)

    aliases = ["wave-one", "wave-two", "wave-three"]
    for alias in aliases:
        allocate_sprint_number(alias, ledger_path=lp, receipts_dir=rd)

    # Repeat allocations must NOT add new entries
    allocate_sprint_number("wave-one", ledger_path=lp, receipts_dir=rd)
    allocate_sprint_number("wave-two", ledger_path=lp, receipts_dir=rd)

    ledger = load_ledger(lp)
    entries = ledger["entries"]
    assert len(entries) == 3, f"expected 3 entries, got {len(entries)}"
    assert ledger["highest_allocated_number"] == entries[0]["sprint_number"] + 2


# ---------------------------------------------------------------------------
# TC-SRB-022-04  No stale .tmp file remains after allocation
# ---------------------------------------------------------------------------


def test_no_stale_tmp_after_allocation(tmp_path: Path) -> None:
    """TC-SRB-022-04: Successful allocation leaves no orphaned .tmp file."""
    lp = _ledger(tmp_path)
    rd = _receipts(tmp_path)
    tmp_path_lock = Path(str(lp) + ".tmp")

    allocate_sprint_number("clean-run", ledger_path=lp, receipts_dir=rd)

    assert not tmp_path_lock.exists(), "stale .tmp file must not remain after allocation"


# ---------------------------------------------------------------------------
# TC-SRB-022  Receipt file written with correct fields
# ---------------------------------------------------------------------------


def test_receipt_file_written(tmp_path: Path) -> None:
    """Allocation writes a receipt file with required fields."""
    lp = _ledger(tmp_path)
    rd = _receipts(tmp_path)

    result = allocate_sprint_number(
        "receipt-check",
        mission_id="TEST-MISSION-001",
        plan_id="plans/.claude/test-plan.md",
        ledger_path=lp,
        receipts_dir=rd,
    )

    sprint_id = result["sprint_id"]
    receipt_path = rd / f"{sprint_id}.json"
    assert receipt_path.exists(), f"receipt file not found at {receipt_path}"

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["schema_version"] == "1.0"
    assert receipt["verdict"] == "ALLOCATED"
    assert receipt["sprint_id"] == sprint_id
    assert receipt["sprint_number"] == result["sprint_number"]
    assert receipt["mission_id"] == "TEST-MISSION-001"
    assert receipt["plan_id"] == "plans/.claude/test-plan.md"
    assert "allocated_at" in receipt


# ---------------------------------------------------------------------------
# TC-SRB-023  Concurrent allocation safety (monotonicity, no duplicates)
# ---------------------------------------------------------------------------


def test_concurrent_allocations_are_unique_and_monotonic(tmp_path: Path) -> None:
    """TC-SRB-023: Concurrent allocations produce unique, monotonic sprint numbers."""
    lp = _ledger(tmp_path)
    rd = _receipts(tmp_path)

    results: list[dict] = []
    errors: list[Exception] = []
    lock = threading.Lock()

    def allocate(alias: str) -> None:
        try:
            r = allocate_sprint_number(alias, ledger_path=lp, receipts_dir=rd)
            with lock:
                results.append(r)
        except Exception as exc:
            with lock:
                errors.append(exc)

    thread_count = 8
    threads = [
        threading.Thread(target=allocate, args=(f"concurrent-{i:02d}",))
        for i in range(thread_count)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"allocation errors during concurrency test: {errors}"
    assert len(results) == thread_count

    numbers = sorted(r["sprint_number"] for r in results)
    unique_numbers = sorted(set(numbers))
    assert numbers == unique_numbers, "duplicate sprint numbers detected in concurrent run"

    # Verify ledger is consistent
    ledger = load_ledger(lp)
    assert len(ledger["entries"]) == thread_count
    assert ledger["highest_allocated_number"] == max(numbers)


# ---------------------------------------------------------------------------
# TC-SRB-024  Interrupted allocation recovery
# ---------------------------------------------------------------------------


def test_recover_from_orphaned_tmp(tmp_path: Path) -> None:
    """TC-SRB-024: An orphaned .tmp file is recovered correctly by recover_sprint()."""
    lp = _ledger(tmp_path)
    rd = _receipts(tmp_path)
    tmp_lock = Path(str(lp) + ".tmp")

    # Simulate an interrupted write: .tmp exists but ledger rename never happened
    orphan_sprint_id = "SPRINT-00999"
    orphan_ledger = {
        "schema_version": "1.0",
        "highest_allocated_number": 999,
        "entries": [
            {
                "sprint_number": 999,
                "sprint_id": orphan_sprint_id,
                "semantic_alias": "orphaned-alias",
                "status": "ALLOCATED",
                "allocated_at": "2026-01-01T00:00:00+00:00",
                "supervisor_id": "deadbeef",
            }
        ],
    }
    tmp_lock.write_text(json.dumps(orphan_ledger, indent=2), encoding="utf-8")

    # Ledger itself does NOT exist (crash before os.replace())
    assert not lp.exists()

    result = recover_sprint(orphan_sprint_id, ledger_path=lp, receipts_dir=rd)
    assert result["verdict"] == "RECOVERED", f"unexpected verdict: {result}"

    # After recovery the ledger exists and contains the orphaned sprint
    assert lp.exists()
    recovered_ledger = load_ledger(lp)
    ids = [e["sprint_id"] for e in recovered_ledger["entries"]]
    assert orphan_sprint_id in ids


def test_recover_clean_when_no_tmp(tmp_path: Path) -> None:
    """TC-SRB-024b: recover_sprint() returns CLEAN when no .tmp exists."""
    lp = _ledger(tmp_path)
    rd = _receipts(tmp_path)

    result = recover_sprint("SPRINT-00001", ledger_path=lp, receipts_dir=rd)
    assert result["verdict"] == "CLEAN"


def test_recover_clean_when_tmp_does_not_contain_sprint(tmp_path: Path) -> None:
    """TC-SRB-024c: .tmp exists but doesn't contain target sprint → CLEAN (no action)."""
    lp = _ledger(tmp_path)
    rd = _receipts(tmp_path)
    tmp_lock = Path(str(lp) + ".tmp")

    # .tmp exists but has a DIFFERENT sprint
    other_ledger = {
        "schema_version": "1.0",
        "highest_allocated_number": 100,
        "entries": [{"sprint_id": "SPRINT-00100", "sprint_number": 100, "status": "ALLOCATED"}],
    }
    tmp_lock.write_text(json.dumps(other_ledger), encoding="utf-8")

    result = recover_sprint("SPRINT-00999", ledger_path=lp, receipts_dir=rd)
    assert result["verdict"] == "CLEAN"
    # .tmp must still exist (we didn't apply it)
    assert tmp_lock.exists()
