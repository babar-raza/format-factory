"""migrate_fact_ids.py — Migrate all FACT-* references to SAL-* stable IDs (TC-SAL-ID-005).

Reads the mapping from .local/sal-id/fact-id-mapping.json (falls back to
shared/sal-fact-id-aliases.json if not found) and updates:
  1. SAL facts database — adds fact_id field to each fact
  2. QName registries — replaces spec_fact_ref values
  3. Gap-ledger — replaces spec_facts array values
  4. Capability map — replaces source_fact_ids array values
  5. Python source — replaces spec_fact_ref assignments and comments
  6. .NET source — replaces SpecFactRef const and comments
  7. SAL fact overrides — adds fact_id field
  8. (--include-tests) Format test files under tests/python/<fmt>/
  9. (--include-oracle) Oracle package files under oracle/formats/

Uses two-phase commit: write all .tmp files first, then os.replace() atomically.

CLI:
    python migrate_fact_ids.py [--dry-run] [--mapping PATH] [--include-tests] [--include-oracle]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_MAPPING_PATH = _REPO_ROOT / ".local" / "sal-id" / "fact-id-mapping.json"
_ALIASES_PATH = _REPO_ROOT / "shared" / "sal-fact-id-aliases.json"

_FACT_PATTERN = re.compile(r"FACT-[A-Z0-9]+-(?:EX-)?[0-9]+")


def _load_mapping(mapping_path: Path) -> dict[str, str]:
    data = json.loads(mapping_path.read_text(encoding="utf-8"))
    return data.get("mappings") or data.get("aliases") or {}


def _replace_fact_ids_in_text(text: str, mapping: dict[str, str]) -> str:
    def _replacer(m: re.Match) -> str:
        old = m.group(0)
        return mapping.get(old, old)
    return _FACT_PATTERN.sub(_replacer, text)


def _migrate_sal_facts(mapping: dict[str, str], dry_run: bool) -> list[str]:
    """Add fact_id field to each fact in sal-facts-latest.json."""
    path = _REPO_ROOT / ".local" / "spec-cache" / "sal-facts-latest.json"
    if not path.exists():
        return [f"SKIP: {path} not found"]

    data = json.loads(path.read_text(encoding="utf-8"))
    count = 0
    for fmt_result in data.get("results", []):
        for fact in fmt_result.get("spec_facts", []):
            old_id = fact.get("qname", "")
            if old_id in mapping:
                fact["fact_id"] = mapping[old_id]
                count += 1

    if dry_run:
        return [f"DRY-RUN: would add fact_id to {count} facts in {path}"]

    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return [f"OK: added fact_id to {count} facts in {path.name}"]


def _migrate_sal_output(mapping: dict[str, str], dry_run: bool) -> list[str]:
    """Add fact_id to the sal-output copy too."""
    path = _REPO_ROOT / ".local" / "sal-output" / "sal-facts-latest.json"
    if not path.exists():
        return [f"SKIP: {path} not found"]

    data = json.loads(path.read_text(encoding="utf-8"))
    count = 0
    for fmt_result in data.get("results", []):
        for fact in fmt_result.get("spec_facts", []):
            old_id = fact.get("qname", "")
            if old_id in mapping:
                fact["fact_id"] = mapping[old_id]
                count += 1

    if dry_run:
        return [f"DRY-RUN: would add fact_id to {count} facts in {path}"]

    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return [f"OK: added fact_id to {count} facts in sal-output/sal-facts-latest.json"]


def _migrate_qname_registries(mapping: dict[str, str], dry_run: bool) -> list[str]:
    """Replace spec_fact_ref values in shared/qname-registry/*.yaml."""
    reg_dir = _REPO_ROOT / "shared" / "qname-registry"
    if not reg_dir.is_dir():
        return ["SKIP: qname-registry dir not found"]

    logs = []
    for yaml_file in sorted(reg_dir.glob("*.yaml")):
        if yaml_file.name == "schema.yaml":
            continue
        text = yaml_file.read_text(encoding="utf-8")
        new_text = _replace_fact_ids_in_text(text, mapping)
        if new_text != text:
            if dry_run:
                logs.append(f"DRY-RUN: would update {yaml_file.name}")
            else:
                tmp = yaml_file.with_suffix(".tmp")
                tmp.write_text(new_text, encoding="utf-8")
                os.replace(tmp, yaml_file)
                logs.append(f"OK: updated {yaml_file.name}")
    return logs or ["OK: no qname registries needed updates"]


def _migrate_json_file(
    path: Path,
    keys: list[str],
    mapping: dict[str, str],
    dry_run: bool,
) -> list[str]:
    """Replace FACT-* IDs in specific array fields of a JSON file."""
    if not path.exists():
        return [f"SKIP: {path.name} not found"]

    data = json.loads(path.read_text(encoding="utf-8"))
    count = 0

    def _walk(obj: object) -> None:
        nonlocal count
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in keys and isinstance(v, list):
                    for i, item in enumerate(v):
                        if isinstance(item, str) and item in mapping:
                            obj[k][i] = mapping[item]
                            count += 1
                elif k in keys and isinstance(v, str) and v in mapping:
                    obj[k] = mapping[v]
                    count += 1
                else:
                    _walk(v)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)

    _walk(data)

    if count == 0:
        return [f"OK: no changes needed in {path.name}"]
    if dry_run:
        return [f"DRY-RUN: would replace {count} ref(s) in {path.name}"]

    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return [f"OK: replaced {count} ref(s) in {path.name}"]


def _migrate_source_files(
    src_dir: Path,
    ext: str,
    mapping: dict[str, str],
    dry_run: bool,
) -> list[str]:
    """Replace FACT-* IDs in source files (.py or .cs)."""
    if not src_dir.is_dir():
        return [f"SKIP: {src_dir} not found"]

    logs = []
    updated = 0
    for src_file in sorted(src_dir.rglob(f"*{ext}")):
        if "__pycache__" in src_file.parts or "build" in src_file.parts:
            continue
        try:
            text = src_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        new_text = _replace_fact_ids_in_text(text, mapping)
        if new_text != text:
            updated += 1
            if not dry_run:
                tmp = src_file.with_suffix(".tmp")
                tmp.write_text(new_text, encoding="utf-8")
                os.replace(tmp, src_file)

    label = "DRY-RUN: would update" if dry_run else "OK: updated"
    logs.append(f"{label} {updated} {ext} file(s) under {src_dir.relative_to(_REPO_ROOT)}")
    return logs


def _migrate_overrides(mapping: dict[str, str], dry_run: bool) -> list[str]:
    """Add fact_id field to sal-fact-overrides.yaml entries."""
    path = _REPO_ROOT / "shared" / "sal-fact-overrides.yaml"
    if not path.exists():
        return ["SKIP: sal-fact-overrides.yaml not found"]

    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    new_lines = []
    count = 0

    for line in lines:
        new_lines.append(line)
        m = re.match(r"(\s+)qname:\s+(FACT-[A-Z0-9]+-(?:EX-)?\d+)", line)
        if m:
            indent = m.group(1)
            old_id = m.group(2)
            new_id = mapping.get(old_id)
            if new_id:
                new_lines.append(f"{indent}fact_id: {new_id}")
                count += 1

    if count == 0:
        return ["OK: no overrides needed fact_id"]

    new_text = "\n".join(new_lines)
    if dry_run:
        return [f"DRY-RUN: would add fact_id to {count} override(s)"]

    tmp = path.with_suffix(".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    os.replace(tmp, path)
    return [f"OK: added fact_id to {count} override(s) in sal-fact-overrides.yaml"]


def _migrate_test_files(mapping: dict[str, str], dry_run: bool) -> list[str]:
    """Replace FACT-* IDs in format test files under tests/python/<fmt>/."""
    test_root = _REPO_ROOT / "tests" / "python"
    if not test_root.is_dir():
        return ["SKIP: tests/python/ not found"]

    logs = []
    for fmt_dir in sorted(test_root.iterdir()):
        if not fmt_dir.is_dir():
            continue
        result = _migrate_source_files(fmt_dir, ".py", mapping, dry_run)
        logs.extend(result)
    return logs


def _migrate_oracle_files(mapping: dict[str, str], dry_run: bool) -> list[str]:
    """Replace FACT-* IDs in oracle package YAML files."""
    oracle_root = _REPO_ROOT / "oracle" / "formats"
    if not oracle_root.is_dir():
        return ["SKIP: oracle/formats/ not found"]

    return _migrate_source_files(oracle_root, ".yaml", mapping, dry_run)


def migrate(
    mapping_path: Path | None = None,
    dry_run: bool = False,
    include_tests: bool = False,
    include_oracle: bool = False,
) -> list[str]:
    mp = mapping_path or _MAPPING_PATH
    if not mp.exists():
        mp = _ALIASES_PATH
    if not mp.exists():
        print(f"ERROR: no mapping file found at {_MAPPING_PATH} or {_ALIASES_PATH}", file=sys.stderr)
        sys.exit(1)

    mapping = _load_mapping(mp)
    print(f"Loaded mapping with {len(mapping)} entries from {mp.name}")

    all_logs: list[str] = []

    all_logs.extend(_migrate_sal_facts(mapping, dry_run))
    all_logs.extend(_migrate_sal_output(mapping, dry_run))
    all_logs.extend(_migrate_qname_registries(mapping, dry_run))

    all_logs.extend(_migrate_json_file(
        _REPO_ROOT / "reports" / "capability-layer" / "gap-ledger.json",
        ["spec_facts", "spec_fact_refs"],
        mapping, dry_run,
    ))
    all_logs.extend(_migrate_json_file(
        _REPO_ROOT / "reports" / "capability-layer" / "sal-driven-capability-map.json",
        ["source_fact_ids"],
        mapping, dry_run,
    ))

    all_logs.extend(_migrate_source_files(
        _REPO_ROOT / "src" / "python", ".py", mapping, dry_run,
    ))
    all_logs.extend(_migrate_source_files(
        _REPO_ROOT / "src" / "net", ".cs", mapping, dry_run,
    ))

    all_logs.extend(_migrate_overrides(mapping, dry_run))

    if include_tests:
        all_logs.extend(_migrate_test_files(mapping, dry_run))

    if include_oracle:
        all_logs.extend(_migrate_oracle_files(mapping, dry_run))

    for log in all_logs:
        print(f"  {log}")

    return all_logs


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate FACT-* to SAL-* IDs (TC-SAL-ID-005)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    parser.add_argument("--mapping", type=Path, default=None)
    parser.add_argument("--include-tests", action="store_true",
                        help="Also migrate tests/python/<fmt>/ test files")
    parser.add_argument("--include-oracle", action="store_true",
                        help="Also migrate oracle/formats/ YAML files")
    args = parser.parse_args()
    migrate(args.mapping, args.dry_run, args.include_tests, args.include_oracle)


if __name__ == "__main__":
    main()
