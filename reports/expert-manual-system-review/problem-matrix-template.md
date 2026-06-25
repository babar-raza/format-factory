# Problem Matrix Template
# Format Factory — Expert Manual System Review
# Phase 7 output — Generated: 2026-06-25

## Purpose

Every confirmed problem in Format Factory receives one entry in this template.
The template ensures each problem is fully characterized with:
- Direct evidence (not inference)
- System root cause (not just product symptom)
- System-first healing path
- Product fix after system healing
- Recurrence prevention

---

## Problem Entry Template

```
PROBLEM ID: PROB-NNN
Category: DOTNET_COMMERCIAL | PYTHON_FOSS | SYSTEM_GAP | EVIDENCE | SKILLS | PROCESS
Severity: CRITICAL | HIGH | MEDIUM | LOW
Confidence: VERIFIED | LIKELY | NEEDS_CONFIRMATION
Status: OPEN | CLOSED_FIXED | CLOSED_WONT_FIX | CLOSED_DUPLICATE

## Summary
One-sentence description of the problem.

## Direct Evidence
Exact source location, code snippet, or file that proves the problem exists.

## Why It Matters
Impact to developer using this library. Commercial / FOSS impact.

## System Root Cause
Which system component is the root cause?
- Gap ledger: gap not tracked → not worked
- SAL: no spec facts → spec parity unverifiable
- Governance: no validator → defect recurs
- Skill: no skill → ad-hoc fixes without governing
- Evidence: quality deferred → claims unverified

## System Healing First
What system component must be healed BEFORE the product fix?

## Product Fix (after system healing)
Specific code change needed in src/. Path, class, method, behavior change.

## Test Strategy
How to verify the fix is correct and complete.

## Verification Strategy
How to confirm the gap is closed (via governance, gap ledger, spec fact).

## Recurrence Prevention
Validator or test to prevent regression.

## Fix Complexity: LOW | MEDIUM | HIGH
## Owner Lane: dotnet_commercial | python_foss | system | skills | governance
## Suggested Sprint: sprint ID or description
## Dependencies: [list of PROB-IDs that must be resolved first]
```

---

## Problem Categories

| Category | Meaning |
|---------|---------|
| DOTNET_COMMERCIAL | Defect in src/net/ product code |
| PYTHON_FOSS | Defect in src/python/ package |
| SYSTEM_GAP | Defect in autonomous machinery (gap ledger, SAL, evidence, skills) |
| EVIDENCE | Discrepancy between claimed state and actual state |
| SKILLS | Missing or broken skill in .supervisor/skill-registry.yaml |
| PROCESS | Governance or process failure |

## Severity Definitions

| Severity | Meaning |
|---------|---------|
| CRITICAL | Blocks commercial publication; renders product non-functional |
| HIGH | Significant user-facing limitation; blocks commercial-grade claim |
| MEDIUM | Noticeable limitation; does not block publication but affects quality |
| LOW | Minor issue; cosmetic or edge case |

## Confidence Definitions

| Confidence | Meaning |
|-----------|---------|
| VERIFIED | Direct source evidence found and read |
| LIKELY | Inferred from indirect evidence (test count, known design) |
| NEEDS_CONFIRMATION | Suspected but not directly verified |
