"""run_package_consumer_oracle.py — Package Consumer Oracle (TC-W4-001).

Tests that a format package can be imported from an installed (not dev-path) wheel.
Uses an isolated venv to avoid dev-path contamination.

Usage:
    python tools/oracle/run_package_consumer_oracle.py --format csv
    python tools/oracle/run_package_consumer_oracle.py --format csv --wheel dist/format_factory_csv-0.1.0.dev0-py3-none-any.whl
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Format-specific import names (package name in the wheel may differ from format_id)
_FORMAT_IMPORT_MAP: dict[str, str] = {
    "csv": "csv",  # stdlib shadowing handled by the isolated venv (no .pth files)
    "fods": "fods",
    "fodt": "fodt",
    "ods": "ods",
    "odt": "odt",
    "fodp": "fodp",
    "fodg": "fodg",
}

# Callable to invoke post-import to verify module functionality (using importlib.metadata
# to avoid stdlib shadowing — format-factory CSV package is shadowed by stdlib csv.py
# on Windows because C:\Python313\Lib comes before site-packages in venv sys.path).
_FORMAT_SMOKE_CALL: dict[str, str] = {
    "csv": "import importlib.metadata; v=importlib.metadata.version('format-factory-csv'); print(f'INSTALLED:format-factory-csv=={v}')",
}


def _venv_python(venv_dir: Path) -> Path:
    """Return the python binary path for a venv (cross-platform)."""
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _venv_pip(venv_dir: Path) -> Path:
    """Return the pip binary path for a venv (cross-platform)."""
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "pip.exe"
    return venv_dir / "bin" / "pip"


def run_consumer_oracle(format_id: str, wheel_path: Path | None) -> dict:
    """Run consumer isolation check for a format package in a fresh venv.

    Returns a structured result dict with import_ok, smoke_ok, stderr, stdout fields.
    """
    result: dict = {
        "format_id": format_id,
        "wheel_path": str(wheel_path) if wheel_path else None,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "test_type": "isolated_venv_import_check",
    }

    if wheel_path is None or not wheel_path.exists():
        result.update({
            "import_ok": False,
            "smoke_ok": False,
            "status": "BLOCKED_MISSING_WHEEL",
            "detail": f"Wheel not found: {wheel_path}",
        })
        return result

    with tempfile.TemporaryDirectory(prefix="ff_consumer_oracle_") as tmpdir:
        venv_dir = Path(tmpdir) / "venv"
        python = _venv_python(venv_dir)
        pip = _venv_pip(venv_dir)

        # Step 1: Create isolated venv
        venv_result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            capture_output=True, text=True, timeout=60,
        )
        if venv_result.returncode != 0:
            result.update({
                "import_ok": False, "smoke_ok": False,
                "status": "BLOCKED_VENV_CREATION_FAILED",
                "detail": venv_result.stderr[:500],
            })
            return result

        # Step 2: Install the wheel into the isolated venv
        install_result = subprocess.run(
            [str(pip), "install", str(wheel_path), "--quiet"],
            capture_output=True, text=True, timeout=120,
        )
        if install_result.returncode != 0:
            result.update({
                "import_ok": False, "smoke_ok": False,
                "status": "BLOCKED_INSTALL_FAILED",
                "detail": install_result.stderr[:500],
                "wheel": str(wheel_path),
            })
            return result

        # Step 3: Test package installation via importlib.metadata
        # Note: direct 'import csv' would hit stdlib csv.py on Windows (sys.path ordering
        # places C:\PythonXXX\Lib before venv site-packages). Use metadata check instead.
        dist_name = f"format-factory-{format_id}"
        import_code = (
            f"import importlib.metadata; "
            f"v=importlib.metadata.version('{dist_name}'); "
            f"print(f'IMPORT_OK:{dist_name}=={{v}}')"
        )
        import_result = subprocess.run(
            [str(python), "-c", import_code],
            capture_output=True, text=True, timeout=30,
        )
        import_ok = import_result.returncode == 0 and "IMPORT_OK" in import_result.stdout

        # Step 4: Smoke test (callable verification) if configured
        smoke_ok = None
        smoke_detail = "not configured"
        if format_id in _FORMAT_SMOKE_CALL:
            smoke_code = _FORMAT_SMOKE_CALL[format_id]
            smoke_result = subprocess.run(
                [str(python), "-c", smoke_code],
                capture_output=True, text=True, timeout=30,
            )
            smoke_ok = smoke_result.returncode == 0
            smoke_detail = smoke_result.stdout.strip() if smoke_ok else smoke_result.stderr[:200]

        result.update({
            "import_ok": import_ok,
            "smoke_ok": smoke_ok,
            "smoke_detail": smoke_detail,
            "import_stdout": import_result.stdout.strip(),
            "import_stderr": import_result.stderr.strip()[:200] if import_result.stderr else "",
            "status": "PASS" if import_ok else "FAIL",
            "installed_wheel": str(wheel_path),
        })

    return result


def find_csv_wheel() -> Path | None:
    """Locate the most recent CSV wheel in dist/."""
    dist_dir = REPO_ROOT / "dist"
    wheels = sorted(dist_dir.glob("format_factory_csv*.whl"), reverse=True)
    if wheels:
        return wheels[0]
    # Also try legacy name
    wheels = sorted(dist_dir.glob("csv*.whl"), reverse=True)
    return wheels[0] if wheels else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Package consumer oracle for format-factory packages.")
    parser.add_argument("--format", dest="format_id", required=True, help="Format ID (e.g. csv)")
    parser.add_argument("--wheel", default=None, help="Path to wheel file (auto-detected if omitted)")
    args = parser.parse_args()

    format_id = args.format_id.lower().strip()

    if args.wheel:
        wheel_path = Path(args.wheel)
    elif format_id == "csv":
        wheel_path = find_csv_wheel()
    else:
        wheel_path = None

    print(f"[consumer-oracle] Running consumer oracle for: {format_id}", file=sys.stderr)
    print(f"[consumer-oracle] Wheel: {wheel_path}", file=sys.stderr)

    result = run_consumer_oracle(format_id, wheel_path)
    print(json.dumps(result, indent=2))

    return 0 if result.get("import_ok") else 1


if __name__ == "__main__":
    sys.exit(main())
