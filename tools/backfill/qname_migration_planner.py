"""
qname_migration_planner.py — QName Migration Map Generator (Phase F — Forensic Audit)

Generates a structured migration map from the current state of each format's source
code to the target qname-compliant architecture. Reads:
  - shared/qname-registry/{format}.yaml (target spec)
  - tools/backfill/qname_structure_validator output (gap inventory)
  - src/python/{format}/ actual files

Produces:
  - reports/qname-migration/{format}-migration-map.json per format
  - reports/qname-migration/summary.json  overall migration status

Each migration map entry has:
  qname: "csv:record"
  current_state: MATCH | MISSING_CLASS | WRONG_PATH | MISSING_FILE | MISSING_SPEC_QNAME | NO_PYTHON_FILE
  target_path: src/python/csv/spec/record/record.py
  current_path: src/python/csv/spec/record/record.py  (or None)
  action_required: NONE | ADD_SPEC_QNAME | ADD_CLASS | MOVE_FILE | CREATE_FILE
  migration_risk: LOW | MEDIUM | HIGH
  estimated_effort: trivial | small | medium | large
  blocks_gate: bool  (true if this gap would block Gate 11 readiness)
  test_changes_required: list of test files that import from current_path

Usage:
    python tools/backfill/qname_migration_planner.py [--format FORMAT] [--out-dir PATH]

Exit codes:
    0: All formats at MATCH (no migration needed)
    1: Migration needed for at least one format
"""
from __future__ import annotations

import ast
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_DIR = REPO_ROOT / "shared" / "qname-registry"
SRC_PYTHON = REPO_ROOT / "src" / "python"
TESTS_PYTHON = REPO_ROOT / "tests" / "python"
OUT_DIR = REPO_ROOT / "reports" / "qname-migration"

ACTIVE_STATUSES = {"implementing", "implemented", "stable"}
ARCHITECTURE_ONLY = "architecture_only"


# ---------------------------------------------------------------------------
# YAML loading (same as qname_structure_validator)
# ---------------------------------------------------------------------------

def _load_registry(path: Path) -> list[dict]:
    try:
        import yaml
        with path.open(encoding="utf-8") as f:
            result = yaml.safe_load(f)
        return result if isinstance(result, list) else []
    except ImportError:
        return _load_yaml_simple(path)
    except Exception as e:
        raise RuntimeError(f"Cannot load {path}: {e}") from e


def _load_yaml_simple(path: Path) -> list[dict]:
    entries: list[dict] = []
    current: dict | None = None
    with path.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("- ") or line == "-":
                if current is not None:
                    entries.append(current)
                current = {}
                rest = line[2:].strip()
                if rest and ":" in rest:
                    k, _, v = rest.partition(":")
                    current[k.strip()] = _val(v.strip())
            elif current is not None and line.startswith("  "):
                stripped = line.strip()
                if stripped.startswith("- "):
                    continue
                if ":" in stripped:
                    k, _, v = stripped.partition(":")
                    current[k.strip()] = _val(v.strip())
    if current is not None:
        entries.append(current)
    return entries


def _val(v: str):
    v = v.strip().strip('"').strip("'")
    if v in ("null", "~", ""):
        return None
    return v


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def _get_class_names(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        return {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    except Exception:
        return set()


def _canonical_short(canonical_class: str) -> str:
    return canonical_class.split(".")[-1] if canonical_class else ""


def _expected_path(qname: str, format_id: str) -> str:
    if ":" not in qname:
        return f"src/python/{format_id}/spec/unknown.py"
    ns, local = qname.split(":", 1)
    local_snake = local.replace("-", "_")
    return f"src/python/{format_id}/spec/{ns}/{local_snake}.py"


def _find_test_files_importing(file_path: str, format_id: str) -> list[str]:
    """Find test files that import from the given source file."""
    results = []
    module_stem = Path(file_path).stem
    test_dir = TESTS_PYTHON / format_id
    if not test_dir.exists():
        return []
    for tf in test_dir.rglob("test_*.py"):
        try:
            content = tf.read_text(encoding="utf-8", errors="replace")
            if module_stem in content:
                results.append(str(tf.relative_to(REPO_ROOT)).replace("\\", "/"))
        except Exception:
            pass
    return results


def _assess_risk(action: str, current_path: str | None) -> tuple[str, str]:
    """Return (migration_risk, estimated_effort) for a given action."""
    if action == "NONE":
        return "LOW", "trivial"
    if action == "ADD_SPEC_QNAME":
        return "LOW", "trivial"
    if action == "ADD_CLASS":
        return "LOW", "small"
    if action == "CREATE_FILE":
        return "MEDIUM", "small"
    if action == "MOVE_FILE":
        # Moving a file risks breaking all importers
        return "HIGH", "medium"
    return "MEDIUM", "medium"


# ---------------------------------------------------------------------------
# Per-entry migration assessment
# ---------------------------------------------------------------------------

def _assess_entry(entry: dict, format_id: str) -> dict:
    qname = entry.get("qname", "?")
    status = entry.get("status", "seeded")
    python_file = entry.get("python_file")
    canonical_class = entry.get("canonical_class", "")
    source_layer = entry.get("source_layer", "")
    short_class = _canonical_short(canonical_class)
    expected = _expected_path(qname, format_id)

    assessment = {
        "qname": qname,
        "status": status,
        "canonical_class": canonical_class,
        "current_path": python_file,
        "target_path": expected if source_layer == "Spec" else python_file,
        "source_layer": source_layer,
        "current_state": "UNKNOWN",
        "action_required": "NONE",
        "migration_risk": "LOW",
        "estimated_effort": "trivial",
        "blocks_gate": False,
        "test_changes_required": [],
        "notes": [],
    }

    if status in ("seeded", "deprecated"):
        assessment["current_state"] = "NOT_YET_ACTIVE"
        assessment["action_required"] = "NONE"
        return assessment

    if status == ARCHITECTURE_ONLY and python_file is None:
        assessment["current_state"] = "ARCHITECTURE_ONLY_NO_FILE"
        assessment["action_required"] = "NONE"
        assessment["notes"].append("architecture_only with null python_file is intentional — body represented by facade")
        return assessment

    if python_file is None and status in ACTIVE_STATUSES:
        assessment["current_state"] = "MISSING_FILE"
        assessment["action_required"] = "CREATE_FILE"
        assessment["migration_risk"] = "MEDIUM"
        assessment["estimated_effort"] = "small"
        assessment["blocks_gate"] = True
        assessment["notes"].append(f"Active entry has no python_file. Expected: {expected}")
        return assessment

    if python_file is not None:
        py_path = REPO_ROOT / python_file
        if not py_path.exists():
            assessment["current_state"] = "MISSING_FILE"
            assessment["action_required"] = "CREATE_FILE"
            assessment["migration_risk"] = "MEDIUM"
            assessment["estimated_effort"] = "small"
            assessment["blocks_gate"] = status in ACTIVE_STATUSES
            assessment["notes"].append(f"Registered python_file does not exist: {python_file}")
            return assessment

        content = py_path.read_text(encoding="utf-8", errors="replace")
        has_spec_qname = bool(re.search(r"spec_qname\s*(?::[^=]+)?\s*=", content))
        defined_classes = _get_class_names(py_path)
        in_spec_dir = "/spec/" in python_file.replace("\\", "/")
        path_matches_expected = python_file.replace("\\", "/").endswith(
            expected.split(f"{format_id}/spec/")[-1]
        ) if in_spec_dir else False

        # Determine current state
        if has_spec_qname and (short_class in defined_classes or not source_layer == "Spec"):
            if source_layer == "Spec" and not in_spec_dir:
                assessment["current_state"] = "WRONG_PATH"
                assessment["action_required"] = "MOVE_FILE"
                assessment["migration_risk"] = "HIGH"
                assessment["estimated_effort"] = "medium"
                assessment["blocks_gate"] = False  # Structural but not blocking
                assessment["test_changes_required"] = _find_test_files_importing(python_file, format_id)
                assessment["notes"].append(
                    f"Spec-layer entry in non-spec/ file. Move from {python_file} to {expected}"
                )
            elif source_layer == "Spec" and in_spec_dir and not path_matches_expected:
                assessment["current_state"] = "WRONG_PATH_IN_SPEC"
                assessment["action_required"] = "MOVE_FILE"
                assessment["migration_risk"] = "MEDIUM"
                assessment["estimated_effort"] = "small"
                assessment["notes"].append(
                    f"In spec/ but wrong sub-path. Got {python_file}, expected {expected}"
                )
            else:
                assessment["current_state"] = "MATCH"
                assessment["action_required"] = "NONE"
                if not short_class or short_class in defined_classes:
                    assessment["notes"].append("Fully compliant")
                else:
                    assessment["notes"].append(f"spec_qname present; canonical class '{short_class}' uses alternative name")
        elif not has_spec_qname:
            assessment["current_state"] = "MISSING_SPEC_QNAME"
            assessment["action_required"] = "ADD_SPEC_QNAME"
            assessment["migration_risk"] = "LOW"
            assessment["estimated_effort"] = "trivial"
            assessment["blocks_gate"] = status in ACTIVE_STATUSES
        elif source_layer == "Spec" and short_class not in defined_classes:
            assessment["current_state"] = "MISSING_CLASS"
            assessment["action_required"] = "ADD_CLASS" if in_spec_dir else "MOVE_FILE"
            assessment["migration_risk"] = "MEDIUM"
            assessment["estimated_effort"] = "small"
            assessment["notes"].append(
                f"Registry canonical_class '{canonical_class}' (short: '{short_class}') "
                f"not found in {python_file}. Defined: {sorted(defined_classes)[:5]}"
            )

    assessment["migration_risk"], assessment["estimated_effort"] = _assess_risk(
        assessment["action_required"], python_file
    )
    return assessment


# ---------------------------------------------------------------------------
# Per-format migration plan
# ---------------------------------------------------------------------------

def plan_format(format_id: str, registry_path: Path) -> dict:
    entries = _load_registry(registry_path)
    assessments = []
    state_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    risk_counts: dict[str, int] = {}
    blocks_gate_count = 0

    for entry in entries:
        a = _assess_entry(entry, format_id)
        assessments.append(a)
        state_counts[a["current_state"]] = state_counts.get(a["current_state"], 0) + 1
        action_counts[a["action_required"]] = action_counts.get(a["action_required"], 0) + 1
        risk_counts[a["migration_risk"]] = risk_counts.get(a["migration_risk"], 0) + 1
        if a["blocks_gate"]:
            blocks_gate_count += 1

    match_count = state_counts.get("MATCH", 0) + state_counts.get("ARCHITECTURE_ONLY_NO_FILE", 0) + state_counts.get("NOT_YET_ACTIVE", 0)
    total = len(entries)
    compliant_pct = round(match_count / total, 3) if total > 0 else 1.0

    return {
        "format_id": format_id,
        "date": date.today().strftime("%Y%m%d"),
        "total_entries": total,
        "compliant_count": match_count,
        "compliant_pct": compliant_pct,
        "blocks_gate_count": blocks_gate_count,
        "state_counts": state_counts,
        "action_counts": action_counts,
        "risk_counts": risk_counts,
        "migration_ready": blocks_gate_count == 0,
        "entries": assessments,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(args: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate QName migration maps per format"
    )
    parser.add_argument("--format", dest="format_filter", help="Plan one format only")
    parser.add_argument("--out-dir", default=str(OUT_DIR), help="Output directory for migration maps")
    parsed = parser.parse_args(args)

    out_dir = Path(parsed.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    registry_files = sorted(f for f in REGISTRY_DIR.glob("*.yaml") if f.name != "schema.yaml")
    if parsed.format_filter:
        registry_files = [f for f in registry_files if f.stem == parsed.format_filter]
        if not registry_files:
            print(f"ERROR: No registry for format '{parsed.format_filter}'", file=sys.stderr)
            return 2

    all_plans = []
    needs_migration = 0

    for reg_path in registry_files:
        fmt = reg_path.stem
        try:
            plan = plan_format(fmt, reg_path)
        except Exception as e:
            print(f"ERROR planning {fmt}: {e}", file=sys.stderr)
            plan = {"format_id": fmt, "error": str(e)}

        # Write per-format map
        map_path = out_dir / f"{fmt}-migration-map.json"
        map_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

        all_plans.append({k: v for k, v in plan.items() if k != "entries"})
        if not plan.get("migration_ready", True) or plan.get("compliant_pct", 1.0) < 1.0:
            needs_migration += 1

    # Write summary
    today = date.today().strftime("%Y%m%d")
    summary = {
        "date": today,
        "tool": "qname_migration_planner",
        "description": "Per-format migration readiness maps from current src/ to qname-compliant architecture",
        "formats_planned": len(all_plans),
        "formats_needing_migration": needs_migration,
        "formats_fully_compliant": len(all_plans) - needs_migration,
        "formats": all_plans,
    }
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Console output
    print(f"\n=== QName Migration Planner — {today} ===")
    print(f"Formats planned: {len(all_plans)}")
    print(f"Fully compliant: {len(all_plans) - needs_migration}")
    print(f"Need migration:  {needs_migration}\n")
    print(f"{'Format':<12} {'Entries':>7} {'Compliant':>10} {'Pct':>6} {'GateBlock':>10} {'Ready':>7}")
    print("-" * 58)
    for p in all_plans:
        if "error" in p:
            print(f"{p['format_id']:<12} ERROR")
            continue
        ready = "YES" if p.get("migration_ready") else "NO"
        print(
            f"{p['format_id']:<12} {p['total_entries']:>7} "
            f"{p['compliant_count']:>10} {p['compliant_pct']:>6.0%} "
            f"{p['blocks_gate_count']:>10} {ready:>7}"
        )
    print(f"\nPer-format maps: {out_dir}/")
    print(f"Summary: {summary_path}")
    return 1 if needs_migration > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
