<!--plan_identity:
  schema_version: "1.1"
  plan_id: "generic-soaring-chipmunk-hardening-addendum"
  parent_plan_id: "generic-soaring-chipmunk"
  mission_id: "SAL-VERIFICATION-HARDENING-001"
  parent_plan_path: "C:/Users/prora/.claude/plans/generic-soaring-chipmunk.md"
  plan_type: "hardening_addendum"
  created_at: "2026-06-25"
  audit_source: ".local/evidences/sal-vhip-001-verification-hardening/stage1-issue-model.json"
  status: "OPEN — carry-forward taskcards for next SAL sprint"
-->

# SAL-VHIP-001 Plan Hardening Addendum
# Parent plan: generic-soaring-chipmunk.md (TERMINAL_CLOSED — executed 2026-06-25)
# Audit source: stage1-issue-model.json + stage1-sprint-audit-summary.md
# Addendum purpose: Governs carry-forward work, unresolved issues, and next-sprint handoff

---

## Plan File Hardening Change Log

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-06-25 | PSL-PROMPT-2 (plan-hardening) | Initial hardening addendum from stage1 audit |
| 1.1 | 2026-06-26 | execution_agent | TC-WIRE-001/006 completed_verified; BACKFILL-001 completed_verified; NON-ODF-001 blocked_local |

---

## Audit Findings Incorporated

Source: `.local/evidences/sal-vhip-001-verification-hardening/stage1-issue-model.json`

| Issue ID | Level | Severity | Status in Addendum |
|----------|-------|----------|--------------------|
| L1-001 | L1_EXECUTION | HIGH | **RESOLVED** — committed as c54d2685 |
| L1-002 | L1_EXECUTION | MEDIUM | **RESOLVED** — governance_validators_sal.py in commit |
| L2-001 | L2_INTEGRATION | HIGH | **CLOSED** → TC-SAL-CARRY-WIRE-001 completed_verified |
| L2-002 | L2_INTEGRATION | MEDIUM | **CLOSED** → TC-SAL-CARRY-WIRE-006 completed_verified |
| L2-003 | L2_INTEGRATION | MEDIUM | **RESOLVED** — baseline updated in c54d2685 |
| L3-001 | L3_SYSTEM | MEDIUM | **CLOSED** → TC-SAL-CARRY-BACKFILL-001 completed_verified |
| L3-002 | L3_SYSTEM | MEDIUM | **BLOCKED_LOCAL** → TC-SAL-CARRY-NON-ODF-001 (no spec text for non-ODF beyond ZST) |

---

## Resolved / Preserved Work

All work from the parent sprint (generic-soaring-chipmunk.md) is CLOSED. Summary:

| Item | Result | Commit |
|------|--------|--------|
| qname=None eliminated (14,794 facts) | ACCEPTED_VERIFIED | c54d2685 |
| ZST upgrade: 15→120 verified | ACCEPTED_VERIFIED | c54d2685 |
| Gap-ledger spec_facts 84%→98% | ACCEPTED_VERIFIED | prior sprint (e1e0ece3) |
| V-NEW-001 inflation validator | ACCEPTED_VERIFIED | c54d2685 |
| spec_fact_ref canonical format check | ACCEPTED_VERIFIED | c54d2685 |
| All pilots F1/F2/F3/F4 PASS | ACCEPTED_VERIFIED | c54d2685 |
| master-plan.md Section 75 | ACCEPTED_VERIFIED | c54d2685 |
| governance_validators_sal.py in baseline | ACCEPTED_VERIFIED | c54d2685 |

---

## Unresolved Work Register

### TC-SAL-CARRY-WIRE-001 — Wire requirement_extractor into sal_master_runner.py
**Status:** not_attempted
**Priority:** HIGH
**Origin:** TC-SAL-WIRE-001 (deferred from generic-soaring-chipmunk.md with documented rationale)

**Why it matters:**
Without this wiring, the SAL pipeline cannot auto-discover new requirements from spec text. Every new requirement addition requires manual workbench creation. The REQ-to-FACT extraction chain is broken at the runner level.

**Risk addressed:**
The SAL pipeline is manual-only for non-ODF formats. As new formats are added, manual workbench creation does not scale. Automation is required for SAL coverage to grow beyond ODF+ZST.

**What deferred it:**
Regression risk in `sal_master_runner.py` — the runner is 1,140 LOC and wiring a new extractor call requires careful review. A failed wiring could corrupt the production fact output for all 29 formats.

### TC-SAL-CARRY-WIRE-006 — REQ-to-FACT context pack bridge
**Status:** not_attempted
**Priority:** MEDIUM
**Origin:** TC-SAL-WIRE-006 (deferred from generic-soaring-chipmunk.md with documented rationale)

**Why it matters:**
Context packs currently use REQ-* IDs (requirement IDs). SAL uses FACT-* IDs. These two namespaces are not translated. The autonomous sprint selector cannot match context pack requirements to spec facts, making context packs effectively disconnected from SAL authority.

**What deferred it:**
Requires changes to `extractor_to_workbench_adapter.py` — complex refactor with cross-tool dependencies.

### TC-SAL-CARRY-BACKFILL-001 — Per-capability relevance in spec_facts backfill
**Status:** partially_done
**Priority:** LOW
**Origin:** L3-001 system weakness from stage1 audit

**Why it matters:**
The current backfill assigns the same top-N format-level facts to ALL gaps for a format. An FODS load gap and an FODS inspect gap get identical spec_facts. Spec authority is nominal rather than meaningful.

### TC-SAL-CARRY-NON-ODF-001 — Non-ODF formats spec coverage beyond bootstrap
**Status:** not_attempted
**Priority:** MEDIUM
**Origin:** L3-002 system weakness from stage1 audit

**Why it matters:**
18+ formats still have 2-109 bootstrap-only facts. V-NEW-001 warns for PBM/PGM/PPM/QOI inflation (37-42x) but does not block. Without real spec extraction for non-ODF formats, SAL authority remains ODF-centric.

---

## Taskcard Register

### TC-SAL-CARRY-WIRE-001: Wire requirement_extractor into sal_master_runner.py

```yaml
taskcard_id: TC-SAL-CARRY-WIRE-001
title: Wire requirement_extractor into sal_master_runner.py
source_issue_ids: [L2-001, TC-SAL-WIRE-001]
source_issue_level: L2_INTEGRATION
source_audit_finding: >
  requirement_extractor.py (136 LOC) exists but is NOT called by sal_master_runner.py.
  The SAL pipeline cannot auto-discover new requirements from spec text.
why_it_matters: >
  Without wiring, SAL is manual-only for non-ODF formats. New format spec facts require
  manual workbench creation — this does not scale.
risk_addressed: Manual-only SAL limits growth beyond ODF+ZST
status: completed_verified
completed_at: "2026-06-26"
completion_commit: 5e0f5cf6
priority: HIGH
lane_owner: SAL_INFRASTRUCTURE_LANE
supervisor_role: execution_agent

required_implementation:
  - Identify the correct insertion point in sal_master_runner.py for requirement_extractor call
  - Create a dry-run mode flag (--extract-requirements) so wiring can be tested without full run
  - Implement insertion with regression guard (compare fact counts before/after)
  - Add unit test: test_runner_calls_extractor.py

required_verification:
  - Run sal_master_runner.py --from-cache-only --all and verify fact counts unchanged
  - Run sal_master_runner.py --extract-requirements and verify new REQ-* entries created
  - Run tests/specification-authority-layer/ suite — 0 regressions

required_evidence:
  - Before/after fact counts (total facts must not decrease)
  - Test output showing extractor called
  - git diff showing insertion point

acceptance_criteria:
  - sal_master_runner.py calls requirement_extractor.py for at least one format
  - No regression in existing test suite
  - New facts total >= prior total

stop_conditions:
  - fact count drops by >1% — revert and re-plan
  - test suite failures increase — revert

allowed_actions:
  - Modify tools/specification-authority-layer/sal_master_runner.py
  - Create tests/specification-authority-layer/test_runner_calls_extractor.py

forbidden_actions:
  - Modify autonomous_cycle.py (already over LOC cap)
  - Add >100 LOC to sal_master_runner.py without LOC check first
  - Remove existing --from-cache-only behavior

dependencies:
  - requirement_extractor.py must remain unchanged
  - sal_master_runner.py LOC cap must be checked before modification

closeout_rules:
  - Evidence declaration with fact count before/after
  - Test run output showing 0 regressions
  - Pilot: run on FODS format and verify REQ-* entries generated

machine_state: OPEN
```

---

### TC-SAL-CARRY-WIRE-006: REQ-to-FACT context pack bridge

```yaml
taskcard_id: TC-SAL-CARRY-WIRE-006
title: REQ-to-FACT mapping tool for context pack bridge
source_issue_ids: [L2-002, TC-SAL-WIRE-006]
source_issue_level: L2_INTEGRATION
source_audit_finding: >
  Context packs use REQ-* IDs; SAL uses FACT-* IDs. No translation bridge exists.
  Autonomous sprint selector cannot match context requirements to spec facts.
why_it_matters: >
  Without bridge, context packs are disconnected from SAL authority. The REQ-to-FACT
  chain is broken at the context pack level, making spec-parity verification advisory-only.
risk_addressed: Context packs cite requirements that cannot be matched to verified spec facts
status: completed_verified
completed_at: "2026-06-26"
completion_commit: 5e0f5cf6
priority: MEDIUM
lane_owner: SAL_INFRASTRUCTURE_LANE
supervisor_role: execution_agent

required_implementation:
  - Analyze extractor_to_workbench_adapter.py to understand REQ-* → FACT-* mapping logic
  - Create tools/specification-authority-layer/req_to_fact_bridge.py
  - Bridge reads context pack REQ-* IDs, looks up matching FACT-* entries in sal-facts-latest.json
  - Output: context_pack_fact_coverage.json per format

required_verification:
  - Run bridge on FODS context pack (most complete format)
  - Verify output contains FACT-* citations from sal-facts-latest.json
  - At least 10 FODS REQ-* entries map to FACT-* entries

required_evidence:
  - context_pack_fact_coverage.json for FODS
  - Before/after comparison showing REQ-* → FACT-* links
  - Pilot: verify 1 downstream consumer reads the bridge output

acceptance_criteria:
  - Bridge runs without error on all 7 existing context packs
  - At least 1 format has ≥10 REQ-FACT links

stop_conditions:
  - Context pack loading fails — debug before proceeding
  - sal-facts-latest.json not at expected path — check path first

allowed_actions:
  - Create tools/specification-authority-layer/req_to_fact_bridge.py (new file)
  - Read context packs from reports/specification-authority-layer-mwp/

forbidden_actions:
  - Modify existing context pack files (read-only)
  - Modify sal-facts-latest.json structure

dependencies:
  - TC-SAL-CARRY-WIRE-001 is independent — can be run in parallel
  - sal-facts-latest.json must be at .local/sal-output/sal-facts-latest.json

closeout_rules:
  - Bridge output for ≥1 format
  - Evidence: context_pack_fact_coverage.json with ≥10 links

machine_state: OPEN
```

---

### TC-SAL-CARRY-BACKFILL-001: Per-capability spec_facts relevance improvement

```yaml
taskcard_id: TC-SAL-CARRY-BACKFILL-001
title: Improve backfill_gap_spec_fact_refs.py for per-capability relevance
source_issue_ids: [L3-001]
source_issue_level: L3_SYSTEM_WEAKNESS
source_audit_finding: >
  All gaps for a format receive identical top-N fact list regardless of gap capability type.
  FODS load gap and FODS inspect gap get the same facts.
why_it_matters: >
  Spec authority is nominal (coverage) rather than meaningful (relevance).
  The quality of spec_facts citations is low even when coverage is high.
risk_addressed: False sense of spec authority; capability-specific gaps not matched to capability-specific facts
status: partially_done
priority: LOW
lane_owner: SAL_INFRASTRUCTURE_LANE
supervisor_role: advisory

required_implementation:
  - Extend backfill_gap_spec_fact_refs.py with --semantic-match flag
  - When flag active: match gap capability_name keywords to fact text rather than top-N by format
  - Pilot: run on FODS gaps and compare coverage vs relevance

acceptance_criteria:
  - At least 10 FODS gaps have different spec_facts from each other (not all identical)

machine_state: CLOSED
completion_evidence: FODS unique spec_fact sets went from 2 → 45 (acceptance: ≥10)
```

---

### TC-SAL-CARRY-NON-ODF-001: Non-ODF spec extraction beyond bootstrap

```yaml
taskcard_id: TC-SAL-CARRY-NON-ODF-001
title: Non-ODF format spec extraction — ZST model replication to other RFC-backed formats
source_issue_ids: [L3-002]
source_issue_level: L3_SYSTEM_WEAKNESS
source_audit_finding: >
  18+ formats still have 2-109 bootstrap-only facts. V-NEW-001 warns (37-42x inflation)
  for PBM/PGM/PPM/QOI. No RFC/XSD adapter for non-ODF spec text ingestion exists.
why_it_matters: >
  SAL authority is limited to ODF+ZST. All other formats rely on bootstrap templates.
  V-NEW-001 warns but cannot block without real spec facts to compare against.
risk_addressed: Capability inflation for non-ODF formats is undetectable without real spec facts
status: blocked_local
blocked_reason: >
  Only .local/spec-cache/fods/1.3/normalized/text.txt and .local/spec-cache/zst/rfc8878/normalized/text.txt
  exist. No other non-ODF format has normalized spec text in the spec-cache. Cannot ingest
  spec text for PBM/PGM/PPM/QOI without external spec acquisition (TRUE_EXTERNAL_GATE for
  spec documents that require downloading/verifying external files).
blocked_at: "2026-06-26"
priority: MEDIUM
lane_owner: SAL_EXPANSION_LANE
supervisor_role: advisory

required_implementation:
  - Identify 3 formats with RFC or public spec text: candidates include ZST (done), PBM/PGM/PPM (Netpbm spec), TOML (toml.io)
  - For each: ingest spec text into .local/spec-cache/<format>/ using ZST extraction as template
  - Run sal_master_runner.py --from-cache-only on each format
  - Target: ≥15 verified facts per format (ZST model)

acceptance_criteria:
  - At least 1 additional non-ODF format has ≥15 verified facts (beyond ZST)
  - V-NEW-001 inflation ratio drops for at least 1 format

machine_state: OPEN
```

---

## Lane Ownership

| Lane | Owner | Status |
|------|-------|--------|
| SAL_INFRASTRUCTURE_LANE | execution_agent | CLOSED — TC-SAL-CARRY-WIRE-001 completed_verified, TC-SAL-CARRY-WIRE-006 completed_verified |
| SAL_EXPANSION_LANE | execution_agent (advisory) | BLOCKED_LOCAL — TC-SAL-CARRY-NON-ODF-001 (no spec text for non-ODF beyond ZST) |
| SAL_QUALITY_LANE | execution_agent (advisory) | CLOSED — TC-SAL-CARRY-BACKFILL-001 completed_verified |

---

## Gate Contract

| Gate | Condition | Current State |
|------|-----------|---------------|
| G-WIRE-001 | sal_master_runner.py calls requirement_extractor | **MET** — ZST extracts 58 reqs; artifact written |
| G-WIRE-006 | REQ-to-FACT bridge produces ≥10 links for 1 format | **MET** — FODS: 99/100 matched (99%); ZST: 96/96 (100%) |
| G-QUALITY | ≥10 FODS gaps have different spec_facts | **MET** — 45 unique sets (was 2) |
| G-NONODF | ≥1 non-ODF format has ≥15 verified facts beyond ZST | NOT MET — BLOCKED_LOCAL (no spec text available) |

Gates G-QUALITY and G-NONODF are advisory (not blocking for product advancement).
Gates G-WIRE-001 and G-WIRE-006 are BLOCKING for full SAL integration.

---

## Evidence Contract

For each taskcard, the following evidence is required at closure:

| Taskcard | Required Evidence |
|----------|-----------------|
| TC-SAL-CARRY-WIRE-001 | Before/after fact counts, test run output, git diff |
| TC-SAL-CARRY-WIRE-006 | context_pack_fact_coverage.json for ≥1 format |
| TC-SAL-CARRY-BACKFILL-001 | Before/after spec_facts comparison for ≥10 FODS gaps |
| TC-SAL-CARRY-NON-ODF-001 | sal-facts output for ≥1 new format with ≥15 verified |

Evidence must be in `.local/evidences/<run_id>/` (gitignored per project policy).
Evidence must NOT be synthetic (fabricated expected values are rejected).

---

## Verification Matrix

| Claim | Verification Command | Pass Condition |
|-------|---------------------|----------------|
| requirement_extractor called | `.venv/Scripts/pytest tests/specification-authority-layer/ -v` | 0 failures |
| REQ-FACT bridge produces output | `python tools/specification-authority-layer/req_to_fact_bridge.py --format fods` | Exit 0, output file created |
| No regression after WIRE-001 | `python tools/specification-authority-layer/sal_master_runner.py --from-cache-only --all --dry-run` | fact count >= prior count |
| Baseline still clean | `python tools/validators/source_structure_validator.py` | 0 new violations |

---

## Repair Loop

If any taskcard fails verification:

1. Do NOT mark as completed
2. Check the stop conditions in the taskcard
3. If stop condition triggered (e.g., fact count drops): revert via `git checkout -- <file>`
4. Document the failure in the evidence file
5. Re-plan with narrower scope

Permitted repair actions:
- Reduce scope (one format only instead of all)
- Add dry-run flag before live execution
- Consult spec-cache directly before modifying runner

---

## Anti-Overclaim Rules

1. **Do not claim TC-SAL-CARRY-WIRE-001 complete** unless the test suite confirms 0 regressions AND sal_master_runner.py actually calls requirement_extractor.py
2. **Do not claim coverage improvement** from TC-SAL-CARRY-BACKFILL-001 unless a before/after comparison shows at least 10 gaps have distinct facts
3. **Do not claim SAL authority** for non-ODF formats until real spec text has been ingested — bootstrap facts count as NO authority
4. **Do not claim REQ-FACT bridge complete** unless at least 10 links exist in the bridge output for a real format
5. **Do not use .local/ paths as proof** in declarations — .local/ is gitignored; cite the script and its output separately

---

## Closeout Criteria

This addendum is CLOSED when:

- TC-SAL-CARRY-WIRE-001: status = `completed_verified` ✓ (2026-06-26)
- TC-SAL-CARRY-WIRE-006: status = `completed_verified` ✓ (2026-06-26)
- TC-SAL-CARRY-BACKFILL-001: status = `completed_verified` ✓ (2026-06-26)
- TC-SAL-CARRY-NON-ODF-001: status = `blocked_local` — external spec acquisition required

**ADDENDUM STATUS: ACCEPTED_VERIFIED (with one BLOCKED_LOCAL item)**
Minimum acceptance: WIRE-001 + WIRE-006 completed_verified. ✓ MET.
BACKFILL-001 completed_verified. ✓ MET.
NON-ODF-001: BLOCKED_LOCAL — requires external spec documents not available in local cache.

---

## Remaining True Blockers

| Blocker | Type | Resolution Path |
|---------|------|----------------|
| autonomous_cycle.py over LOC cap (2628/2401) | GOV_BLOCK | Do NOT wire new calls into autonomous_cycle.py; use sal_master_runner.py only |
| RCAL system absent | EXTERNAL | .local/rcal/ does not exist; TC-SAL-WIRE-003 (RCAL wiring) remains impossible until RCAL is built |

**No TRUE_EXTERNAL_GATEs** for the taskcards in this addendum — all work is agent-executable.

---

## Pre-existing Failures (Do Not Regress)

These 3 test failures are pre-existing and must not worsen:
1. `test_registered_formats_have_bootstrap_level_1`
2. `test_fodt_neutral_model_cites_fact_refs`
3. `test_total_fact_refs_across_product_source`

If any new failure is introduced, it is a regression — revert immediately.

---

*End of hardening addendum — generic-soaring-chipmunk-hardening-addendum.md v1.0 — 2026-06-25*
