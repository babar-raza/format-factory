"""test_settings_src_allow_scoped.py — SFC-GAP-A (2026-07-17).

Static regression guard: `.claude/settings.json`'s `permissions.allow` list
must never contain a blanket `Write(src/**)`-style entry for product source.
Per the production hardening plan, src/ writes are sequenced to depend on
Gap C's tool-layer skill-resolution check reaching `enforcing` for `src/**`
specifically (with real would-block-rate evidence from the analyzer) before
any widening happens — and even then, only incrementally, per-format, never
as a blanket re-open of the coarse case this whole design exists to replace.

This guard does not (and cannot) verify the *authorization process* was
followed — it verifies the *artifact*: any current or future `Write(src/...)`
allow entry must be scoped to a specific, named format directory (at least
one literal path segment under `src/python/` or `src/net/` before any glob
wildcard appears), never a bare/blanket wildcard.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = REPO_ROOT / ".claude" / "settings.json"

# A scoped src/ allow must have a literal (non-glob) directory segment
# between the src/{python,net}/ root and the first wildcard character.
_SCOPED_SRC_RE = re.compile(
    r"^src/(python|net)/[A-Za-z0-9_.\-]+/"  # literal format dir, e.g. fods/
)
_GLOB_CHARS = set("*?[")


def _load_permissions() -> dict:
    data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    return data.get("permissions", {})


def _write_entries(rules: list, prefix: str = "Write(") -> list:
    out = []
    for r in rules:
        if isinstance(r, str) and r.startswith(prefix) and r.endswith(")"):
            out.append(r[len(prefix):-1])
    return out


def test_settings_file_exists_and_parses():
    assert SETTINGS_PATH.exists()
    perms = _load_permissions()
    assert "allow" in perms


def test_no_blanket_src_write_allow_exists_today():
    """Ground-truth snapshot: today's allow list has zero Write(src/**)-style
    blanket entries (only exact _readme.md file allows). This pins the
    current, intentional state so a future PR that widens it is forced to
    go through THIS test (and be scoped), not silently pass unnoticed."""
    perms = _load_permissions()
    src_allows = [p for p in _write_entries(perms.get("allow", []))
                 if p.startswith("src/")]
    for p in src_allows:
        assert not any(c in p for c in _GLOB_CHARS), (
            f"Write({p}) in the allow list is a glob pattern under src/, but "
            "today's baseline should contain only exact, non-glob file "
            f"allows (e.g. src/python/_readme.md). Found: {p}"
        )


def test_any_future_src_glob_allow_must_be_format_scoped():
    """The actual regression guard: if/when a glob-pattern Write(src/**)
    allow is ever added, it MUST be scoped to a named format directory."""
    perms = _load_permissions()
    src_allows = [p for p in _write_entries(perms.get("allow", []))
                 if p.startswith("src/") and any(c in p for c in _GLOB_CHARS)]
    for p in src_allows:
        assert _SCOPED_SRC_RE.match(p), (
            f"Write({p}) is a src/ glob allow with no literal format-directory "
            "scope before the wildcard — this reopens the blanket case the "
            "Skills-First Control production hardening plan explicitly "
            "sequences behind Gap C's staged rollout. Scope it to a specific "
            "format, e.g. Write(src/python/{format}/**)."
        )


def test_deny_list_still_carries_the_coarse_boundary():
    """The coarse denies must remain in place as the outer boundary; this
    guard does not (yet) verify the fine-grained Gap C authorizer is live for
    a given format — only that the static wall hasn't been silently removed."""
    perms = _load_permissions()
    deny_entries = _write_entries(perms.get("deny", []))
    assert any(p.startswith("src/python/") for p in deny_entries)
    assert any(p.startswith("src/net/") for p in deny_entries)
