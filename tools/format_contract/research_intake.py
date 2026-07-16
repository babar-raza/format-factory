"""Research-plane intake for the Format Contract Layer (L30).

Validates a DRAFT research file and commits it to the hash-bound store
shared/format-contracts/research/{format_id}.yaml. This is the review gate
that quarantines the non-deterministic plane (RC2/RC3): only findings whose
review verdict is ACCEPTED/ACCEPTED_WITH_EDITS are committed; every finding
must cite source records; normative claims are REFUSED here and routed to the
SAL candidate queue (.local/supervisor/sal-candidates/{format_id}.yaml) for
L01-governed commit via the ingest-spec-sal manual-seed path.

Draft location: .local/format-contracts/drafts/{format_id}-draft.yaml
Draft shape:  {format_id, source_records: [...], findings: [...],
               sal_candidates: [{claim, element_qname, section, authority}, ...]}

Exit codes: 0 committed · 1 validation error (nothing committed).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import stores
from canonical_io import canonical_write, load_yaml

DRAFTS_DIR = stores.REPO_ROOT / ".local" / "format-contracts" / "drafts"
SAL_CANDIDATES_DIR = stores.REPO_ROOT / ".local" / "supervisor" / "sal-candidates"
RESEARCH_SCHEMA = stores.REPO_ROOT / "schemas" / "format-contracts" / "research-findings.schema.json"

_NORMATIVE_MARKERS = ("the specification defines", "the spec says", "normative", "spec section")


def _validate_store_shape(store: dict) -> list[str]:
    import jsonschema
    schema = json.loads(RESEARCH_SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    return [
        f"{'/'.join(str(p) for p in e.absolute_path)}: {e.message[:160]}"
        for e in validator.iter_errors(store)
    ]


def _review_gate(findings: list[dict]) -> tuple[list[dict], list[str]]:
    """Only ACCEPTED findings pass; PENDING/REJECTED are refused with reasons."""
    accepted, errors = [], []
    for finding in findings:
        verdict = (finding.get("review") or {}).get("verdict")
        if verdict in ("ACCEPTED", "ACCEPTED_WITH_EDITS"):
            accepted.append(finding)
        else:
            errors.append(
                f"{finding.get('finding_id')}: review verdict '{verdict}' does not pass the gate"
            )
    return accepted, errors


def _source_closure(store: dict) -> list[str]:
    known = {r["source_id"] for r in store.get("source_records", [])}
    errors = []
    for finding in store.get("findings", []):
        for sid in finding.get("source_ids", []):
            if sid not in known:
                errors.append(f"{finding.get('finding_id')}: unknown source_id {sid}")
    return errors


def intake(format_id: str, draft_path: Path | None = None) -> dict:
    draft_path = draft_path or (DRAFTS_DIR / f"{format_id}-draft.yaml")
    draft = load_yaml(draft_path)
    if not draft:
        raise stores.StoreError(f"draft not found or empty: {draft_path}")
    if draft.get("format_id") != format_id:
        raise stores.StoreError("draft format_id mismatch")

    findings = draft.get("findings", [])
    accepted, gate_errors = _review_gate(findings)
    if gate_errors:
        raise stores.StoreError("review gate refused: " + "; ".join(gate_errors))

    store = {
        "format_id": format_id,
        "schema_version": "1.0",
        "canonical": True,
        "note": (
            "Committed canonical research store (L30 research plane). Findings are "
            "PRODUCT_REQUIREMENT knowledge with mandatory sources and review verdicts. "
            "Normative claims live in shared/sal-facts/ (L01), never here."
        ),
        "source_records": sorted(draft.get("source_records", []),
                                 key=lambda r: r["source_id"]),
        "findings": sorted(accepted, key=lambda f: f["finding_id"]),
    }
    errors = _validate_store_shape(store) + _source_closure(store)
    for finding in store["findings"]:
        req = finding["requirement"].lower()
        if any(marker in req for marker in _NORMATIVE_MARKERS):
            errors.append(
                f"{finding['finding_id']}: reads as a normative claim - route it to the "
                "SAL candidate queue instead of the research store"
            )
    if errors:
        raise stores.StoreError("intake validation failed: " + "; ".join(errors[:10]))

    canonical_write(stores.research_path(format_id), store)

    candidates = draft.get("sal_candidates", [])
    queued = 0
    if candidates:
        SAL_CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
        queue_doc = {
            "format_id": format_id,
            "route": "ingest-spec-sal manual-seed path (L01 commits; L30 never writes shared/sal-facts/)",
            "candidates": sorted(candidates, key=lambda c: str(c.get("claim", ""))[:80]),
        }
        canonical_write(SAL_CANDIDATES_DIR / f"{format_id}.yaml", queue_doc)
        queued = len(candidates)

    store_path = stores.research_path(format_id)
    try:
        store_str = str(store_path.relative_to(stores.REPO_ROOT))
    except ValueError:  # monkeypatched/out-of-repo store (tests)
        store_str = str(store_path)
    return {
        "committed_findings": len(store["findings"]),
        "source_records": len(store["source_records"]),
        "sal_candidates_queued": queued,
        "store": store_str.replace("\\", "/"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format-id", required=True)
    parser.add_argument("--draft")
    args = parser.parse_args(argv)
    try:
        result = intake(args.format_id.lower(),
                        Path(args.draft) if args.draft else None)
    except stores.StoreError as exc:
        print(f"[fcl-intake] REFUSED {exc}", file=sys.stderr)
        return 1
    print(f"[fcl-intake] {args.format_id}: {result['committed_findings']} findings committed, "
          f"{result['sal_candidates_queued']} SAL candidates queued -> {result['store']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
