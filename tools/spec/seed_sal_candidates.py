"""SAL candidate seeding — the ingest-spec-sal manual-seed path (L01).

Commits reviewed SAL candidates from the L30 research-plane queue
(.local/supervisor/sal-candidates/{format_id}.yaml) into the committed
canonical store shared/sal-facts/{format_id}.yaml with proper fact IDs and
structural_fact_manual provenance (the exact pattern used by prior manual
seeding, e.g. TC-GWB-H03), then recompiles the derived cache via
merge_sal_facts.py.

Idempotent: a candidate whose claim already exists verbatim in the store is
skipped. Never modifies or removes existing facts (union semantics).

Usage:
    python tools/spec/seed_sal_candidates.py --format-id ubl --added-by TC-FCL-050
Exit codes: 0 seeded (or nothing to do) · 1 error.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
QUEUE_DIR = REPO_ROOT / ".local" / "supervisor" / "sal-candidates"
SAL_DIR = REPO_ROOT / "shared" / "sal-facts"
RESEARCH_DIR = REPO_ROOT / "shared" / "format-contracts" / "research"
FORMAT_REGISTRY = REPO_ROOT / "registry" / "format-registry.yaml"
MERGE = REPO_ROOT / "tools" / "spec" / "merge_sal_facts.py"


def _format_metadata(format_id: str) -> dict[str, Any]:
    registry = cast(
        dict[str, Any],
        yaml.safe_load(FORMAT_REGISTRY.read_text(encoding="utf-8")) or {},
    )
    for entry in registry.get("formats", []):
        if str(entry.get("format_id", "")).lower() == format_id:
            return cast(dict[str, Any], entry)
    return {}


def _new_store(format_id: str) -> dict[str, Any]:
    metadata = _format_metadata(format_id)
    return {
        "format_id": format_id,
        "display_name": metadata.get("display_name", format_id.upper()),
        "schema_version": "1.0",
        "canonical": True,
        "note": (
            "Committed canonical SAL fact store initialized from reviewed, "
            "digest-bound authority candidates."
        ),
        "facts": [],
    }


def _authority_sources(format_id: str) -> dict[str, str]:
    research_path = RESEARCH_DIR / f"{format_id}.yaml"
    if not research_path.is_file():
        return {}
    research = yaml.safe_load(research_path.read_text(encoding="utf-8")) or {}
    sources: dict[str, str] = {}
    for record in research.get("source_records", []):
        source_id = str(record.get("source_id", ""))
        digest = str(record.get("content_hash", ""))
        if (
            source_id
            and record.get("acquisition_status") == "ACQUIRED"
            and len(digest) == 64
        ):
            sources[source_id] = digest
    return sources


def _candidate_authority(
    candidate: dict[str, Any], acquired_sources: dict[str, str]
) -> list[dict[str, str]]:
    source_ids = candidate.get("source_ids")
    if source_ids is None and candidate.get("source_id"):
        source_ids = [candidate["source_id"]]
    if not isinstance(source_ids, list) or not source_ids:
        raise RuntimeError("new SAL candidate has no acquired source_ids")
    resolved = []
    for source_id in source_ids:
        source_id = str(source_id)
        digest = acquired_sources.get(source_id)
        if not digest:
            raise RuntimeError(
                f"new SAL candidate references an unacquired authority: {source_id}"
            )
        declared = candidate.get("source_sha256")
        if declared and str(declared) != digest:
            raise RuntimeError(
                f"candidate source digest mismatch for {source_id}: "
                f"declared {declared}, acquired {digest}"
            )
        resolved.append({"source_id": source_id, "sha256": digest})
    return resolved


def seed(format_id: str, added_by: str) -> dict[str, Any]:
    queue_path = QUEUE_DIR / f"{format_id}.yaml"
    if not queue_path.is_file():
        return {"seeded": 0, "skipped": 0, "note": "no candidate queue"}
    queue = yaml.safe_load(queue_path.read_text(encoding="utf-8")) or {}
    candidates = queue.get("candidates", [])
    if not candidates:
        return {"seeded": 0, "skipped": 0, "note": "empty queue"}

    store_path = SAL_DIR / f"{format_id}.yaml"
    store = (
        yaml.safe_load(store_path.read_text(encoding="utf-8"))
        if store_path.is_file()
        else _new_store(format_id)
    )
    facts = store.setdefault("facts", [])
    existing_claims = {str(f.get("claim", "")).strip() for f in facts}
    acquired_sources = _authority_sources(format_id)
    max_num = 0
    for fact in facts:
        fid = str(fact.get("fact_id", ""))
        if fid.startswith(f"SAL-{format_id.upper()}-"):
            try:
                max_num = max(max_num, int(fid.rsplit("-", 1)[1]))
            except ValueError:
                pass

    seeded = skipped = 0
    today = date.today().isoformat()
    for cand in candidates:
        claim = str(cand.get("claim", "")).strip()
        if not claim or len(claim) < 25:
            skipped += 1
            continue
        if claim in existing_claims:
            skipped += 1
            continue
        authority_sources = _candidate_authority(cand, acquired_sources)
        max_num += 1
        facts.append({
            "fact_id": f"SAL-{format_id.upper()}-{max_num:05d}",
            "qname": f"FACT-{format_id.upper()}-{max_num}",
            "element_qname": cand.get("element_qname", f"{format_id}:unspecified"),
            "claim": claim,
            "section": cand.get("section", "structural derivation"),
            "authority": cand.get("authority", "unspecified"),
            "source": "structural_fact_manual",
            "fact_status": "verified",
            "verification_status": "structural_derivation",
            "provenance": {
                "extraction_method": "structural_derivation",
                "confidence": "medium",
                "added_by": added_by,
                "added_at": today,
                "authority_sources": authority_sources,
            },
        })
        existing_claims.add(claim)
        seeded += 1

    if seeded:
        store_path.parent.mkdir(parents=True, exist_ok=True)
        with store_path.open("w", encoding="utf-8", newline="\n") as fh:
            yaml.safe_dump(store, fh, sort_keys=False, allow_unicode=True, width=110)
        merge = subprocess.run(
            [sys.executable, str(MERGE)], cwd=str(REPO_ROOT),
            capture_output=True, text=True, timeout=300,
        )
        if merge.returncode != 0:
            raise RuntimeError(f"merge_sal_facts failed: {merge.stderr[-400:]}")
    return {"seeded": seeded, "skipped": skipped, "total_facts": len(facts)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format-id", required=True)
    parser.add_argument("--added-by", required=True)
    args = parser.parse_args(argv)
    try:
        result = seed(args.format_id.lower(), args.added_by)
    except Exception as exc:  # noqa: BLE001
        print(f"[sal-seed] ERROR {exc}", file=sys.stderr)
        return 1
    print(f"[sal-seed] {args.format_id}: seeded {result['seeded']}, "
          f"skipped {result['skipped']} (store total {result.get('total_facts', '?')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
