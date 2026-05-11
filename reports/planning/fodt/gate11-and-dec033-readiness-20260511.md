# FODT Gate 11 and DEC-033 Readiness Plan
**Date:** 2026-05-11
**Sprint:** FODT-GATE10-APPROVAL-AND-SWARM-NEXT-LANES-001 (Lane B)

---

## 1. What Gate 11 Requires

Gate 11 is **Commercial Readiness Assessment**. Per docs/gates.md:
- .NET product source implemented (or decision to defer)
- Commercial licensing terms confirmed
- Packaging plan for commercial distribution
- CI/CD for commercial build (or plan)
- DEC-033 resolved (FOSS .NET packaging decision)

## 2. What DEC-033 Blocks

DEC-033 governs whether format-factory produces a .NET FOSS package alongside the commercial .NET product. Until resolved:
- No `src/net/fodt/` or `src/net/fods/` may be created
- Gate 11 cannot be approved for either FODS or FODT
- .NET CI/CD cannot be configured
- Commercial licensing cannot be finalized

**Both FODS and FODT Gate 11 are blocked by DEC-033.**

## 3. Options for DEC-033 Resolution

| Option | Description | Impact |
|--------|-------------|--------|
| A. .NET FOSS + Commercial | Produce both .NET FOSS (Tiers 0-2) and .NET commercial (Tiers 0-6) | Doubles .NET packaging work but maximizes community |
| B. .NET Commercial Only | No .NET FOSS; Python is the FOSS track, .NET is commercial | Simpler; Python OSS already covers FOSS obligation |
| C. Defer .NET Entirely | Focus on Python FOSS for both FODS and FODT; .NET deferred indefinitely | Fastest path; loses .NET market |
| D. .NET FOSS Only, No Commercial | Abandon commercial .NET; produce only FOSS .NET | Unlikely to match project goals |

**Recommended:** Option B or A, decided by project lead. Option B is simplest and aligns with current Python-first strategy.

## 4. Can .NET Source Start Before DEC-033?

**No.** The source layout (`src/net/{format}/`) and packaging model depend on whether FOSS and commercial coexist. Starting .NET source without DEC-033 resolution risks rework.

## 5. Required Evidence for Gate 11

- DEC-033 resolution decision document
- .NET source (if applicable) or deferral decision
- Commercial licensing terms (if applicable)
- Packaging plan for .NET distribution
- Gate 11 human review packet

## 6. Proposed Next Main-Lane Sprint

**DEC-033 Resolution Sprint:** A planning-only sprint where the human decides Option A, B, C, or D. The sprint records the decision, updates DEC-033 status, and creates the Gate 11 execution plan.

## 7. Risks

- DEC-033 may require legal review (licensing implications)
- .NET SDK version (9.0.200) is near EOL; may need upgrade to .NET 10
- If Option A chosen, .NET FOSS and commercial separation requires careful CI/CD

## 8. Stop Conditions

- Do not start Gate 11 execution until DEC-033 is resolved
- Do not create src/net/ until DEC-033 is resolved
- Do not finalize commercial licensing until DEC-033 is resolved
