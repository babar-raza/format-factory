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


def _dim_status(data: dict[str, Any], key: str = "status", default: str = "NOT_AUDITED") -> str:
    return data.get(key, data.get("alignment_status", data.get("status", default)))


def collect_format_status(fmt: str) -> dict[str, Any]:
    fmt_dir = CERT_ROOT / fmt
    if not fmt_dir.exists():
        return {"format_id": fmt, "status": "NOT_STARTED", "dimensions": {}}

    api = _load_json(fmt_dir / "api-contract.json")
    trace = _load_json(fmt_dir / "traceability-audit.json")
    stub = _load_json(fmt_dir / "stub-audit.json")
    exc = _load_json(fmt_dir / "exception-audit.json")
    oracle = _load_json(fmt_dir / "oracle-alignment.json")
    quality = _load_json(fmt_dir / "assertion-quality.json")
    rt = _load_json(fmt_dir / "roundtrip-audit.json")
    pkg = _load_json(fmt_dir / "package-proof.json")
    consumer = _load_json(fmt_dir / "consumer-proof.json")

    py_count = len(api.get("python", {}).get("contracts", []))
    net_count = len(api.get("dotnet", {}).get("contracts", []))
    mat_stubs = stub.get("material_finding_count", 0)
    uncov_exc = exc.get("uncovered_exception_count", 0)
    qname_pass = trace.get("pass_count", 0)
    qname_total = trace.get("qname_count", 0)
    avg_score = quality.get("overall_avg_score", 0)
    weak = quality.get("weak_assertion_count", 0)

    dimensions = {
        "api_contract": {
            "status": "PASS" if py_count > 0 else "NOT_AUDITED",
            "python_apis": py_count,
            "dotnet_apis": net_count,
        },
        "traceability": {
            "status": "PASS" if qname_pass == qname_total and qname_total > 0 else "FAIL" if qname_total > 0 else "NOT_AUDITED",
            "pass_count": qname_pass,
            "total": qname_total,
        },
        "stubs": {
            "status": "PASS" if mat_stubs == 0 else "KNOWN_GAPS",
            "material_count": mat_stubs,
        },
        "exceptions": {
            "status": "PASS" if uncov_exc == 0 else "KNOWN_GAPS",
            "uncovered": uncov_exc,
            "total": exc.get("exception_count", 0),
        },
        "oracle": {
            "status": _dim_status(oracle),
            "pass_rate": oracle.get("pass_rate", oracle.get("oracle_summary", {}).get("pass_rate", "?")),
        },
        "test_quality": {
            "status": "PASS" if weak == 0 and avg_score >= 3 else "KNOWN_GAPS" if avg_score > 0 else "NOT_AUDITED",
            "avg_score": avg_score,
            "weak_count": weak,
        },
        "roundtrip": {
            "status": _dim_status(rt, "status", "NOT_AUDITED"),
        },
        "package": {
            "status": _dim_status(pkg, "status", "NOT_AUDITED"),
        },
        "consumer": {
            "status": _dim_status(consumer, "status", "NOT_AUDITED"),
        },
    }

    # Compute overall verdict
    statuses = [d["status"] for d in dimensions.values()]
    acceptable = {"PASS", "KNOWN_GAPS", "NOT_APPLICABLE", "GAP"}
    if all(s == "PASS" for s in statuses):
        verdict = "CERTIFIED"
    elif any(s == "FAIL" for s in statuses):
        verdict = "NOT_CERTIFIED"
    elif all(s in acceptable for s in statuses):
        verdict = "CERTIFIED_WITH_KNOWN_GAPS"
    else:
        verdict = "IN_PROGRESS"

    return {
        "format_id": fmt,
        "overall_verdict": verdict,
        "dimensions": dimensions,
    }


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
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
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
