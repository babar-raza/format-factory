"""
merge_sal_facts.py — Compile committed SAL fact stores into the combined
sal-facts-latest.json database.

TC-LA-001 (original ingestion) + GAP-FORENSIC-008 machinery hardening (Phase 2).

Sources per format, in priority order:
  1. shared/sal-facts/{format}.yaml       — committed canonical store (preferred)
  2. .local/spec-cache/sal-facts-*.json   — legacy per-format cache (fallback)

Merge semantics (union, never clobber):
  - Facts are keyed by fact_id (falling back to the alias-resolved legacy
    FACT-* id in 'qname'/'claim_id'). The merged entry is the UNION of the
    combined database's existing facts and the source facts — existing facts
    are never dropped, even if absent from the source file.
  - Conflict — same fact key but different 'claim' text — is a hard error
    (exit 1) listing both claims. Resolve in the committed store explicitly;
    this tool never silently overwrites a claim.
  - On matching keys, the canonical source wins on field content; fields
    present only in the combined record are preserved.
  - Facts in rebuilt entries are sorted by fact key; if the union changes
    nothing for any format, the combined database is not rewritten (reruns
    are no-ops, output is deterministic).

Modes:
    python tools/spec/merge_sal_facts.py                 # merge all covered formats
    python tools/spec/merge_sal_facts.py --formats qoi   # merge selected formats
    python tools/spec/merge_sal_facts.py --dry-run       # report, no writes
    python tools/spec/merge_sal_facts.py --check         # drift check: exit 2 if the
                                                         # combined DB is missing facts
                                                         # or diverges from the stores

Exit codes:
    0 — success / no drift
    1 — error (unreadable inputs, fact conflict, invalid fact)
    2 — drift detected (--check only)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
    _HAS_YAML = True
except ImportError:  # pragma: no cover
    _HAS_YAML = False

_REPO = Path(__file__).resolve().parent.parent.parent
_SPEC_CACHE = _REPO / ".local" / "spec-cache"
_COMBINED = _SPEC_CACHE / "sal-facts-latest.json"
_STORE_DIR = _REPO / "shared" / "sal-facts"
_ALIASES_PATH = _REPO / "shared" / "sal-fact-id-aliases.json"

# Known filename variations for legacy per-format cache files
_FORMAT_FILE_CANDIDATES = {
    "csv": ["sal-facts-CSV.json", "sal-facts-csv.json"],
    "tsv": ["sal-facts-tsv.json"],
    "toml": ["sal-facts-toml.json"],
    "abw": ["sal-facts-abw.json"],
    "dif": ["sal-facts-dif.json"],
    "gnumeric": ["sal-facts-gnumeric.json"],
    "sylk": ["sal-facts-sylk.json"],
    "ndjson": ["sal-facts-ndjson.json"],
    "xcf": ["sal-facts-xcf.json"],
    "zst": ["sal-facts-zst.json"],
    "qoi": ["sal-facts-qoi.json"],
    "pbm": ["sal-facts-pbm.json"],
    "pgm": ["sal-facts-pgm.json"],
    "ppm": ["sal-facts-ppm.json"],
}


class FactConflictError(ValueError):
    """Same fact key carries different claims in two sources."""


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_aliases() -> dict[str, str]:
    if not _ALIASES_PATH.exists():
        return {}
    try:
        return _load_json(_ALIASES_PATH).get("aliases", {})
    except Exception:
        return {}


def _fact_key(fact: dict, aliases: dict[str, str]) -> str | None:
    """Stable identity for a fact: fact_id, else alias-resolved legacy id."""
    fid = fact.get("fact_id")
    if fid:
        return fid
    legacy = fact.get("qname") or fact.get("claim_id")
    if legacy and legacy in aliases:
        return aliases[legacy]
    return legacy


def _normalize_fact(fact: dict) -> dict:
    """Ensure fact has required fields, normalizing schema variants.

    Some sources use 'description' instead of 'claim' — normalize to 'claim'.
    A fact must carry an identity ('qname', 'claim_id', or 'fact_id') and a claim.
    """
    fact = dict(fact)
    if "claim" not in fact and "description" in fact:
        fact["claim"] = fact["description"]
    if "claim" not in fact:
        raise ValueError(f"Fact missing required field 'claim': {fact}")
    if not (fact.get("qname") or fact.get("claim_id") or fact.get("fact_id")):
        raise ValueError(f"Fact missing identity (qname/claim_id/fact_id): {fact}")
    return fact


def _find_per_format_file(format_id: str) -> Path | None:
    for candidate in _FORMAT_FILE_CANDIDATES.get(format_id, [f"sal-facts-{format_id}.json"]):
        p = _SPEC_CACHE / candidate
        if p.exists():
            return p
    return None


def _default_formats() -> list[str]:
    """All formats with any source: committed stores are auto-discovered so a
    new shared/sal-facts/{fmt}.yaml is covered WITHOUT editing this file
    (TC-GWB-H06 — hardcoded lists silently skip new stores)."""
    discovered = {p.stem.lower() for p in _STORE_DIR.glob("*.yaml")} if _STORE_DIR.is_dir() else set()
    return sorted(discovered | set(_FORMAT_FILE_CANDIDATES))


def _load_source_facts(fmt_id: str) -> tuple[list[dict], str, dict] | None:
    """Load facts for a format from the canonical store or legacy cache.

    Returns (facts, source_label, metadata) or None if no source exists.
    """
    store_path = _STORE_DIR / f"{fmt_id}.yaml"
    if _HAS_YAML and store_path.exists():
        doc = yaml.safe_load(store_path.read_text(encoding="utf-8")) or {}
        meta = {
            "display_name": doc.get("display_name", fmt_id.upper()),
            "spec_body": doc.get("spec_body", ""),
            "spec_version": doc.get("spec_version", ""),
            "spec_url": doc.get("spec_url", ""),
        }
        return list(doc.get("facts", [])), str(store_path.relative_to(_REPO)), meta

    legacy_path = _find_per_format_file(fmt_id)
    if legacy_path is not None:
        doc = _load_json(legacy_path)
        meta = {
            "display_name": doc.get("display_name", fmt_id.upper()),
            "spec_body": doc.get("spec_body", doc.get("spec_source", "")),
            "spec_version": doc.get("spec_version", ""),
            "spec_url": doc.get("spec_url", ""),
        }
        return list(doc.get("spec_facts", [])), str(legacy_path.name), meta

    return None


def _union_facts(
    existing: list[dict],
    source: list[dict],
    aliases: dict[str, str],
    fmt_id: str,
) -> tuple[list[dict], dict]:
    """Union existing combined-DB facts with canonical source facts.

    Returns (merged_facts_sorted, stats). Raises FactConflictError on
    claim divergence for the same fact key.
    """
    merged: dict[str, dict] = {}
    unkeyed: list[dict] = []

    for fact in existing:
        key = _fact_key(fact, aliases)
        if key is None:
            unkeyed.append(dict(fact))  # preserve verbatim, never drop
        else:
            merged[key] = dict(fact)

    added = 0
    updated = 0
    for fact in source:
        fact = _normalize_fact(fact)
        key = _fact_key(fact, aliases)
        if key is None:
            raise ValueError(f"[{fmt_id}] source fact without resolvable id: {fact.get('claim', '')[:80]}")
        if key in merged:
            old_claim = merged[key].get("claim", "")
            new_claim = fact.get("claim", "")
            if old_claim and new_claim and old_claim != new_claim:
                raise FactConflictError(
                    f"[{fmt_id}] fact '{key}' claim conflict:\n"
                    f"  combined: {old_claim}\n"
                    f"  source:   {new_claim}\n"
                    f"Resolve explicitly in shared/sal-facts/{fmt_id}.yaml."
                )
            record = dict(merged[key])
            before = dict(record)
            record.update(fact)  # canonical source wins on content
            if "fact_id" not in record and key.startswith("SAL-"):
                record["fact_id"] = key
            merged[key] = record
            if record != before:
                updated += 1
        else:
            record = dict(fact)
            if key.startswith("SAL-"):
                record.setdefault("fact_id", key)
            merged[key] = record
            added += 1

    ordered = [merged[k] for k in sorted(merged)] + unkeyed
    return ordered, {"added": added, "updated": updated, "unkeyed_preserved": len(unkeyed)}


def merge_formats(
    formats: list[str] | None = None,
    dry_run: bool = False,
    check: bool = False,
) -> dict:
    """Union per-format canonical stores into the combined database.

    Returns a summary dict with keys: merged, skipped, errors, drift,
    total_facts_before, total_facts_after.
    """
    if _COMBINED.exists():
        combined = _load_json(_COMBINED)
    else:
        # Fresh checkout: .local/ is gitignored. Bootstrap an empty combined DB
        # and populate it from the committed canonical stores.
        combined = {
            "generated_at": "",
            "generator": "merge_sal_facts.py (bootstrap)",
            "formats_processed": 0,
            "spec_facts_total": 0,
            "workbench_verified_fact_total": 0,
            "results": [],
        }
        _COMBINED.parent.mkdir(parents=True, exist_ok=True)
    results: list[dict] = combined.get("results", [])
    aliases = _load_aliases()

    results_index: dict[str, int] = {e["format_id"]: i for i, e in enumerate(results)}
    total_before = sum(len(e.get("spec_facts", [])) for e in results)

    formats_to_check = formats or _default_formats()
    summary: dict = {
        "merged": [], "skipped": [], "errors": [], "drift": [],
        "total_facts_before": total_before, "total_facts_after": total_before,
    }
    changed = False

    for fmt_id in formats_to_check:
        loaded = _load_source_facts(fmt_id)
        if loaded is None:
            summary["skipped"].append({"format_id": fmt_id, "reason": "no_source_file"})
            continue
        source_facts, source_label, meta = loaded
        if not source_facts:
            summary["skipped"].append({"format_id": fmt_id, "reason": "no_facts_in_source"})
            continue

        existing_idx = results_index.get(fmt_id)
        existing_facts = results[existing_idx].get("spec_facts", []) if existing_idx is not None else []

        try:
            merged_facts, stats = _union_facts(existing_facts, source_facts, aliases, fmt_id)
        except (FactConflictError, ValueError) as exc:
            summary["errors"].append({"format_id": fmt_id, "reason": str(exc)})
            continue

        entry_changed = (
            stats["added"] > 0
            or stats["updated"] > 0
            or [f for f in existing_facts] != merged_facts
        )

        if check:
            if stats["added"] or stats["updated"]:
                summary["drift"].append({
                    "format_id": fmt_id,
                    "missing_in_combined": stats["added"],
                    "content_divergence": stats["updated"],
                    "source": source_label,
                })
            continue

        if not entry_changed:
            summary["skipped"].append({"format_id": fmt_id, "reason": "already_in_sync"})
            continue

        if existing_idx is not None:
            new_entry = dict(results[existing_idx])
        else:
            new_entry = {"format_id": fmt_id}
        for k, v in meta.items():
            new_entry.setdefault(k, v)
        new_entry["spec_facts"] = merged_facts

        if not dry_run:
            if existing_idx is not None:
                results[existing_idx] = new_entry
            else:
                results.append(new_entry)
                results_index[fmt_id] = len(results) - 1
        changed = True

        summary["merged"].append({
            "format_id": fmt_id,
            "facts_before": len(existing_facts),
            "facts_after": len(merged_facts),
            "added": stats["added"],
            "updated": stats["updated"],
            "source": source_label,
        })

    if not check and not dry_run and changed:
        combined["results"] = results
        total_after = sum(len(e.get("spec_facts", [])) for e in results)
        combined["spec_facts_total"] = total_after
        combined["formats_processed"] = len(results)
        combined["generated_at"] = datetime.now(timezone.utc).isoformat()
        combined["generator"] = "merge_sal_facts.py (union, GAP-FORENSIC-008)"
        _COMBINED.write_text(json.dumps(combined, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        summary["total_facts_after"] = total_after

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Union SAL fact stores into the combined database")
    parser.add_argument("--dry-run", action="store_true", help="Report what would merge; no writes")
    parser.add_argument("--check", action="store_true",
                        help="Drift check: exit 2 if the combined DB diverges from the stores")
    parser.add_argument("--formats", help="Comma-separated format ids (default: all covered)")
    args = parser.parse_args()

    formats = [f.strip().lower() for f in args.formats.split(",")] if args.formats else None
    try:
        summary = merge_formats(formats=formats, dry_run=args.dry_run, check=args.check)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    for item in summary["merged"]:
        print(f"  {item['format_id']}: {item['facts_before']} -> {item['facts_after']} facts "
              f"(+{item['added']} added, {item['updated']} updated) from {item['source']}")
    for item in summary["skipped"]:
        print(f"  {item['format_id']}: skipped ({item['reason']})")
    for item in summary["drift"]:
        print(f"  DRIFT {item['format_id']}: {item['missing_in_combined']} facts missing in combined, "
              f"{item['content_divergence']} divergent (source: {item['source']})")
    for item in summary["errors"]:
        print(f"  {item['format_id']}: ERROR {item['reason']}", file=sys.stderr)

    if summary["errors"]:
        return 1
    if args.check and summary["drift"]:
        return 2
    if args.check:
        print("No drift: combined database is a superset of all canonical stores.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
