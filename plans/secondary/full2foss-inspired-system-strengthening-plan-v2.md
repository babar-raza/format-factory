# Full2Foss-Inspired System Strengthening — Secondary Roadmap Plan v2
# Sprint: S-F2F-00 (plan repair)
# Date: 2026-05-08
# Status: PROPOSED — pending human approval for all implementation phases
# Repairs: D-01 through D-15 from full2foss-inspired-plan-repair-review.md

---

## 1. Title and Status

Full2Foss-Inspired Reusable System Strengthening — Secondary Roadmap Plan v2

Status: PROPOSED_PENDING_HUMAN_APPROVAL for all implementation phases (S-F2F-01 through S-F2F-08).
Plan-repair (S-F2F-00) is authorized by the execution prompt and is the only completed sprint.

---

## 2. Relationship to MAIN SPRINT

This secondary roadmap is FULLY SUBORDINATE to the MAIN SPRINT. The MAIN SPRINT is the
only active delivery path for format acquisition gate execution. As of this sprint (2026-05-08,
run044): FODS Gates 1-6 are PASSED, Gate 7 is planning_ready; FODT Gates 1-3 are PASSED,
Gate 4 is planning_ready. No action in this secondary roadmap may change any of those states,
redirect MAIN SPRINT execution, pause MAIN SPRINT work, or cause gate approval delays.

A secondary sprint may run only when it does not conflict with MAIN SPRINT timing. If any
conflict arises, MAIN SPRINT takes priority unconditionally.

---

## 3. Decision Summary

| Category | Decision |
|----------|----------|
| This plan-repair sprint (S-F2F-00) | AUTHORIZED by execution prompt |
| S-F2F-01: Playbook schema + policy | CLOSED_VERIFIED — executed 2026-05-08; S-F2F-01B verification 2026-05-08 |
| S-F2F-02: Playbook validation tool | CLOSED_VERIFIED — executed 2026-05-08; schema gap repaired (S-F2F-02B); 42/42 tests PASS; verified 2026-05-08 |
| S-F2F-03: Dry-run replay + review queue | CLOSED_VERIFIED — executed 2026-05-09; 3 tools; 96 tests PASS |
| S-F2F-04: Golden dry-run tests | CLOSED_VERIFIED — executed 2026-05-09; 140 PASS, 1 skip; 7 golden fixtures; FODT format-agnostic; commits: 5908d91 + b71e1ee + 4d7e536 |
| S-F2F-05: ODF-flat family playbook | PROPOSED — requires S-F2F-01 complete + approval |
| S-F2F-06: Apply-mode risk review | PROPOSED — requires S-F2F-04 complete + approval |
| S-F2F-07: Product dependency closure design | PROPOSED — requires Gate 8 PASSED + human auth |
| S-F2F-08: Product skeleton/stub design | PROPOSED — requires S-F2F-07 complete + approval |
| Apply mode implementation | NOT AUTHORIZED — S-F2F-06 is risk review only |
| Product source creation | NOT AUTHORIZED — Gate 10+ required |
| settings.json changes | NOT IN THIS SPRINT — each future sprint requests separately |

---

## 4. What Is Approved Now (S-F2F-00 Only)

The execution prompt for this sprint authorizes creating:
- plans/secondary/full2foss-inspired-plan-repair-review.md (defect catalogue)
- plans/secondary/full2foss-inspired-system-strengthening-plan-v2.md (this document)
- taskcards/S-F2F-00 through S-F2F-08 (9 proposed taskcards)
- plans/master-plan.md Section 34 (append only)
- AGENTS.md Section AA (append only, marked proposed-only)
- GOVERNANCE.md Section 20 (append only, marked proposed-only)
- docs/python-foss/acquisition-workflow.md one-paragraph note (append only)
- docs/governance/current-state-and-evidence-authority.md one-paragraph note (append only)
- tools/evidence/contracts/secondary-full2foss-plan-repair.yaml
- Staging metadata (39 files) and evidence bundle

---

## 5. What Is Proposed But Not Approved

All implementation phases S-F2F-01 through S-F2F-08 are proposed only.
None may be executed without a separate human authorization prompt naming the taskcard.

---

## 6. What Is Explicitly Forbidden

The following are hard prohibitions that apply to ALL secondary sprints forever:
- tools/playbook/ (until S-F2F-03 is explicitly authorized)
- schemas/playbook/ (until S-F2F-01 is explicitly authorized)
- schemas/product/ (until separately authorized after P1 docs approved)
- tools/product/ (until Gate 10+ product source authorized)
- acquisition-packs/fods/playbook.yaml (until explicitly named in authorization prompt)
- acquisition-packs/fodt/playbook.yaml (until explicitly named in authorization prompt)
- acquisition-packs/_families/ (until S-F2F-05 is explicitly authorized)
- tests/playbook/ — CREATED by S-F2F-04 (CLOSED_VERIFIED 2026-05-09); acquisition-packs/_families/ remains forbidden until S-F2F-05 is explicitly authorized
- plans/review-queues/ (until S-F2F-03 is explicitly authorized)
- docs/playbook-layer.md (until S-F2F-01 is explicitly authorized)
- docs/product-dependency-closure.md and related (until S-F2F-07 is explicitly authorized)
- Any product source, parsers, neutral models, samples (until gate-appropriate authorization)
- LLM endpoint calls (existing policy)
- New spec downloads (existing spec-cache authorization policy)
- Embeddings, vector DB files (existing policy)
- Push to remote (existing policy)

---

## 7. Full2Foss Ideas Being Borrowed

All borrowing is conceptual only — no Full2Foss code, no Full2Foss product goal.

| Full2Foss Pattern | format-factory Mapping |
|------------------|------------------------|
| Playbook as durable transformation memory | acquisition-packs/{format}/playbook.yaml — records gate operations, expected outputs, evidence requirements, conflict policy for each format |
| Deterministic replay before LLM fallback | Replay engine tries deterministic execution first; LLM fallback is future optional and never authority for spec/legal claims |
| Review queue for unresolved conflicts | Structured review-queue items when deterministic replay cannot resolve a conflict; severity=high blocks apply mode |
| Source format → derived format with overrides | ODF-flat family playbook with per-format override table; FODT inherits FODS patterns where safe, with explicit reuse_level classification |
| Golden replay tests | tests/playbook/ golden cases for dry-run validation; regression protection before apply mode |
| API dependency closure | Python AST + Roslyn-inspired design for product tracks (deferred to Phase P1-P2, Gate 8+ prerequisite) |
| Stub/skeleton generation | Design plan for FOSS-minimal API skeletons with explicit unsupported-feature errors (deferred to Phase P2, Gate 10+ prerequisite) |

---

## 8. Full2Foss Ideas NOT Being Borrowed

| Full2Foss Pattern | Why NOT Borrowing |
|------------------|-------------------|
| Product goal (commercial→FOSS conversion) | format-factory acquires format knowledge, not converts codebases |
| LLM-inferred reasons as evidence authority | format-factory governance requires DEC-034 independent verification; LLM output is never authoritative for spec/legal claims |
| Token-in-query-string metrics | format-factory uses safe auth (.env only, never in query strings) |
| One-off format-specific design | All playbook/replay tooling must accept format_id parameter and be reusable |
| Weakened governance | format-factory's gate discipline (DEC-034 + human approval) is stronger than Full2Foss — not weakened |
| Automatic gate approval via replay | DEC-034 + human approval always required; no replay score can approve a gate |

---

## 9. Current Format-Factory State (run044, 2026-05-08)

| Format | Gate States |
|--------|-------------|
| FODS | Gates 1-6: PASSED; Gate 7: planning_ready (TC-0033) |
| FODT | Gates 1-3: PASSED; Gate 4: planning_ready (TC-0034/TC-0035) |
| Product source | NONE — Phase 4+ only |
| Secondary planning | This sprint creates plans/secondary/ for first time |

MAIN SPRINT next actions:
- FODS Gate 7 execution (TC-0033 malformed/fuzz testing)
- FODT Gate 4 execution (TC-0034/TC-0035 parser prototype)

---

## 10. Gap Analysis

### Gap 1: Acquisition Playbook Layer
Current: No playbook.yaml per format. Gate steps live in ad-hoc acquisition pack docs and
taskcards (spec-evidence.md, legal-notes.md, gate*-human-review-packet.md).
Missing: Structured machine-readable gate operation definitions with expected outputs,
validation commands, conflict policy, and reuse classification.
Impact: FODT was acquired using ~40-50% FODS effort via informal human knowledge reuse. Future
formats (FODP, FODG) would repeat the same discovery without systematic guidance.
Borrowing: Playbook as durable transformation memory.

### Gap 2: Gate Replay Engine
Current: Gate execution is fully manual. No deterministic replay capability.
Missing: tools/playbook/replay_acquisition_playbook.py with validate/dry-run modes. No
review queue output, no structured replay report.
Borrowing: Deterministic first; no silent mutation.

### Gap 3: Review Queue
Current: Unresolved issues go into gap logs (G-NNN), taskcards, or blocker reports. No
structured queue with operation_id, severity, required action.
Missing: Structured review items linking replay failure to specific operation and gate.
Borrowing: Conflict review queue.

### Gap 4: Format-Family Reuse Playbooks
Current: docs/python-foss/odf-flat-family-reuse-strategy.md documents reuse informally. No machine-
readable family playbook or override model.
Missing: acquisition-packs/_families/odf-flat/ with machine-readable reuse classification.
Borrowing: Source format → derived format with per-format overrides.

### Gap 5: Golden Replay Tests
Current: tests/evidence/ has negative bundle validation tests. No golden-output comparisons.
Missing: tests/playbook/ with golden dry-run tests, no-mutation assertion.
Borrowing: Golden replay tests.

### Gap 6: Python Product Dependency Closure
Current: Product source not started. src/python/ does not exist.
Future: Python AST/import/API surface closure for src/python/{format}/ (Phase P1+, Gate 8+).
Borrowing: Dependency closure from public API surface.

### Gap 7: .NET Product Dependency Closure
Current: Product source not started. src/net/ does not exist.
Future: Roslyn-style API surface closure for src/net/{format}/ (Phase P1+, Gate 8+).
Borrowing: Roslyn API surface tracing.

### Gap 8: Stub/Skeleton Generator
Current: No product skeletons. Correct — product gates not reached.
Future: Explicit unsupported-feature errors, FOSS-minimal skeletons (Phase P2+, Gate 10+).
Borrowing: NotImplementedException-style stubs.

### Gap 9: Playbook-Level Metrics
Current: Evidence bundles record metadata counts. No playbook-level operation counts.
Future: Metrics hooks in replay tools (operation counts, conflict counts, deterministic/fallback).
Borrowing: Run telemetry. NOT borrowing token-in-query-string pattern.

### Gap 10: Evidence Contracts for Playbook Sprints
Current: Contracts cover gate execution, verification, gate approval. No playbook contracts.
Future: Contract templates for playbook-driven sprints.
Borrowing: Evidence integration for replay results.

---

## 11. Corrected Target Architecture

### Layer 1: Acquisition Playbook Schema (Phase S1)
Files (created in S-F2F-01):
- schemas/playbook/acquisition-playbook.schema.json — JSON schema (draft-7)
- schemas/playbook/review-queue.schema.json — review item schema
- docs/playbook-layer.md — policy and design

Key schema fields:
```yaml
playbook_id: fods-acquisition-v1
format_id: fods               # required; format_id parameter in all tools
format_family: odf-flat
source_format_if_derived: null
gate_scope: [gate1, gate2, gate3, gate4, gate5, gate6]
operations:
  - operation_id: gate1-scoring
    operation_type: score_and_register
    target_path: registry/format-registry.yaml
    input_dependencies: [registry/scoring/_scoring-model.md]
    expected_outputs: [registry/format-registry.yaml]
    validation_commands: [python tools/evidence/check_current_state_consistency.py]
    evidence_requirements: [gate-approval.yaml]
    conflict_policy: queue_for_review
    reuse_level: full          # full | adapt | guide | new
    reusable_across_formats: true
    format_specific_overrides: {}
    provenance: run015
    status: completed
```

### Layer 2: Playbook Validation Tool (Phase S2)
Files (created in S-F2F-02):
- tools/playbook/validate_playbook.py — read-only; validates YAML against schema
- tests/playbook/test_playbook_schema.py — schema structure unit tests
Mode: validate only. No file writes.

### Layer 3: Dry-Run Replay + Review Queue (Phase S3)
Files (created in S-F2F-03):
- tools/playbook/replay_acquisition_playbook.py — dry-run and review queue modes only
- tools/playbook/diff_playbook_outputs.py — compare expected vs actual
- tools/playbook/export_review_queue.py — export structured review queue

Required modes: validate, dry-run, explain, export-review-queue.
NOT included: apply mode (deferred to after S-F2F-06 risk review + explicit authorization).

Review queue item schema:
```yaml
item_id: RQ-001
format_id: fods               # required; format-agnostic via parameter
gate: gate6
operation_id: gate6-oracle-comparison
target_path: acquisition-packs/fods/gate6-oracle-comparison-report.md
issue_type: deterministic_failure
severity: high                # high | medium | low
deterministic_failure_reason: LibreOffice not found
required_action: install_oracle_tool
suggested_fix: See acquisition-packs/fods/oracle-installation-checklist.md
evidence_required: preflight_oracle.py PASS
status: open                  # open | pending_human | resolved | escalated
```

### Layer 4: Golden Dry-Run Tests (Phase S4)
Files (created in S-F2F-04):
- tests/playbook/test_replay_dry_run.py — dry-run assertions
- tests/playbook/golden/ — checked-in golden fixture files
- tools/playbook/create_golden_case.py — capture current state as golden

Golden test scenarios:
1. FODS dry-run → expected replay report matches golden
2. FODT Gate 2 dry-run → expected outputs match
3. Expected review queue for known missing oracle tool input
4. No file mutations in dry-run mode assertion

### Layer 5: ODF-Flat Family Playbook (Phase S5 — parallel to S2-S4)
Files (created in S-F2F-05, after S-F2F-01 schema is approved):
- acquisition-packs/_families/odf-flat/playbook.yaml
- acquisition-packs/_families/odf-flat/reuse-policy.md
- acquisition-packs/_families/odf-flat/format-overrides.yaml

Reuse level classifications:
- full: identical operation; no format-specific adaptation needed
- adapt: same operation type; format-specific parameters required
- guide: pattern is reusable; content must be regenerated
- new: no meaningful reuse from base format

Rules (non-negotiable):
1. Family playbook PROPOSES reuse — cannot APPROVE gate passes
2. Each format's gate still requires independent DEC-034 + human approval
3. No inherited gate pass under any circumstances
4. Per-format overrides take precedence over family-level defaults

### Layer 6: Apply-Mode Risk Review (Phase S6 — after S4)
Files (created in S-F2F-06):
- plans/secondary/apply-mode-risk-review.md — risk assessment document only

Apply mode IMPLEMENTATION is NOT authorized by this plan. The risk review doc assesses:
- What files apply mode would mutate
- Checksum anchor strategy
- Review queue integration requirements
- Rollback plan
- Testing requirements
After human reads the risk review, a SEPARATE explicit authorization prompt names apply mode.

### Layer 7: Future Product Dependency Closure (Phase P1 — Gate 8 PASSED required)
Files (created in S-F2F-07, documentation only):
- docs/product-dependency-closure.md
- docs/python-product-closure-strategy.md
- docs/dotnet-product-closure-strategy.md

Schema files (schemas/product/) require a SEPARATE explicit authorization after P1 docs
are reviewed. No tools, no stubs.

### Layer 8: Future Product Skeleton/Stub Design (Phase P2 — Gate 10 required)
Files (created in S-F2F-08, documentation only):
- docs/product-skeleton-generator.md

No tools, no placeholder files, no stubs. Design document only.

---

## 12. Minimal Viable Secondary Implementation Path

The smallest safe first step is S-F2F-01: schema files + policy doc.
- Zero execution capability (no tools)
- Schema validates YAML structure; does not run anything
- Policy doc explains what playbooks are and are not
- Can be reviewed and rejected without any system impact
- Rollback: delete schemas/playbook/ and docs/playbook-layer.md

Start here. Do not proceed to S-F2F-02 until S-F2F-01 is reviewed and approved.

---

## 13. Deferred Product-Track Path

Product dependency closure and skeleton generation are explicitly deferred:
- Phase P1 (design docs only): Requires FODS Gate 8 PASSED + explicit human authorization
- Phase P2 (one design doc): Requires P1 complete + Gate 10 progress + explicit authorization
- Phase P3 (implementation): NOT AUTHORIZED by this plan; requires Gate 10+ product source auth

The deference is firm. No schema files, no tool stubs, no placeholder implementations before
the stated prerequisites are satisfied.

---

## 14. Corrected Rollout Phases

### S0 — Plan Repair (THIS SPRINT — COMPLETED)
Sprint: S-F2F-00
Outputs: plans/secondary/, taskcards/S-F2F-*.md, master-plan Section 34, governance notes,
evidence contract, evidence bundle
Gate changes: NONE

### S1 — Playbook Schema and Policy (CLOSED_VERIFIED — S-F2F-01B, 2026-05-08)
Sprint: S-F2F-01
Authorization required: explicit prompt naming "S-F2F-01 Playbook Schema and Policy"
Outputs: schemas/playbook/{schema}.json (2 files), docs/playbook-layer.md
NOT included: actual playbook.yaml files in acquisition-packs/, replay tools

### S2 — Playbook Validation Tool (CLOSED_VERIFIED — S-F2F-02B, 2026-05-08)
Sprint: S-F2F-02
Authorization required: explicit prompt naming "S-F2F-02 Playbook Validation Tool"
Outputs: tools/playbook/validate_playbook.py, tests/playbook/test_playbook_schema.py
Mode: read-only schema validation; no file writes

### S3 — Dry-Run Replay and Review Queue (CLOSED_VERIFIED — 2026-05-09)
Sprint: S-F2F-03
Authorization required: explicit prompt naming "S-F2F-03 Dry-Run Replay and Review Queue"
Outputs: tools/playbook/replay_acquisition_playbook.py (dry-run + review-queue modes only),
tools/playbook/diff_playbook_outputs.py, tools/playbook/export_review_queue.py
NOT included: apply mode

### S4 — Golden Dry-Run Tests (CLOSED_VERIFIED — 2026-05-09)
Sprint: S-F2F-04
Status: CLOSED_VERIFIED — executed 2026-05-09; 140 PASS, 1 skip, 0 fail; 7 golden fixtures
Commits: 5908d91 + b71e1ee + 4d7e536
Created: tests/playbook/test_replay_golden.py, tests/playbook/test_diff_golden.py,
tests/playbook/test_review_queue_golden.py, tests/playbook/golden/ (7 fixtures),
tests/playbook/fixtures/replay-fodt-valid.yaml, tools/playbook/create_golden_case.py

### S5 — ODF-Flat Family Playbook (FUTURE — requires S-F2F-01 + approval; parallel to S2-S4 OK)
Sprint: S-F2F-05
Authorization required: explicit prompt naming "S-F2F-05 ODF-Flat Family Playbook"
Outputs: acquisition-packs/_families/odf-flat/ (3 files)
Note: Can run after S1; does not require S2/S3/S4

### S6 — Apply-Mode Risk Review (FUTURE — requires S-F2F-04 + approval)
Sprint: S-F2F-06
Authorization required: explicit prompt naming "S-F2F-06 Apply-Mode Risk Review"
Outputs: plans/secondary/apply-mode-risk-review.md ONLY
Apply mode implementation: NOT authorized; requires additional separate human authorization

### P1 — Product Dependency Closure Design (FUTURE — Gate 8 PASSED required)
Sprint: S-F2F-07
Authorization required: FODS Gate 8 PASSED + explicit prompt naming "S-F2F-07"
Outputs: docs/product-dependency-closure.md, docs/python-product-closure-strategy.md,
docs/dotnet-product-closure-strategy.md (design docs only; no schemas, no tools)

### P2 — Product Skeleton/Stub Design (FUTURE — Gate 10 progress required)
Sprint: S-F2F-08
Authorization required: Gate 10 progress + explicit prompt naming "S-F2F-08"
Outputs: docs/product-skeleton-generator.md only

### P3 — Implementation (NOT AUTHORIZED by this plan)
Deferred until product-track gates explicitly authorize source work.

---

## 15. Taskcard Map

| Card | Phase | Topic | Status | Can parallel MAIN SPRINT? |
|------|-------|-------|--------|--------------------------|
| S-F2F-00 | S0 | Plan repair | completed_by_plan_repair | N/A |
| S-F2F-01 | S1 | Playbook schema + policy | CLOSED_VERIFIED (S-F2F-01B, 2026-05-08) | YES — no gate conflict |
| S-F2F-02 | S2 | Validation tool | CLOSED_VERIFIED — schema gap repaired (S-F2F-02B); 42/42 tests PASS | YES — tool dev only |
| S-F2F-03 | S3 | Dry-run + review queue | CLOSED_VERIFIED (2026-05-09) | YES — no apply mode |
| S-F2F-04 | S4 | Golden dry-run tests | CLOSED_VERIFIED (2026-05-09) | YES — tests only |
| S-F2F-05 | S5 | ODF-flat family playbook | proposed | YES — docs only |
| S-F2F-06 | S6 | Apply-mode risk review | proposed | YES — docs only |
| S-F2F-07 | P1 | Product closure design | proposed | Only after Gate 8 PASSED |
| S-F2F-08 | P2 | Skeleton/stub design | proposed | Only after Gate 10 progress |

Dependency diagram:
```
S0 (complete)
├── S1 (schema + policy)
│   ├── S2 (validation tool)
│   │   └── S3 (dry-run + review queue)
│   │       └── S4 (golden tests)
│   │           └── S6 (apply-mode risk review)
│   └── S5 (family playbook — parallel to S2-S4)
Gate 8 PASSED
└── P1 (product closure design)
    Gate 10 progress
    └── P2 (skeleton design)
```

---

## 16. Evidence and Governance Requirements

- All sprints must build evidence bundles with BUNDLE_VALIDATION: PASS
- All sprints must satisfy the base-run.yaml v1.2 contract plus a sprint-specific contract
- All implementation sprints must have a dedicated contract file
- Governance notes in AGENTS.md Section AA and GOVERNANCE.md Section 20 are PROPOSED ONLY
  until S-F2F-01 is implemented and running — they do not govern behavior until the system exists
- Playbooks are execution aids: they are never evidence authority
- Replay reports are evidence-eligible inputs: they require human review before gate use
- Family playbooks cannot auto-approve gates: independent DEC-034 + human required per gate

---

## 17. Validation Requirements

All implementation sprints must validate:
1. Playbook YAML validates against acquisition-playbook.schema.json
2. Review queue YAML validates against review-queue.schema.json
3. Dry-run produces no file mutations in repo/
4. apply mode (when implemented) logs all writes before executing
5. Golden tests pass before apply mode is trusted
6. Evidence bundle BUNDLE_VALIDATION: PASS
7. Current-state consistency check passes

---

## 18. Reproducibility Requirements

All playbook artifacts must be reproducible:
- Same input playbook + same format state → same dry-run output
- Deterministic operation IDs (no random generation)
- All format_id parameters explicit (no hardcoded format assumptions)
- Golden test fixtures checked into repo/tests/playbook/golden/ (not local-only)
- Evidence contracts capture all required files

---

## 19. All-Format Applicability Requirements

Every tool and schema created under this roadmap must:
1. Accept format_id as a required parameter (never hardcode "fods")
2. Work identically for fods, fodt, and any future format
3. Validate format_id against registry/format-registry.yaml before executing
4. Store format-specific outputs under format-namespaced paths
5. Report errors using format_id in the message

This is the primary lesson from Full2Foss: do not build a one-off system.

---

## 20. Risk Register

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|-----------|
| Secondary sprint conflicts with MAIN SPRINT | HIGH | LOW | WIP limit: max 1 secondary sprint per MAIN SPRINT sprint; MAIN SPRINT always wins |
| Playbook declared authority for gate state | HIGH | MEDIUM | AGENTS.md AA + GOVERNANCE.md 20 explicitly prohibit this |
| Apply mode mutates files before review queue works | HIGH | LOW | Apply mode not authorized until S-F2F-04 complete + S-F2F-06 risk review |
| Family playbook interpreted as inherited approval | HIGH | MEDIUM | reuse-policy.md explicitly prohibits inherited approval |
| Product schemas created before product gates | MEDIUM | LOW | S-F2F-07 requires Gate 8 PASSED + explicit auth |
| Numbering confusion (old D-13 defect) | MEDIUM | LOW | Corrected: S-F2F-00=repair, S-F2F-01=schema |
| Governance notes activate before system exists | MEDIUM | LOW | Sections marked "Proposed — Requires S-F2F-01 Human Approval" |
| settings.json unauthorized changes | MEDIUM | LOW | settings.json NOT in this sprint; future sprints request separately |
| LLM fallback declared spec/legal authority | HIGH | LOW | Explicit prohibition in governance notes |
| Sprint scope creep into MAIN SPRINT work | HIGH | MEDIUM | Self-challenge question 7; plan clearly forbids MAIN SPRINT modification |

---

## 21. Reversibility

All phases are fully reversible:

| Phase | How to Reverse |
|-------|----------------|
| S0 (this sprint) | Revert the single commit (`git revert <hash>`) |
| S1 | Delete schemas/playbook/ and docs/playbook-layer.md |
| S2 | Delete tools/playbook/validate_playbook.py and tests/playbook/test_playbook_schema.py |
| S3 | Delete tools/playbook/ (all files) |
| S4 | Delete tests/playbook/ (all files) |
| S5 | Delete acquisition-packs/_families/ |
| S6 | Delete plans/secondary/apply-mode-risk-review.md |
| P1 | Delete 3 docs/product-*.md files |
| P2 | Delete docs/product-skeleton-generator.md |

No phase creates database records, deployed services, or irreversible infrastructure.
All phases are append-only to repo structure.

---

## 22. Acceptance Criteria

| Phase | Done When |
|-------|-----------|
| S0 | plans/secondary/ exists; 9 taskcards created; master-plan Section 34 appended; BUNDLE_VALIDATION: PASS; commit hash recorded |
| S1 | 2 schema files validate (jsonschema draft-7); docs/playbook-layer.md present; 0 tool files created; BUNDLE_VALIDATION: PASS |
| S2 | validate_playbook.py runs without error on FODS example YAML; test_playbook_schema.py: all tests PASS; 0 new file writes from tool |
| S3 | dry-run against FODS playbook produces expected report; review queue exports correctly; 0 file mutations in repo/; BUNDLE_VALIDATION: PASS |
| S4 | 4+ golden test scenarios PASS; test_replay_dry_run.py: all tests PASS; golden files checked in |
| S5 | family playbook validates against schema; reuse-policy.md explicitly prohibits inherited approval; override table complete |
| S6 | apply-mode-risk-review.md present; risk register complete; NO apply mode implementation |
| P1 | 3 design docs present; no schema files created; no tool files created |
| P2 | 1 design doc present; no tool stubs, no placeholder implementations |

---

## 23. Required Approval Gates

| Implementation Sprint | Approval Required |
|----------------------|-------------------|
| S-F2F-01 | Human approval prompt explicitly naming "S-F2F-01 Playbook Schema and Policy" |
| S-F2F-02 | Human approval prompt explicitly naming "S-F2F-02 Playbook Validation Tool" |
| S-F2F-03 | Human approval prompt explicitly naming "S-F2F-03 Dry-Run Replay and Review Queue" |
| S-F2F-04 | Human approval prompt explicitly naming "S-F2F-04 Golden Dry-Run Tests" |
| S-F2F-05 | Human approval prompt explicitly naming "S-F2F-05 ODF-Flat Family Playbook" |
| S-F2F-06 | Human approval prompt explicitly naming "S-F2F-06 Apply-Mode Risk Review" |
| S-F2F-07 | FODS Gate 8 PASSED + human approval prompt explicitly naming "S-F2F-07" |
| S-F2F-08 | Gate 10 progress confirmed + human approval prompt explicitly naming "S-F2F-08" |

An agent MUST NOT execute any sprint without the exact naming condition being met in the
execution prompt. "Let's continue with the playbook work" is not sufficient. The sprint name
must appear explicitly.

---

## 24. Next Recommended Secondary Sprint

After this plan-repair sprint (S-F2F-00) is reviewed and approved by the human:

**Next:** S-F2F-01 — Playbook Schema and Policy

Scope:
- schemas/playbook/acquisition-playbook.schema.json (JSON schema draft-7)
- schemas/playbook/review-queue.schema.json (JSON schema draft-7)
- docs/playbook-layer.md (policy doc, ~4 sections)
- Example YAML snippet (in docs/, NOT in acquisition-packs/)

Risk: LOW — no executable tools; docs + schemas only; fully reversible
Parallelism: Can run between any MAIN SPRINT sprints without conflict
DEC-034: Not required for schema/docs sprint; required for any sprint that produces
gate evidence or requests human gate review

---

## 25. Final Verdict

This plan (v2) corrects all 15 defects from the original planning session
(iridescent-coalescing-stearns.md). It cleanly separates:

1. What is authorized NOW (S-F2F-00 plan repair — this sprint)
2. What is PROPOSED for future implementation (S-F2F-01 through S-F2F-08)
3. What is DEFERRED to product-track gates (P1-P3)
4. What is EXPLICITLY FORBIDDEN (hard prohibition list)

The plan is subordinate to MAIN SPRINT. No gate states are changed. No implementation
is authorized. The roadmap is format-agnostic (format_id parameter required throughout).
All phases are reversible. Acceptance criteria are explicit per phase.

SECONDARY SPRINT ONLY.
MAIN SPRINT NOT REPLACED.
NO GATE STATUS CHANGED.
NO IMPLEMENTATION AUTHORIZED.
