"""Portfolio certification dashboard generator.

Reads all reports/certification/{fmt}/ directories and produces a portfolio-wide
certification matrix and markdown report.

mission_id: CERT-EXHAUST-20260628
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
CERT_ROOT = REPO_ROOT / "reports" / "certification"

ALL_FORMATS = [
    "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt", "gnumeric",
    "ndjson", "ods", "odt", "pbm", "pgm", "ppm", "qoi", "sylk",
    "toml", "tsv", "xcf", "zst",
]

DIMENSIONS = [
    "api_contract", "traceability", "stubs", "exceptions", "oracle",
    "test_quality", "roundtrip", "package", "consumer",
]


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_json_with_manifest_check(
    path: Path, run_manifest_paths: "set[str] | None"
) -> "tuple[dict[str, Any], bool]":
    """Load JSON and report whether the file was in the run manifest.

    Returns: (data_dict, in_manifest)
    - in_manifest=False means MISSING_EVIDENCE (not in run manifest)
    - in_manifest=True means the report was part of a coherent run
    - when run_manifest_paths is None, behaves like _load_json (no manifest check)
    """
    if run_manifest_paths is not None:
        # Convert path to relative form for comparison
        try:
            rel = path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            rel = path.as_posix()
        if rel not in run_manifest_paths:
            return {}, False
    return _load_json(path), True


def _dim_status(data: dict[str, Any], key: str = "status", default: str = "NOT_AUDITED") -> str:
    return data.get(key, data.get("alignment_status", data.get("status", default)))


def collect_format_status(fmt: str, use_run_manifest: bool = True) -> dict[str, Any]:
    fmt_dir = CERT_ROOT / fmt
    if not fmt_dir.exists():
        return {"format_id": fmt, "status": "NOT_STARTED", "dimensions": {}}

    # Run manifest awareness (TC-002/TC-003): determine which reports are "current"
    run_manifest_paths: "set[str] | None" = None
    run_manifest_meta: "dict | None" = None
    if use_run_manifest:
        try:
            import sys as _sys
            _cert_tools = str(REPO_ROOT / "tools" / "certification")
            if _cert_tools not in _sys.path:
                _sys.path.insert(0, _cert_tools)
            from run_manager import get_latest_run_manifest as _glrm  # noqa: PLC0415
            run_manifest_meta = _glrm(fmt)
            if run_manifest_meta:
                run_manifest_paths = set(run_manifest_meta.get("reports_written", []))
        except Exception:
            pass  # run_manager not available — fall back to file-exists check

    def _load_dim(filename: str) -> "tuple[dict[str, Any], bool]":
        return _load_json_with_manifest_check(fmt_dir / filename, run_manifest_paths)

    api, api_ok = _load_dim("api-contract.json")
    trace, trace_ok = _load_dim("traceability-audit.json")
    stub, stub_ok = _load_dim("stub-audit.json")
    exc, exc_ok = _load_dim("exception-audit.json")
    oracle, oracle_ok = _load_dim("oracle-alignment.json")
    quality, quality_ok = _load_dim("assertion-quality.json")
    rt, rt_ok = _load_dim("roundtrip-audit.json")
    pkg, pkg_ok = _load_dim("package-proof.json")
    consumer, consumer_ok = _load_dim("consumer-proof.json")

    py_count = len(api.get("python", {}).get("contracts", []))
    net_count = len(api.get("dotnet", {}).get("contracts", []))
    mat_stubs = stub.get("material_finding_count", 0)
    uncov_exc = exc.get("uncovered_exception_count", 0)
    qname_pass = trace.get("pass_count", 0)
    qname_total = trace.get("qname_count", 0)
    avg_score = quality.get("overall_avg_score", 0)
    weak = quality.get("weak_assertion_count", 0)

    def _api_status() -> str:
        if not api_ok:
            return "MISSING_EVIDENCE"
        return "PASS" if py_count > 0 else "NOT_AUDITED"

    def _trace_status() -> str:
        if not trace_ok:
            return "MISSING_EVIDENCE"
        if qname_total > 0:
            return "PASS" if qname_pass == qname_total else "FAIL"
        return "NOT_AUDITED"

    def _stub_status() -> str:
        if not stub_ok:
            return "MISSING_EVIDENCE"
        return "PASS" if mat_stubs == 0 else "KNOWN_GAPS"

    def _exc_status() -> str:
        if not exc_ok:
            return "MISSING_EVIDENCE"
        return "PASS" if uncov_exc == 0 else "KNOWN_GAPS"

    def _oracle_status() -> str:
        if not oracle_ok:
            return "MISSING_EVIDENCE"
        return _dim_status(oracle)

    def _quality_status() -> str:
        if not quality_ok:
            return "MISSING_EVIDENCE"
        return "PASS" if weak == 0 and avg_score >= 3 else "KNOWN_GAPS" if avg_score > 0 else "NOT_AUDITED"

    def _rt_status() -> str:
        if not rt_ok:
            return "MISSING_EVIDENCE"
        return _dim_status(rt, "status", "NOT_AUDITED")

    def _pkg_status() -> str:
        if not pkg_ok:
            return "MISSING_EVIDENCE"
        return _dim_status(pkg, "status", "NOT_AUDITED")

    def _consumer_status() -> str:
        if not consumer_ok:
            return "MISSING_EVIDENCE"
        return _dim_status(consumer, "status", "NOT_AUDITED")

    dimensions = {
        "api_contract": {
            "status": _api_status(),
            "python_apis": py_count,
            "dotnet_apis": net_count,
        },
        "traceability": {
            "status": _trace_status(),
            "pass_count": qname_pass,
            "total": qname_total,
        },
        "stubs": {
            "status": _stub_status(),
            "material_count": mat_stubs,
        },
        "exceptions": {
            "status": _exc_status(),
            "uncovered": uncov_exc,
            "total": exc.get("exception_count", 0),
        },
        "oracle": {
            "status": _oracle_status(),
            "pass_rate": oracle.get("pass_rate", oracle.get("oracle_summary", {}).get("pass_rate", "?")),
        },
        "test_quality": {
            "status": _quality_status(),
            "avg_score": avg_score,
            "weak_count": weak,
        },
        "roundtrip": {
            "status": _rt_status(),
        },
        "package": {
            "status": _pkg_status(),
        },
        "consumer": {
            "status": _consumer_status(),
        },
    }

    # Compute overall verdict (TC-003: MISSING_EVIDENCE blocks CERTIFIED)
    statuses = [d["status"] for d in dimensions.values()]
    blocking = {"MISSING_EVIDENCE", "STALE_EVIDENCE", "FAIL"}
    acceptable = {"PASS", "KNOWN_GAPS", "NOT_APPLICABLE", "GAP"}
    if all(s in {"PASS", "NOT_APPLICABLE"} for s in statuses):
        verdict = "CERTIFIED"
    elif any(s in blocking for s in statuses):
        if "FAIL" in statuses:
            verdict = "NOT_CERTIFIED"
        else:
            verdict = "INCOMPLETE_EVIDENCE"
    elif all(s in acceptable for s in statuses):
        verdict = "CERTIFIED_WITH_KNOWN_GAPS"
    else:
        verdict = "IN_PROGRESS"

    result: dict[str, Any] = {
        "format_id": fmt,
        "overall_verdict": verdict,
        "dimensions": dimensions,
    }
    if run_manifest_meta:
        result["run_manifest"] = {
            "run_id": run_manifest_meta.get("run_id"),
            "source_revision": run_manifest_meta.get("source_revision"),
            "is_synthetic": run_manifest_meta.get("is_synthetic", False),
        }
    return result


def build_dashboard() -> dict[str, Any]:
    entries = [collect_format_status(fmt) for fmt in ALL_FORMATS]
    verdicts = {e["overall_verdict"] for e in entries}

    return {
        "metadata": {
            "authoritative_plan": "plans/.claude/crispy-jingling-snail.md",
            "mission_id": "CERT-EXHAUST-20260628",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "schema_version": "1.0.0",
        },
        "portfolio_summary": {
            "total_formats": len(entries),
            "certified": sum(1 for e in entries if e["overall_verdict"] == "CERTIFIED"),
            "certified_with_gaps": sum(1 for e in entries if e["overall_verdict"] == "CERTIFIED_WITH_KNOWN_GAPS"),
            "not_certified": sum(1 for e in entries if e["overall_verdict"] == "NOT_CERTIFIED"),
            "in_progress": sum(1 for e in entries if e["overall_verdict"] == "IN_PROGRESS"),
            "not_started": sum(1 for e in entries if e["overall_verdict"] == "NOT_STARTED"),
        },
        "formats": entries,
    }


def generate_markdown(dashboard: dict[str, Any]) -> str:
    lines = [
        "# Portfolio Certification Report",
        "",
        f"Generated: {dashboard['metadata']['generated_at']}",
        f"Plan: `{dashboard['metadata']['authoritative_plan']}`",
        "",
        "## Summary",
        "",
    ]

    ps = dashboard["portfolio_summary"]
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Formats | {ps['total_formats']} |")
    lines.append(f"| Certified | {ps['certified']} |")
    lines.append(f"| Certified with Known Gaps | {ps['certified_with_gaps']} |")
    lines.append(f"| Not Certified | {ps['not_certified']} |")
    lines.append(f"| In Progress | {ps['in_progress']} |")
    lines.append(f"| Not Started | {ps['not_started']} |")
    lines.append("")

    # Per-format table
    lines.append("## Per-Format Status")
    lines.append("")
    header = "| Format | Verdict | API | Trace | Stubs | Except | Oracle | Quality | RT | Pkg | Consumer |"
    sep = "|--------|---------|-----|-------|-------|--------|--------|---------|----|----|----------|"
    lines.append(header)
    lines.append(sep)

    for entry in dashboard["formats"]:
        dims = entry["dimensions"]
        row = [
            entry["format_id"],
            entry["overall_verdict"],
        ]
        for dim in DIMENSIONS:
            d = dims.get(dim, {})
            s = d.get("status", "?")
            if s == "PASS":
                row.append("PASS")
            elif s == "KNOWN_GAPS":
                row.append("GAPS")
            elif s == "NOT_APPLICABLE":
                row.append("N/A")
            elif s == "NOT_AUDITED":
                row.append("-")
            else:
                row.append(s[:4])
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("## Material Findings")
    lines.append("")

    # Stubs summary
    total_stubs = sum(
        e["dimensions"].get("stubs", {}).get("material_count", 0)
        for e in dashboard["formats"]
    )
    lines.append(f"- **Material stubs:** {total_stubs} across all formats")

    # Weak assertions
    total_weak = sum(
        e["dimensions"].get("test_quality", {}).get("weak_count", 0)
        for e in dashboard["formats"]
    )
    lines.append(f"- **Weak assertions (score 1/5):** {total_weak} test functions")

    # Uncovered exceptions
    total_uncov = sum(
        e["dimensions"].get("exceptions", {}).get("uncovered", 0)
        for e in dashboard["formats"]
    )
    lines.append(f"- **Uncovered exception classes:** {total_uncov}")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", type=Path, default=CERT_ROOT / "portfolio-certification-matrix.json")
    parser.add_argument("--output-md", type=Path, default=CERT_ROOT / "certification-report.md")
    args = parser.parse_args()

    dashboard = build_dashboard()

    json_out = args.output_json if args.output_json.is_absolute() else REPO_ROOT / args.output_json
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(dashboard, indent=2) + "\n", encoding="utf-8")

    md_out = args.output_md if args.output_md.is_absolute() else REPO_ROOT / args.output_md
    md_out.write_text(generate_markdown(dashboard), encoding="utf-8")

    ps = dashboard["portfolio_summary"]
    print(json.dumps({
        "json_output": str(json_out),
        "md_output": str(md_out),
        "certified": ps["certified"],
        "certified_with_gaps": ps["certified_with_gaps"],
        "not_certified": ps["not_certified"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
