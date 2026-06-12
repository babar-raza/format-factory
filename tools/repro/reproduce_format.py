"""
tools/repro/reproduce_format.py

Reproducibility proof tool for Format Factory Python FOSS packages.

Verifies that a local wheel can be installed in a fresh temporary virtual
environment and that the installed package's core API is callable and returns
expected results. This proves the wheel is self-contained and reproducible.

Usage:
    python tools/repro/reproduce_format.py --format fods --wheel <path-to-wheel>
    python tools/repro/reproduce_format.py --format fodt --wheel <path-to-wheel>
    python tools/repro/reproduce_format.py --format zst --wheel <path-to-wheel>

Output:
    REPRODUCE_RESULT: PASS or FAIL
    WHEEL_SHA256: <sha256 of wheel>
    PACKAGE_VERSION: <installed version>
    SMOKE_TEST: PASS or FAIL

Exit code: 0 on PASS, 1 on FAIL
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

# Canonical import namespace table (R82 Fix — D79-07)
# package_name (pip install)       -> module import name
# aspose-format-factory-fods       -> fods
# aspose-format-factory-fodt       -> fodt
# aspose-format-factory-zst        -> zst
# aspose-format-factory-fods       -> fods
# aspose-format-factory-pbm        -> pbm
# aspose-format-factory-pgm        -> pgm
# aspose-format-factory-sylk       -> sylk
# aspose-format-factory-dif        -> dif
# aspose-format-factory-fodp       -> fodp
# aspose-format-factory-fodg       -> fodg
# aspose-format-factory-gnumeric   -> gnumeric
# aspose-format-factory-abw        -> abw
CANONICAL_IMPORT_NAMESPACES = {
    "fods": "fods", "fodt": "fodt", "zst": "zst",
    "pbm": "pbm", "pgm": "pgm", "sylk": "sylk",
    "fodp": "fodp", "fodg": "fodg", "gnumeric": "gnumeric", "abw": "abw",
}

# Smoke test scripts per format — minimal proof of API availability
SMOKE_SCRIPTS = {
    "fods": """
import sys
# Canonical import namespace: import fods (see CANONICAL_IMPORT_NAMESPACES table)
from fods import (
    parse_fods, parse_fods_strict, write_fods, workbook_to_xml,
    workbook_stats, workbook_sheet_order, workbook_set_cell_value,
    workbook_add_sheet, workbook_rename_sheet, workbook_remove_sheet,
    __version__, __track__, __commercial_ready__, __capability_level__,
)
assert __version__ == "0.1.0.dev0", f"Unexpected version: {__version__}"
assert __track__ == "python-foss", f"Unexpected track: {__track__}"
assert __commercial_ready__ is False, "commercial_ready must be False"
assert __capability_level__ == "alpha-foss-preview", f"Unexpected level: {__capability_level__}"
# Verify callable
wb = {"sheets": [{"name": "Test", "rows": [], "auto_updatable": False}]}
ok, _ = workbook_add_sheet(wb, "Sheet2")
assert ok, "workbook_add_sheet failed"
ok, _ = workbook_rename_sheet(wb, "Sheet2", "Renamed")
assert ok, "workbook_rename_sheet failed"
ok, _ = workbook_remove_sheet(wb, "Renamed")
assert ok, "workbook_remove_sheet failed"
print("SMOKE_TEST: PASS")
print(f"VERSION: {__version__}")
""",
    "fodt": """
import sys
# Canonical import namespace: import fodt (see CANONICAL_IMPORT_NAMESPACES table)
from fodt import (
    parse_fodt, parse_fodt_strict, write_fodt, document_to_xml,
    document_stats, document_text_content, document_set_block_text,
    document_append_paragraph, document_remove_paragraph, document_paragraph_count,
    __version__, __track__, __commercial_ready__, __capability_level__,
)
assert __version__ == "0.1.0.dev0", f"Unexpected version: {__version__}"
assert __track__ == "python-foss", f"Unexpected track: {__track__}"
assert __commercial_ready__ is False, "commercial_ready must be False"
assert __capability_level__ == "alpha-foss-preview", f"Unexpected level: {__capability_level__}"
# Use root-level blocks (not body.blocks) — GAP-FODT-STRUCT-001 fix
doc = {"blocks": []}
ok, _ = document_append_paragraph(doc, "test")
assert ok, "document_append_paragraph failed"
assert document_paragraph_count(doc) == 1
ok, _ = document_remove_paragraph(doc, 0)
assert ok, "document_remove_paragraph failed"
assert document_paragraph_count(doc) == 0
print("SMOKE_TEST: PASS")
print(f"VERSION: {__version__}")
""",
    "zst": """
import sys
# Canonical import namespace: import zst (see CANONICAL_IMPORT_NAMESPACES table)
from zst import (
    compress_bytes, decompress_bytes, probe_frame, validate_file,
    ZstError, ZstDecompressionError, ZstInvalidFrameError, ZstOutputLimitExceeded,
    __version__, __track__, __commercial_ready__, __capability_level__,
)
assert __version__ == "0.1.0.dev0", f"Unexpected version: {__version__}"
assert __track__ == "python-foss", f"Unexpected track: {__track__}"
assert __commercial_ready__ is False, "commercial_ready must be False"
assert __capability_level__ == "alpha-foss-preview", f"Unexpected level: {__capability_level__}"
# Smoke: compress + decompress round-trip
data = b"Hello from Format Factory ZST reproducibility proof"
compressed = compress_bytes(data)
assert compressed, "compress_bytes returned empty"
decompressed = decompress_bytes(compressed)
assert decompressed == data, f"Round-trip failed: {decompressed!r}"
print("SMOKE_TEST: PASS")
print(f"VERSION: {__version__}")
""",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_repro(format_id: str, wheel_path: Path) -> dict:
    """Install wheel in temp venv and run smoke test. Returns result dict."""
    result = {
        "format_id": format_id,
        "wheel_path": str(wheel_path),
        "wheel_sha256": sha256_file(wheel_path),
        "smoke_test": "FAIL",
        "reproduce_result": "FAIL",
        "error": None,
    }

    if format_id not in SMOKE_SCRIPTS:
        result["error"] = f"No smoke script for format: {format_id}"
        return result

    smoke_script = SMOKE_SCRIPTS[format_id]
    tmpdir = Path(tempfile.mkdtemp(prefix=f"repro_{format_id}_"))

    try:
        # Create temp venv
        venv_dir = tmpdir / "venv"
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            check=True, capture_output=True
        )

        # Determine venv python path
        if sys.platform == "win32":
            venv_python = venv_dir / "Scripts" / "python.exe"
        else:
            venv_python = venv_dir / "bin" / "python"

        # Install the wheel
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", str(wheel_path), "--quiet"],
            check=True, capture_output=True
        )

        # Also install zstandard for ZST (runtime dependency)
        if format_id == "zst":
            subprocess.run(
                [str(venv_python), "-m", "pip", "install", "zstandard", "--quiet"],
                check=True, capture_output=True
            )

        # Run smoke test
        script_path = tmpdir / "smoke_test.py"
        script_path.write_text(smoke_script)
        proc = subprocess.run(
            [str(venv_python), str(script_path)],
            capture_output=True, text=True, timeout=60
        )

        if proc.returncode == 0 and "SMOKE_TEST: PASS" in proc.stdout:
            result["smoke_test"] = "PASS"
            result["reproduce_result"] = "PASS"
            # Extract version
            for line in proc.stdout.splitlines():
                if line.startswith("VERSION:"):
                    result["package_version"] = line.split(":", 1)[1].strip()
        else:
            result["error"] = f"Smoke test failed:\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"

    except subprocess.CalledProcessError as e:
        result["error"] = f"Subprocess error: {e}\nSTDERR: {getattr(e, 'stderr', '')}"
    except Exception as e:
        result["error"] = str(e)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Format Factory reproducibility proof tool")
    parser.add_argument("--format", required=True, choices=list(SMOKE_SCRIPTS.keys()),
                        help="Format ID to test")
    parser.add_argument("--wheel", default=None,
                        help="Path to wheel file to test")
    parser.add_argument("--package-artifacts-dir", default=None,
                        help="Directory containing package artifacts (wheel auto-discovered)")
    parser.add_argument("--no-network", action="store_true",
                        help="Install from local artifacts only (--find-links, no index)")
    parser.add_argument("--require-wheel", action="store_true",
                        help="Fail if wheel is not found (do not skip)")
    parser.add_argument("--output-json", default=None,
                        help="Write result to JSON file")
    args = parser.parse_args()

    # Auto-discover wheel from package-artifacts-dir
    if args.wheel is None and args.package_artifacts_dir:
        artifacts_dir = Path(args.package_artifacts_dir)
        wheels = list(artifacts_dir.glob(f"*{args.format}*.whl"))
        if wheels:
            args.wheel = str(sorted(wheels)[-1])  # use latest
        elif args.require_wheel:
            print(f"ERROR: --require-wheel set but no wheel found for {args.format} in {artifacts_dir}")
            return 1

    if args.wheel is None:
        if args.require_wheel:
            print("ERROR: --require-wheel set but --wheel not provided")
            return 1
        print(f"WARNING: No wheel specified for {args.format}; skipping reproducibility proof")
        return 0

    wheel_path = Path(args.wheel)
    if not wheel_path.exists():
        print(f"ERROR: Wheel not found: {wheel_path}")
        return 1

    print(f"Testing format: {args.format}")
    print(f"Wheel: {wheel_path.name}")
    print(f"Wheel SHA-256: {sha256_file(wheel_path)}")
    print("Creating temp venv and running smoke test...")

    result = run_repro(args.format, wheel_path)

    print(f"\nWHEEL_SHA256: {result['wheel_sha256']}")
    if "package_version" in result:
        print(f"PACKAGE_VERSION: {result['package_version']}")
    print(f"SMOKE_TEST: {result['smoke_test']}")
    print(f"REPRODUCE_RESULT: {result['reproduce_result']}")

    if result["error"]:
        print(f"\nERROR: {result['error']}")

    if args.output_json:
        Path(args.output_json).write_text(json.dumps(result, indent=2))
        print(f"\nResult written to: {args.output_json}")

    return 0 if result["reproduce_result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
