"""
replay_lineage.py -- Lane R9-7 Deliverable (CONWAY-R9)

Replay lineage persistence for the governed planning/orchestration layer.

PURPOSE:
  Track the history of replay fingerprints across sprints, enabling:
  - Detection of fingerprint drift (REPLAY_MISMATCH)
  - Authority continuity across sprint boundaries
  - Lineage chain validation (each sprint's fingerprint derives from prior)
  - Tamper evidence (hash-chained lineage records)

THIS MODULE DOES NOT MODIFY replay_fingerprint.py.
It reads from replay_fingerprint.py and adds lineage tracking on top.

LINEAGE RECORD:
  Each lineage entry records:
  - sprint_id: which sprint produced this fingerprint
  - fingerprint: the actual fingerprint value
  - prior_fingerprint: the immediately prior entry's fingerprint (null for genesis)
  - lineage_hash: SHA-256 of (prior_fingerprint + fingerprint + sprint_id)
  - format_id: which format this lineage entry belongs to
  - created_date: when this record was created

DRIFT DETECTION:
  A REPLAY_MISMATCH is detected when:
  - The current fingerprint differs from the expected fingerprint
  - The lineage chain is broken (prior_fingerprint mismatch)
  - A genesis record is not the first entry

NOT ALLOWED:
  - Modifying replay_fingerprint.py
  - Approving gates to clear replay mismatches
  - Accepting a broken lineage chain without human review

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

# Lineage status constants
LINEAGE_CONSISTENT = "LINEAGE_CONSISTENT"
LINEAGE_MISMATCH = "LINEAGE_MISMATCH"
LINEAGE_GENESIS = "LINEAGE_GENESIS"
LINEAGE_CHAIN_BROKEN = "LINEAGE_CHAIN_BROKEN"
LINEAGE_EMPTY = "LINEAGE_EMPTY"


def _stable_hash(data: Any) -> str:
    """Deterministic SHA-256 of any JSON-serializable object. Sorted keys."""
    normalized = json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def _lineage_hash(prior_fingerprint: str | None, fingerprint: str, sprint_id: str) -> str:
    """
    Compute the hash-chained lineage hash for a new entry.
    Chains: prior_fingerprint → fingerprint → sprint_id
    """
    return _stable_hash({
        "prior": prior_fingerprint or "GENESIS",
        "fingerprint": fingerprint,
        "sprint_id": sprint_id,
    })


def build_lineage_entry(
    fmt: str,
    sprint_id: str,
    fingerprint: str,
    prior_entry: dict | None = None,
) -> dict:
    """
    Build a new lineage entry for a format's replay fingerprint.

    Parameters
    ----------
    fmt : str
        Format ID (e.g. 'fods', 'fodt')
    sprint_id : str
        Sprint ID that produced this fingerprint
    fingerprint : str
        The replay fingerprint value from replay_fingerprint module
    prior_entry : dict, optional
        The prior lineage entry (None for genesis)

    Returns
    -------
    dict — lineage entry
    """
    prior_fp = prior_entry["fingerprint"] if prior_entry else None
    prior_lineage_hash = prior_entry["lineage_hash"] if prior_entry else None
    entry_index = (prior_entry["entry_index"] + 1) if prior_entry else 0
    is_genesis = prior_entry is None

    lhash = _lineage_hash(prior_fp, fingerprint, sprint_id)

    return {
        "entry_id": _stable_hash({"fmt": fmt, "sprint_id": sprint_id, "fingerprint": fingerprint}),
        "format_id": fmt,
        "sprint_id": sprint_id,
        "fingerprint": fingerprint,
        "prior_fingerprint": prior_fp,
        "prior_lineage_hash": prior_lineage_hash,
        "lineage_hash": lhash,
        "entry_index": entry_index,
        "is_genesis": is_genesis,
        "created_date": str(date.today()),
        "governance": {
            "commercial_product_ready": False,
            "autonomous_execution_allowed": False,
            "gate_self_approval_allowed": False,
            "dry_run_only": True,
        },
    }


def validate_lineage_chain(entries: list[dict]) -> dict:
    """
    Validate the integrity of a lineage chain.

    Parameters
    ----------
    entries : list[dict]
        Ordered list of lineage entries (oldest first)

    Returns
    -------
    dict with:
      status: str — LINEAGE_CONSISTENT | LINEAGE_CHAIN_BROKEN | LINEAGE_EMPTY | LINEAGE_GENESIS
      entry_count: int
      violations: list[str]
      is_consistent: bool
    """
    if not entries:
        return {
            "status": LINEAGE_EMPTY,
            "entry_count": 0,
            "violations": [],
            "is_consistent": True,
        }

    if len(entries) == 1:
        entry = entries[0]
        if not entry.get("is_genesis"):
            return {
                "status": LINEAGE_CHAIN_BROKEN,
                "entry_count": 1,
                "violations": ["Single entry is not marked as genesis"],
                "is_consistent": False,
            }
        return {
            "status": LINEAGE_GENESIS,
            "entry_count": 1,
            "violations": [],
            "is_consistent": True,
        }

    violations = []

    # Check first entry is genesis
    if not entries[0].get("is_genesis"):
        violations.append(f"Entry 0 is not marked as genesis (sprint: {entries[0].get('sprint_id')})")

    # Validate chain continuity
    for i in range(1, len(entries)):
        prev = entries[i - 1]
        curr = entries[i]

        # Check prior_fingerprint matches previous fingerprint
        if curr.get("prior_fingerprint") != prev.get("fingerprint"):
            violations.append(
                f"Entry {i}: prior_fingerprint mismatch "
                f"(expected {prev.get('fingerprint')!r}, got {curr.get('prior_fingerprint')!r})"
            )

        # Check prior_lineage_hash matches previous lineage_hash
        if curr.get("prior_lineage_hash") != prev.get("lineage_hash"):
            violations.append(
                f"Entry {i}: prior_lineage_hash mismatch "
                f"(expected {prev.get('lineage_hash')!r}, got {curr.get('prior_lineage_hash')!r})"
            )

        # Check entry_index is sequential
        expected_index = prev.get("entry_index", 0) + 1
        if curr.get("entry_index") != expected_index:
            violations.append(
                f"Entry {i}: entry_index {curr.get('entry_index')} != expected {expected_index}"
            )

        # Re-derive and verify lineage_hash
        expected_lhash = _lineage_hash(
            prior_fingerprint=prev.get("fingerprint"),
            fingerprint=curr["fingerprint"],
            sprint_id=curr["sprint_id"],
        )
        if curr.get("lineage_hash") != expected_lhash:
            violations.append(
                f"Entry {i}: lineage_hash mismatch (possible tampering detected) "
                f"sprint={curr.get('sprint_id')}"
            )

        # Check genesis flag is False for non-first entries
        if curr.get("is_genesis"):
            violations.append(f"Entry {i}: is_genesis=True on non-first entry (sprint: {curr.get('sprint_id')})")

    status = LINEAGE_CONSISTENT if not violations else LINEAGE_CHAIN_BROKEN
    return {
        "status": status,
        "entry_count": len(entries),
        "violations": violations,
        "is_consistent": status == LINEAGE_CONSISTENT,
    }


def detect_fingerprint_drift(
    fmt: str,
    current_fingerprint: str,
    prior_entries: list[dict],
) -> dict:
    """
    Detect whether the current fingerprint has drifted from the last known lineage.

    Parameters
    ----------
    fmt : str
        Format ID
    current_fingerprint : str
        The fingerprint computed in the current sprint
    prior_entries : list[dict]
        All prior lineage entries (ordered, oldest first)

    Returns
    -------
    dict with:
      drift_detected: bool
      drift_status: str
      prior_fingerprint: str | None
      current_fingerprint: str
      explanation: str
    """
    if not prior_entries:
        return {
            "format_id": fmt,
            "drift_detected": False,
            "drift_status": LINEAGE_GENESIS,
            "prior_fingerprint": None,
            "current_fingerprint": current_fingerprint,
            "explanation": "No prior entries. This is a genesis fingerprint.",
        }

    last_entry = prior_entries[-1]
    prior_fp = last_entry.get("fingerprint")

    if current_fingerprint == prior_fp:
        return {
            "format_id": fmt,
            "drift_detected": False,
            "drift_status": LINEAGE_CONSISTENT,
            "prior_fingerprint": prior_fp,
            "current_fingerprint": current_fingerprint,
            "explanation": "Fingerprint matches prior entry. No drift detected.",
        }

    return {
        "format_id": fmt,
        "drift_detected": True,
        "drift_status": LINEAGE_MISMATCH,
        "prior_fingerprint": prior_fp,
        "current_fingerprint": current_fingerprint,
        "explanation": (
            f"Fingerprint drift detected for {fmt.upper()}. "
            f"Prior: {prior_fp!r}. Current: {current_fingerprint!r}. "
            f"This means requirements or planning inputs changed since the last sprint. "
            f"Human review required to determine if this drift is expected."
        ),
    }


def build_live_lineage_entry(fmt: str, sprint_id: str, prior_entry: dict | None = None) -> dict:
    """
    Build a live lineage entry for a format by reading from replay_fingerprint.

    Parameters
    ----------
    fmt : str
        Format ID
    sprint_id : str
        Sprint ID to record
    prior_entry : dict, optional
        Prior lineage entry (if None, creates genesis entry)

    Returns
    -------
    dict — lineage entry
    """
    try:
        from replay_fingerprint import compute_requirements_fingerprint
    except ImportError as exc:
        return {
            "entry_id": "ERROR",
            "format_id": fmt,
            "sprint_id": sprint_id,
            "fingerprint": "ERROR",
            "error": str(exc),
        }

    fp = compute_requirements_fingerprint(fmt)
    fingerprint_value = fp.get("fingerprint", "")

    return build_lineage_entry(
        fmt=fmt,
        sprint_id=sprint_id,
        fingerprint=fingerprint_value,
        prior_entry=prior_entry,
    )


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Replay lineage tracker")
    parser.add_argument("format", nargs="?", default="fods", help="Format ID")
    parser.add_argument("--sprint", default="SPRINT-UNKNOWN", help="Sprint ID")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    entry = build_live_lineage_entry(args.format, args.sprint)
    if args.json:
        print(json.dumps(entry, indent=2))
        return

    print(f"=== Replay Lineage Entry: {args.format.upper()} ===")
    print(f"  Sprint:       {entry.get('sprint_id')}")
    print(f"  Fingerprint:  {entry.get('fingerprint')}")
    print(f"  Is genesis:   {entry.get('is_genesis')}")
    print(f"  Lineage hash: {entry.get('lineage_hash')}")
    print(f"  Entry index:  {entry.get('entry_index')}")


if __name__ == "__main__":
    main()
