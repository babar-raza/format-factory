# Deterministic Context-Pack Contract
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Contract Statement

**Canonical property:** For any set of registered source snapshots, a given request type,
and a given index version:

```
same source_sha256_set + same request_type + same index_version
  → same context pack contents
  → same manifest.sha256
```

This holds regardless of: wall-clock time, agent instance, machine, or session context.
Timestamps are recorded in the pack metadata but EXCLUDED from the semantic hash comparison.

---

## Hash Computation

### Canonical Input Construction

```python
def compute_canonical_input(source_sha256_list, request_type, index_version):
    # Sort for determinism (order-independent)
    sorted_sources = sorted(source_sha256_list)
    canonical = "|".join(sorted_sources) + "|" + request_type + "|" + str(index_version)
    return canonical

def compute_manifest_sha256(canonical_input, pack_contents_bytes):
    import hashlib
    combined = canonical_input.encode('utf-8') + b"|" + pack_contents_bytes
    return hashlib.sha256(combined).hexdigest()
```

### Fields INCLUDED in semantic hash
- sorted list of source_sha256 (SHA-256 of each raw_snapshot)
- request_type (string: "implementation" | "test_generation" | "coverage_audit" | ...)
- index_version (integer)
- pack_contents (serialized pack bytes with requirements, sections, examples)

### Fields EXCLUDED from semantic hash (recorded but not hashed)
- created_at (timestamp)
- created_by (agent ID)
- pack_id (UUID assigned at creation time)
- usage_record_ids (appended after pack creation)

---

## Manifest Structure

```json
{
  "context_pack_id": "<uuid>",
  "sprint_id": "<sprint_id>",
  "manifest_sha256": "<64-char-hex>",
  "source_sha256s": ["<sha256-1>", "<sha256-2>"],
  "request_type": "implementation",
  "index_version": 1,
  "canonical_input": "<sorted_sources>|<request_type>|<index_version>",
  "created_at": "<ISO datetime>",
  "format_ids": ["zst", "netpbm"],
  "requirement_ids": ["req-001", "req-002"],
  "stale": false,
  "stale_reason": null
}
```

---

## Validation Protocol

### Pack Freshness Check (before use)
```python
def validate_pack_freshness(context_pack):
    for source_sha256 in context_pack["source_sha256s"]:
        vault_record = spec_vault.get_record(source_sha256)
        if vault_record is None:
            return FAIL("source snapshot not found in vault")
        current_sha256 = spec_vault.fetch_current_sha256(vault_record["url"])
        if current_sha256 != source_sha256:
            mark_stale(context_pack, reason=f"source {source_sha256} updated to {current_sha256}")
            return FAIL("context pack stale")
    return PASS
```

### Determinism Regression Test (category D)
```python
def test_context_pack_determinism():
    inputs = {
        "source_sha256s": ["abc123..."],
        "request_type": "implementation",
        "index_version": 1
    }
    pack1 = context_pack_builder.build(**inputs)
    pack2 = context_pack_builder.build(**inputs)
    assert pack1["manifest_sha256"] == pack2["manifest_sha256"]
```

---

## Anti-bypass Rules

| Bypass Attempt | Detection | Response |
|----------------|-----------|----------|
| Context pack without manifest.sha256 | Check manifest.sha256 field is 64-char hex | Reject: MISSING_MANIFEST_SHA256 |
| Stale source in pack | Freshness check compares vault sha256 to current | Reject: STALE_SOURCE_SHA256 |
| context_pack_id not in usage ledger | Ledger lookup | Warn: UNLEDGERED_PACK (caveat) |
| Pack built from unregistered source | SpecSourceRegistry lookup | Reject: UNREGISTERED_SOURCE |
| ai_draft presented as context pack | Check for ai_draft label | Reject: AI_DRAFT_CANNOT_BE_CONTEXT_PACK |

---

## Contract Guarantees

1. **Reproducibility:** manifest.sha256 uniquely identifies the pack contents for given inputs.
2. **Auditability:** Any pack can be reproduced from (source_sha256s, request_type, index_version).
3. **Staleness detection:** Pack becomes stale when any source sha256 changes at source.
4. **Non-repudiation:** Usage ledger records every pack consumption with timestamp.
5. **Timestamp exclusion:** Generated timestamps do not affect manifest.sha256 — only content does.
