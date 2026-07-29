"""Source researcher for the L30 research plane.

Builds/refreshes the source-record skeleton for a format's research draft:
the registry's spec authority (spec_body/spec_version/spec_url) plus any
already-committed research sources. Network acquisition is OPT-IN
(--allow-network) and runs only through the tracked authority lock,
content-addressed materializer, and live digest audit. The default offline
mode merges lock declarations without fabricating byte availability.

Writes: .local/format-contracts/drafts/{format_id}-sources.yaml
Exit codes: 0 ok · 1 error.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = MODULE_DIR.parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))
sys.path.insert(0, str(MODULE_DIR))

import stores
from canonical_io import canonical_write, load_yaml
from tools.format_contract.authority_lock import (
    DEFAULT_LOCK,
    AuthorityLockError,
    load_lock,
    merge_locked_sources,
    records_for_format,
)
from tools.format_contract.authority_runtime import materialize_sources

DRAFTS_DIR = stores.REPO_ROOT / ".local" / "format-contracts" / "drafts"
ACQUIRED_DIR = stores.REPO_ROOT / ".local" / "format-contracts" / "acquired"


def _fetch(url: str, dest: Path) -> str | None:
    """Legacy opt-in fetch for formats not yet enrolled in the authority lock."""

    try:
        import urllib.request

        with urllib.request.urlopen(  # noqa: S310 - legacy opt-in compatibility
            url, timeout=30
        ) as response:
            payload = response.read()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(payload)
        return hashlib.sha256(payload).hexdigest()
    except Exception as exc:  # noqa: BLE001 - failure is recorded, not promoted
        print(
            f"[fcl-sources] fetch failed ({exc}); recording URL_ONLY",
            file=sys.stderr,
        )
        return None


def _source_records(
    format_id: str, committed: list[dict], *, reset_draft: bool
) -> list[dict]:
    """Merge the durable local draft over committed source records.

    Source discovery often needs several official artifacts.  The local draft
    is the transaction workspace between invocations; discarding it makes a
    second acquisition silently erase the first.
    """

    records = {
        str(record.get("source_id", "")): dict(record)
        for record in committed
        if record.get("source_id")
    }
    draft_path = DRAFTS_DIR / f"{format_id}-sources.yaml"
    if not reset_draft and draft_path.is_file():
        draft = load_yaml(draft_path)
        if draft.get("format_id") == format_id:
            for record in draft.get("source_records", []):
                source_id = str(record.get("source_id", ""))
                if source_id:
                    records[source_id] = dict(record)
    return list(records.values())


def _next_source_id(format_id: str, records: list[dict]) -> str:
    prefix = format_id.upper().replace("_", "")
    used = {str(record.get("source_id", "")) for record in records}
    number = 1
    while f"SRC-{prefix}-{number:03d}" in used:
        number += 1
    return f"SRC-{prefix}-{number:03d}"


def research_sources(
    format_id: str,
    allow_network: bool = False,
    *,
    source_id: str | None = None,
    source_url: str | None = None,
    source_version: str | None = None,
    prepare_intake: bool = False,
    reset_draft: bool = False,
) -> dict:
    reg = stores.load_format_registry_entry(format_id)
    research = stores.load_research(format_id)
    existing = research.get("source_records", [])

    records = _source_records(format_id, existing, reset_draft=reset_draft)
    lock_document = None
    if (stores.REPO_ROOT / DEFAULT_LOCK).is_file():
        try:
            lock_document, _ = load_lock(stores.REPO_ROOT)
        except AuthorityLockError as exc:
            raise stores.StoreError(f"authority lock refused: {exc}") from exc
        records = merge_locked_sources(records, lock_document, format_id)
    if source_id or source_url:
        if not source_id or not source_url:
            raise stores.StoreError("--source-id and --source-url must be supplied together")
        record = next((item for item in records if item.get("source_id") == source_id), None)
        if record is None:
            record = {
                "source_id": source_id,
                "title": f"{reg.get('display_name', format_id)} pinned authority",
                "organization": reg.get("spec_body"),
                "authority_class": "AUTHORITATIVE",
            }
            records.append(record)
        record["canonical_url"] = source_url
        if source_version:
            record["version"] = source_version
        record["acquisition_status"] = "URL_ONLY"

    known_urls = {r.get("canonical_url") for r in records}
    spec_url = reg.get("spec_url")
    if spec_url and spec_url not in known_urls:
        record = {
            "source_id": _next_source_id(format_id, records),
            "title": f"{reg.get('spec_body', 'unknown authority')} {reg.get('spec_version', '')}".strip(),
            "organization": reg.get("spec_body"),
            "version": str(reg.get("spec_version", "")) or None,
            "canonical_url": spec_url,
            "authority_class": "AUTHORITATIVE",
            "acquisition_status": "URL_ONLY",
        }
        records.append(record)
    elif not spec_url and not records:
        records.append({
            "source_id": _next_source_id(format_id, records),
            "title": f"{format_id} specification source (not yet identified)",
            "organization": None,
            "authority_class": "UNVERIFIED",
            "acquisition_status": "NEEDS_AUTHORITY",
        })

    materialization = []
    if allow_network:
        locked = (
            records_for_format(lock_document, format_id)
            if lock_document is not None
            else []
        )
        if locked:
            assert lock_document is not None
            materialization = materialize_sources(
                stores.REPO_ROOT,
                lock_document,
                online=True,
                formats=[format_id],
            )
            failed = [item for item in materialization if item.status != "MATCH"]
            if failed:
                detail = "; ".join(
                    f"{item.source_id}={item.status}({item.detail})"
                    for item in failed
                )
                raise stores.StoreError(
                    f"{format_id}: locked authority materialization failed: {detail}"
                )
        else:
            for record in records:
                if (
                    record.get("authority_class") != "AUTHORITATIVE"
                    or not record.get("canonical_url")
                ):
                    continue
                dest = (
                    ACQUIRED_DIR
                    / format_id
                    / f"{record['source_id'].lower()}.bin"
                )
                digest = _fetch(str(record["canonical_url"]), dest)
                if digest:
                    record["content_hash"] = digest
                    try:
                        local_path = dest.relative_to(stores.REPO_ROOT).as_posix()
                    except ValueError:
                        local_path = f"<external-acquired>/{dest.name}"
                    record["local_path"] = local_path
                    record["acquisition_status"] = "ACQUIRED"

    records.sort(key=lambda item: str(item.get("source_id", "")))
    doc = {"format_id": format_id, "source_records": records}
    out = DRAFTS_DIR / f"{format_id}-sources.yaml"
    canonical_write(out, doc)
    intake_path = None
    if prepare_intake:
        intake_doc = {
            "format_id": format_id,
            "source_records": records,
            "findings": research.get("findings", []),
            "sal_candidates": [],
        }
        intake_path = DRAFTS_DIR / f"{format_id}-draft.yaml"
        canonical_write(intake_path, intake_doc)
    return {
        "records": len(records),
        "out": str(out),
        "intake_draft": str(intake_path) if intake_path else None,
        "materialized": len(materialization),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format-id", required=True)
    parser.add_argument("--allow-network", action="store_true")
    parser.add_argument("--source-id")
    parser.add_argument("--source-url")
    parser.add_argument("--source-version")
    parser.add_argument("--prepare-intake", action="store_true")
    parser.add_argument(
        "--reset-draft",
        action="store_true",
        help="ignore the local source draft and rebuild from committed research",
    )
    args = parser.parse_args(argv)
    try:
        result = research_sources(
            args.format_id.lower(),
            args.allow_network,
            source_id=args.source_id,
            source_url=args.source_url,
            source_version=args.source_version,
            prepare_intake=args.prepare_intake,
            reset_draft=args.reset_draft,
        )
    except stores.StoreError as exc:
        print(f"[fcl-sources] ERROR {exc}", file=sys.stderr)
        return 1
    print(f"[fcl-sources] {args.format_id}: {result['records']} source records -> {result['out']}")
    if result["intake_draft"]:
        print(f"[fcl-sources] intake draft -> {result['intake_draft']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
