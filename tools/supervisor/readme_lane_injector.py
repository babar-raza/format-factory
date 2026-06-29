"""readme_lane_injector — Inject dual-lane status sections into format READMEs.

TC-DL2-014: Adds a "Dual-Lane Status" section to README files for formats
with FULL DOM applicability, using BEGIN/END markers for idempotent updates.

Usage:
    python tools/supervisor/readme_lane_injector.py [--format FMT] [--dry-run]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MARKER_BEGIN = "<!-- BEGIN:README-DUAL-LANE generated={ts} source=registry/product-deepening-ledger.yaml -->"
_MARKER_END = "<!-- END:README-DUAL-LANE -->"


def _load_ledger() -> list[dict]:
    ledger_path = _REPO_ROOT / "registry" / "product-deepening-ledger.yaml"
    if not ledger_path.exists():
        return []
    data = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("entries", [])
    return data if isinstance(data, list) else []


def _load_applicability() -> dict[str, str]:
    app_path = _REPO_ROOT / "reports" / "dual-lane-deepening" / "format-dom-applicability.yaml"
    if not app_path.exists():
        return {}
    data = yaml.safe_load(app_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {e.get("format_id") or e.get("format", ""): e.get("dom_applicability", "") for e in data}
    if isinstance(data, dict):
        return {k: v.get("dom_applicability", "") if isinstance(v, dict) else str(v)
                for k, v in data.items()}
    return {}


def generate_lane_section(fmt: str) -> str | None:
    """Generate a dual-lane status markdown section for a format."""
    ledger = _load_ledger()
    applicability = _load_applicability()

    app = applicability.get(fmt, "")
    if app != "FULL":
        return None

    entry = None
    for e in ledger:
        if (e.get("format") or e.get("format_id", "")).lower() == fmt.lower():
            entry = e
            break
    if not entry:
        return None

    lane_a = entry.get("lane_a_maturity", "?")
    lane_b = entry.get("lane_b_maturity", "?")
    lane_b_ceil = entry.get("lane_b_ceiling", "?")
    exec_mode = entry.get("execution_mode", "AUTO")
    a_consec = entry.get("lane_a_consecutive", 0)
    b_consec = entry.get("lane_b_consecutive", 0)

    lines = [
        "## Dual-Lane Status",
        "",
        "| Property | Value |",
        "|----------|-------|",
        f"| DOM Applicability | FULL |",
        f"| Lane A (Features) | {lane_a} |",
        f"| Lane B (DOM/Object Model) | {lane_b} (ceiling: {lane_b_ceil}) |",
        f"| Execution Mode | {exec_mode} |",
        f"| Lane A Consecutive | {a_consec} |",
        f"| Lane B Consecutive | {b_consec} |",
    ]
    return "\n".join(lines)


def inject_into_readme(readme_path: Path, section_content: str, dry_run: bool = False) -> bool:
    """Inject or update the dual-lane section in a README file."""
    if not readme_path.exists():
        return False

    text = readme_path.read_text(encoding="utf-8")
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    begin = _MARKER_BEGIN.format(ts=ts)

    block = f"{begin}\n{section_content}\n{_MARKER_END}"

    pattern = re.compile(
        r"<!-- BEGIN:README-DUAL-LANE[^>]*-->.*?<!-- END:README-DUAL-LANE -->",
        re.DOTALL,
    )

    if pattern.search(text):
        new_text = pattern.sub(block, text)
    else:
        new_text = text.rstrip() + "\n\n" + block + "\n"

    if new_text == text:
        return False

    if not dry_run:
        readme_path.write_text(new_text, encoding="utf-8")
    return True


def inject_all(dry_run: bool = False, fmt_filter: str | None = None) -> dict:
    """Inject dual-lane sections into all eligible README files."""
    applicability = _load_applicability()
    results: dict[str, str] = {}

    for fmt, app in applicability.items():
        if app != "FULL":
            results[fmt] = "SKIPPED_NOT_FULL"
            continue
        if fmt_filter and fmt.lower() != fmt_filter.lower():
            continue

        section = generate_lane_section(fmt)
        if not section:
            results[fmt] = "SKIPPED_NO_LEDGER"
            continue

        readme = _REPO_ROOT / "src" / "python" / fmt / "README.md"
        if not readme.exists():
            results[fmt] = "SKIPPED_NO_README"
            continue

        changed = inject_into_readme(readme, section, dry_run=dry_run)
        results[fmt] = "UPDATED" if changed else "UNCHANGED"

    return results


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Inject dual-lane status into format READMEs")
    parser.add_argument("--format", help="Single format to inject (default: all FULL)")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    args = parser.parse_args()

    results = inject_all(dry_run=args.dry_run, fmt_filter=args.format)
    for fmt, status in sorted(results.items()):
        print(f"  {fmt}: {status}")


if __name__ == "__main__":
    main()
