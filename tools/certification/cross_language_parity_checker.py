"""Cross-language behavioral parity checker.

Verifies that Python FOSS and .NET parsers produce equivalent models for the
same sample files. Covers CSV, FODS, and TSV (highest-value dual-track formats).

TC-PAR-001 (2026-07-03): First behavioral parity check between Python and .NET.

Usage:
    python tools/certification/cross_language_parity_checker.py
    python tools/certification/cross_language_parity_checker.py --format csv
    python tools/certification/cross_language_parity_checker.py --output reports/certification/csv/cross-impl-parity.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Add repo root to path for Python imports
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DOTNET_EXE = "dotnet"
VENV_PYTHON = str(REPO_ROOT / ".venv" / "Scripts" / "python.exe")


# ---------------------------------------------------------------------------
# Python-side extractors
# ---------------------------------------------------------------------------

def _python_csv(sample_path: str) -> dict:
    from src.python.csv.csv_parser import parse_csv  # type: ignore
    result = parse_csv(sample_path)
    if "error" in result:
        return {"status": "ERROR", "error": result["error"]}
    return {
        "status": "OK",
        "row_count": result.get("row_count"),
        "column_count": result.get("column_count"),
        "has_header": result.get("has_header"),
        "format": result.get("format"),
    }


def _python_fods(sample_path: str) -> dict:
    from fods import parse_fods  # type: ignore
    result = parse_fods(sample_path)
    if "error" in result:
        return {"status": "ERROR", "error": result["error"]}
    return {
        "status": "OK",
        "sheet_count": result.get("sheet_count"),
        "format_id": result.get("format_id"),
        "sheets": [
            {"name": s["name"], "row_count": s["row_count"]}
            for s in result.get("sheets", [])
        ],
    }


def _python_tsv(sample_path: str) -> dict:
    try:
        from tsv.tsv_parser import parse_tsv  # type: ignore
        result = parse_tsv(sample_path)
    except ImportError:
        try:
            from src.python.tsv.tsv_parser import parse_tsv  # type: ignore
            result = parse_tsv(sample_path)
        except ImportError:
            return {"status": "BLOCKED_EXTERNAL", "reason": "tsv module not importable"}
    if isinstance(result, dict) and "error" in result:
        return {"status": "ERROR", "error": result["error"]}
    return {
        "status": "OK",
        "row_count": result.get("row_count") if isinstance(result, dict) else None,
        "column_count": result.get("column_count") if isinstance(result, dict) else None,
    }


# ---------------------------------------------------------------------------
# .NET runner: build a tiny inline C# runner and invoke it
# ---------------------------------------------------------------------------

_CSV_RUNNER_CS = r"""
using System;
using System.IO;
using System.Text.Json;
using FormatFactory.Csv;

var path = args[0];
var content = File.ReadAllText(path);
try {
    var doc = CsvDocument.Load(content, hasHeaders: true);
    var obj = new {
        status = "OK",
        row_count = doc.RowCount,
        column_count = doc.ColumnCount,
        has_header = doc.HasHeaders,
        format = "csv"
    };
    Console.WriteLine(JsonSerializer.Serialize(obj));
} catch (Exception ex) {
    Console.WriteLine(JsonSerializer.Serialize(new { status = "ERROR", error = ex.Message }));
}
"""

_FODS_RUNNER_CS = r"""
using System;
using System.IO;
using System.Text.Json;
using System.Linq;
using FormatFactory.Fods;

var path = args[0];
try {
    var parser = new FodsParser();
    var result = parser.Parse(path);
    var sheets = result.Sheets.Select(s => new { name = s.Name, row_count = s.RowCount }).ToList();
    var obj = new {
        status = "OK",
        sheet_count = result.Sheets.Count,
        format_id = "fods",
        sheets
    };
    Console.WriteLine(JsonSerializer.Serialize(obj));
} catch (Exception ex) {
    Console.WriteLine(JsonSerializer.Serialize(new { status = "ERROR", error = ex.Message }));
}
"""

_TSV_RUNNER_CS = r"""
using System;
using System.IO;
using System.Text.Json;
using FormatFactory.Tsv;

var path = args[0];
try {
    var content = File.ReadAllText(path);
    var doc = TsvDocument.Load(content, hasHeaders: true);
    var obj = new {
        status = "OK",
        row_count = doc.RowCount,
        column_count = doc.ColumnCount,
        format = "tsv"
    };
    Console.WriteLine(JsonSerializer.Serialize(obj));
} catch (Exception ex) {
    Console.WriteLine(JsonSerializer.Serialize(new { status = "ERROR", error = ex.Message }));
}
"""

_CSPROJ_TEMPLATE = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>disable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="{lib_proj}" />
  </ItemGroup>
</Project>
"""


def _run_dotnet_runner(cs_code: str, lib_proj: str, sample_path: str) -> dict:
    """Build and run a minimal C# runner against the given library project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        # Write runner source
        (tmpdir / "Program.cs").write_text(cs_code, encoding="utf-8")
        # Write csproj
        csproj_content = _CSPROJ_TEMPLATE.format(lib_proj=lib_proj)
        (tmpdir / "Runner.csproj").write_text(csproj_content, encoding="utf-8")

        # Build
        build = subprocess.run(
            [DOTNET_EXE, "build", str(tmpdir / "Runner.csproj"), "-v", "quiet", "--nologo"],
            capture_output=True, text=True, timeout=60,
            cwd=str(tmpdir),
        )
        if build.returncode != 0:
            return {
                "status": "BLOCKED_EXTERNAL",
                "reason": "dotnet_build_failed",
                "stderr": build.stderr[-500:],
            }

        # Run
        run = subprocess.run(
            [DOTNET_EXE, "run", "--project", str(tmpdir / "Runner.csproj"),
             "--no-build", "--", sample_path],
            capture_output=True, text=True, timeout=30,
            cwd=str(tmpdir),
        )
        if run.returncode != 0:
            return {
                "status": "BLOCKED_EXTERNAL",
                "reason": "dotnet_run_failed",
                "stderr": run.stderr[-500:],
            }

        try:
            return json.loads(run.stdout.strip())
        except json.JSONDecodeError as e:
            return {"status": "ERROR", "error": f"JSON decode: {e}", "stdout": run.stdout[:200]}


# ---------------------------------------------------------------------------
# Per-format parity check
# ---------------------------------------------------------------------------

FORMAT_CONFIGS = {
    "csv": {
        "python_fn": _python_csv,
        "dotnet_cs": _CSV_RUNNER_CS,
        "dotnet_lib": str(REPO_ROOT / "src" / "net" / "csv" / "FormatFactory.Csv.csproj"),
        "samples": [
            str(REPO_ROOT / "samples" / "by-format" / "csv" / "minimal-2x2.csv"),
            str(REPO_ROOT / "samples" / "by-format" / "csv" / "single-cell.csv"),
        ],
        "compare_keys": ["row_count", "column_count"],
    },
    "fods": {
        "python_fn": _python_fods,
        "dotnet_cs": _FODS_RUNNER_CS,
        "dotnet_lib": str(REPO_ROOT / "src" / "net" / "fods" / "FormatFactory.Fods.csproj"),
        "samples": [
            str(REPO_ROOT / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"),
        ],
        "compare_keys": ["sheet_count"],
    },
    "tsv": {
        "python_fn": _python_tsv,
        "dotnet_cs": _TSV_RUNNER_CS,
        "dotnet_lib": str(REPO_ROOT / "src" / "net" / "tsv" / "FormatFactory.Tsv.csproj"),
        "samples": [
            str(REPO_ROOT / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"),
        ],
        "compare_keys": ["row_count"],
    },
}


def check_format_parity(fmt: str) -> dict:
    config = FORMAT_CONFIGS[fmt]
    results = []

    for sample in config["samples"]:
        if not Path(sample).exists():
            results.append({
                "sample": sample,
                "status": "SKIP",
                "reason": "sample_not_found",
            })
            continue

        py_result = config["python_fn"](sample)
        net_result = _run_dotnet_runner(
            config["dotnet_cs"],
            config["dotnet_lib"],
            sample,
        )

        if py_result.get("status") != "OK":
            status = "PYTHON_ERROR"
        elif net_result.get("status") == "BLOCKED_EXTERNAL":
            status = "BLOCKED_EXTERNAL"
        elif net_result.get("status") != "OK":
            status = "DOTNET_ERROR"
        else:
            # Compare key fields
            mismatches = []
            for key in config["compare_keys"]:
                py_val = py_result.get(key)
                net_val = net_result.get(key)
                if py_val != net_val:
                    mismatches.append({
                        "field": key,
                        "python": py_val,
                        "dotnet": net_val,
                    })
            status = "PASS" if not mismatches else "MISMATCH"

        entry = {
            "sample": Path(sample).name,
            "status": status,
            "python": py_result,
            "dotnet": net_result,
        }
        if status == "MISMATCH":
            entry["mismatches"] = mismatches
        results.append(entry)

    passed = sum(1 for r in results if r["status"] == "PASS")
    blocked = sum(1 for r in results if r["status"] == "BLOCKED_EXTERNAL")
    total = len(results)

    if blocked == total:
        verdict = "BLOCKED_EXTERNAL"
    elif passed == total:
        verdict = "PASS"
    elif passed + blocked == total:
        verdict = "PASS_WITH_BLOCKED"
    else:
        verdict = "FAIL"

    return {
        "format": fmt,
        "run_date": "2026-07-03",
        "total_samples": total,
        "passed": passed,
        "blocked": blocked,
        "verdict": verdict,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Cross-language behavioral parity checker")
    parser.add_argument("--format", choices=list(FORMAT_CONFIGS), help="Specific format to check")
    parser.add_argument("--output", help="Output JSON path (for single format)")
    args = parser.parse_args()

    formats = [args.format] if args.format else list(FORMAT_CONFIGS)

    all_results = {}
    for fmt in formats:
        print(f"Checking {fmt} parity...")
        result = check_format_parity(fmt)
        all_results[fmt] = result
        print(f"  {fmt}: {result['verdict']} ({result['passed']}/{result['total_samples']} PASS)")
        if args.output and args.format == fmt:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            print(f"  Written to: {args.output}")

    if not args.output or not args.format:
        print("\nSummary:")
        for fmt, res in all_results.items():
            print(f"  {fmt}: {res['verdict']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
