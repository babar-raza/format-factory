"""
export_sal_fact_stores.py — One-shot migration: export manually-seeded formats'
SAL facts into committed canonical stores at shared/sal-facts/{format}.yaml.

GAP-FORENSIC-008 machinery hardening (Phase 1).

Problem: .local/spec-cache/sal-facts-latest.json is gitignored, yet it is the
only complete store for the 14 manually-seeded formats. A fresh checkout cannot
reconstruct their facts. shared/sal-fact-overrides.yaml commits only a partial
overlay. This script unions both sources per format and writes one committed
YAML store per format, which merge_sal_facts.py then treats as the canonical
input (committed store > per-format cache).

Union rules:
  - Facts keyed by fact_id (falling back to qname for legacy records).
  - Combined-DB record wins on field content; override entries contribute
    facts absent from the DB and supplement missing fields (never overwrite).
  - Missing fact_id is filled from shared/sal-fact-id-aliases.json.
  - Facts sorted by fact_id for deterministic output.

Usage:
    python tools/spec/export_sal_fact_stores.py [--dry-run] [--formats qoi,zst]

Exit codes:
    0 — success
    1 — error (missing inputs, fact without resolvable fact_id)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
_COMBINED = _REPO / ".local" / "spec-cache" / "sal-facts-latest.json"
_OVERRIDES = _REPO / "shared" / "sal-fact-overrides.yaml"
_ALIASES = _REPO / "shared" / "sal-fact-id-aliases.json"
_STORE_DIR = _REPO / "shared" / "sal-facts"

# The manually-seeded formats whose facts have no reproducible extraction
# pipeline. Mirrors merge_sal_facts._FORMAT_FILE_CANDIDATES keys.
MANUALLY_SEEDED_FORMATS = (
    "csv", "tsv", "toml", "abw", "dif", "gnumeric", "sylk",
    "ndjson", "xcf", "zst", "qoi", "pbm", "pgm", "ppm",
)

# Canonical key order for fact records in the committed store.
_KEY_ORDER = (
    "fact_id", "qname", "element_qname", "claim", "section", "description",
    "authority", "source", "fact_status", "verification_status",
    "authority_class", "code_bindings", "provenance",
)


def _load_aliases() -> dict[str, str]:
    data = json.loads(_ALIASES.read_text(encoding="utf-8"))
    return data.get("aliases", {})


def _fact_key(fact: dict, aliases: dict[str, str]) -> str | None:
    """Stable identity for a fact: fact_id, else alias of qname/claim_id."""
    fid = fact.get("fact_id")
    if fid:
        return fid
    legacy = fact.get("qname") or fact.get("claim_id")
    if legacy and legacy in aliases:
        return aliases[legacy]
    return legacy


def _order_keys(fact: dict) -> dict:
    ordered: dict = {}
    for key in _KEY_ORDER:
        if key in fact:
            ordered[key] = fact[key]
    for key in fact:
        if key not in ordered:
            ordered[key] = fact[key]
    return ordered


def _override_to_fact(entry: dict) -> dict:
    """Convert a sal-fact-overrides.yaml entry to a spec_fact record."""
    fact = {
        "fact_id": entry.get("fact_id"),
        "qname": entry.get("qname"),
        "claim": entry.get("claim"),
        "verification_status": entry.get("verification_status"),
    }
    if entry.get("element_qname"):
        fact["element_qname"] = entry["element_qname"]
    provenance = {
        k: entry[k]
        for k in ("spec_id", "section_id", "extraction_method", "confidence",
                  "added_by", "added_at")
        if k in entry
    }
    if provenance:
        fact["provenance"] = provenance
    return {k: v for k, v in fact.items() if v is not None}


def export_stores(formats: list[str] | None = None, dry_run: bool = False) -> dict:
    if not _COMBINED.exists():
        raise FileNotFoundError(f"Combined SAL database not found: {_COMBINED}")

    combined = json.loads(_COMBINED.read_text(encoding="utf-8"))
    overrides_doc = yaml.safe_load(_OVERRIDES.read_text(encoding="utf-8")) or {}
    aliases = _load_aliases()

    db_by_format: dict[str, dict] = {
        e["format_id"]: e for e in combined.get("results", [])
    }
    overrides_by_format: dict[str, list[dict]] = {}
    for entry in overrides_doc.get("overrides", []):
        overrides_by_format.setdefault(entry.get("format_id", "").lower(), []).append(entry)

    targets = formats or list(MANUALLY_SEEDED_FORMATS)
    summary: dict = {"written": [], "skipped": [], "errors": []}

    for fmt in targets:
        db_entry = db_by_format.get(fmt)
        facts_by_key: dict[str, dict] = {}

        for fact in (db_entry or {}).get("spec_facts", []):
            fact = dict(fact)
            key = _fact_key(fact, aliases)
            if key is None:
                summary["errors"].append(
                    {"format_id": fmt, "reason": f"fact without resolvable id: {fact.get('claim', '')[:80]}"}
                )
                continue
            fact.setdefault("fact_id", key if key.startswith("SAL-") else aliases.get(key, key))
            facts_by_key[key] = fact

        for entry in overrides_by_format.get(fmt, []):
            fact = _override_to_fact(entry)
            key = _fact_key(fact, aliases)
            if key is None:
                continue
            if key in facts_by_key:
                # Supplement missing fields only — DB record wins on content.
                for k, v in fact.items():
                    facts_by_key[key].setdefault(k, v)
            else:
                facts_by_key[key] = fact

        if not facts_by_key:
            summary["skipped"].append({"format_id": fmt, "reason": "no_facts_in_any_source"})
            continue

        facts = [_order_keys(facts_by_key[k]) for k in sorted(facts_by_key)]
        store = {
            "format_id": fmt,
            "display_name": (db_entry or {}).get("display_name", fmt.upper()),
            "schema_version": "1.0",
            "canonical": True,
            "note": (
                "Committed canonical SAL fact store for a manually-seeded format. "
                "This file is the source of truth; .local/spec-cache/ copies are "
                "derived. Compile with: python tools/spec/merge_sal_facts.py"
            ),
            "facts": facts,
        }

        out_path = _STORE_DIR / f"{fmt}.yaml"
        if not dry_run:
            _STORE_DIR.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                yaml.safe_dump(store, sort_keys=False, allow_unicode=True, width=100),
                encoding="utf-8",
            )
        summary["written"].append({"format_id": fmt, "facts": len(facts), "path": str(out_path.relative_to(_REPO))})

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--formats", help="Comma-separated format ids (default: all 14)")
    args = parser.parse_args()

    formats = [f.strip().lower() for f in args.formats.split(",")] if args.formats else None
    try:
        summary = export_stores(formats=formats, dry_run=args.dry_run)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    for item in summary["written"]:
        print(f"  {item['format_id']}: {item['facts']} facts -> {item['path']}")
    for item in summary["skipped"]:
        print(f"  {item['format_id']}: SKIPPED ({item['reason']})")
    for item in summary["errors"]:
        print(f"  {item['format_id']}: ERROR ({item['reason']})", file=sys.stderr)

    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
