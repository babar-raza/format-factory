# DEC-033 and Gate 11: Next Main-Lane Decision Material
**Date:** 2026-05-12
**Sprint:** POST-FODT-GATE10-CONTROLLED-SWARM-001 (Lane D)
**Status:** PLANNING_READY — awaiting human decision on DEC-033

---

## 1. Current Blocker State

DEC-033 (.NET FOSS packaging decision) is unresolved. Both FODS and FODT Gate 11 are blocked. No .NET source may be created until DEC-033 is resolved. This report documents exactly what the next main-lane sprint must do to unblock Gate 11.

## 2. What Has Been Completed (Gates 1-10)

| Format | Phase 4 Python | Gate 10 | Gate 11 |
|--------|---------------|---------|---------|
| FODS | COMPLETED (run051) | PASSED (2026-05-08) | not_started — DEC-033 blocked |
| FODT | COMPLETED (run052/TC-0052) | PASSED (2026-05-11) | not_started — DEC-033 blocked |

Python FOSS source is complete and independent. The only remaining acquisition work is Gate 11 (commercial .NET readiness) and DEC-033 resolution.

## 3. DEC-033 Decision Matrix

| Option | Description | Gate 11 Path | Risk |
|--------|-------------|--------------|------|
| A | .NET FOSS + Commercial | Produce both net8.0 FOSS (Tiers 0-2) and full commercial .NET | Doubles .NET work; needs OSS/commercial solution split |
| B | .NET Commercial Only | No .NET FOSS; Python is the sole FOSS track | Simplest; Python OSS already satisfies FOSS obligation |
| C | Defer .NET Entirely | Skip Gate 11 for now; return when commercial opportunity arises | No .NET product; can revisit later |
| D | .NET FOSS Only | No commercial .NET; produce FOSS .NET only | Unlikely: loses commercial opportunity |

**Recommended by Lane D:** Option B (.NET Commercial Only). Rationale:
- Python FOSS (src/python/fods/ and src/python/fodt/) already covers the FOSS obligation.
- Maintaining two .NET tracks (FOSS + commercial) adds significant complexity.
- Option B unblocks Gate 11 with the smallest scope increase.
- Option C should be selected only if .NET commercial plans are not confirmed for the near term.

## 4. What the Next Main-Lane Sprint Must Do

### Step 1: Human Records DEC-033 Decision
The human must explicitly state which option (A, B, C, or D) is chosen. No agent can resolve DEC-033 unilaterally.

### Step 2: Record Decision in Registry
Update `registry/format-registry.yaml`:
- `dec033_status: resolved`
- `dec033_option: <chosen_option>`
- `dec033_resolved_date: <date>`
- `dec033_resolved_by: <human_name>`

### Step 3: Update GOVERNANCE.md
Add DEC-033 resolution to Decision Register (Section I of the master plan). Update DEC-033 entry in GOVERNANCE.md Decision Register (Section 8).

### Step 4: Gate 11 Execution (Option B example)
If Option B chosen:
- Create .NET project skeleton: `src/net/fods/` and `src/net/fodt/`
- Implement Tier 0 parser baseline for each format
- Gate 11 commercial readiness review packet
- CI configuration for .NET commercial build
- `acquisition-packs/fods/gate11-human-review-packet.md`
- `acquisition-packs/fodt/gate11-human-review-packet.md`

If Option C chosen:
- Record deferral decision; close Gate 11 with deferral status
- No .NET source created

### Step 5: Evidence Bundle and Human Approval
Gate 11 requires human approval per standard governance rules. No agent self-approval.

## 5. .NET SDK Version Note

.NET SDK 9.0.200 is installed but approaching EOL. Gate 11 execution should target net10.0 LTS. The `.NET target framework` must be confirmed before .NET source creation begins.

## 6. Pre-Conditions for Next Main-Lane Sprint Authorization

The next main-lane sprint (DEC-033 Resolution + Gate 11 Execution) requires:
1. Human explicitly chooses DEC-033 Option (A, B, C, or D).
2. Human confirms target .NET framework version (net8.0 or net10.0).
3. Human authorizes TC-DEC033-EXEC (see `taskcards/DEC-033-resolution-execution-plan.md`).
4. Human authorizes TC-GATE11-EXEC-FODT (see `taskcards/FODT-GATE11-readiness-execution-plan.md`).

## 7. Files Produced by Lane D

| File | Purpose |
|------|---------|
| reports/planning/fodt/dec033-and-gate11-next-main-lane-20260512.md | This report — full decision material |
| reports/planning/fodt/dec033-and-gate11-next-main-lane-20260512.yaml | Machine-readable summary |
| taskcards/DEC-033-resolution-execution-plan.md | Execution-ready taskcard for DEC-033 decision |
| taskcards/FODT-GATE11-readiness-execution-plan.md | Execution-ready taskcard for FODT Gate 11 |

## 8. Stop Conditions (This Report Only)

This report does NOT:
- Resolve DEC-033 (human decision required)
- Start Gate 11 execution
- Create any .NET source
- Approve any gate
