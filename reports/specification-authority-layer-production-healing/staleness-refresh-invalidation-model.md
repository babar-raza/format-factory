# Staleness, Refresh, and Invalidation Model
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Overview

The staleness model ensures that all downstream artifacts become invalid when an upstream
spec source changes. SpecGovernanceRuntime enforces that stale artifacts cannot be used
in production context packs.

---

## Staleness Propagation Chain

```
Source URL content changes (new SHA-256 detected)
  │
  ▼
refresh_event (M) created
  │
  ├─► raw_snapshot (C): new snapshot ingested → new sha256
  │     │
  │     ├─► parsed_artifact (D): stale=true (source sha256 changed)
  │     │     │
  │     │     └─► normalized_artifact (E): stale=true
  │     │           │
  │     │           ├─► indexed_artifact (F): stale=true
  │     │           ├─► digest_artifact (G): stale=true
  │     │           └─► candidate_requirement (H): stale=true
  │     │                 │
  │     │                 └─► verified_requirement (I): stale=true
  │     │                       │
  │     │                       └─► context_pack (J): stale=true
  │     │
  │     └─► (old snapshot retained in vault — immutable; sha256 still valid for old packs)
  │
  └─► All stale artifacts flagged; SpecGovernanceRuntime blocks new pack builds from stale chain
```

---

## Staleness Detection

### Method 1 — Scheduled Check (polling)
```python
def check_staleness(source_id, interval_hours=24):
    registry_record = spec_source_registry.get(source_id)
    current_sha256 = fetch_sha256(registry_record["url"])
    stored_sha256 = spec_vault.get_latest_sha256(source_id)
    if current_sha256 != stored_sha256:
        create_refresh_event(source_id, current_sha256, stored_sha256)
        propagate_staleness(stored_sha256)
```

### Method 2 — On-demand Check (before context pack build)
```python
def validate_before_build(source_sha256s):
    for sha256 in source_sha256s:
        record = spec_vault.get_record(sha256)
        current = fetch_sha256(record["url"])
        if current != sha256:
            raise StaleSourceError(f"Source {sha256} is stale; current={current}")
```

---

## Staleness Flags

Each artifact carries:
```json
{
  "stale": false,
  "stale_reason": null,
  "stale_detected_at": null,
  "stale_source_sha256": null
}
```

When stale propagation runs:
```json
{
  "stale": true,
  "stale_reason": "source_sha256_changed",
  "stale_detected_at": "2026-06-04T16:30:00Z",
  "stale_source_sha256": "abc123..."
}
```

---

## Refresh Protocol

### Step 1 — Create refresh_event
```json
{
  "event_id": "refresh-<uuid>",
  "source_id": "<source_id>",
  "old_sha256": "<old>",
  "new_sha256": "<new>",
  "detected_at": "<ISO datetime>",
  "propagation_complete": false
}
```

### Step 2 — Re-ingest raw_snapshot
```python
new_snapshot_id = spec_vault.ingest(source_id)
# new_snapshot_id = new SHA-256
```

### Step 3 — Re-run pipeline from C
```
new_snapshot (C) → parse (D) → normalize (E) → index (F) → digest (G)
                                               → extract (H) → verify (I)
                                               → context pack rebuild (J)
```

### Step 4 — Update refresh_event
```json
{ "propagation_complete": true, "completed_at": "<ISO datetime>" }
```

---

## Invalidation vs Staleness

| Concept | Definition | Recoverable? |
|---------|-----------|-------------|
| Stale | Artifact exists but source sha256 changed; needs re-processing | Yes (refresh) |
| Invalid | Artifact was produced by a failed or rejected process | Yes (re-run) |
| Quarantined | Source has unclear license; ingestion blocked | Blocked (needs license review) |
| Archived | Old artifact retained for audit but not active | Read-only |

---

## SpecGovernanceRuntime Enforcement

SpecGovernanceRuntime runs staleness check at:
1. context_pack build time — blocks build if any source stale
2. stream handoff validation — blocks handoff if context_pack is stale
3. evidence declaration review — flags stale context_pack_ids in declaration

```python
def validate_handoff(context_pack_id):
    pack = context_pack_store.get(context_pack_id)
    if pack["stale"]:
        return FAIL(f"context pack {context_pack_id} is stale: {pack['stale_reason']}")
    for source_sha256 in pack["source_sha256s"]:
        if not spec_vault.exists(source_sha256):
            return FAIL(f"source snapshot {source_sha256} not in vault")
    return PASS
```
