# Skill Inventory and Gaps

**Sprint/Run ID:** ff-archaeology-20260625

---

## Summary

37 command files exist in `.claude/commands/`. Skills are governed with transcript
requirements, QName-enforcement (V53), SAL awareness (V18), and analytics placement
enforcement (V41). Key gaps: no skill for auto-backfill, no skill for Gen3→Gen4 upgrade
(domain model creation), no skill for .NET spec_qname injection.

---

## Command File Inventory

### Product-Generating Skills

| Skill | File | Purpose | QName Enforced | SAL Enforced |
|-------|------|---------|---------------|-------------|
| add-python-api | add-python-api.md | Add Python API functions to codec/parser | YES (V53 post-check) | YES (V18) |
| add-dotnet-api | add-dotnet-api.md | Add .NET API methods | YES | YES |
| add-analytics-function | add-analytics-function.md | Add analytics functions | YES | YES (spec_fact_refs) |
| add-python-object-model-feature | add-python-object-model-feature.md | Add domain model feature | YES (V53) | YES |
| add-dotnet-object-model-feature | add-dotnet-object-model-feature.md | Add .NET object model feature | YES | YES |
| add-roundtrip-test | add-roundtrip-test.md | Add roundtrip test | YES | PARTIAL |
| add-same-format-writer-feature | add-same-format-writer-feature.md | Add writer capability | YES | YES |
| add-dogfood-export | add-dogfood-export.md | Create dogfood export example | YES | YES |
| add-installed-package-example | add-installed-package-example.md | Package install proof | YES | PARTIAL |
| implement-spec-stub | implement-spec-stub.md | Implement architecture_only stub | YES (V48 checks) | YES |
| decompose-monolithic-codec | decompose-monolithic-codec.md | Extract analytics from monolith | YES | YES |
| extract-analytics-from-monolith | extract-analytics-from-monolith.md | Analytics extraction | YES (V41) | YES |

### Audit and Review Skills

| Skill | File | Purpose |
|-------|------|---------|
| python-qname-code-reviewer | python-qname-code-reviewer.md | QName compliance review |
| spec-parity-verification | spec-parity-verification.md | Spec parity check |
| score-format | score-format.md | Format maturity score |
| check-gate | check-gate.md | Gate readiness check |
| check-release-boundary | check-release-boundary.md | Release boundary check |
| check-skill-coverage | check-skill-coverage.md | Skill coverage validation |
| validate-skill-contracts | validate-skill-contracts.md | Skill contract check |
| validate-skill-transcript | validate-skill-transcript.md | Transcript validation |
| validate-mutation-guard | validate-mutation-guard.md | Mutation guard check |
| validate-product-code-ledger | validate-product-code-ledger.md | Ledger validation |
| scan-residual-bypasses | scan-residual-bypasses.md | Residual bypass scan |
| detect-ad-hoc-execution | detect-ad-hoc-execution.md | Ad-hoc execution detection |
| detect-duplicate-skills | detect-duplicate-skills.md | Duplicate skill detection |

### Planning and Architecture Skills

| Skill | File | Purpose |
|-------|------|---------|
| spec-shaped-product-architecture-blueprint | spec-shaped-product-architecture-blueprint.md | Architecture blueprint |
| spec-literal-qname-to-code-mapping | spec-literal-qname-to-code-mapping.md | QName-to-code mapping |
| spec-parity-source-regeneration-and-migration | spec-parity-source-regeneration-and-migration.md | Source migration |
| python-reduced-spec-parity-model | python-reduced-spec-parity-model.md | Reduced parity model |
| qname-backfill | qname-backfill.md | QName backfill execution |

### Supervision and Management Skills

| Skill | File | Purpose |
|-------|------|---------|
| autonomous-loop | autonomous-loop.md | Main supervisor loop |
| post-sprint-audit | post-sprint-audit.md | Sprint audit |
| post-sprint-loop | post-sprint-loop.md | Sprint loop closeout |
| plan-hardening | plan-hardening.md | Plan hardening |
| build-evidence-bundle | build-evidence-bundle.md | Evidence bundle creation |
| build-context-pack | build-context-pack.md | Context pack |
| create-taskcard | create-taskcard.md | Taskcard creation |
| create-acquisition-pack | create-acquisition-pack.md | Acquisition pack |
| promote-gap-to-taskcard | promote-gap-to-taskcard.md | Gap-to-taskcard |
| select-poc-gap | select-poc-gap.md | POC gap selection |
| reproduce-master-plan | reproduce-master-plan.md | Master plan reproduction |
| record-lane-execution | record-lane-execution.md | Lane execution recording |
| rollback-and-recovery | rollback-and-recovery.md | Rollback procedures |

---

## Skill Governance Framework

### Global Controls

- `skill_invocation_transcript_required: true` (global_controls in command-registry.yaml)
- Every skill execution must produce a transcript entry
- Missing transcript = V44 validation warning

### Key Enforcement Validators

| Validator | What It Enforces |
|-----------|-----------------|
| V41 (validate_analytics_skill_required) | Analytics functions must go to analytics.py |
| V43 (enforce_skill_first_execution) | Skill must be invoked before manual coding |
| V44 (check_skill_coverage) | Checks that required skills have transcripts |
| V45 (validate_canonical_naming) | No format-prefixed names outside Compat/ |
| V48 (validate_architecture_only_stub_gate) | Blocks RELEASE_GATE citing architecture_only stubs |
| V53 (validate_spec_qname_refs) | spec_qname ClassVar on all authority classes |
| V18 (validate_spec_fact_refs_wired) | Work items must reference SAL fact IDs |

---

## QName Enforcement Per Skill

**add-python-api.md:** Includes clause requiring spec_qname on any new class introduced.
V53 runs post-submission and catches violations.

**add-analytics-function.md:** Requires `analytics.py` placement (RULE-AM-001).
Analytics functions outside analytics.py are flagged by V41.

**implement-spec-stub.md:** Specifically for implementing architecture_only stubs.
V48 enforces that RELEASE_GATE items don't cite stubs as evidence.

---

## Skill Gaps

### Gap 1: No Auto-Backfill Skill (HIGH)
**Missing:** A skill that scans all 20 codec/parser files, identifies classes missing
spec_qname ClassVar, and injects them from the registry.
**Impact:** Manual process required per format (TC-QHARD-POST-* pattern)
**Taskcard:** SKILL-HARD-001 (create add-domain-model-class skill)

### Gap 2: No Gen3→Gen4 Upgrade Skill (HIGH)
**Missing:** A skill specifically for creating `models.py` + domain model class for
Gen3 formats (ODS, ODT, PBM, PGM, PPM, QOI, SYLK).
**Current approach:** Ad-hoc per-format sprint tasks
**Impact:** 7 formats stuck at Gen3
**Taskcard:** SKILL-HARD-001

### Gap 3: No .NET spec_qname Injection Skill (MEDIUM)
**Missing:** Equivalent to add-python-api but enforces spec_qname in C# projects.
**Current approach:** Manual C# file edits
**Impact:** CSV .NET, NetPBM .NET lack spec_qname
**Taskcard:** SKILL-HARD-002

### Gap 4: No Unified Cross-Language Parity Skill (LOW)
**Missing:** A single skill that checks Python spec_qname matches .NET spec_qname for
shared formats.
**Current approach:** validate_cross_language_parity.py (manual run)
**Taskcard:** PARITY-002

---

## Analytics Suspension State

**SUSPENDED** (per `keen-dancing-hopper` plan, 2026-06-18):
- No new `{format}_mod_N_times_N` arithmetic analytics functions
- ZST/XCF/FODG analytics.py files are at LOC cap
- V42 (`validate_deepening_suspension`) blocks these patterns
- `add-analytics-function` skill is registered but suspended for ZST/XCF/FODG

Future analytics must:
1. Trace to a GAP-* entry in gap-ledger.json
2. Reference a spec fact (FACT-FORMAT-*)
3. Route to `{format}_analytics.py` (not main codec)

---

## Skill Registry Status

**File:** `.supervisor/skill-registry.yaml`
**Size:** 51.8 KB
**Content:** Full registry with spec_qname_required, product_track, skill_version,
dependencies, capability_refs, gap_ledger_refs per skill.

**Registration completeness:** All 37+ skills are registered. Skill-first enforcement
is active (V43/V44).

**Skill idempotency:** `run-skill-idempotency` skill exists for verifying idempotent
execution. Idempotency proof run stored in `.supervisor/skill-idempotency-proof.yaml`.
