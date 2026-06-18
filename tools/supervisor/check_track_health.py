"""
check_track_health.py — Per-track state consistency health check (TC-P2-006).

Advisory tool — non-blocking. Outputs WARNING/CRITICAL for state inconsistencies
but does NOT set any stop conditions in continuation-signal.json.

Usage:
    python tools/supervisor/check_track_health.py --track product
    python tools/supervisor/check_track_health.py --track machinery
    python tools/supervisor/check_track_health.py  # checks both tracks

Exit codes:
    0 — healthy (or advisory warnings only)
    1 — CRITICAL: missing state bundle required for that track
    (Advisory WARNINGs still exit 0 — they do not block continuation)

TC-P2-006 — REQ-TRK-010
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_here = Path(__file__).resolve().parent
_default_repo = _here.parent.parent

# Maximum acceptable state file age difference in seconds before WARNING
_SKEW_WARN_SECONDS = 120
# State files that must exist for a healthy track state bundle
_PRODUCT_REQUIRED_FILES = [
    ".local/supervisor/continuation-signal.json",  # legacy fallback OK
]
_MACHINERY_REQUIRED_FILES: list[str] = []  # machinery has no hard-required legacy files


def _read_json_safe(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _file_mtime_iso(path: Path) -> str | None:
    try:
        import os
        ts = os.path.getmtime(path)
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    except Exception:
        return None


def _mtime_seconds(path: Path) -> float | None:
    try:
        import os
        return os.path.getmtime(path)
    except Exception:
        return None


def check_track(track: str, repo_root: Path) -> dict:
    """Check health of the given track's state files.

    Returns a health report dict with:
      - verdict: "HEALTHY" | "WARNING" | "CRITICAL"
      - findings: list of finding dicts
    """
    findings: list[dict] = []
    verdict = "HEALTHY"

    supervisor_dir = repo_root / ".local" / "supervisor"
    shared_dir = supervisor_dir / "shared"

    if track == "product":
        track_dir = supervisor_dir / "product"
        signal_path = (track_dir / "continuation-signal.json"
                       if (track_dir / "continuation-signal.json").exists()
                       else supervisor_dir / "continuation-signal.json")
        work_items_path = (track_dir / "next-work-items.json"
                           if (track_dir / "next-work-items.json").exists()
                           else supervisor_dir / "next-work-items.json")
        grade_cache_path = track_dir / "grade-cache.json"
        approval_gates_path = repo_root / "reports" / "supervisor" / "approval-gates.md"
        next_sprint_path = repo_root / "reports" / "supervisor" / "next-sprint.md"

        # Check 1: continuation-signal.json exists
        if not signal_path.exists():
            findings.append({
                "level": "CRITICAL",
                "code": "SIGNAL_MISSING",
                "message": f"Track P continuation signal not found at {signal_path}",
            })
            verdict = "CRITICAL"
        else:
            sig = _read_json_safe(signal_path)
            if sig is None:
                findings.append({
                    "level": "CRITICAL",
                    "code": "SIGNAL_CORRUPT",
                    "message": f"Track P continuation signal is invalid JSON: {signal_path}",
                })
                verdict = "CRITICAL"
            else:
                findings.append({
                    "level": "INFO",
                    "code": "SIGNAL_OK",
                    "message": f"Continuation signal: iteration={sig.get('iteration',0)}/{sig.get('max_iterations',5)}, autonomous_continue={sig.get('autonomous_continue')}",
                })

        # Check 2: next-work-items.json exists
        if not work_items_path.exists():
            findings.append({
                "level": "WARNING",
                "code": "WORK_ITEMS_MISSING",
                "message": f"Track P next-work-items.json not found at {work_items_path}",
            })
            if verdict == "HEALTHY":
                verdict = "WARNING"
        else:
            findings.append({
                "level": "INFO",
                "code": "WORK_ITEMS_OK",
                "message": f"Work items file found: {work_items_path.name}",
            })

        # Check 3: approval-gates.md
        if not approval_gates_path.exists():
            findings.append({
                "level": "WARNING",
                "code": "APPROVAL_GATES_MISSING",
                "message": "approval-gates.md not found",
            })
            if verdict == "HEALTHY":
                verdict = "WARNING"
        else:
            gates_text = approval_gates_path.read_text(encoding="utf-8", errors="replace")
            if "AUTONOMOUS_CONTINUE: YES" in gates_text:
                findings.append({"level": "INFO", "code": "GATES_OPEN", "message": "AUTONOMOUS_CONTINUE: YES"})
            else:
                findings.append({"level": "WARNING", "code": "GATES_CLOSED", "message": "AUTONOMOUS_CONTINUE not YES in approval-gates.md"})
                if verdict == "HEALTHY":
                    verdict = "WARNING"

        # Check 4: Timestamp skew between signal and approval-gates.md
        sig_mtime = _mtime_seconds(signal_path) if signal_path.exists() else None
        gates_mtime = _mtime_seconds(approval_gates_path) if approval_gates_path.exists() else None
        if sig_mtime and gates_mtime:
            skew = abs(sig_mtime - gates_mtime)
            if skew > _SKEW_WARN_SECONDS:
                findings.append({
                    "level": "WARNING",
                    "code": "STATE_SKEW",
                    "message": f"Signal and approval-gates.md differ by {skew:.0f}s (>{_SKEW_WARN_SECONDS}s threshold)",
                    "skew_seconds": round(skew, 1),
                })
                if verdict == "HEALTHY":
                    verdict = "WARNING"

        # Check 5: grade-cache.json freshness
        if grade_cache_path.exists():
            gc = _read_json_safe(grade_cache_path)
            findings.append({
                "level": "INFO",
                "code": "GRADE_CACHE_OK",
                "message": f"Track P grade cache: {len(gc) if gc else 0} entries at {grade_cache_path.relative_to(repo_root)}",
            })

        # Check 6: machinery_to_product handoff freshness (advisory for Track P gap selection)
        handoff_path = shared_dir / "track-handoff.json"
        if handoff_path.exists():
            hf = _read_json_safe(handoff_path)
            if hf and hf.get("machinery_to_product"):
                m2p = hf["machinery_to_product"]
                findings.append({
                    "level": "INFO",
                    "code": "HANDOFF_AVAILABLE",
                    "message": (
                        f"Track M handoff available: {m2p.get('validated_gap_count','?')} gaps, "
                        f"written_at={m2p.get('written_at','?')}"
                    ),
                })
            else:
                findings.append({
                    "level": "INFO",
                    "code": "HANDOFF_NO_M2P",
                    "message": "No machinery_to_product in handoff (Track M has not published gaps yet)",
                })

    elif track == "machinery":
        track_dir = supervisor_dir / "machinery"
        signal_path = track_dir / "continuation-signal.json"
        work_items_path = track_dir / "next-work-items.json"
        grade_cache_path = track_dir / "grade-cache.json"
        chat_id_path = track_dir / "current-chat-id.json"

        # Check 1: machinery signal (strict — no legacy fallback for Track M)
        if not signal_path.exists():
            findings.append({
                "level": "WARNING",
                "code": "SIGNAL_MISSING",
                "message": f"Track M continuation signal not found — no active machinery cycle (expected at {signal_path})",
            })
            if verdict == "HEALTHY":
                verdict = "WARNING"
        else:
            sig = _read_json_safe(signal_path)
            if sig is None:
                findings.append({
                    "level": "CRITICAL",
                    "code": "SIGNAL_CORRUPT",
                    "message": f"Track M continuation signal is invalid JSON: {signal_path}",
                })
                verdict = "CRITICAL"
            else:
                chat_id_in_sig = sig.get("chat_id")
                findings.append({
                    "level": "INFO",
                    "code": "SIGNAL_OK",
                    "message": f"Track M signal: iteration={sig.get('iteration',0)}, chat_id={'set' if chat_id_in_sig else 'NOT SET (isolation risk)'}",
                })
                if not chat_id_in_sig:
                    findings.append({
                        "level": "WARNING",
                        "code": "CHAT_ID_MISSING",
                        "message": "Track M signal has no chat_id — per-chat isolation is inactive (REQ-CCI-M-002)",
                    })
                    if verdict == "HEALTHY":
                        verdict = "WARNING"

        # Check 2: current-chat-id.json for chat isolation registry
        if not chat_id_path.exists():
            findings.append({
                "level": "INFO",
                "code": "CHAT_ID_REGISTRY_MISSING",
                "message": "current-chat-id.json not found — no active Track M machinery chat",
            })
        else:
            cid = _read_json_safe(chat_id_path)
            findings.append({
                "level": "INFO",
                "code": "CHAT_ID_REGISTRY_OK",
                "message": f"Active machinery chat_id: {cid.get('chat_id','?') if cid else 'unreadable'}",
            })

        # Check 3: grade-cache.json
        if grade_cache_path.exists():
            gc = _read_json_safe(grade_cache_path)
            findings.append({
                "level": "INFO",
                "code": "GRADE_CACHE_OK",
                "message": f"Track M grade cache: {len(gc) if gc else 0} entries",
            })

        # Check 4: product_to_machinery handoff (so Track M knows what Track P has produced)
        handoff_path = shared_dir / "track-handoff.json"
        if handoff_path.exists():
            hf = _read_json_safe(handoff_path)
            if hf and hf.get("product_to_machinery"):
                p2m = hf["product_to_machinery"]
                findings.append({
                    "level": "INFO",
                    "code": "HANDOFF_AVAILABLE",
                    "message": (
                        f"Track P handoff available: sprint_id={p2m.get('sprint_id','?')}, "
                        f"capabilities={p2m.get('new_capabilities_count','?')}, "
                        f"written_at={p2m.get('written_at','?')}"
                    ),
                })
            else:
                findings.append({
                    "level": "INFO",
                    "code": "HANDOFF_NO_P2M",
                    "message": "No product_to_machinery in handoff (Track P has not published a sprint yet)",
                })
    else:
        findings.append({
            "level": "CRITICAL",
            "code": "INVALID_TRACK",
            "message": f"Unknown track: {track!r} (must be 'product' or 'machinery')",
        })
        verdict = "CRITICAL"

    return {
        "track": track,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Per-track state consistency health check (advisory)"
    )
    parser.add_argument(
        "--track", type=str, choices=["product", "machinery"], default=None,
        help="Track to check (default: check both)",
    )
    parser.add_argument(
        "--repo-root", type=Path, default=_default_repo,
        help="Repository root (default: auto-detected)",
    )
    parser.add_argument(
        "--json", action="store_true", default=False,
        help="Output machine-readable JSON",
    )
    args = parser.parse_args(argv)

    tracks = [args.track] if args.track else ["product", "machinery"]
    reports = [check_track(t, args.repo_root) for t in tracks]

    if args.json:
        import json as _json
        print(_json.dumps(reports if len(reports) > 1 else reports[0], indent=2))
    else:
        for report in reports:
            print(f"\n=== Track {report['track'].upper()} Health: {report['verdict']} ===")
            print(f"  Checked at: {report['checked_at']}")
            for f in report["findings"]:
                level = f["level"]
                code = f["code"]
                msg = f["message"]
                if level == "INFO":
                    print(f"  [INFO]  {code}: {msg}")
                elif level == "WARNING":
                    print(f"  [WARN]  {code}: {msg}")
                elif level == "CRITICAL":
                    print(f"  [CRIT]  {code}: {msg}")

    # Exit 1 if any track is CRITICAL, else 0 (even for WARNINGs)
    if any(r["verdict"] == "CRITICAL" for r in reports):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
