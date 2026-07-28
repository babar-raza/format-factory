"""skill_gate_bridge.py — load the shared skill-gate checkers from validator context.

WHY THIS EXISTS (and why it is not just `from tools.governance.skill_gates import ...`)
---------------------------------------------------------------------------------------
The rules for three defect classes live ONCE, in `tools/governance/skill_gates/`, and are
called from two moments: creation time (the skills) and sprint time (V249/V250/V251). See
`docs/governance/skill-gate-validator-seam.md`. Validators must call those checkers rather
than re-implement them — a second implementation drifts, and this repo has already been
burned by exactly that (GVD-2026-07-17: a divergent dispatch path rotted silently for 10
days).

The obvious import does not work from validator context:

    from tools.governance.skill_gates import import_hygiene   # ModuleNotFoundError

`tools/` has no `__init__.py`, so `tools.governance...` is a namespace package resolvable
only when the REPO ROOT is on sys.path. The repo root is NOT injected by the editable-install
.pth files (they inject `src/python` and `src`) — verified 2026-07-17 from a neutral cwd. It
is on sys.path only incidentally, via `sys.path[0] == ''` when the interpreter's cwd happens
to be the repo root, or via pytest's `pythonpath = ["."]`. The seam doc's claim that "tools/
is importable from validator context" holds only under those conditions.

That makes the plain import CWD-DEPENDENT. In the runner, a failed import lands in an
`except` branch that appends to `_skipped_validators` — so V249 would silently NOT RUN
whenever the sweep is invoked from another directory, while the sweep still reports green.
That is the precise failure mode V249 exists to prevent, reintroduced in its own wiring.

The two alternatives were both worse:
  * `sys.path.insert(0, repo_root)` in the validator — V249 would be built from the exact
    anti-pattern it bans (this is PA-F3 / V149's sin, and it is why V149 could not be fully
    healed).
  * Duplicating the checker — the drift this bridge exists to prevent.

So: load the module from an ABSOLUTE PATH anchored on THIS file's location, via importlib.
No sys.path mutation, no cwd dependency, no duplication. The checkers import only stdlib
(verified), so loading each standalone is sound.

FAIL-CLOSED: if a checker cannot be loaded, this raises. Callers must let that surface as a
FAIL, never as a PASS — an enforcer that cannot load its rule has not certified anything.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

# tools/supervisor/skill_gate_bridge.py -> tools/governance/skill_gates/
_SKILL_GATES_DIR = Path(__file__).resolve().parent.parent / "governance" / "skill_gates"

_CACHE: dict[str, ModuleType] = {}


class SkillGateUnavailable(RuntimeError):
    """The shared checker could not be loaded. Never swallow this into a PASS."""


def load_skill_gate(module_name: str) -> ModuleType:
    """Load `tools/governance/skill_gates/<module_name>.py` by absolute path.

    Cached per process. Raises SkillGateUnavailable if the module is missing or will
    not execute — callers must fail closed on that.
    """
    if module_name in _CACHE:
        return _CACHE[module_name]

    path = _SKILL_GATES_DIR / f"{module_name}.py"
    if not path.is_file():
        raise SkillGateUnavailable(
            f"shared skill-gate checker not found: {path}. V249/V250/V251 delegate "
            f"detection to tools/governance/skill_gates/ (see "
            f"docs/governance/skill-gate-validator-seam.md); without it they cannot enforce."
        )

    # A distinct module name avoids colliding with any real `tools.governance...` import
    # that a caller may already have performed.
    qualname = f"_ff_skill_gate_{module_name}"
    if qualname in sys.modules:
        _CACHE[module_name] = sys.modules[qualname]
        return _CACHE[module_name]

    spec = importlib.util.spec_from_file_location(qualname, path)
    if spec is None or spec.loader is None:
        raise SkillGateUnavailable(f"could not build an import spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[qualname] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:  # noqa: BLE001 — surface the real cause, fail closed
        sys.modules.pop(qualname, None)
        raise SkillGateUnavailable(f"{path} failed to execute: {exc!r}") from exc

    _CACHE[module_name] = mod
    return mod


def import_hygiene() -> ModuleType:
    """Shared AST sys.path detector (alias-resolving). Public API: check_source/check_file/check_paths."""
    return load_skill_gate("import_hygiene")


def namespace_collision() -> ModuleType:
    """Shared stdlib/popular-package name collision checker. Public API: check_name/stdlib_names."""
    return load_skill_gate("namespace_collision")


def converter_compat() -> ModuleType:
    """Shared converter compatibility checker. Public API: load_matrix/check_pair/pair_id."""
    return load_skill_gate("converter_compat")
