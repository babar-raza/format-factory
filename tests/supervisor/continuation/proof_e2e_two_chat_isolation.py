"""
proof_e2e_two_chat_isolation.py — TC-CCI-H-04: Multi-chat E2E behavioral proof.

Demonstrates that CCI prevents a new chat (Chat B) from consuming another chat's
(Chat A's) continuation signal, and that explicit adoption via reset_track_signal.py
unblocks the new chat correctly.

Run directly:
    python tests/supervisor/continuation/proof_e2e_two_chat_isolation.py

All steps print PASS or FAIL. Exit code 0 = all PASS, non-zero = any FAIL.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_SUPERVISOR = _REPO_ROOT / "tools" / "supervisor"
_CHECK_CONTINUATION = str(_SUPERVISOR / "check_continuation.py")
_RESET_SIGNAL = str(_SUPERVISOR / "reset_track_signal.py")

_failures: list[str] = []


def _run(step: str, *, argv: list[str], env: dict, expect_exit: int) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable] + argv,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    combined = result.stdout + result.stderr
    ok = result.returncode == expect_exit
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {step}")
    if not ok:
        print(f"       Expected exit {expect_exit}, got {result.returncode}")
        print(f"       stdout: {result.stdout.strip()[:400]}")
        print(f"       stderr: {result.stderr.strip()[:400]}")
        _failures.append(step)
    return ok, combined


def _contains(step: str, combined: str, needle: str) -> bool:
    ok = needle in combined
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {step} — '{needle}' in output")
    if not ok:
        print(f"       Full output: {combined.strip()[:400]}")
        _failures.append(step)
    return ok


_LIVE_SIGNAL = _REPO_ROOT / ".local" / "supervisor" / "product" / "continuation-signal.json"


def main() -> int:
    print("=" * 60)
    print("TC-CCI-H-04: Multi-Chat E2E Isolation Proof")
    print("=" * 60)
    print("NOTE: Uses live product signal path; saves/restores original signal.")

    CHAT_A_SESSION = "aabbccddeeff"
    CHAT_B_SESSION = "112233445566"

    # Save original signal (restore on exit)
    original_signal: str | None = None
    if _LIVE_SIGNAL.exists():
        original_signal = _LIVE_SIGNAL.read_text(encoding="utf-8")

    try:
        base_env = {k: v for k, v in os.environ.items()}

        # Write Chat A's signal to the live path
        _LIVE_SIGNAL.parent.mkdir(parents=True, exist_ok=True)
        _LIVE_SIGNAL.write_text(json.dumps({
            "session_id": CHAT_A_SESSION,
            "autonomous_continue": True,
            "iteration": 3,
            "max_iterations": 5,
            "continuation_state": "YES_RESET_CLEAN",
            "hard_stops_detected": [],
            "rework_items": [],
            "owner": "proof_script",
        }), encoding="utf-8")

        # -- Step 1: Chat B tries to consume Chat A's signal --
        print("\n-- Step 1: Chat B -> check_continuation (should REJECT) --")
        chat_b_env = {**base_env, "CLAUDE_SESSION_ID": CHAT_B_SESSION}

        ok, output = _run(
            "Chat B: check_continuation exits 1 (SESSION_MISMATCH)",
            argv=[_CHECK_CONTINUATION, "--repo-root", str(_REPO_ROOT), "--track", "product"],
            env=chat_b_env,
            expect_exit=1,
        )
        _contains("Chat B output contains SESSION_MISMATCH", output, "SESSION_MISMATCH")

        # -- Step 2: Chat B resets the signal (explicit adoption) --
        print("\n-- Step 2: Chat B -> reset_track_signal (adopt) --")
        _run(
            "Chat B: reset_track_signal exits 0",
            argv=[_RESET_SIGNAL, "--track", "product"],
            env=chat_b_env,
            expect_exit=0,
        )

        # -- Step 3: Verify signal now has Chat B's session --
        print("\n-- Step 3: Verify signal updated to Chat B's session --")
        try:
            sig = json.loads(_LIVE_SIGNAL.read_text(encoding="utf-8"))
            actual_session = sig.get("session_id", "")
            if actual_session == CHAT_B_SESSION:
                print(f"[PASS] Signal session_id updated to Chat B: {actual_session}")
            else:
                print(f"[FAIL] Signal session_id not updated. Expected {CHAT_B_SESSION!r}, got {actual_session!r}")
                _failures.append("Signal session_id updated to Chat B's session")

            cont_state = sig.get("continuation_state", "")
            if cont_state.startswith("YES"):
                print(f"[PASS] Signal continuation_state is YES_*: {cont_state}")
            else:
                print(f"[FAIL] Signal continuation_state is not YES_*: {cont_state}")
                _failures.append("Signal continuation_state is YES_* after reset")

            hard_stops = sig.get("hard_stops_detected", ["non-empty"])
            if hard_stops == []:
                print("[PASS] Signal hard_stops_detected is empty after reset")
            else:
                print(f"[FAIL] Signal hard_stops_detected not cleared: {hard_stops}")
                _failures.append("Signal hard_stops_detected cleared after reset")
        except Exception as e:
            print(f"[FAIL] Could not read signal after reset: {e}")
            _failures.append("Signal readable after reset")

        # -- Step 4: Chat B -> check_continuation (should CONTINUE) --
        print("\n-- Step 4: Chat B -> check_continuation (should CONTINUE) --")
        _run(
            "Chat B: check_continuation exits 0 (CONTINUE) after reset",
            argv=[_CHECK_CONTINUATION, "--repo-root", str(_REPO_ROOT), "--track", "product"],
            env=chat_b_env,
            expect_exit=0,
        )

        # -- Step 5: Chat A can no longer consume (signal now owned by B) --
        print("\n-- Step 5: Chat A tries to consume (signal now Chat B's) --")
        chat_a_env = {**base_env, "CLAUDE_SESSION_ID": CHAT_A_SESSION}
        _run(
            "Chat A: check_continuation exits 1 after Chat B's reset",
            argv=[_CHECK_CONTINUATION, "--repo-root", str(_REPO_ROOT), "--track", "product"],
            env=chat_a_env,
            expect_exit=1,
        )

    finally:
        # Restore original signal
        if original_signal is not None:
            _LIVE_SIGNAL.write_text(original_signal, encoding="utf-8")
            print("\n[INFO] Original signal restored.")

    print()
    print("=" * 60)
    if _failures:
        print(f"RESULT: FAIL — {len(_failures)} step(s) failed:")
        for f in _failures:
            print(f"  - {f}")
        return 1
    else:
        print("RESULT: ALL PASS — cross-chat isolation verified E2E")
        return 0


if __name__ == "__main__":
    sys.exit(main())
