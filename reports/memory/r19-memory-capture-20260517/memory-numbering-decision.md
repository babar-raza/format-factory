# Memory Numbering Decision
**Sprint:** R19-MEMORY-CAPTURE-DEDICATED-001
**Date:** 2026-05-17

## Available Memory Numbers

Inspected memory/ directory listing:
- memory/35 — EXISTS (R18)
- memory/36 — DOES NOT EXIST
- memory/37 — DOES NOT EXIST
- memory/38 — EXISTS (R21)

## Decision

Use **memory/36** for the R19 backfill.

Rationale:
- memory/36 is unused
- R19 is chronologically the next sprint after R18 (memory/35)
- Using 36 preserves numbering intent even though R20 memory/37 is also missing
- The file will include a backfill note explaining that memory/38 (R21) already exists

## File Name

`memory/36-r19-high-throughput-acquisition-train-20260517.md`

## Backfill Note (to include in file)

> **BACKFILL NOTE:** This memory file was created 2026-05-17, after R20 (memory/37 missing) and
> R21 (memory/38) were committed. It captures R19 state only. memory/38 remains authoritative for
> R21 and later state. memory/37 (R20) remains unwritten — separate backfill if needed.
