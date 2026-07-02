"""Collect project-wide statistics from repository evidence sources.

Reads canonical registries, oracle results, test directories, source trees,
and supervisor state to produce a structured statistics summary.

Usage:
    python tools/docs/generate_statistics.py
    python tools/docs/generate_statistics.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read_yaml(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _read_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _count_files(directory: Path, pattern: str, exclude: tuple[str, ...] = ()) -> int:
    if not directory.exists():
        return 0
    count = 0
    for f in directory.rglob(pattern):
        parts = f.parts
        if any(ex in parts for ex in exclude):
            continue
        count += 1
    return count


def _count_formats(repo_root: Path) -> dict:
    data = _read_yaml(repo_root / "registry" / "format-registry.yaml")
    if not data or not isinstance(data, dict):
        return {"total_in_registry": 0, "active_with_source": 0, "families": {}, "family_count": 0}
    formats = data.get("formats", [])
    families: dict[str, int] = {}
    active = 0
    for f in formats:
        fid = f.get("format_id", "")
        family = f.get("family", "unknown")
        if fid == "odf-shared":
            continue
        families[family] = families.get(family, 0) + 1
        # Check if format has product source
        py_dir = repo_root / "src" / "python" / fid
        if py_dir.is_dir():
            active += 1
    return {
        "total_in_registry": len(formats),
        "active_with_source": active,
        "families": families,
        "family_count": len(families),
    }


def _count_source(repo_root: Path) -> dict:
    py_files = _count_files(
        repo_root / "src" / "python", "*.py",
        exclude=("__pycache__", "build", "egg-info", ".egg-info"),
    )
    cs_files = _count_files(
        repo_root / "src" / "net", "*.cs",
        exclude=("obj", "bin"),
    )
    return {"python_files": py_files, "dotnet_files": cs_files}


def _count_tests(repo_root: Path) -> dict:
    py_tests = _count_files(
        repo_root / "tests" / "python", "*.py",
        exclude=("__pycache__",),
    )
    net_tests = _count_files(
        repo_root / "tests" / "net", "*.cs",
        exclude=("obj", "bin"),
    )
    supervisor_tests = _count_files(
        repo_root / "tests" / "supervisor", "*.py",
        exclude=("__pycache__",),
    )
    certification_tests = _count_files(
        repo_root / "tests" / "certification", "*.py",
        exclude=("__pycache__",),
    )
    return {
        "python": py_tests,
        "dotnet": net_tests,
        "supervisor": supervisor_tests,
        "certification": certification_tests,
        "total": py_tests + net_tests + supervisor_tests + certification_tests,
    }


def _count_governance(repo_root: Path) -> dict:
    # Validators
    validator_count = 0
    for f in sorted(repo_root.glob("tools/supervisor/governance_validators*.py")):
        try:
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith("def validate_"):
                    validator_count += 1
        except Exception:
            pass

    # Capabilities
    cap_data = _read_yaml(repo_root / ".governance" / "capabilities" / "registry.yaml")
    cap_count = 0
    cap_active = 0
    if cap_data and isinstance(cap_data, dict):
        caps = cap_data.get("capabilities", [])
        cap_count = len(caps)
        cap_active = sum(1 for c in caps if c.get("status") == "active")

    # Skills
    skill_data = _read_yaml(repo_root / ".supervisor" / "skill-registry.yaml")
    skill_count = 0
    if skill_data and isinstance(skill_data, dict):
        skills_list = skill_data.get("skills", [])
        if isinstance(skills_list, list):
            skill_count = len(skills_list)

    # Commands
    cmd_dir = repo_root / ".claude" / "commands"
    cmd_count = 0
    if cmd_dir.is_dir():
        cmd_count = sum(1 for f in cmd_dir.glob("*.md") if f.name != "_readme.md")

    return {
        "validators": validator_count,
        "capabilities_total": cap_count,
        "capabilities_active": cap_active,
        "skills": skill_count,
        "commands": cmd_count,
    }


def _count_oracle(repo_root: Path) -> dict:
    oracle_dir = repo_root / "oracle" / "formats"
    if not oracle_dir.is_dir():
        return {"formats_verified": 0, "total_cases": 0, "total_pass": 0, "pass_rate": "0/0"}
    formats_verified = 0
    total_cases = 0
    total_pass = 0
    for fmt_dir in sorted(oracle_dir.iterdir()):
        summary = _read_json(fmt_dir / "reports" / "oracle-run-summary.json")
        if not summary:
            continue
        formats_verified += 1
        total_cases += summary.get("total_cases", 0)
        results = summary.get("results", {})
        total_pass += results.get("PASS", 0)
    return {
        "formats_verified": formats_verified,
        "total_cases": total_cases,
        "total_pass": total_pass,
        "pass_rate": f"{total_pass}/{total_cases}" if total_cases > 0 else "0/0",
    }


def _count_infrastructure(repo_root: Path) -> dict:
    # Sprint count
    mt = _read_json(repo_root / "reports" / "supervisor" / "maturity-trend.json")
    sprint_count = mt.get("sprint_count", 0) if mt else 0
    avg_quality = mt.get("summary", {}).get("avg_evidence_quality_score", 0) if mt else 0

    # Evidence runs
    evidence_dir = repo_root / ".local" / "evidences"
    evidence_runs = 0
    if evidence_dir.is_dir():
        evidence_runs = sum(1 for d in evidence_dir.iterdir() if d.is_dir())

    # Samples
    samples = _count_files(repo_root / "samples" / "by-format", "*",
                           exclude=("__pycache__",))

    # Documentation
    docs = _count_files(repo_root / "docs", "*.md")

    # Examples
    py_examples = _count_files(repo_root / "examples" / "python", "*.py",
                               exclude=("__pycache__",))
    net_examples = _count_files(repo_root / "examples" / "net", "*.csx")

    return {
        "sprint_count": sprint_count,
        "avg_quality": round(avg_quality, 3),
        "evidence_runs": evidence_runs,
        "sample_files": samples,
        "doc_files": docs,
        "python_examples": py_examples,
        "dotnet_examples": net_examples,
    }


def _count_certification(repo_root: Path) -> dict:
    matrix = _read_json(
        repo_root / "reports" / "certification" / "portfolio-certification-matrix.json"
    )
    if not matrix or not isinstance(matrix, dict):
        return {"total": 0, "certified": 0}
    summary = matrix.get("portfolio_summary", {})
    return {
        "total": summary.get("total_formats", 0),
        "certified": summary.get("certified", 0),
        "certified_with_gaps": summary.get("certified_with_gaps", 0),
        "not_certified": summary.get("not_certified", 0),
    }


def collect_statistics(repo_root: Path = REPO_ROOT) -> dict:
    """Collect all project statistics from evidence sources."""
    return {
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "formats": _count_formats(repo_root),
        "source": _count_source(repo_root),
        "tests": _count_tests(repo_root),
        "governance": _count_governance(repo_root),
        "oracle": _count_oracle(repo_root),
        "infrastructure": _count_infrastructure(repo_root),
        "certification": _count_certification(repo_root),
    }


def render_statistics_markdown(stats: dict) -> str:
    """Render statistics as a markdown section."""
    fmt = stats.get("formats", {})
    src = stats.get("source", {})
    tst = stats.get("tests", {})
    gov = stats.get("governance", {})
    orc = stats.get("oracle", {})
    inf = stats.get("infrastructure", {})
    cert = stats.get("certification", {})

    lines = [
        "## Statistics Summary",
        "",
        "| Category | Metric | Value |",
        "|---|---|---|",
        f"| Formats | Active (with source) | {fmt.get('active_with_source', 0)} |",
        f"| Formats | In registry | {fmt.get('total_in_registry', 0)} |",
        f"| Formats | Format families | {fmt.get('family_count', 0)} |",
        f"| Source | Python files | {src.get('python_files', 0)} |",
        f"| Source | .NET files | {src.get('dotnet_files', 0)} |",
        f"| Tests | Python | {tst.get('python', 0)} |",
        f"| Tests | .NET | {tst.get('dotnet', 0)} |",
        f"| Tests | Supervisor + Certification | {tst.get('supervisor', 0) + tst.get('certification', 0)} |",
        f"| Tests | Total | {tst.get('total', 0)} |",
        f"| Governance | Validators | {gov.get('validators', 0)} |",
        f"| Governance | Capabilities (active) | {gov.get('capabilities_active', 0)} |",
        f"| Governance | Registered skills | {gov.get('skills', 0)} |",
        f"| Governance | Commands | {gov.get('commands', 0)} |",
        f"| Oracle | Formats verified | {orc.get('formats_verified', 0)} |",
        f"| Oracle | Cases pass/total | {orc.get('pass_rate', 'N/A')} |",
        f"| Certification | Certified formats | {cert.get('certified', 0)}/{cert.get('total', 0)} |",
        f"| Sprints | Autonomous cycles | {inf.get('sprint_count', 0)} |",
        f"| Sprints | Avg evidence quality | {inf.get('avg_quality', 0)} |",
        f"| Evidence | Evidence runs | {inf.get('evidence_runs', 0)} |",
        f"| Samples | Sample files | {inf.get('sample_files', 0)} |",
        f"| Documentation | Doc files | {inf.get('doc_files', 0)} |",
        f"| Examples | Python examples | {inf.get('python_examples', 0)} |",
        f"| Examples | .NET examples | {inf.get('dotnet_examples', 0)} |",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect project statistics")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    stats = collect_statistics(args.repo_root)
    if args.json:
        print(json.dumps(stats, indent=2))
    else:
        print(render_statistics_markdown(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
