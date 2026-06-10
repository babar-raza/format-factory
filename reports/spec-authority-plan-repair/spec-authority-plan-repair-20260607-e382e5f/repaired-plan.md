# Repaired Healing Plan
# FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-HARDENING-TASKCARD-STATE-MACHINE-AND-HEALING-SYSTEM-001
# Repaired by: FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-REPAIR-FOR-SINGLE-GO-EXECUTION-001
# Run: spec-authority-plan-repair-20260607-e382e5f
# HEAD: e382e5f (branch: main)
# Date: 2026-06-07

---

## Plan Identity

Sprint ID: FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-HARDENING-TASKCARD-STATE-MACHINE-AND-HEALING-SYSTEM-001
State machine: 32 states (corrected from 29 — REPAIR-001)
Taskcard count: 25 (TCA-000 through TCA-024)
Lanes: 9 (L-COORD, L-EVIDENCE, L-STATEMACHINE, L-GOVERNANCE, L-SCHEMA, L-SELECTOR, L-VERIFY, L-ADVERSARIAL, L-BUNDLE)

---

## Repairs Applied (REPAIR-001 through REPAIR-010)

All repairs have been applied in this sprint. See required-plan-repairs.md for full details.

REPAIR-001: State count corrected to 32 everywhere (markdown, JSON).
REPAIR-002: All paths use ${REPO_ROOT}/... (no hardcoded platform-specific absolute paths).
REPAIR-002A: Normalization output path corrected to ${REPO_ROOT}/.local/spec-cache/fods/1.3/normalized/text.txt
REPAIR-003: Use validated_by: independent_agent_verifier for all agent-verifiable facts. External authority decisions require explicit human_approval_required_reason.
REPAIR-004: TCA-000 starts as IMPLEMENTING; closes to CLOSED_VERIFIED only when validate_repaired_plan.py exits 0.
REPAIR-005: 9-lane swarm model with exclusive write ownership; lane-ownership-map.json; overlap checker passes.
REPAIR-006: rollback-recovery-plan.md + .json covering 12 failure modes.
REPAIR-007: spec_fact_refs enforcement is BLOCKING (mandatory, hard gate) for all new PRODUCT_SOURCE, TEST, REQUIREMENT, READINESS, RELEASE_GATE work items.
REPAIR-008: Bypass pilot for Gnumeric and ABW added (TCA-012); non_goals confirms no product code.
REPAIR-009: FODS PDF check: TCA-011 transitions to BLOCKED_MISSING_SPEC if absent; SHA-256 read from spec-index.yaml at runtime.
REPAIR-010: No CI/hooks present; all verification gates marked ci_available=false.

---

## Confirmed Investigation Findings (as of HEAD e382e5f)

The following gaps are confirmed against live repo state at HEAD e382e5f:

- GAP-001 PARTIALLY_UPDATED: .local/spec-normalize/ path is wrong; actual output is at ${REPO_ROOT}/.local/spec-cache/fods/1.3/normalized/text.txt (2.2MB, real normalized text)
- GAP-002 CONFIRMED: FODS-SPEC-001-requirements.json contains synthetic text ("Document root SHALL be office:document element.")
- GAP-003 CONFIRMED: .local/spec-source-registry/sources.jsonl is missing
- GAP-004 CONFIRMED: No spec_fact_refs field in any schema
- GAP-005 CONFIRMED: No FACT-xxx annotations in src/
- GAP-006 CONFIRMED: verified-facts.yaml has 10 facts set to verified by automated tool (no validated_by field)
- GAP-007 CONFIRMED: No SPEC-FACT: citations in tests/
- GAP-008 CONFIRMED: authority_integration_fabric.py not imported by autonomous_cycle.py
- GAP-009 CONFIRMED: Product ledger missing spec_fact_ids
- GAP-010 CANNOT_VERIFY_FROM_LISTINGS: tools/ai/ structure extensive but wiring to authority not confirmed

---

## spec_fact_refs Enforcement (REPAIR-007)

spec_fact_refs is BLOCKING for new product work. This is a standing constraint.

BLOCKING applies to work item types: PRODUCT_SOURCE, TEST, REQUIREMENT, READINESS, RELEASE_GATE

Exception classifications (must be explicitly set; no silent bypass):
- investigation_only: pure investigation/audit work
- sample_only_non_product: sample files with no production code
- legacy_backfill: pre-existing code being documented retroactively
- fallback_authority_approved: explicitly approved fallback by governance
- no_public_spec_available: no publicly accessible spec document exists

Citation: GAP-004, investigation-001/root-cause-gap-matrix.md, REPAIR-007 in required-plan-repairs.md

---

## Human Approval Rules (REPAIR-003)

The `human_approval_required: true` flag is ONLY used for:
1. git push or commit — requires explicit user authorization
2. Gate 11 (G11-G) commercial readiness — requires Babar Raza specifically
3. Package publication (NuGet, PyPI) — requires explicit user authorization
4. MCP activation changes — requires explicit user authorization

All other verification uses `validated_by: independent_agent_verifier`.
Never write a `Babar Raza` attribution unless Babar actually reviewed the item.

---

## State Machine (32 states)

See authority-healing-state-machine.md and authority-healing-state-machine.json.

Terminal states: CLOSED_VERIFIED, CLOSED_WITH_AUTHORITY_DEBT, REJECTED_FALSE_CLAIM
Blocked states: BLOCKED_BY_MISSING_EVIDENCE, BLOCKED_BY_MISSING_SPEC, BLOCKED_BY_EXTERNAL_AUTHORITY, BLOCKED_BY_PREREQUISITE_TASKCARD, VALIDATION_FAILED, PILOT_FAILED

---

## Taskcard Summary (TCA-000 through TCA-024)

See authority-healing-taskcards.md and authority-healing-taskcards.json.

In this plan-repair sprint, the following taskcards are produced and ready:
- TCA-000 (IMPLEMENTING — this sprint): plan repair execution
- TCA-001 (CLOSED_VERIFIED): evidence import review
- TCA-005 (CLOSED_VERIFIED): 32-state machine
- TCA-006 (CLOSED_VERIFIED): 25 taskcards
- TCA-007 (CLOSED_VERIFIED): plan readiness review
- TCA-008 (CLOSED_VERIFIED): required plan repairs
- TCA-011 (CLOSED_VERIFIED): FODS normalization check
- TCA-018 (CLOSED_VERIFIED): lane ownership map

The following taskcards are DISCOVERED and will be executed in the next sprint (stop-the-bleeding):
- TCA-002, TCA-003, TCA-004, TCA-009, TCA-010, TCA-012, TCA-013, TCA-014, TCA-015, TCA-016, TCA-017

---

## FODS Normalization Status (Path Corrected — REPAIR-002A)

The investigation sprint expected normalization output at ${REPO_ROOT}/.local/spec-normalize/fods/1.3/.
Actual output location: ${REPO_ROOT}/.local/spec-cache/fods/1.3/normalized/

The FODS PDF exists and has been normalized. All healing steps (TCA-011) use the corrected path.

FODS PDF: ${REPO_ROOT}/.local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf
SHA-256: sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066 (from spec-index.yaml)
Normalized text: ${REPO_ROOT}/.local/spec-cache/fods/1.3/normalized/text.txt (2224560 bytes)

---

## Bypass Pilot (Gnumeric and ABW) — REPAIR-008

TCA-012 covers the bypass pilot for formats without spec PDFs.

Exception classification: no_public_spec_available
Formats: gnumeric, abw
Scope: metadata-only — populate exception_classification fields in existing evidence declarations

Non-goals of TCA-012 (explicitly):
- new_product_implementation
- new_test_files
- src_changes
- modifying gnumeric_codec.py or abw_codec.py

---

## Constraints (standing, always apply)

- NO commits, NO pushes, NO gate approvals
- NO product source file changes (no src/ changes in this sprint)
- NO embeddings or vector DB activation
- NO network access
- NO overwriting prior investigation reports (reports/spec-authority/ is read-only)
- NO hardcoded user-specific paths (always use ${REPO_ROOT})
- NO default human approval for agent-verifiable facts — use independent_agent_verifier
- NO named-person attribution in validated_by unless that person actually reviewed
- NO spec_fact_refs configured as non-blocking for new product work (must be BLOCKING)
- NO pre-marking TCA-000 as CLOSED_VERIFIED before validator passes
- All paths computed dynamically from git rev-parse --show-toplevel

---

## Stop Gates

STOP and report PLAN_REPAIR_BLOCKED if:
- Investigation evidence bundle not found
- Prior plan file not readable
- All JSON artifacts fail to parse (environment issue)

PLAN_NEEDS_REPAIR if:
- Any validator check fails
- Adversarial review finds CRITICAL issue
- State count != 32
- Hardcoded Windows paths found in repaired-plan.md

---

## Verification

```bash
# Run from run_dir:
python validate_repaired_plan.py --run-dir .
```

Expected: all checks pass, exit 0.
