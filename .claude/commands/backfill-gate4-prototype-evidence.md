---
version: "1.0"
last-updated: "2026-07-01"
phase-available: "all"
gate-required: null
created-by: FF-G4-BACKFILL-001
spec_qname_required: "false"
product_track: "acquisition"
---

# /backfill-gate4-prototype-evidence

Inventory Gate 4 status, classify evidence strategy, create evidence wrappers, create minimal prototypes only when allowed, update registries and acquisition packs, run focused validation, emit resumable evidence.

## What It Does

1. Inventories all tracked formats for Gate 4 evidence gaps
2. Classifies evidence strategy per format (wrapper, minimal prototype, prerequisite blocker)
3. Creates or updates Gate 4 evidence artifacts and registries
4. Runs Gate 4 governance validation
5. Emits resumable evidence records

## Usage

```bash
python tools/gates/validate_gate4_evidence.py --format <format>
python tools/gates/update_gate4_registry.py --format <format>
python tools/gates/patch_gate4_registry_fields.py
```

## Layer

Acquisition — Gate 4 evidence backfill (FF-G4-BACKFILL-001)
