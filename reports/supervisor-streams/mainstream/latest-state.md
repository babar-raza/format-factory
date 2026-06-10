# Mainstream Stream — Latest State
**Updated:** 2026-06-04 (memory sync)

## Current Status
- **State:** DEFERRED
- **Reason:** Waiting for Supervisor + Skills + Acceleration to each have independent hardening proof

## What Mainstream Needs Before Starting
1. Skills Hardening IV completed: `SKILLS_GOVERNED_EXECUTION_HARDENED_INDEPENDENTLY_VERIFIED` or `_WITH_LIMITATIONS`
2. Supervisor Hardening IV completed: `SUPERVISOR_TRAFFIC_CONTROLLER_HARDENED_INDEPENDENTLY_VERIFIED` or `_WITH_LIMITATIONS`
3. Acceleration Hardening IV completed

## Eventual Mainstream Sprint
When hardening proofs are available, Mainstream targets at minimum:

### Commercial .NET (priority)
1. FODS CSV dogfood/export (Gap: GAP-FODS-DOGFOOD-CSV-DOTNET-001, Skill: add-dotnet-api)
2. FODT Markdown/TXT dogfood/export
3. Netpbm proof

### FOSS
- ZST, Python Netpbm, SYLK/DIF as capacity allows

## Format Rules
- **Netpbm must be retained.** SVG must NOT replace Netpbm.
- DIF may supplement SYLK if proof validates faster.
- Gnumeric only if required capabilities validate.

## Mainstream Must NOT
- Commit, push, publish, approve gates
- Spend sprint on evidence cleanup
- Directly mutate poc-targets.yaml (propose CapabilityDelta only)
- Use Skills capability-matrix update as direct authority (treat as proposed delta)

## Mainstream Must Produce
- Source changes in src/net/ and/or src/python/
- Tests
- Dogfood outputs
- Transcripts
- CapabilityDelta proposals
- Evidence declaration/review package

## PASS Quota
Minimum 3 new capabilities with tests across 2+ product tracks per sprint.

## Templates Available
- `docs/prompt-templates/mainstream-product-execution-template.md`
- `docs/prompt-templates/mainstream-poc-mega-train-template.md`
