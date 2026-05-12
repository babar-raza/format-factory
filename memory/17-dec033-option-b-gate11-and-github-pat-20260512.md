---
memory_id: 17
topic: DEC-033 Option B Resolution, Gate 11 Commercial Readiness, GitHub PAT Handling
created: "2026-05-12"
sprint: DEC033-OPTION-B-GATE11-COMMERCIAL-SWARM-001
---

# Memory 17: DEC-033 Option B, Gate 11, GitHub PAT

## DEC-033 Resolution

**Status:** RESOLVED as Option B — .NET Commercial Only

**Decision:** Babar Raza authorized on 2026-05-12.

**Option B definition:**
- `src/net/{format}/` is **commercial-only** .NET; no .NET FOSS package produced
- Python (`src/python/{format}/`) is the **sole FOSS track** (Apache-2.0)
- One .NET package per format: `FormatFactory.{Format}` (commercial)

**Evidence files:**
- `reports/decision/dec033-option-b-resolution-20260512.md` (narrative)
- `reports/decision/dec033-option-b-resolution-20260512.yaml` (machine-readable)
- `acquisition-packs/fods/dec033-resolution-record.md`
- `acquisition-packs/fodt/dec033-resolution-record.md`
- `taskcards/DEC-033-resolution-execution-plan.md` (status: completed)

**Registry:** Both FODS and FODT `gate_11` sections contain `dec033_status: resolved`, `dec033_option: B`, `dotnet_target: net10.0`.

## Gate 11 Commercial Skeleton Status

### FODS .NET Skeleton
- `src/net/fods/FormatFactory.Fods.csproj` — net10.0 target, v0.1.0-skeleton
- `src/net/fods/FodsParser.cs` — `GetSheetNames()` XML well-formedness only
- `src/net/fods/README.md` — commercial-only scope, DEC-033 Option B, SDK blocker

### FODT .NET Skeleton
- `src/net/fodt/FormatFactory.Fodt.csproj` — net10.0 target
- `src/net/fodt/FodtParser.cs` — `GetParagraphCount()` XML well-formedness only
- `src/net/fodt/README.md` — algorithm reference to list_traversal.py

### SDK Blocker
- Current: .NET 9.0.200 — CANNOT target net10.0 (NETSDK1045)
- Required: .NET 10 SDK from https://aka.ms/dotnet/download
- Gate 11 stays `commercial_readiness_in_progress` until SDK installed + full Tier 0 impl

### Gate 11 Taskcards
- `taskcards/FODS-GATE11-commercial-readiness.md` — status: in_progress, blocked_by: dotnet_10_sdk_required
- `taskcards/FODT-GATE11-readiness-execution-plan.md` — commercial_skeleton_created: true

### Gate 11 Review Packets
- `acquisition-packs/fods/gate11-human-review-packet.md` (8-item checklist, 3 done)
- `acquisition-packs/fodt/gate11-human-review-packet.md` (8-item checklist)
- `acquisition-packs/fods/gate11-commercial-licensing.md`
- `acquisition-packs/fods/gate11-packaging-plan.md`
- `acquisition-packs/fodt/gate11-commercial-licensing.md`
- `acquisition-packs/fodt/gate11-packaging-plan.md`

## GitHub PAT Readiness

**Probe sprint:** Lane D of DEC033-OPTION-B-GATE11-COMMERCIAL-SWARM-001

| Check | Result |
|-------|--------|
| Machine scope | MISSING (User scope, not System) |
| User scope | PRESENT |
| Bash propagation | NOT automatic — requires explicit export |
| gh auth status | PASS — babar-raza, GH_TOKEN, fine-grained PAT |
| Repo | format-factory PUBLIC, owned babar-raza |
| Push permission | INFERRED LIKELY |
| Remote mutation | NONE executed |

**Key rule:** GITHUB_PAT must NEVER be printed or written to disk. Map in-memory
to GH_TOKEN only, within the PowerShell process scope.

**Bash propagation pattern (when needed):**
```
export GITHUB_PAT=$(powershell.exe -NoProfile -Command '[Environment]::GetEnvironmentVariable("GITHUB_PAT","User")')
```

**Evidence files:**
- `reports/github/github-pat-readiness-probe-20260512.md`
- `reports/github/github-pat-readiness-probe-20260512.yaml`
- `taskcards/GITHUB-PAT-readiness-probe.md`

## ACCEL-003 Hardening

**Change:** After Pass 2 validates the final bundle, the proof file is now updated with
**both** candidate AND final bundle metrics.

**Proof file sections after hardening:**
1. `=== CANDIDATE (Pass 1) ===` — name, SHA-256, entries, bytes, metadata
2. `=== FINAL BUNDLE (Pass 2) ===` — name, SHA-256, entries, bytes, metadata
3. `Validator: validate_evidence_bundle.py --check-no-pending`
4. `Final validation: PASS`
5. Timestamp

**Tests:** 7/7 PASS in `tests/evidence/test_auto_proof_bundle.py` (Test 7 is the hardening test).

**Note:** The proof file INSIDE the final zip still has candidate-only data (written before Pass 2).
The on-disk proof file (in metadata_dir) is updated with full details after Pass 2.
