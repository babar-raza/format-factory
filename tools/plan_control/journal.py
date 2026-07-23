from __future__ import annotations

import hashlib
import json
import os
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class JournalError(RuntimeError):
    pass


_THREAD_LOCKS: dict[str, threading.RLock] = {}
_THREAD_LOCKS_GUARD = threading.Lock()


def _thread_lock(path: Path) -> threading.RLock:
    key = str(path.resolve())
    with _THREAD_LOCKS_GUARD:
        return _THREAD_LOCKS.setdefault(key, threading.RLock())


@contextmanager
def _exclusive_file_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    thread_lock = _thread_lock(path)
    with thread_lock, path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(slots=True)
class AppendResult:
    event: dict[str, Any]
    appended: bool


class EventJournal:
    def __init__(self, path: Path, *, lock_path: Path | None = None):
        self.path = path
        self.lock_path = lock_path or path.with_suffix(path.suffix + ".lock")
        self._cache: list[dict[str, Any]] | None = None
        self._signature: tuple[int, int] | None = None

    def _stat_signature(self) -> tuple[int, int] | None:
        if not self.path.exists():
            return None
        stat = self.path.stat()
        return stat.st_size, stat.st_mtime_ns

    def read(self) -> list[dict[str, Any]]:
        signature = self._stat_signature()
        if self._cache is not None and signature == self._signature:
            return self._cache
        if not self.path.exists():
            self._cache = []
            self._signature = None
            return []
        events: list[dict[str, Any]] = []
        for number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise JournalError(f"invalid JSON at journal line {number}: {exc}") from exc
        self.verify(events)
        self._cache = events
        self._signature = signature
        return events

    @staticmethod
    def verify(events: list[dict[str, Any]]) -> None:
        previous = "GENESIS"
        for index, event in enumerate(events, 1):
            if event.get("sequence") != index:
                raise JournalError(f"sequence mismatch at {index}")
            if event.get("previous_hash") != previous:
                raise JournalError(f"previous hash mismatch at {index}")
            body = {key: value for key, value in event.items() if key != "event_hash"}
            digest = hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()
            if event.get("event_hash") != digest:
                raise JournalError(f"event hash mismatch at {index}")
            previous = digest

    def append(
        self,
        event_type: str,
        payload: dict[str, Any],
        *,
        event_id: str | None = None,
        occurred_at: str | None = None,
    ) -> AppendResult:
        return self.append_many(
            [(event_type, payload, event_id, occurred_at)]
        )[0]

    def append_many(
        self,
        records: list[tuple[str, dict[str, Any], str | None, str | None]],
    ) -> list[AppendResult]:
        with _exclusive_file_lock(self.lock_path):
            self._cache = None
            self._signature = None
            events = self.read()
            existing_by_id = {event["event_id"]: event for event in events}
            results: list[AppendResult] = []
            new_events: list[dict[str, Any]] = []
            previous_hash = events[-1]["event_hash"] if events else "GENESIS"
            for event_type, payload, event_id, occurred_at in records:
                identity = event_id or hashlib.sha256(
                    f"{event_type}:{canonical_json(payload)}".encode("utf-8")
                ).hexdigest()[:32]
                if identity in existing_by_id:
                    existing = existing_by_id[identity]
                    if existing["event_type"] != event_type or existing["payload"] != payload:
                        raise JournalError(f"idempotency collision for event_id {identity}")
                    results.append(AppendResult(existing, False))
                    continue
                body = {
                    "event_id": identity,
                    "sequence": len(events) + len(new_events) + 1,
                    "occurred_at": occurred_at or datetime.now(timezone.utc).isoformat(),
                    "event_type": event_type,
                    "payload": payload,
                    "previous_hash": previous_hash,
                }
                body["event_hash"] = hashlib.sha256(
                    canonical_json(body).encode("utf-8")
                ).hexdigest()
                previous_hash = body["event_hash"]
                existing_by_id[identity] = body
                new_events.append(body)
                results.append(AppendResult(body, True))
            if not new_events:
                return results
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.writelines(canonical_json(event) + "\n" for event in new_events)
                handle.flush()
                os.fsync(handle.fileno())
            events.extend(new_events)
            self._cache = events
            self._signature = self._stat_signature()
            return results

    @property
    def head(self) -> str:
        events = self.read()
        return events[-1]["event_hash"] if events else "GENESIS"
