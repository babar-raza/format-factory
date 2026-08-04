"""IPYNB-EXEC-001, second clause: the core path must never execute notebook code.

The obligation reads: "Keep execution in an opt-in adapter with kernel
selection, timeouts, error policy, and isolation boundary; return a structured
execution report; never execute during load/validate/diff/save."

Only the second half is testable today. There is no execution adapter in the
package -- the sole `kernel` references are kernelspec *metadata* parsing -- so
the timeout, kernel-failure and partial-output cases the requirement also names
cannot be written against anything. That half is recorded `missing` in the
ledger rather than papered over here.

The no-execution half matters on its own: a notebook is untrusted input, and a
loader that evaluated cell source would be a remote-code-execution hole. These
tests prove it with a CPython audit hook rather than by observing side effects,
because absence of an observed side effect is weak evidence -- it only shows the
particular payload chosen did not fire. The audit hook fails on the *attempt*.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import pytest

from format_factory.ipynb import diff_notebooks, dumps, loads, upgrade, validate

# CPython audit events raised by any code-execution or process-spawning path.
FORBIDDEN_EVENTS = (
    "exec",
    "compile",
    "subprocess.Popen",
    "os.system",
    "os.exec",
    "os.spawn",
    "os.fork",
    "socket.connect",
    "urllib.Request",
)

# Payloads that would be conspicuous if any of them ever ran.
HOSTILE_SOURCES = [
    "import os; os.system('echo pwned')",
    "__import__('subprocess').Popen(['echo', 'pwned'])",
    "eval(\"__import__('os').system('echo pwned')\")",
    "exec(compile('x=1', '<n>', 'exec'))",
    "import urllib.request; urllib.request.urlopen('http://example.invalid')",
]


class _AuditRecorder:
    """Records forbidden audit events raised while active."""

    def __init__(self) -> None:
        self.events: list[str] = []
        self._armed = False

    def hook(self, event: str, args: tuple[Any, ...]) -> None:
        if not self._armed:
            return
        for forbidden in FORBIDDEN_EVENTS:
            if event == forbidden or event.startswith(forbidden):
                self.events.append(event)

    def __enter__(self) -> "_AuditRecorder":
        self._armed = True
        return self

    def __exit__(self, *exc: object) -> None:
        self._armed = False


@pytest.fixture(scope="module")
def recorder() -> _AuditRecorder:
    """One hook for the module -- audit hooks cannot be removed once added."""
    instance = _AuditRecorder()
    sys.addaudithook(instance.hook)
    return instance


def _notebook(sources: list[str]) -> dict[str, Any]:
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {},
        "cells": [
            {
                "cell_type": "code",
                "id": f"cell-{index}",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": source,
            }
            for index, source in enumerate(sources)
        ],
    }


def _assert_no_execution(recorder: _AuditRecorder, operation: str) -> None:
    assert not recorder.events, (
        f"{operation} raised code-execution audit events {recorder.events}; "
        "the core path must never execute notebook source"
    )


# ── The audit hook itself must work, or every test below is vacuous ────────


def test_the_audit_hook_actually_detects_execution(recorder: _AuditRecorder) -> None:
    """A guard that cannot fire proves nothing. This proves it fires."""
    with recorder:
        recorder.events.clear()
        exec(compile("_ = 1", "<probe>", "exec"))  # noqa: S102
        detected = list(recorder.events)
    assert detected, "the audit hook did not observe a real exec; the suite would be vacuous"


# ── load / validate / diff / save must not execute ─────────────────────────


@pytest.mark.parametrize("source", HOSTILE_SOURCES)
def test_load_never_executes_cell_source(recorder: _AuditRecorder, source: str) -> None:
    payload = json.dumps(_notebook([source]))
    with recorder:
        recorder.events.clear()
        loads(payload)
    _assert_no_execution(recorder, "loads()")


@pytest.mark.parametrize("source", HOSTILE_SOURCES)
def test_validate_never_executes_cell_source(
    recorder: _AuditRecorder, source: str
) -> None:
    notebook = _notebook([source])
    with recorder:
        recorder.events.clear()
        validate(notebook, profile="4.5")
    _assert_no_execution(recorder, "validate()")


@pytest.mark.parametrize("source", HOSTILE_SOURCES)
def test_save_never_executes_cell_source(recorder: _AuditRecorder, source: str) -> None:
    document = loads(json.dumps(_notebook([source])))
    with recorder:
        recorder.events.clear()
        dumps(document)
    _assert_no_execution(recorder, "dumps()")


def test_diff_never_executes_cell_source(recorder: _AuditRecorder) -> None:
    left = loads(json.dumps(_notebook(HOSTILE_SOURCES[:2])))
    right = loads(json.dumps(_notebook(HOSTILE_SOURCES[2:4])))
    with recorder:
        recorder.events.clear()
        diff_notebooks(left, right)
    _assert_no_execution(recorder, "diff_notebooks()")


def test_upgrade_never_executes_cell_source(recorder: _AuditRecorder) -> None:
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 4,
        "metadata": {},
        "cells": [
            {
                "cell_type": "code",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": HOSTILE_SOURCES[0],
            }
        ],
    }
    with recorder:
        recorder.events.clear()
        upgrade(notebook)
    _assert_no_execution(recorder, "upgrade()")


def test_full_lifecycle_over_every_hostile_payload_executes_nothing(
    recorder: _AuditRecorder,
) -> None:
    """The whole documented core path in one pass, over all payloads at once."""
    payload = json.dumps(_notebook(HOSTILE_SOURCES))
    with recorder:
        recorder.events.clear()
        document = loads(payload)
        validate(json.loads(payload), profile="4.5")
        diff_notebooks(document, loads(payload))
        dumps(document)
    _assert_no_execution(recorder, "load -> validate -> diff -> save")


# ── Hostile payloads in places other than cell source ──────────────────────


def test_hostile_metadata_is_not_executed(recorder: _AuditRecorder) -> None:
    notebook = _notebook(["x = 1"])
    notebook["metadata"]["x-payload"] = HOSTILE_SOURCES[0]
    notebook["cells"][0]["metadata"]["x-payload"] = HOSTILE_SOURCES[1]
    with recorder:
        recorder.events.clear()
        dumps(loads(json.dumps(notebook)))
    _assert_no_execution(recorder, "metadata round-trip")


def test_hostile_output_payload_is_not_executed(recorder: _AuditRecorder) -> None:
    notebook = _notebook(["x = 1"])
    notebook["cells"][0]["outputs"] = [
        {
            "output_type": "display_data",
            "data": {"text/plain": HOSTILE_SOURCES[0], "text/html": "<script>x</script>"},
            "metadata": {},
        }
    ]
    with recorder:
        recorder.events.clear()
        dumps(loads(json.dumps(notebook)))
    _assert_no_execution(recorder, "output round-trip")


# ── The package ships no execution surface at all ──────────────────────────


def test_public_api_exposes_no_execution_entry_point() -> None:
    """The obligation puts execution behind an opt-in adapter. There is no
    adapter today, so there must be no execution entry point either -- an
    execute() on the core API would violate the isolation boundary."""
    import format_factory.ipynb as package

    exported = {name.lower() for name in package.__all__}
    for forbidden in ("execute", "run", "runcell", "executenotebook", "kernel"):
        assert forbidden not in exported, (
            f"{forbidden!r} is exported from the core API; execution must live "
            "in an opt-in adapter"
        )
