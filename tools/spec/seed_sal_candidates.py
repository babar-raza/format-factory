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
import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any, cast

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
QUEUE_DIR = REPO_ROOT / ".local" / "supervisor" / "sal-candidates"
SAL_DIR = REPO_ROOT / "shared" / "sal-facts"
RESEARCH_DIR = REPO_ROOT / "shared" / "format-contracts" / "research"
FORMAT_REGISTRY = REPO_ROOT / "registry" / "format-registry.yaml"
MERGE = REPO_ROOT / "tools" / "spec" / "merge_sal_facts.py"
COMBINED_CACHE = REPO_ROOT / ".local" / "spec-cache" / "sal-facts-latest.json"
ALIASES_PATH = REPO_ROOT / "shared" / "sal-fact-id-aliases.json"


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


def _stable_fact_id(
    format_id: str,
    candidate: dict[str, Any],
    authority_sources: list[dict[str, str]],
) -> str:
    identity = {
        "format_id": format_id,
        "claim": str(candidate.get("claim", "")).strip(),
        "element_qname": str(candidate.get("element_qname", "")).strip(),
        "section": str(candidate.get("section", "")).strip(),
        "authority_sources": sorted(
            authority_sources,
            key=lambda item: (item["source_id"], item["sha256"]),
        ),
    }
    digest = hashlib.sha256(
        json.dumps(
            identity,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()[:16].upper()
    return f"SAL-{format_id.upper()}-{digest}"


def _append_facts_preserving_store(
    store_path: Path,
    store: dict[str, Any],
    new_facts: list[dict[str, Any]],
) -> None:
    if list(store)[-1:] != ["facts"]:
        raise RuntimeError(
            "existing canonical SAL store must keep facts as its final top-level key"
        )
    fragment = yaml.safe_dump(
        {"facts": new_facts},
        sort_keys=False,
        allow_unicode=True,
        width=110,
    )
    prefix = "facts:\n"
    if not fragment.startswith(prefix):
        raise RuntimeError("failed to serialize SAL fact append fragment")
    fact_rows = fragment.removeprefix(prefix).encode("utf-8")
    original = store_path.read_bytes()
    for suffix, newline in (
        (b"facts: []\r\n", b"\r\n"),
        (b"facts: []\n", b"\n"),
        (b"facts: []", b"\n"),
    ):
        if original.endswith(suffix):
            prefix_bytes = original[: -len(suffix)]
            rows = fact_rows.replace(b"\n", newline)
            store_path.write_bytes(prefix_bytes + b"facts:" + newline + rows)
            return
    separator = b"" if original.endswith((b"\n", b"\r")) else b"\n"
    with store_path.open("ab") as fh:
        fh.write(separator + fact_rows)


def _snapshot(path: Path) -> bytes | None:
    return path.read_bytes() if path.is_file() else None


def _restore_snapshot(path: Path, content: bytes | None) -> None:
    if content is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _select_candidates(
    candidates: list[dict[str, Any]],
    candidate_id: str | None,
) -> list[dict[str, Any]]:
    if candidate_id is None:
        return candidates
    selected = [
        candidate
        for candidate in candidates
        if str(candidate.get("candidate_id", "")) == candidate_id
    ]
    if not selected:
        raise RuntimeError(
            f"candidate_id {candidate_id!r} must match exactly one queue row; matched 0"
        )
    if len(selected) > 1:
        raise RuntimeError(
            f"candidate_id {candidate_id!r} must match exactly one queue row; "
            f"matched {len(selected)}"
        )
    return [selected[0]]


def seed(
    format_id: str,
    added_by: str,
    *,
    candidate_id: str | None = None,
) -> dict[str, Any]:
    queue_path = QUEUE_DIR / f"{format_id}.yaml"
    if not queue_path.is_file():
        return {"seeded": 0, "skipped": 0, "note": "no candidate queue"}
    queue = yaml.safe_load(queue_path.read_text(encoding="utf-8")) or {}
    candidates = queue.get("candidates", [])
    if not candidates:
        return {"seeded": 0, "skipped": 0, "note": "empty queue"}
    candidates = _select_candidates(candidates, candidate_id)

    store_path = SAL_DIR / f"{format_id}.yaml"
    store_exists = store_path.is_file()
    original_store_bytes = _snapshot(store_path)
    original_combined_bytes = _snapshot(COMBINED_CACHE)
    original_alias_bytes = _snapshot(ALIASES_PATH)
    store = (
        yaml.safe_load(store_path.read_text(encoding="utf-8"))
        if store_exists
        else _new_store(format_id)
    )
    facts = store.setdefault("facts", [])
    existing_claims = {str(f.get("claim", "")).strip() for f in facts}
    existing_ids = {
        str(f.get("fact_id", "")): str(f.get("claim", "")).strip()
        for f in facts
        if f.get("fact_id")
    }
    acquired_sources = _authority_sources(format_id)
    max_num = 0
    for fact in facts:
        fid = str(fact.get("fact_id", ""))
        if fid.startswith(f"SAL-{format_id.upper()}-"):
            try:
                max_num = max(max_num, int(fid.rsplit("-", 1)[1]))
            except ValueError:
                pass
        qname = str(fact.get("qname", ""))
        if qname.startswith(f"FACT-{format_id.upper()}-"):
            try:
                max_num = max(max_num, int(qname.rsplit("-", 1)[1]))
            except ValueError:
                pass

    seeded = skipped = 0
    new_facts: list[dict[str, Any]] = []
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
        fact_id = _stable_fact_id(format_id, cand, authority_sources)
        existing_claim = existing_ids.get(fact_id)
        if existing_claim is not None and existing_claim != claim:
            raise RuntimeError(
                f"stable SAL identity collision for {fact_id}: "
                "existing and candidate claims differ"
            )
        readiness_categories = cand.get("readiness_categories", [])
        if not isinstance(readiness_categories, list) or not all(
            isinstance(category, str) and category.strip()
            for category in readiness_categories
        ):
            raise RuntimeError("readiness_categories must be a list of non-empty strings")
        max_num += 1
        new_fact = {
            "fact_id": fact_id,
            "qname": f"FACT-{format_id.upper()}-{max_num}",
            "element_qname": cand.get("element_qname", f"{format_id}:unspecified"),
            "claim": claim,
            "section": cand.get("section", "structural derivation"),
            "authority": cand.get("authority", "unspecified"),
            "source": "structural_fact_manual",
            "fact_status": "verified",
            "verification_status": "structural_derivation",
            "readiness_categories": sorted(set(readiness_categories)),
            "provenance": {
                "extraction_method": "structural_derivation",
                "confidence": "medium",
                "added_by": added_by,
                "added_at": today,
                "authority_sources": authority_sources,
            },
        }
        facts.append(new_fact)
        new_facts.append(new_fact)
        existing_claims.add(claim)
        existing_ids[fact_id] = claim
        seeded += 1

    if seeded:
        store_path.parent.mkdir(parents=True, exist_ok=True)
        if store_exists:
            _append_facts_preserving_store(store_path, store, new_facts)
        else:
            with store_path.open("w", encoding="utf-8", newline="\n") as fh:
                yaml.safe_dump(
                    store,
                    fh,
                    sort_keys=False,
                    allow_unicode=True,
                    width=110,
                )
        try:
            merge = subprocess.run(
                [sys.executable, str(MERGE), "--formats", format_id],
                cwd=str(REPO_ROOT),
                capture_output=True, text=True, timeout=300,
            )
            if merge.returncode != 0:
                raise RuntimeError(f"merge_sal_facts failed: {merge.stderr[-400:]}")
        except Exception:
            _restore_snapshot(store_path, original_store_bytes)
            _restore_snapshot(COMBINED_CACHE, original_combined_bytes)
            _restore_snapshot(ALIASES_PATH, original_alias_bytes)
            raise
    return {"seeded": seeded, "skipped": skipped, "total_facts": len(facts)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format-id", required=True)
    parser.add_argument("--added-by", required=True)
    parser.add_argument(
        "--candidate-id",
        help="Seed exactly one stable queue candidate ID and ignore unrelated rows.",
    )
    args = parser.parse_args(argv)
    try:
        result = seed(
            args.format_id.lower(),
            args.added_by,
            candidate_id=args.candidate_id,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[sal-seed] ERROR {exc}", file=sys.stderr)
        return 1
    print(f"[sal-seed] {args.format_id}: seeded {result['seeded']}, "
          f"skipped {result['skipped']} (store total {result.get('total_facts', '?')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
