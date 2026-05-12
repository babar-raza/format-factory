# DEC-033 Resolution: Option B Selected

**Decision:** DEC-033 — .NET FOSS Packaging Strategy
**Status:** RESOLVED
**Option:** B — .NET Commercial Only
**Resolved by:** Babar Raza
**Resolved date:** 2026-05-12
**Sprint:** DEC033-OPTION-B-GATE11-COMMERCIAL-SWARM-001

---

## Decision Summary

DEC-033 governed whether `src/net/{format}/` includes a separate FOSS-tier packaging
model alongside the commercial .NET product. Option B is selected:

**Option B: .NET Commercial Only**

- `src/net/{format}/` is commercial-only source
- No .NET FOSS package is produced for any format
- Python (`src/python/{format}/`) is the sole FOSS track for all formats
- Target .NET framework: net10.0 LTS
- This decision applies to both FODS and FODT (and all future formats)

## Rationale

1. Python FOSS already satisfies the FOSS obligation for the project.
2. Maintaining two parallel .NET tracks (FOSS + commercial) adds complexity
   without corresponding value.
3. Option B enables the simplest Gate 11 path: single .NET commercial product.
4. Developers needing a free parser use `src/python/{format}/` (Apache-2.0).

## What This Unblocks

- FODS Gate 11: `src/net/fods/` may now be created (commercial skeleton)
- FODT Gate 11: `src/net/fodt/` may now be created (commercial skeleton)
- Gate 11 execution path: .NET commercial skeleton → full implementation → human approval

## What This Does NOT Authorize

- Gate 11 approval (requires full .NET implementation + DEC-034 IV + human review)
- .NET FOSS source (prohibited by Option B)
- Any .NET source for formats without Gate 10 approval

## Files Updated

- plans/master-plan.md: DEC-033 entry updated to Resolved, Option B
- registry/format-registry.yaml: dec033_status=resolved, dec033_option=B for fods+fodt
- acquisition-packs/fods/dec033-resolution-record.md (created)
- acquisition-packs/fodt/dec033-resolution-record.md (created)
- taskcards/DEC-033-resolution-execution-plan.md: status → completed

DEC033_RESOLVED: YES
DEC033_OPTION: B
