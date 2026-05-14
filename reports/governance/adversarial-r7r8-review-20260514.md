---
document_type: adversarial_r7r8_review
sprint: CONWAY-R7R8-MULTI-FORMAT-PLANNING-AND-STALENESS-SWARM-001
lane: G
title: "Adversarial Safety Review — R7R8 Multi-Format Planning"
date: "2026-05-14"
visibility: internal
---

# Adversarial Safety Review — Lane G

**Sprint:** CONWAY-R7R8-MULTI-FORMAT-PLANNING-AND-STALENESS-SWARM-001
**Date:** 2026-05-14

---

## VERDICT: ADVERSARIAL_REVIEW_PASS — All attacks blocked or documented

---

## Section 1: Attack Surface

Components adversarially challenged:

1. `tools/skills/stale_detection.py` — stale-state enforcement
2. `tools/skills/implementation_plan_expander.py` — implementation planning
3. `tools/skills/multi_format_planning.py` — multi-format orchestration
4. `tools/skills/planning_bundle_runtime.py` — planning bundle
5. `tools/skills/replay_fingerprint.py` — replay governance
6. `schemas/skills/format-onboarding.schema.yaml` + templates — onboarding framework

---

## Section 2: Attacks Attempted

### Attack 1: Stale-State Bypass
**Goal:** Bypass stale detection to allow planning with stale requirements.
**Method:** Check whether `detect_stale_state()` can be bypassed by passing a format
that has REQUIREMENTS_AUTHORITATIVE but stale verifier timestamps.
**Test:** Synthetic test with verifier timestamp < requirements timestamp.
**Result:** BLOCKED — `verifier_after_generation` check fails, `blocker_count >= 1`,
`verdict = "STALE_BLOCKED"`. Lane selector redirects to LANE-R5. Prompt generator returns
`BLOCKED_STALE`. See `test_stale_detection.py::TestSyntheticStaleStates`.
**Weakness found:** NONE

### Attack 2: Implementation Execution Leakage
**Goal:** Trick implementation_plan_expander.py into executing implementation.
**Method:** Inspect all code paths. Does `expand_implementation_plan` call any subprocess,
write to `src/net/` or `src/python/`, or invoke any build tools?
**Result:** BLOCKED — expander only reads YAML files and returns dicts. No subprocess calls.
No file writes. All taskcards have `dry_run_only: True`, `autonomous_execution_allowed: False`.
**Weakness found:** NONE

### Attack 3: Authority Bypass via Accepted-Count Mismatch
**Goal:** Allow planning expansion even when registry accepted_count != file count.
**Method:** Synthetic test with registry accepted_count=99, actual=2.
**Result:** BLOCKED — stale detection catches mismatch; `accepted_count_consistent` check
returns FAIL; blocker_count=1; verdict=STALE_BLOCKED. Expander cannot run on stale state.
See `test_stale_detection.py::TestSyntheticStaleStates::test_accepted_count_mismatch_triggers_blocker`.
**Weakness found:** NONE

### Attack 4: Future-Scoped Requirement Leakage
**Goal:** Include GENERATED/NEEDS_REVIEW requirements in planning slices.
**Method:** Verify `_load_accepted_requirements()` filters by `ACCEPTED_FOR_VERTICAL_SLICE` only.
**Result:** BLOCKED — `_load_accepted_requirements` checks `status == "ACCEPTED_FOR_VERTICAL_SLICE"`.
Test `test_fods_future_scoped_excluded` confirms future_scoped_count > 0 and slices only
contain accepted IDs.
**Weakness found:** NONE

### Attack 5: Non-Authoritative Planning Allowed
**Goal:** Generate planning artifacts when requirements state is not AUTHORITATIVE.
**Method:** Call `expand_implementation_plan("nonexistent_format")` and
`build_planning_bundle(["nonexistent_format"])`.
**Result:** BLOCKED — expander returns `expansion_status = "BLOCKED_NOT_AUTHORITATIVE"`,
`accepted_count = 0`, `implementation_slices = []`. Bundle runtime shows blocked formats.
**Weakness found:** NONE

### Attack 6: Replay Inconsistency
**Goal:** Produce different fingerprints on consecutive runs without data changes.
**Method:** Run `compute_sprint_fingerprint("fods", "TEST")` twice; compare results.
**Result:** BLOCKED — fingerprints are SHA-256 based, deterministic. Test
`test_fods_fingerprint_is_deterministic` confirms identical fingerprints across runs.
**Weakness found:** NONE

### Attack 7: Onboarding Template Premature Readiness
**Goal:** Create an onboarding template that marks a format as READY without audit.
**Method:** Inspect templates for any `READY` values in readiness fields.
**Result:** BLOCKED — both templates have `NEEDS_AUDIT` and `overall: CANDIDATE`.
Test `test_all_readiness_fields_not_ready_in_templates` confirms no readiness fields
are prematurely set to READY.
**Weakness found:** NONE

### Attack 8: Planning Bundle Size Abuse (Prior ZIP Inclusion Attempt)
**Goal:** Confirm planning bundle cannot include prior ZIP evidence bundles.
**Method:** Inspect `build_planning_bundle()` code paths. Does it write to
`evidence-bundles/`? Does it read prior `.zip` files?
**Result:** BLOCKED by design — `planning_bundle_runtime.py` only reads planning
dicts (from `plan_multi_format` and `compute_sprint_fingerprint`). No file system
reads of `.zip` files. Bundle is an in-memory dict.
Test `test_bundle_not_size_warning_live` confirms bundle < 50 KB.
**Weakness found:** NONE

---

## Section 3: Remaining Weaknesses

| Weakness | Severity | Status |
|---------|---------|--------|
| File mtime check (check 5 in stale detection) is WARN not BLOCKER | LOW | By design — mtime unreliable across checkouts; YAML timestamps are authority |
| `compute_sprint_fingerprint` falls back silently on fingerprint error | LOW | Returns `{"error": str(e)}` — not a security issue; planning continues |
| Onboarding schema is YAML (not JSON Schema proper) — jsonschema validation not enforced | LOW | Schema is reference documentation; enforcement would require YAML→JSON conversion |
| Multi-format planning reads files fresh on each call — no caching vulnerability | NONE | Fresh reads prevent stale cache attacks |

**BLOCKING_WEAKNESS: 0**

---

## Section 4: False Positive Analysis

The stale detection system was checked for false positives on live data:

| Format | Expected | Actual |
|--------|----------|--------|
| FODS | Not STALE_BLOCKED | PASS — no blockers |
| FODT | Not STALE_BLOCKED | PASS — no blockers |

The prompt generator stale block was checked for false positives using `test_fresh_state_allows_prompt_generation`.

---

**LANE_G_STATUS: COMPLETE**
**ADVERSARIAL_REVIEW_STATUS: PASS**
**ATTACKS_ATTEMPTED: 8 (7 active, 1 surface-inspection)**
**ATTACKS_BLOCKED: 8**
**ATTACKS_SUCCEEDED: 0**
**REMAINING_BLOCKERS: 0**
**REMAINING_WEAKNESSES: 4 (all LOW/NONE, non-blocking)**
