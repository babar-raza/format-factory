"""test_precommit_exception_scoping.py — EP-007-EXCEPTION-SCAN-UNSCOPED-GAP fix
(discovered 2026-07-17 during SFC pilot-rerun verification).

The pre-commit skill-guard's check_exception_record() used to scan the ENTIRE
.local/exceptions/ directory for ANY file containing a matching substring, with
no expiry and no relevance check to the files being committed — a single stale
exception from an unrelated, already-completed mission silently bypassed the
skill-guard for every future commit. This fix requires every exception to
declare an unexpired `expires` and a non-empty `paths` scope, and only grants a
bypass when ALL staged files are covered by at least one valid exception.
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import date, timedelta
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".hooks" / "pre-commit-skill-guard"


def _load_hook_module():
    loader = SourceFileLoader("precommit_skill_guard_test", str(HOOK_PATH))
    spec = importlib.util.spec_from_loader("precommit_skill_guard_test", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


@pytest.fixture()
def hook(tmp_path):
    mod = _load_hook_module()
    mod.EXCEPTION_DIR = tmp_path
    return mod


def _write_exception(tmp_path: Path, name: str, **fields) -> None:
    lines = []
    for k, v in fields.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            lines.extend(f"  - {item}" for item in v)
        elif isinstance(v, bool):
            lines.append(f"{k}: {str(v).lower()}")
        else:
            lines.append(f'{k}: "{v}"')
    (tmp_path / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_no_exceptions_dir_fails_closed(hook, tmp_path):
    missing = tmp_path / "nonexistent"
    hook.EXCEPTION_DIR = missing
    assert hook.check_exception_record(["src/a.py"]) is False


def test_empty_staged_list_fails_closed(hook, tmp_path):
    _write_exception(tmp_path, "e.yaml", pre_commit_bypass=True,
                     expires=(date.today() + timedelta(days=30)).isoformat(),
                     paths=["src/a.py"])
    assert hook.check_exception_record([]) is False


def test_exception_missing_expires_is_invalid(hook, tmp_path):
    _write_exception(tmp_path, "e.yaml", pre_commit_bypass=True,
                     paths=["src/a.py"])
    assert hook.check_exception_record(["src/a.py"]) is False


def test_exception_missing_paths_is_invalid(hook, tmp_path):
    _write_exception(tmp_path, "e.yaml", pre_commit_bypass=True,
                     expires=(date.today() + timedelta(days=30)).isoformat())
    assert hook.check_exception_record(["src/a.py"]) is False


def test_expired_exception_does_not_bypass(hook, tmp_path):
    _write_exception(tmp_path, "e.yaml", pre_commit_bypass=True,
                     expires=(date.today() - timedelta(days=1)).isoformat(),
                     paths=["src/a.py"])
    assert hook.check_exception_record(["src/a.py"]) is False


def test_forbidden_reason_does_not_bypass(hook, tmp_path):
    _write_exception(tmp_path, "e.yaml", pre_commit_bypass=True,
                     expires=(date.today() + timedelta(days=30)).isoformat(),
                     paths=["src/a.py"], reason="urgent")
    assert hook.check_exception_record(["src/a.py"]) is False


def test_valid_exception_covers_exact_staged_file(hook, tmp_path):
    _write_exception(tmp_path, "e.yaml", pre_commit_bypass=True,
                     expires=(date.today() + timedelta(days=30)).isoformat(),
                     paths=["src/python/testfmt/foo.py"])
    assert hook.check_exception_record(["src/python/testfmt/foo.py"]) is True


def test_valid_exception_does_not_cover_unstaged_unrelated_file(hook, tmp_path):
    _write_exception(tmp_path, "e.yaml", pre_commit_bypass=True,
                     expires=(date.today() + timedelta(days=30)).isoformat(),
                     paths=["src/python/testfmt/foo.py"])
    assert hook.check_exception_record(["src/python/other/bar.py"]) is False


def test_partial_coverage_fails_closed_all_or_nothing(hook, tmp_path):
    """A staged set with ONE uncovered file must not get a blanket pass just
    because another file in the same commit happens to be covered."""
    _write_exception(tmp_path, "e.yaml", pre_commit_bypass=True,
                     expires=(date.today() + timedelta(days=30)).isoformat(),
                     paths=["src/python/testfmt/foo.py"])
    assert hook.check_exception_record(
        ["src/python/testfmt/foo.py", "src/python/other/bar.py"]) is False


def test_union_of_multiple_valid_exceptions_covers_all_staged(hook, tmp_path):
    _write_exception(tmp_path, "e1.yaml", pre_commit_bypass=True,
                     expires=(date.today() + timedelta(days=30)).isoformat(),
                     paths=["src/python/testfmt/foo.py"])
    _write_exception(tmp_path, "e2.yaml", pre_commit_bypass=True,
                     expires=(date.today() + timedelta(days=30)).isoformat(),
                     paths=["src/python/other/"])
    assert hook.check_exception_record(
        ["src/python/testfmt/foo.py", "src/python/other/bar.py"]) is True


def test_real_retrofitted_stale_exception_is_now_inert():
    """The exact live bug: the actual repo exception file
    fiop-full-001-src-healing.yaml, retrofitted with its true historical
    scope + an expiry the day after its mission completed, must no longer
    authorize anything today."""
    mod = _load_hook_module()  # uses the REAL .local/exceptions/ dir
    if not mod.EXCEPTION_DIR.exists():
        pytest.skip(".local/exceptions/ not present in this checkout")
    # Even its own originally-scoped files no longer get a bypass (expired).
    assert mod.check_exception_record(
        ["src/python/ods/ods_stats.py"]) is False
    # And a completely unrelated file certainly doesn't either.
    assert mod.check_exception_record(
        ["src/python/fods/models.py"]) is False


def test_malformed_yaml_file_is_skipped_not_fatal(hook, tmp_path):
    (tmp_path / "broken.yaml").write_text("not: valid: yaml: at: all:", encoding="utf-8")
    _write_exception(tmp_path, "good.yaml", pre_commit_bypass=True,
                     expires=(date.today() + timedelta(days=30)).isoformat(),
                     paths=["src/a.py"])
    assert hook.check_exception_record(["src/a.py"]) is True
