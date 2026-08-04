"""Append-only writer and validator for the FF6 native controller event journal.

Why this module exists
----------------------
The FF6 controller (``plans/strategic/ff6/events.jsonl`` plus the
``plans/strategic/ff6/controller-state.yaml`` projection) had no writer. The
2026-08-04 independent review recorded this as GAP-007 in
``plans/strategic/ff6/execution-recovery-directive.yaml``:

    Nothing is currently responsible for appending FF6-EVENT-000048 when
    Stage 2/3 complete; the controller will stay silently frozen at Event 47
    indefinitely unless a specific mechanism is assigned.

Assigning the duty to "whichever agent gets there first" makes a hand-edited
hash chain the mechanism, which is exactly how a ledger silently corrupts. This
module is that mechanism instead: it validates the whole existing chain before
it will append, refuses to write when the chain is already broken, derives
every chain field itself (``sequence``, ``event_id``, ``previous_event_hash``,
``event_hash``) so a caller cannot get them wrong, and verifies that
``semantic_commit`` / ``source_checkpoint_commit`` name real commits in this
repository before the event is allowed to claim them.

Authoring event bodies
----------------------
Write the JSON body with a file-writing tool, or a heredoc whose delimiter is
quoted (``<<'JSON'``). Never an unquoted shell heredoc: the shell performs
command substitution on backticks and expands dollar signs *before* the file is
written, silently deleting those words. The damage is invisible to every check
here, because what lands is still valid JSON that hashes and chains correctly --
only the prose is missing words. This happened to FF6-EVENT-000057 and had to be
repaired by appending FF6-EVENT-000058, since an append-only chain cannot be
edited in place.

Canonical hash algorithm
------------------------
``event_hash`` is sha256 over the event's JSON body with ``event_hash`` itself
removed, serialized with ``sort_keys=True``, ``ensure_ascii=False`` and
``separators=(",", ":")``. This module is the canonical implementation. A
second, independently written copy already exists in
``plans/codex/handover/handover_projection.py`` (that file is a portable
handover artifact and is deliberately left self-contained rather than made to
import from here). ``tests/ff6/test_controller_events.py`` carries a drift
guard that asserts the two implementations agree on every real event, so the
GAP-003 failure mode -- multiple copies of one rule quietly diverging -- cannot
repeat here undetected.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
JOURNAL_PATH = REPO_ROOT / "plans" / "strategic" / "ff6" / "events.jsonl"
STATE_PATH = REPO_ROOT / "plans" / "strategic" / "ff6" / "controller-state.yaml"

EVENT_SCHEMA = "ff6/controller-event@1"
GOAL_ID = "FF6-PRODUCTION-LIBRARIES-001"

#: Fields every event in the journal carries. Derived from the real journal
#: (all 47 pre-existing events share exactly these), not invented here.
REQUIRED_FIELDS: frozenset[str] = frozenset(
    {
        "event_hash",
        "event_id",
        "goal_id",
        "previous_event_hash",
        "schema",
        "sequence",
        "state_after",
        "state_before",
        "task_id",
        "transition",
    }
)

#: Fields this module derives. A caller supplying them is a bug, not an
#: override -- deriving them is the entire point of having a writer.
DERIVED_FIELDS: frozenset[str] = frozenset(
    {"event_hash", "event_id", "previous_event_hash", "sequence"}
)

#: Fields naming a git commit. Each is verified to exist before an append.
COMMIT_FIELDS: tuple[str, ...] = ("semantic_commit", "source_checkpoint_commit")


class ControllerEventError(RuntimeError):
    """Raised when the journal or a proposed event fails validation."""


def event_hash(event: Mapping[str, Any]) -> str:
    """Return the canonical sha256 hash of ``event``, ignoring any stored hash."""
    body = {k: v for k, v in event.items() if k != "event_hash"}
    encoded = json.dumps(
        body, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_journal(path: Path = JOURNAL_PATH) -> list[dict[str, Any]]:
    """Parse the event journal. Raises if any line is not a JSON object."""
    if not path.exists():
        raise ControllerEventError(f"event journal not found: {path}")
    events: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ControllerEventError(f"journal line {number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ControllerEventError(f"journal line {number} is not an object")
        events.append(value)
    if not events:
        raise ControllerEventError(f"event journal is empty: {path}")
    return events


def validate_chain(events: Sequence[Mapping[str, Any]]) -> list[str]:
    """Return every chain integrity error found, in journal order.

    An empty list means the chain is intact: sequences are 1-indexed and dense,
    every stored ``event_hash`` matches a recomputation, and every
    ``previous_event_hash`` matches its predecessor's stored hash.
    """
    errors: list[str] = []
    previous: str | None = None
    for expected, event in enumerate(events, start=1):
        event_id = event.get("event_id", f"<position {expected}>")
        if event.get("sequence") != expected:
            errors.append(
                f"{event_id}: sequence is {event.get('sequence')!r}, expected {expected}"
            )
        missing = sorted(REQUIRED_FIELDS - set(event))
        if missing:
            errors.append(f"{event_id}: missing required field(s) {missing}")
        claimed = event.get("event_hash")
        recomputed = event_hash(event)
        if claimed != recomputed:
            errors.append(
                f"{event_id}: stored event_hash {claimed!r} != recomputed {recomputed!r}"
            )
        if expected > 1 and event.get("previous_event_hash") != previous:
            errors.append(
                f"{event_id}: previous_event_hash {event.get('previous_event_hash')!r} "
                f"!= predecessor hash {previous!r}"
            )
        previous = claimed if isinstance(claimed, str) else None
    return errors


def _commit_exists(commit: str, repo_root: Path = REPO_ROOT) -> bool:
    """True when ``commit`` resolves to a commit object in this repository."""
    result = subprocess.run(
        ["git", "cat-file", "-t", commit],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "commit"


def build_event(
    events: Sequence[Mapping[str, Any]],
    body: Mapping[str, Any],
    *,
    repo_root: Path = REPO_ROOT,
    verify_commits: bool = True,
) -> dict[str, Any]:
    """Return ``body`` completed into a chain-valid event appended after ``events``.

    Raises ``ControllerEventError`` if ``body`` presupplies a derived chain
    field, omits a required field, declares the wrong schema or goal, or names
    a commit that does not exist in the repository.
    """
    supplied_derived = sorted(DERIVED_FIELDS & set(body))
    if supplied_derived:
        raise ControllerEventError(
            f"event body must not supply derived chain field(s) {supplied_derived}; "
            "they are computed from the journal head"
        )
    if body.get("schema") != EVENT_SCHEMA:
        raise ControllerEventError(
            f"event schema must be {EVENT_SCHEMA!r}, got {body.get('schema')!r}"
        )
    if body.get("goal_id") != GOAL_ID:
        raise ControllerEventError(
            f"event goal_id must be {GOAL_ID!r}, got {body.get('goal_id')!r}"
        )
    missing = sorted((REQUIRED_FIELDS - DERIVED_FIELDS) - set(body))
    if missing:
        raise ControllerEventError(f"event body missing required field(s) {missing}")

    if verify_commits:
        for field in COMMIT_FIELDS:
            commit = body.get(field)
            if commit is None:
                continue
            if not isinstance(commit, str) or not _commit_exists(commit, repo_root):
                raise ControllerEventError(
                    f"{field}={commit!r} does not resolve to a commit in {repo_root}; "
                    "an event may not claim a commit that does not exist"
                )

    head = events[-1]
    sequence = len(events) + 1
    event = dict(body)
    event["sequence"] = sequence
    event["event_id"] = f"FF6-EVENT-{sequence:06d}"
    event["previous_event_hash"] = head["event_hash"]
    event["event_hash"] = event_hash(event)
    return event


def serialize_event(event: Mapping[str, Any]) -> str:
    """Return the single canonical JSONL line for ``event`` (no trailing newline)."""
    return json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def append_event(
    body: Mapping[str, Any],
    *,
    journal_path: Path = JOURNAL_PATH,
    repo_root: Path = REPO_ROOT,
    verify_commits: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Validate the journal, append one event, and re-validate. Returns the event.

    Existing journal bytes are preserved exactly and the new event is appended
    as one additional line. The journal is append-only and its 47 pre-existing
    lines carry mixed CRLF/LF endings; re-emitting them canonically would
    rewrite every line for no benefit and would obscure the one line that
    actually changed. The whole file is then written atomically (temp file +
    ``os.replace``) so a crash mid-write cannot truncate the ledger.

    Refuses to append when the existing chain is already broken -- appending
    onto a corrupt chain would bury the corruption under a valid-looking head.
    """
    events = load_journal(journal_path)
    errors = validate_chain(events)
    if errors:
        raise ControllerEventError(
            "refusing to append: existing chain is invalid:\n  " + "\n  ".join(errors)
        )

    event = build_event(
        events, body, repo_root=repo_root, verify_commits=verify_commits
    )

    post_errors = validate_chain([*events, event])
    if post_errors:
        raise ControllerEventError(
            "refusing to write: appended chain would be invalid:\n  "
            + "\n  ".join(post_errors)
        )

    if not dry_run:
        existing = journal_path.read_bytes()
        if existing and not existing.endswith(b"\n"):
            existing += b"\n"
        payload = existing + serialize_event(event).encode("utf-8") + b"\n"
        _atomic_write_bytes(journal_path, payload)
    return event


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    """Write ``payload`` to ``path`` via temp file + fsync + atomic replace.

    Byte-oriented on purpose: both files this module writes already contain
    mixed line endings, and a text-mode write would silently rewrite them.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def sync_projection_head(
    *,
    journal_path: Path = JOURNAL_PATH,
    state_path: Path = STATE_PATH,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Point ``controller-state.yaml``'s head fields at the real journal head.

    Deliberately narrow: this updates only ``transition_sequence`` and
    ``last_verified_event`` (``event_id`` / ``event_hash``) -- the three scalars
    that are pure restatements of the journal and therefore mechanically
    derivable. Every other section of the projection (the per-format
    checkpoints, gap summary, promotion table) encodes reviewed judgement about
    what an event *means* and is deliberately left to the author of the
    transition. Line-oriented edits are used rather than a YAML round-trip so
    the file's comments, ordering, and block scalars survive untouched.
    """
    events = load_journal(journal_path)
    errors = validate_chain(events)
    if errors:
        raise ControllerEventError(
            "refusing to sync projection: chain is invalid:\n  " + "\n  ".join(errors)
        )
    head = events[-1]
    # Decode from bytes rather than read_text() so universal-newline translation
    # cannot silently convert this file's line endings on the way back out.
    original = state_path.read_bytes().decode("utf-8")
    lines = original.splitlines(keepends=True)

    def _ending(line: str) -> str:
        for candidate in ("\r\n", "\n", "\r"):
            if line.endswith(candidate):
                return candidate
        return ""

    replaced = {"transition_sequence": False, "event_id": False, "event_hash": False}
    in_last_verified = False
    for index, line in enumerate(lines):
        if line.startswith("transition_sequence:"):
            lines[index] = f"transition_sequence: {head['sequence']}{_ending(line)}"
            replaced["transition_sequence"] = True
            continue
        if line.startswith("last_verified_event:"):
            in_last_verified = True
            continue
        if in_last_verified:
            if line.startswith("  event_id:"):
                lines[index] = f"  event_id: {head['event_id']}{_ending(line)}"
                replaced["event_id"] = True
                continue
            if line.startswith("  event_hash:"):
                lines[index] = f"  event_hash: {head['event_hash']}{_ending(line)}"
                replaced["event_hash"] = True
                continue
            if not line.startswith((" ", "\t")):
                in_last_verified = False

    unmatched = sorted(key for key, done in replaced.items() if not done)
    if unmatched:
        raise ControllerEventError(
            f"could not locate projection field(s) {unmatched} in {state_path}; "
            "refusing to write a partial sync"
        )

    updated = "".join(lines)
    if not dry_run and updated != original:
        _atomic_write_bytes(state_path, updated.encode("utf-8"))
    return {
        "event_id": head["event_id"],
        "event_hash": head["event_hash"],
        "transition_sequence": head["sequence"],
        "changed": updated != original,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.ff6.controller_events",
        description="Validate and append FF6 native controller events.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    verify = sub.add_parser("verify", help="validate the existing event chain")
    verify.add_argument("--journal", type=Path, default=JOURNAL_PATH)

    append = sub.add_parser("append", help="append one event from a JSON body file")
    append.add_argument(
        "body",
        type=Path,
        help="path to a JSON file holding the event body (chain fields omitted)",
    )
    append.add_argument("--journal", type=Path, default=JOURNAL_PATH)
    append.add_argument(
        "--dry-run", action="store_true", help="validate and print without writing"
    )
    append.add_argument(
        "--skip-commit-check",
        action="store_true",
        help="do not verify semantic_commit exists (for tests/fixtures only)",
    )
    append.add_argument(
        "--sync-projection",
        action="store_true",
        help="also point controller-state.yaml's head fields at the new event",
    )

    sync = sub.add_parser(
        "sync-projection",
        help="point controller-state.yaml's head fields at the journal head",
    )
    sync.add_argument("--journal", type=Path, default=JOURNAL_PATH)
    sync.add_argument("--state", type=Path, default=STATE_PATH)
    sync.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)

    try:
        if args.command == "verify":
            events = load_journal(args.journal)
            errors = validate_chain(events)
            if errors:
                print(f"FAIL: {len(errors)} chain error(s)", file=sys.stderr)
                for error in errors:
                    print(f"  {error}", file=sys.stderr)
                return 1
            head = events[-1]
            print(
                f"PASS: {len(events)} events, chain intact, "
                f"head {head['event_id']} {head['event_hash']}"
            )
            return 0

        if args.command == "append":
            body = json.loads(args.body.read_text(encoding="utf-8"))
            event = append_event(
                body,
                journal_path=args.journal,
                verify_commits=not args.skip_commit_check,
                dry_run=args.dry_run,
            )
            prefix = "DRY-RUN " if args.dry_run else ""
            print(f"{prefix}appended {event['event_id']} hash {event['event_hash']}")
            if args.sync_projection and not args.dry_run:
                result = sync_projection_head()
                print(
                    f"projection head -> {result['event_id']} "
                    f"(changed={result['changed']})"
                )
            return 0

        if args.command == "sync-projection":
            result = sync_projection_head(
                journal_path=args.journal,
                state_path=args.state,
                dry_run=args.dry_run,
            )
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0
    except ControllerEventError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
