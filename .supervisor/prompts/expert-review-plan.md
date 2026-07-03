---
espanso_provenance:
  source_trigger: ":ff-expert-review-plan"
  source_block: 108
  source_line_range: [122469, 123646]
  gap_id: GAP-ESP-007
  extraction_date: "2026-07-03"
  capability_id: expert-review-plan
prompt_id: ESP-PROMPT-3
title: "Expert Manual System Review Plan"
version: "1.0"
status: ACTIVE
mutating: false
context_profile: full
mode: PLAN_MODE_ONLY
---

# Expert Manual System Review — Plan Generation Protocol

**MODE: PLAN MODE ONLY — READ-ONLY — DO NOT MODIFY SOURCE CODE**

This protocol produces a structured expert review plan for manual execution in a later sprint.
It does NOT execute any fixes. It does NOT modify `src/`, `tests/`, registries, or plans.

## Short-Context View

Produce a step-by-step expert review plan covering Format Factory's `src/` product code,
autonomous machinery, skill/command governance, evidence system, and specification authority.
For each gap found: identify whether the SYSTEM must be healed before the product can be healed.
Output to `reports/expert-manual-system-review/` only.

---

## Full Protocol

### When to Use
- Beginning a major quality improvement cycle
- Before a Gate 11 readiness assessment
- When autonomous sprint claims seem optimistic and require external verification
- When product quality has not been independently reviewed

### When NOT to Use
- During an active execution sprint (defer until a review sprint)
- When a recent expert review exists that is still valid
- When you are inside a per-chat plan that requires execution work

### Hard Prohibitions (enforced)
You MUST NOT during this protocol:
- Edit any file under `src/`
- Edit any file under `tests/`
- Edit `product-capability-matrix/poc-targets.yaml`
- Edit `registry/format-registry.yaml`
- Edit `.supervisor/policies.yaml`
- Commit or push
- Claim commercial readiness
- Run destructive git operations
- Approve Gate 8 or Gate 11

### Allowed Writes
- `reports/expert-manual-system-review/review-plan-<sprint_id>.md`
- `reports/expert-manual-system-review/gap-matrix-<sprint_id>.yaml`

### Review Dimensions

**Dimension 1: Product Source Quality**
- Inspect `src/python/` and `src/net/` for each format
- Assess: API completeness, module structure, naming, typing, testability, monolith risk
- Compare against production-library-standard-v2.md criteria
- Document: gaps between current state and commercial-quality benchmark

**Dimension 2: Autonomous Machinery**
- Inspect supervisor tools, continuation signal, plan locks, evidence system
- Assess: does the machinery actually iterate? does it detect its own failures?
- Document: disconnections between claimed and actual behavior

**Dimension 3: Skill/Command Governance**
- Inspect skill-registry.yaml, capability-routing-registry.yaml, command-registry.yaml
- Assess: orphaned skills, uncovered routes, commands without skills
- Document: gap coverage and dead entries

**Dimension 4: Evidence and Proof Quality**
- Sample recent evidence declarations and review packages
- Assess: proof level (synthetic vs real), evidence breadth, verification depth
- Document: weak proofs that would not satisfy an external auditor

**Dimension 5: Specification Authority**
- Inspect SAL facts, oracle cases, qname coverage
- Assess: format coverage, case completeness, oracle pass rate
- Document: formats with no SAL facts, no oracle cases, or low qname coverage

### Output Structure

```
reports/expert-manual-system-review/
  review-plan-<sprint_id>.md       — The structured review plan with phases and tasks
  gap-matrix-<sprint_id>.yaml      — Machine-readable gap register
```

Each gap must classify:
- `gap_type`: SYSTEM_GAP | PRODUCT_GAP | GOVERNANCE_GAP | EVIDENCE_GAP
- `heal_system_first`: true | false
- `priority`: CRITICAL | HIGH | MEDIUM | LOW
- `proposed_fix_approach`: string

### System-First Principle
When a product defect is caused by a system defect, the gap_type is SYSTEM_GAP
and heal_system_first is true. The review plan must order system heals before product heals.

### Completion Gate
- All 5 review dimensions inspected
- Gap matrix written to `reports/expert-manual-system-review/`
- Review plan written with phased execution sequence
- Zero source file modifications made
- Plan is actionable: each phase has concrete taskcards estimable by another agent
