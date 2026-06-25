"""Clean consumer proof: NDJSON load -> inspect -> mutate -> save -> reload.

NDJSON (Newline-Delimited JSON) is a flat list of JSON records.
Mutation is record-list-based: modify the list then write_ndjson().

Steps:
  1. Load NDJSON file to list of dicts
  2. Inspect: record_count, fields, NdjsonDocument domain model
  3. Mutate: append record, write to new file
  4. Reload and verify mutation persisted

DOGFOOD CONTRACT:
  - uses `import ndjson` (installed package, not src/)
  - no src/ path manipulation
  - asserts real semantic result at every boundary

Runnable:
  python examples/python/ndjson/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

import ndjson as ndjson_pkg
from ndjson import load_ndjson, write_ndjson, NdjsonDocument

SAMPLE_NDJSON = _REPO / "samples" / "by-format" / "ndjson" / "valid" / "minimal.ndjson"
OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "ndjson"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Source: {SAMPLE_NDJSON}")
    print(f"NDJSON package: {ndjson_pkg.__file__}")
    print()

    # Step 1: Load
    records = load_ndjson(str(SAMPLE_NDJSON))
    assert isinstance(records, list), f"Expected list, got {type(records)}"
    assert len(records) >= 1, "Expected at least 1 record"
    print(f"[LOAD] {len(records)} records loaded")

    # Step 2: Inspect via NdjsonDocument
    doc = NdjsonDocument.from_file(str(SAMPLE_NDJSON))
    assert doc.spec_qname == "ndjson:record", f"spec_qname={doc.spec_qname!r}"
    print(f"[INSPECT] spec_qname={doc.spec_qname}")
    print(f"  record_count={doc.record_count}")
    assert doc.record_count == len(records)

    rec0 = doc.get_record(0)
    assert rec0 is not None
    print(f"  record[0]={rec0!r}")

    # Step 3: Mutate — list-based
    new_records = list(records) + [{"consumer_key": "CONSUMER_PROOF", "verified": True}]
    out_path = str(OUTPUT_DIR / "consumer_proof.ndjson")
    write_ndjson(new_records, out_path)
    print(f"\n[MUTATE+SAVE] appended record, saved to {out_path}")

    # Step 4: Reload and verify
    records2 = load_ndjson(out_path)
    assert len(records2) == len(records) + 1, f"Expected {len(records)+1}, got {len(records2)}"
    last = records2[-1]
    assert last.get("consumer_key") == "CONSUMER_PROOF", f"Last record: {last!r}"
    assert last.get("verified") is True
    print(f"[RELOAD] {len(records2)} records — last={last!r}  OK")

    doc2 = NdjsonDocument.from_file(out_path)
    assert doc2.record_count == len(records) + 1
    print(f"[RELOAD] NdjsonDocument.record_count={doc2.record_count}  OK")

    print("\nCONSUMER_PROOF: PASS -- load -> inspect -> mutate -> save -> reload verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
