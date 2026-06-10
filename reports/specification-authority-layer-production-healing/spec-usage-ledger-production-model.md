# Spec Usage Ledger Production Model
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Overview

The spec usage ledger is an append-only record of every context pack consumption.
It provides auditability, traceability, and a basis for coverage analysis.

---

## Storage

**Path:** `.local/spec-usage-ledger/usage-YYYYMMDD.jsonl`
**Format:** JSONL (one JSON object per line)
**Rotation:** Daily (new file per calendar date)
**Immutability:** No in-place updates; no deletions. Corrections use correction_of pattern.

---

## Record Schema

### Consumption Record (type: consumption)
```json
{
  "record_id": "usage-<uuid>",
  "type": "consumption",
  "timestamp": "2026-06-04T16:30:00Z",
  "context_pack_id": "<uuid>",
  "manifest_sha256": "<64-char-hex>",
  "consumer_stream": "mainstream|acceleration|skills|supervisor",
  "consumer_id": "<sprint_id or agent_id>",
  "requirement_ids": ["req-zst-001", "req-zst-002"],
  "source_sha256s": ["<sha256-1>"],
  "task_type": "implementation|test_generation|coverage_audit|review",
  "format_ids": ["zst"],
  "stale_at_consumption": false
}
```

### Correction Record (type: correction)
```json
{
  "record_id": "usage-<uuid>",
  "type": "correction",
  "timestamp": "2026-06-04T17:00:00Z",
  "correction_of": "usage-<original-record-id>",
  "correction_reason": "Wrong context_pack_id cited; correct pack was ...",
  "corrected_context_pack_id": "<correct-uuid>",
  "corrected_manifest_sha256": "<correct-64-char-hex>",
  "corrector_id": "<sprint_id>"
}
```

### Coverage Record (type: coverage)
```json
{
  "record_id": "usage-<uuid>",
  "type": "coverage",
  "timestamp": "2026-06-04T17:05:00Z",
  "context_pack_id": "<uuid>",
  "requirement_ids_addressed": ["req-zst-001"],
  "requirement_ids_missed": ["req-zst-003"],
  "coverage_ratio": 0.67,
  "format_id": "zst",
  "task_type": "implementation"
}
```

---

## Write Protocol

### At Context Pack Consumption (stream handoff)
```python
def record_consumption(context_pack_id, consumer_stream, consumer_id, requirement_ids, task_type):
    pack = context_pack_store.get(context_pack_id)
    record = {
        "record_id": f"usage-{uuid4()}",
        "type": "consumption",
        "timestamp": utcnow().isoformat(),
        "context_pack_id": context_pack_id,
        "manifest_sha256": pack["manifest_sha256"],
        "consumer_stream": consumer_stream,
        "consumer_id": consumer_id,
        "requirement_ids": requirement_ids,
        "source_sha256s": pack["source_sha256s"],
        "task_type": task_type,
        "format_ids": pack.get("format_ids", []),
        "stale_at_consumption": pack.get("stale", False)
    }
    ledger_path = Path(f".local/spec-usage-ledger/usage-{date.today():%Y%m%d}.jsonl")
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record["record_id"]
```

---

## Query Protocol

### By context_pack_id
```python
def get_by_pack(context_pack_id):
    return [r for r in read_all_records() if r.get("context_pack_id") == context_pack_id]
```

### By source_sha256
```python
def get_by_source(source_sha256):
    return [r for r in read_all_records() if source_sha256 in r.get("source_sha256s", [])]
```

---

## Retention and Archival

| Rule | Value |
|------|-------|
| Hot retention | 90 days (queryable) |
| Cold archive | Forever (compressed JSONL) |
| Deletion | Never (append-only) |
| Backup | Mirror to .local/spec-usage-ledger/archive/ |

---

## Ledger Validation

At evidence closeout:
```python
def validate_ledger():
    for line in read_all_records():
        assert "record_id" in line
        assert "type" in line
        assert "timestamp" in line
        assert "manifest_sha256" in line or line["type"] == "correction"
    return "LEDGER_VALID"
```
