"""governance_validators_gate9_docs_dogfood.py — V228, V229
(TC-S6P4-SYS-003, select-6 Phase 4; hardened TC-S6P4-FINAL-001c, select-6
Phase 4 final re-audit, 2026-07-16)

Both validators close SF3: neither README existence nor dogfood cross-
product export existence was checked by any of the 225+ validators this
project otherwise relies on heavily, so both gaps were invisible for the
select-6 formats until a human-directed audit found them by hand. Wired to
the same grandfather baseline as V227 (registry/gate9-coverage-baseline.yaml)
so pre-Phase-3 formats -- which already independently satisfy both -- are
not retroactively re-litigated by a new rule; any format authorized after
2026-07-15 must satisfy both going forward.

The final independent re-audit found the original V228/V229 only checked
existence, despite V228's docstring claiming readme_sync validation and
V229 claiming a "tested" export without ever running the test. Both are
hardened here to match what they claim:

V228: validate_format_readme_exists
    FAIL (blocks) when an implementation_authorized format lacks
    src/python/<fmt>/README.md, OR the README exists but fails
    tools.readme_sync.validator.validate_readme() (marker begin/end
    integrity, generated package/version claims match real state, no
    broken relative links).

V229: validate_dogfood_export_exists
    FAIL (blocks) when an implementation_authorized format has no
    src/python/<fmt>/<fmt>_to_<target>.py export module with at least one
    corresponding test in tests/python/<fmt>/, OR that test file exists but
    does not actually pass when executed via pytest -- existence of a test
    file proves nothing about whether the export function works.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

from governance_validators_contract import validator

_BASELINE_REL = "registry/gate9-coverage-baseline.yaml"
_TEST_TIMEOUT_SECONDS = 120


def _result(name: str, result: str, summary: str, blocks: bool) -> dict:
    return {"validator": name, "result": result, "summary": summary, "blocks_sprint": blocks}


def _load_registry(repo: Path) -> list[dict] | None:
    path = repo / "registry" / "format-registry.yaml"
    if not path.exists():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    formats = data.get("formats", data)
    if isinstance(formats, dict):
        return list(formats.values())
    if isinstance(formats, list):
        return formats
    return None


def _load_grandfathered(repo: Path) -> set[str]:
    path = repo / _BASELINE_REL
    if not path.exists():
        return set()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return set()
    return {e["format_id"] for e in data.get("grandfathered_pre_phase3", [])
            if e.get("format_id")}


def _authorized_non_grandfathered(repo: Path) -> list[str] | None:
    formats = _load_registry(repo)
    if formats is None:
        return None
    grandfathered = _load_grandfathered(repo)
    return sorted(
        f.get("format_id") for f in formats
        if f.get("implementation_authorized") is True
        and f.get("format_id") not in grandfathered
    )


def _validate_readme_content(repo: Path, fmt: str, readme_path: Path) -> tuple[str, list[str]]:
    """Best-effort call into tools.readme_sync.validator.validate_readme().
    Returns (status, problems): status is "ok" (content genuinely validated
    and clean), "invalid" (genuinely validated and found real errors -- this
    is the only status that should block a sprint), or "unverifiable" (the
    validator could not be loaded or raised, e.g. because `fmt` has no real
    src/python/<fmt>/ state for collect_format_state() to read -- must not
    silently grant PASS, but also must not FAIL on a tooling limitation)."""
    try:
        if str(repo) not in sys.path:
            sys.path.insert(0, str(repo))
        from tools.readme_sync.validator import validate_readme  # noqa: PLC0415
    except Exception as exc:
        return "unverifiable", [f"readme_sync validator unavailable ({exc})"]
    try:
        result = validate_readme(readme_path, fmt, "python")
    except Exception as exc:
        return "unverifiable", [f"validate_readme() raised {exc!r}"]
    if result.ok:
        return "ok", []
    return "invalid", list(result.errors)


@validator(rule_id="V228", domain="governance")
def validate_format_readme_exists(declaration: dict, repo_root: "Path | None" = None) -> dict:
    name = "validate_format_readme_exists"
    repo = Path(repo_root) if repo_root else Path(__file__).resolve().parent.parent.parent
    targets = _authorized_non_grandfathered(repo)
    if targets is None:
        return _result(name, "WARN", f"{name}: registry unreadable", False)
    if not targets:
        return _result(name, "PASS", "V228: no non-grandfathered authorized formats", False)

    missing = [f for f in targets if not (repo / "src" / "python" / f / "README.md").exists()]
    if missing:
        return _result(
            name, "FAIL",
            f"V228: implementation_authorized format(s) missing src/python/<fmt>/README.md: "
            f"{missing} -- generate via: python -m tools.readme_sync.run_sync "
            f"--mode single --format <fmt> --track python",
            True,
        )

    present = [f for f in targets if f not in missing]
    unverifiable: list[str] = []
    invalid: list[str] = []
    for fmt in present:
        readme_path = repo / "src" / "python" / fmt / "README.md"
        status, problems = _validate_readme_content(repo, fmt, readme_path)
        if status == "unverifiable":
            unverifiable.append(fmt)
        elif status == "invalid":
            invalid.append(f"{fmt}: {'; '.join(problems)}")
    if invalid:
        return _result(
            name, "FAIL",
            "V228: README(s) present but fail readme_sync validation for "
            + "; ".join(invalid) +
            " -- run: python -m tools.readme_sync.run_sync --mode validate --format <fmt> --track python",
            True,
        )
    if unverifiable:
        return _result(
            name, "WARN",
            f"V228: {len(unverifiable)} README(s) exist but content could not be verified via "
            f"readme_sync validator ({unverifiable}); presence-only check passed",
            False,
        )
    return _result(name, "PASS",
                   f"V228: all {len(targets)} authorized format(s) have a README that passes "
                   f"readme_sync validation",
                   False)


def _dogfood_test_passes(repo: Path, test_path: Path) -> bool | None:
    """Actually execute the dogfood test file via pytest. Returns True/False
    on a real run, or None if pytest itself could not be invoked (caller
    treats None as WARN, not silent PASS)."""
    venv_pytest = repo / ".venv" / "Scripts" / "pytest.exe"
    cmd = [str(venv_pytest)] if venv_pytest.exists() else [sys.executable, "-m", "pytest"]
    cmd += [str(test_path), "-q", "--tb=no", "-p", "no:cacheprovider"]
    try:
        with tempfile.TemporaryDirectory():
            proc = subprocess.run(
                cmd, cwd=str(repo), capture_output=True, text=True,
                timeout=_TEST_TIMEOUT_SECONDS,
            )
    except (subprocess.SubprocessError, OSError):
        return None
    return proc.returncode == 0


@validator(rule_id="V229", domain="governance")
def validate_dogfood_export_exists(declaration: dict, repo_root: "Path | None" = None) -> dict:
    name = "validate_dogfood_export_exists"
    repo = Path(repo_root) if repo_root else Path(__file__).resolve().parent.parent.parent
    targets = _authorized_non_grandfathered(repo)
    if targets is None:
        return _result(name, "WARN", f"{name}: registry unreadable", False)
    if not targets:
        return _result(name, "PASS", "V229: no non-grandfathered authorized formats", False)

    missing = []
    unexecutable: list[str] = []
    failing: list[str] = []
    for fmt in targets:
        src_dir = repo / "src" / "python" / fmt
        test_dir = repo / "tests" / "python" / fmt
        exports = list(src_dir.glob(f"{fmt}_to_*.py")) if src_dir.is_dir() else []
        if not exports:
            missing.append(f"{fmt}: no src/python/{fmt}/{fmt}_to_*.py export module")
            continue
        test_files = [
            test_dir / f"test_{e.stem}.py" for e in exports
        ] if test_dir.is_dir() else []
        test_files = [t for t in test_files if t.exists()]
        if not test_files:
            missing.append(f"{fmt}: export module(s) {[e.name for e in exports]} have no "
                          f"matching test in tests/python/{fmt}/")
            continue
        outcome = _dogfood_test_passes(repo, test_files[0])
        if outcome is None:
            unexecutable.append(fmt)
        elif outcome is False:
            failing.append(f"{fmt}: {test_files[0].relative_to(repo)} exists but does not pass")
    if missing or failing:
        problems = missing + failing
        return _result(
            name, "FAIL",
            "V229: dogfood export gap for " + "; ".join(problems) +
            " -- use /add-dogfood-export",
            True,
        )
    if unexecutable:
        return _result(
            name, "WARN",
            f"V229: {len(unexecutable)} dogfood test(s) could not be executed to verify "
            f"({unexecutable}); presence-only check passed",
            False,
        )
    return _result(name, "PASS",
                   f"V229: all {len(targets)} authorized format(s) have a dogfood export with a "
                   f"passing test",
                   False)
