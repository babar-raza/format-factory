"""Source researcher for the L30 research plane.

Builds/refreshes the source-record skeleton for a format's research draft:
the registry's spec authority (spec_body/spec_version/spec_url) plus any
already-committed research sources. Network acquisition is OPT-IN
(--allow-network); the default offline mode records URL_ONLY /
NEEDS_AUTHORITY statuses honestly instead of fabricating acquisition.

Writes: .local/format-contracts/drafts/{format_id}-sources.yaml
Exit codes: 0 ok · 1 error.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import stores
from canonical_io import canonical_write

DRAFTS_DIR = stores.REPO_ROOT / ".local" / "format-contracts" / "drafts"
ACQUIRED_DIR = stores.REPO_ROOT / ".local" / "format-contracts" / "acquired"


def _fetch(url: str, dest: Path) -> str | None:
    """Fetch a source (opt-in only); returns sha256 or None on failure."""
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310 (opt-in, governed)
            payload = resp.read()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(payload)
        return hashlib.sha256(payload).hexdigest()
    except Exception as exc:  # noqa: BLE001 - recorded, not raised
        print(f"[fcl-sources] fetch failed ({exc}); recording URL_ONLY", file=sys.stderr)
        return None


def research_sources(
    format_id: str,
    allow_network: bool = False,
    *,
    source_id: str | None = None,
    source_url: str | None = None,
    source_version: str | None = None,
    prepare_intake: bool = False,
) -> dict:
    reg = stores.load_format_registry_entry(format_id)
    research = stores.load_research(format_id)
    existing = research.get("source_records", [])
    fmt = format_id.upper().replace("_", "")

    records = [dict(record) for record in existing]
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
            "source_id": f"SRC-{fmt}-{len(records) + 2:03d}",
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
            "source_id": f"SRC-{fmt}-002",
            "title": f"{format_id} specification source (not yet identified)",
            "organization": None,
            "authority_class": "UNVERIFIED",
            "acquisition_status": "NEEDS_AUTHORITY",
        })

    if allow_network:
        for record in records:
            if (
                record.get("authority_class") != "AUTHORITATIVE"
                or not record.get("canonical_url")
            ):
                continue
            dest = ACQUIRED_DIR / format_id / f"{record['source_id'].lower()}.bin"
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
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format-id", required=True)
    parser.add_argument("--allow-network", action="store_true")
    parser.add_argument("--source-id")
    parser.add_argument("--source-url")
    parser.add_argument("--source-version")
    parser.add_argument("--prepare-intake", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = research_sources(
            args.format_id.lower(),
            args.allow_network,
            source_id=args.source_id,
            source_url=args.source_url,
            source_version=args.source_version,
            prepare_intake=args.prepare_intake,
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
