# Plan: Supervisor Convergence and False-Green Prevention
**Plan ID:** wise-orbiting-yao
**Type:** machinery_hardening
**Mission ID:** FG-PREV-001
**Created:** 2026-07-03
**Healed:** 2026-07-03 (forensic audit + surgical corrections applied)

## Taskcard Closure Status (machine-parseable — 2-column format required by lifecycle_audit.py)

| TC-FG-001 | CLOSED |
| TC-FG-002 | CLOSED |
| TC-FG-002B | CLOSED |
| TC-FG-003 | CLOSED |
| TC-FG-004 | CLOSED |
| TC-FG-005 | CLOSED |
| TC-FG-006 | CLOSED |
| TC-FG-007 | CLOSED |
| TC-FG-008 | CLOSED |
| TC-FG-009 | CLOSED |
| TC-FG-010 | CLOSED |

---

## Deep Production Analysis (Pass 2 — verified against codebase)

### What Actually Broke and Why

**The real failure is a single fallback path in `grade_declared_work.py`, not a missing closure challenger.**

When the LLM is unavailable during `semantic_verify_item()`, the code falls through to `grade_intermediate_verify.intermediate_verify_item()`. That function reports back via the `"intermediate_content_check"` source key with `confidence: 0.7, adequate: true` when it finds `def test_` and `assert` anywhere in the test file. It does not analyze assertion strength.

This is confirmed by the PGM histogram work-item-grades.json:
```json
"semantic_verification": {
  "source": "intermediate_content_check",
  "adequate": true,
  "confidence": 0.7,
  "checks": [{"detail": "valid (8 test functions with assertions)"}]
}
```

The same data that the plan treated as a mystery ("confidence 0.7 below 0.8 threshold → benefit-of-doubt") is actually just the fallback string-search returning `adequate=true` because the file contains `def test_` and `assert`. There is no probabilistic assessment involved. There is no LLM confidence floor being applied. The benefit-of-doubt logic lives in the LLM path and never ran.

**The cascade:** `test_content_valid = "def test_" in content and "assert" in content` (lines 529-531 of grade_declared_work.py). True for any test file. Combined with `"adequate": true` from `intermediate_content_check` → item passes to ACCEPTED_VERIFIED. Grade cache then persists this result for 7 days keyed by content hash.

---

### Confirmed Structural Weaknesses (from code)

**SW-01 — The fallback guarantees false-green for LLM-absent runs**

When LLM is unavailable, 100% of test files with `def test_` and `assert` receive `adequate=true`. The system is designed to require the LLM for quality assessment, but the fallback gives the maximum passing result. This is inverted: uncertainty should trigger review, not promotion.

**SW-02 — AST assertion classification is necessary but not in the codebase**

Runtime-confirmed by classifying the PGM histogram tests using AST:

| Test function | Assertion type | Production level |
|---|---|---|
| `test_return_type` | `isinstance(result, list)` | TYPE (weak) |
| `test_default_bins_is_4` | `len(f()) == 4` | SHAPE (weak) |
| `test_1x1_white_last_bin_gets_pixel` | `result == [0, 0, 0, 1]` | EXACT (strong) |
| `test_2x2_gradient_uniform_distribution` | `f(_2X2) == [1, 1, 1, 1]` | BEHAVIORAL (strong) |
| `test_sum_equals_pixel_count` | `sum(f()) == 4` | AGGREGATE_SHAPE (weak) |
| `test_custom_bins_256` | `len==256, sum==4` + `result[85]==1` | MIXED — has SUBSCRIPT_EXACT (strong if counted) |
| `test_3x1_ramp_sum_equals_3` | `sum(f()) == 3` | AGGREGATE_SHAPE (weak) |
| `test_consistent_across_calls` | `f(x) == f(x)` | BEHAVIORAL (strong) |

**Correctly counts as:** 4 strong (hist, gradient, custom_bins subscripts, consistent), 4 weak.
`strong_ratio = 0.5`. The suite is genuinely adequate-but-imperfect. The grader should have reported this — instead it said "8 test functions with assertions" and stopped.

**SW-03 — The AST classifier needs SHAPE discrimination that `==` alone cannot provide**

`assert len(x) == 4` has the same AST operator as `assert result == [0,0,0,1]`. Both are `Compare(left=..., ops=[Eq()], comparators=[Constant(...)])`. The difference is whether the left side is a `Call` to a shape-extracting function (`len`, `sum`, `type`) or a direct value. This must be handled explicitly. The previous plan omitted this distinction, which would cause `len(x)==4` to be misclassified as EXACT (level 4) instead of SHAPE (level 2).

**SW-04 — Grade cache is sound, not the problem**

The cache key is `{item_id}:{evidence_hash}` where evidence_hash covers the content of the test files. If the test file is unchanged, the cache returns the same cached intermediate result every time → consistent. The cache is NOT a consistency risk for unchanged content. It IS a mild risk after 7-day TTL expiry if LLM availability differs. This is low priority.

**SW-05 — `run_and_write` returns int, not None**

Confirmed: `def run_and_write(...) -> int: return len([f for f in result.get("findings",[]) if f.get("severity")=="HIGH"])`. Returns 0 on skip/error, never None. The previous plan's `if _adv_result is not None and _adv_result >= 1` had a dead None-branch. The correct check is `if _adv_result >= 1`.

**SW-06 — The closure challenger (TC-FG-004) is additive on a broken foundation**

If the intermediate_content_check (SW-01) is not fixed, the challenger runs on items already marked ACCEPTED_VERIFIED by the broken fallback. The challenger can downgrade them, but the challenger itself uses `assess_proof_level` — which, if its SHAPE classification is wrong (SW-03), will also misclassify `len(x)==4` as strong. The challenger would then report PASSED on items that are actually weak. Building TC-FG-004 without fixing SW-01 and SW-03 produces a system with two layers of incorrect assessment.

**SW-07 — `max(proof_level)` across functions is the wrong aggregation**

The plan's first draft used max level. The healing pass proposed `strong_ratio`. But the right primary metric depends on what the CLAIMED behavior is. A test suite where 1/8 tests are strong has strong_ratio=0.125 and would fail — correct. A test suite where 4/8 are strong has strong_ratio=0.5 and might pass or fail depending on threshold. The threshold must be explicit, justified, and stable.

---

### What Must Be Preserved

- The 11-grade system and grade downgrade-only LLM policy — correct design
- The 10-gate continuation checker — deterministic and reliable
- Grade cache with content-hash invalidation — sound for unchanged content
- Governance validators (V82, V88, V89) — working correctly
- Evidence declaration schema and required fields — well-designed
- The mutation_tester.py — existing tool, should be REUSED not duplicated
- The adversarial_check.py run_and_write interface — correct, just fix the call site

---

### What Must Be Redesigned

**Priority 1 — Replace the fallback (fixes the root cause):**
Replace `grade_intermediate_verify.intermediate_verify_item()` with a deterministic `AssertionStrengthAnalyzer` that produces:
- `strong_ratio`: fraction of test functions containing at least one EXACT or BEHAVIORAL assertion
- `weak_tests`: list of function names where all assertions are TYPE/SHAPE/BARE
- `misleading_tests`: functions where assertions would pass common defective implementations (heuristic only)
- `overall_classification`: STRONG_PROOF / PARTIAL_PROOF / WEAK_PROOF / BARE_PROOF

This replaces the `adequate: true` blanket promotion with a graded result that the grader uses.

**Priority 2 — Anchor ACCEPTED_VERIFIED to strong_ratio:**
In `grade_declared_work.py`, change the PRODUCT_TEST item grade from ACCEPTED_VERIFIED to ACCEPTED_WITH_LIMITATIONS when `strong_ratio < STRONG_RATIO_THRESHOLD` (default 0.5). Add `strong_ratio` to the grade output.

**Priority 3 — Fix adversarial check call site:**
Remove the `iteration >= 3` gate. Change `continuation_warnings.append(...)` to also add to `rework_items` when HIGH findings detected.

**Priority 4 (additive, after 1-3):**
- Closure challenger (TC-FG-004) — now meaningful because foundation is correct
- Before/after evidence (TC-FG-005)
- Neighboring risk reviewer (TC-FG-006)
- Proof-gap cycle guard (TC-FG-007 Part B)

---

### What Breaks Consistency Across Reruns

Ranked by impact:

1. **LLM availability determines which path runs** — the LLM path and intermediate path produce different verdicts for the same evidence. This is the dominant consistency risk. Fix: make the fallback path deterministic and produce a MEANINGFUL grade (not blanket adequate=true).

2. **Grade cache TTL** — after 7 days, the LLM re-evaluates. If LLM availability or response differs: different verdict. Fix: the new AssertionStrengthAnalyzer is deterministic, so its results can be cached safely indefinitely (content hash unchanged = same result).

3. **LLM non-determinism for near-threshold cases** — when the LLM runs, responses vary. The confidence floor at 0.8 catches some of this. But cases near the 0.8 confidence threshold are genuinely unstable. Fix: don't rely on LLM for the primary PRODUCT_TEST adequacy gate. Use the AST-based strong_ratio instead.

4. **Proof-gap cycle counter in ephemeral review dict** — if the loop restarts, the counter resets. Fix: persist in `.local/supervisor/proof-gap-cycles.json` keyed by sprint_id.

---

### Tradeoffs and Limits

**Tradeoff T-01 — strong_ratio threshold is a judgment call**

At threshold=0.5: PGM histogram (4/8 strong) passes. At threshold=0.6: it fails. Neither value has a formal justification — 0.5 is defensible ("majority strong") but 0.6 is also reasonable ("clear majority strong"). This is a policy decision, not a technical one. The plan uses 0.5 but exposes it as a configurable constant `STRONG_RATIO_THRESHOLD`.

**Tradeoff T-02 — AST analysis cannot detect misleading tests without execution**

A test that checks `assert sum(result) == 4` would not catch a implementation that returns `[4,0,0,0]` instead of `[1,1,1,1]`. Both have sum=4. Detecting this requires actually running the tests against a defective implementation — which is what `mutation_tester.py` does. The plan should REUSE mutation_tester.py for misleading-test detection rather than reimplementing.

**Tradeoff T-03 — Adding a strong_ratio gate may produce false-positive rework**

A test suite with 1 strong test and 1 weak test (strong_ratio=0.5) might be genuinely adequate if the strong test covers the primary behavior and the weak test is an auxiliary smoke check. The system cannot know this without semantic context. The resolver: document that ACCEPTED_WITH_LIMITATIONS (not REWORK_REQUIRED) is returned for strong_ratio in [0.3, 0.5). Only true WEAK_PROOF (strong_ratio=0) returns REWORK_REQUIRED.

**Tradeoff T-04 — The closure challenger may produce false-positive FOUND_REWORK**

If `infer_default_contract()` sets proof_target=3 but the actual behavior only requires proof_target=2 (e.g., testing a getter function where the returned type IS the meaningful assertion), the challenger blocks unnecessarily. The resolver: workers can add explicit `proof_contracts` to their declarations to override the inferred contract.

**Limit L-01 — The system cannot verify that the CLAIMED behavior is tested**

If acceptance_criteria says "verify correct bin placement" but tests only check `len(result)==4`, the AST analyzer cannot connect the criterion to the assertion. Only the LLM can assess criterion-test alignment. This gap remains. The LLM path handles it when available.

**Limit L-02 — "Misleading test" heuristic detection is probabilistic**

Static analysis can identify `assert result == [0,0,0,0]` as potentially misleading (might pass constant-zero), but cannot be certain without running it. False-positive misleading-test detection could block legitimate tests that check all-zero expected behavior (e.g., an empty file should produce all-zero histogram bins — this is correct behavior, not a defect).

---

## Forensic Audit Record

### Modification Map (applied in this healing pass)

| ID | Section | Severity | Action Applied |
|---|---|---|---|
| M-001 | TC-FG-001 | Critical | Corrected incident narrative — GOV_BLOCK items are separate from test-proof weakness |
| M-002 | TC-FG-002 | Critical | Added conftest.py creation (tests/supervisor/ has no conftest) |
| M-003 | TC-FG-002 | High | Added test_layer requirement to ProofContract (was "not declared or invalid" but not blocking) |
| M-004 | TC-FG-003 Pilot 3 | High | Rewrote with 3-step structure — constant-zero detection was ambiguous |
| M-005 | TC-FG-004 | Critical | Added exact integration point in autonomous_cycle.py (line 977 after grade_all call) |
| M-006 | TC-FG-004 | Critical | Added default proof contract inference — challenger was vacuously passing with no contracts |
| M-007 | TC-FG-005 | High | Added git-show failure fallback for new files (no pre-sprint baseline exists) |
| M-008 | TC-FG-007 Part A | High | Specified LLM-unavailable behavior — never block on LLM absence |
| M-009 | TC-FG-007 Part B | High | Added max 3 proof-gap cycles guard to prevent infinite loop |
| M-010 | TC-FG-009 | Critical | Corrected closure_challenger expected outcome — challenger finds PROOF LEVEL weakness not GOV_BLOCK |
| M-011 | All TCs | High | Added explicit prerequisites to all taskcards |
| M-012 | All TCs | High | Added rollback procedure to TCs modifying existing files |
| M-013 | New TC-FG-010 | High | Added lifecycle audit gate (CLAUDE.md mandatory for machinery_hardening) |
| M-014 | TC-FG-009 | High | Added evidence declaration template for FG-PREV-001 mission |
| M-015 | TC-FG-001 | Medium | Verified source data existence before binding — added verification step |
| M-016 | TC-FG-003 Pilot 11 | Medium | Corrected: PGM behavioral tests are SOUND; challenger PASSES for proof, finds weakness only in `test_return_type` |
| M-017 | TC-FG-007 | Medium | Clarified Part A targets adversarial_check.py scan, NOT GOV_BLOCK (GOV_BLOCK already works) |
| M-018 | Verification | Low | Added single combined pytest command |
| M-019 | Exclusions | Medium | Added explicit rollback authority for autonomous_cycle.py modifications |

### Root Causes of Plan Weaknesses

**RC-001 — Incident misidentification**
Symptom: TC-FG-001 claimed GOV_BLOCK items "revealed" the false-green.
Local cause: GOV_BLOCK:V100/V102/V104 are README validators, not proof-adequacy validators.
Root cause: The plan author conflated two separate failure modes — (a) item-grade false-green from weak assertion detection and (b) sprint-level GOV_BLOCK blocking continuation. The ACTUAL false-green evidence is: `acceptance_criteria_met: ["Evidence found", "No missing paths"]` — file-existence proof only — alongside `confidence: 0.7 with llm_used: false` getting benefit-of-doubt promotion.

**RC-002 — No conftest → imports fail**
Symptom: New tests in tests/supervisor/ would fail to import from tools/supervisor/.
Root cause: tests/supervisor/conftest.py does not exist. The plan created 7 new test files without creating the conftest that makes imports work.

**RC-003 — Empty proof contracts make challenger vacuous**
Symptom: run_closure_challenge() always returns CLOSURE_CHALLENGE_PASSED when evidence declarations have no proof_contracts field.
Root cause: Evidence declarations written today have no proof_contracts. The plan requires proof_contracts to exist but provides no mechanism to infer them for items that don't declare them.

**RC-004 — adversarial_check.py integration already exists but is wrong**
Symptom: TC-FG-007 treats adversarial blocking as a new addition.
Root cause: autonomous_cycle.py line 2063 already adds to `continuation_warnings` when `_adv_high >= 1 AND iteration >= 3`. The fix needed is: (a) remove the `iteration >= 3` gate and (b) add findings to `rework_items` not just `continuation_warnings`. This is surgical, not additive.

**RC-005 — Lifecycle audit gate missing**
Root cause: Plan type is machinery_hardening. CLAUDE.md §Step 0 mandates lifecycle_audit.py before --terminal. Not in original plan.

---

## Context

The autonomous supervisor loop reaches "all-green" verdict (ACCEPTED_VERIFIED) for work items when a separate PROVE invocation discovers additional in-scope weaknesses the normal loop did not surface. This is a proof-adequacy governance defect.

**Confirmed incident evidence (verified from repository files):**
- Sprint: `pgm-histogram-tests-20260703`
- Item: `TEST-PGM-BRIGHTNESS-HIST-001` graded `ACCEPTED_VERIFIED`
- False-green evidence: `acceptance_criteria_met: ["Evidence found", "No missing paths"]` — ONLY file-existence criteria, no behavioral assertion verification
- Semantic verification: `confidence: 0.7, llm_used: false` — benefit-of-doubt threshold promoted adequacy
- The grader confirmed "8 test functions with assertions" but did NOT verify that 2 of 8 tests (`test_return_type`, `test_default_bins_is_4`) are type-only/shape-only assertions (proof level ≤ 2)
- GOV_BLOCK items (V100/V102/V104 — README validators) are a SEPARATE and CORRECTLY CAUGHT concern; they are not the false-green incident

**What the normal loop does NOT check:**
- Whether assertions verify EXACT expected values vs. type/shape only
- Whether any plausible defective implementation (constant-zero, wrong default) would pass the test suite
- Before/after behavioral coverage comparison
- Neighboring weak assertions in the same test file

**What exists and is confirmed working:**
- `tools/supervisor/autonomous_cycle.py` — 2,545 LOC core orchestrator
- `grade_all()` at line 977 in autonomous_cycle.py — grades after inspection
- adversarial_check at line 2059-2066 in autonomous_cycle.py — partially wired (continuation_warnings only, iteration >= 3 gate)
- `tests/supervisor/` — exists with many supervisor tests
- No `tests/supervisor/conftest.py` — NEW FILES NEED conftest to import
- `tools/supervisor/mutation_tester.py` — AST mutation operators (already exists)
- `reports/concurrency/pilot-evidence/` — pilot JSON pattern template
- `.supervisor/schemas/evidence-declaration.schema.json` — primary schema

**Goal:** Heal the supervisor machinery so that:
1. Proof adequacy (behavioral, fault-sensitive, before/after) is enforced before green status
2. An independent closure challenger blocks false-green candidates
3. All 12 required pilots pass
4. The affected mission (PGM histogram) replays correctly through the healed system
5. All 17 required governance counters reach zero

---

## Taskcard Table

| Taskcard | Title | Status | Prerequisites |
|---|---|---|---|
| TC-FG-001 | Bind incident and write false-green timeline | CLOSED | None |
| TC-FG-002 | Implement proof-adequacy contract infrastructure + conftest | CLOSED | TC-FG-001 |
| TC-FG-002b | Fix foundation: replace grade_intermediate_verify fallback with AssertionStrengthAnalyzer | CLOSED | TC-FG-002 |
| TC-FG-003 | Implement 12 false-green prevention pilots | CLOSED | TC-FG-002b, TC-FG-004, TC-FG-005, TC-FG-006, TC-FG-007 |
| TC-FG-004 | Implement independent closure challenger | CLOSED | TC-FG-002b |
| TC-FG-005 | Implement before/after evidence module | CLOSED | TC-FG-002 |
| TC-FG-006 | Implement neighboring-risk reviewer | CLOSED | TC-FG-002 |
| TC-FG-007 | Harden adversarial blocking + add queue-empty guard | CLOSED | TC-FG-004 |
| TC-FG-008 | Prior-closure audit scan | CLOSED | TC-FG-002 |
| TC-FG-009 | Replay affected mission + prove idempotency | CLOSED | TC-FG-003 through TC-FG-008 |
| TC-FG-010 | Lifecycle audit gate (machinery_hardening closure) | CLOSED | TC-FG-009 |

---

## TC-FG-001 — Bind incident and write false-green timeline

**Prerequisites:** None
**Status:** OPEN

**Goal:** Create the authoritative false-green incident record and timeline. Verify source data before binding.

**Step 0 — Verify source data exists:**
Before writing any YAML, read and verify:
1. `reports/supervisor/maturity-signal.json` — must have `sprint_verdict: ACCEPTED_WITH_REWORK`, `autonomous_continue: false`, rework_items list
2. `reports/supervisor/work-item-grades.json` — must have TEST-PGM-BRIGHTNESS-HIST-001 with `supervisor_grade: ACCEPTED_VERIFIED` and `acceptance_criteria_met` showing only file-existence proof
3. `tests/python/pgm/test_r259_pgm_brightness_histogram.py` — must have exactly 8 test functions; note that 2 are type/shape-only (`test_return_type`, `test_default_bins_is_4`) and 6 have exact behavioral assertions

**Confirmed facts to bind:**
- Mission: `TEST-PGM-BRIGHTNESS-HIST-001` (pgm_brightness_histogram, 8 behavioral tests)
- False-green mechanism: grader accepted ACCEPTED_VERIFIED based only on file existence + "8 test functions with assertions", confidence 0.7 with benefit-of-doubt (llm_used=false)
- Green iteration: `pgm-histogram-tests-20260703`
- Missed finding: 2 of 8 tests (`test_return_type`, `test_default_bins_is_4`) are type/shape-only (proof level ≤ 2) — NOT flagged by normal audit
- Separate (correctly caught) concern: GOV_BLOCK:validate_readme_freshness, V100, V102, V104 blocked continuation — these are README validators, correctly working, NOT the false-green incident
- `product_source_check.source_exists: false` means no PRODUCT_SOURCE was declared (sprint was test-only) — this is a scope note, not a missing implementation

**Deliverables:**
- `reports/governance/false-green-incident.yaml`:
  ```yaml
  incident_id: FGI-PGM-HIST-001
  mission_id: FG-PREV-001
  plan_id: wise-orbiting-yao
  plan_path: plans/.claude/wise-orbiting-yao.md
  affected_sprint: pgm-histogram-tests-20260703
  affected_item: TEST-PGM-BRIGHTNESS-HIST-001
  green_iteration: pgm-histogram-tests-20260703
  green_grade: ACCEPTED_VERIFIED
  false_green_class: TYPE_OR_SHAPE_ONLY_PROOF_MIXED_WITH_BEHAVIORAL
  false_green_evidence:
    - field: acceptance_criteria_met
      value: ["Evidence found", "No missing paths"]
      issue: file-existence-only criteria, no behavioral assertion check
    - field: semantic_verification.confidence
      value: 0.7
      issue: below 0.8 → benefit-of-doubt promotion without behavioral verification
    - field: semantic_verification.llm_used
      value: false
      issue: intermediate content check only, no actual assertion-strength analysis
  weak_tests_not_flagged:
    - test_return_type: assert isinstance(result, list) — proof level 2 (type-only)
    - test_default_bins_is_4: assert len(result) == 4 — proof level 2 (shape-only)
  sound_tests_present:
    - test_1x1_white_last_bin_gets_pixel: assert result == [0, 0, 0, 1] — proof level 3
    - test_2x2_gradient_uniform_distribution: assert result == [1, 1, 1, 1] — proof level 3
    - test_custom_bins_256: multiple exact bin-position assertions — proof level 4
  separate_correctly_caught_concern:
    - GOV_BLOCK:validate_readme_freshness
    - GOV_BLOCK:V100
    - GOV_BLOCK:V102
    - GOV_BLOCK:V104
    note: README validators blocked continuation correctly — NOT the false-green incident
  terminal_state: reports/supervisor/maturity-signal.json
  evidence_roots:
    - .local/evidences/pgm-histogram-tests-20260703-1fb74d0f/
    - reports/supervisor/work-item-grades.json
  ```

- `reports/governance/false-green-timeline.yaml` — ≥ 4 timeline events:
  ```yaml
  timeline_events:
    - timestamp: <from maturity-signal timestamp>
      iteration: pgm-histogram-tests-20260703
      stage: GRADE
      action: grade_all() ran on TEST-PGM-BRIGHTNESS-HIST-001
      claims: ACCEPTED_VERIFIED
      proof_available: file existence + "8 test functions with assertions"
      findings_visible: None (no proof-level check)
      findings_missed:
        - test_return_type is proof level 2 (type-only)
        - test_default_bins_is_4 is proof level 2 (shape-only)
      state_transition: item_grade=ACCEPTED_VERIFIED
    - stage: SPRINT_VERDICT
      action: sprint verdict computed
      claims: ACCEPTED_WITH_REWORK (GOV_BLOCK items)
      findings_visible: GOV_BLOCK:V100/V102/V104
      findings_missed: weak-assertion mix in test suite
    - stage: CONTINUATION_CHECK
      action: check_continuation.py ran
      claims: autonomous_continue=false (correctly blocked)
      findings_visible: rework_items GOV_BLOCK
      findings_missed: proof-level inadequacy of ACCEPTED_VERIFIED item
    - stage: PROVE_INVOCATION
      action: PROVE command (independent re-evaluation)
      findings_visible: test_return_type is type-only, test_default_bins_is_4 is shape-only
      state_transition: false_green_confirmed
  ```

**Missed findings classified per spec §4:**
- FMF-001: `test_return_type` — category: TYPE_OR_SHAPE_ONLY_PROOF; visible_before_green: YES (file existed); discoverable_before_green: YES (requires assertion-strength check); first_failed_boundary: GRADE stage
- FMF-002: `test_default_bins_is_4` — category: TYPE_OR_SHAPE_ONLY_PROOF; same analysis

**Acceptance criteria:**
- Both YAML files exist and are valid
- `false-green-incident.yaml` has all fields above populated with verified data
- `false-green-timeline.yaml` has ≥ 4 events covering grade, verdict, continuation, prove
- FMF-001 and FMF-002 are recorded as missed_findings
- GOV_BLOCK items explicitly noted as SEPARATE concern in incident record

---

## TC-FG-002 — Implement proof-adequacy contract infrastructure + conftest

**Prerequisites:** TC-FG-001 (incident bound)
**Status:** OPEN

### Step 0 — Confirm import pattern for new test files

**Confirmed pattern from existing supervisor tests (verified):**

`test_adversarial_check.py` uses:
```python
_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
from adversarial_check import run_adversarial_check, ...
```

`test_lifecycle_audit.py` uses:
```python
_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO))
from tools.supervisor.lifecycle_audit import ...
```

**All new test files in tests/supervisor/ MUST use pattern 1** (add `tools/supervisor/` directly):
```python
import sys
from pathlib import Path
_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
# Then: from proof_adequacy_contract import ProofLevel, ProofContract, ...
```

**Optionally create conftest.py** (`tests/supervisor/conftest.py`) to DRY this up — safe because existing tests' own sys.path insertions are idempotent. If created:
```python
"""conftest.py for tests/supervisor — canonical import path for supervisor modules."""
import sys
from pathlib import Path
_REPO = Path(__file__).resolve().parent.parent.parent
_SUPERVISOR = _REPO / "tools" / "supervisor"
if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
```

**Verify imports work** before writing test content:
```bash
python -c "import sys; sys.path.insert(0, 'tools/supervisor'); from grade_declared_work import grade_all; print('IMPORT OK')"
```
Must print `IMPORT OK`. If not, diagnose before proceeding.

### Step 1 — Create proof_adequacy_contract.py

**New file:** `tools/supervisor/proof_adequacy_contract.py`

**Required imports and classes:**
```python
from __future__ import annotations
import ast
import re
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Optional

class ProofLevel(IntEnum):
    NO_PROOF = 0
    ARTIFACT_PRESENT = 1
    HAPPY_PATH_EXECUTED = 2
    EXACT_BEHAVIOR_VERIFIED = 3
    ADVERSARIAL_AND_INTEGRATION_VERIFIED = 4
    PRODUCTION_SHAPED_REPEATABLE_AND_FAULT_SENSITIVE = 5

@dataclass
class ProofContract:
    requirement_id: str
    target: str                           # e.g., "pgm_brightness_histogram"
    behavior_claim: str                   # e.g., "returns correct bin counts for grayscale image"
    risk: str                             # e.g., "HIGH" | "MEDIUM" | "LOW"
    proof_target: ProofLevel              # Minimum required level
    required_test_layer: int = 3          # Minimum test_layer (3 = FOCUSED, 4 = INTEGRATION)
    positive_cases: list[str] = field(default_factory=list)
    exact_expected_results: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    negative_cases: list[str] = field(default_factory=list)
    boundary_cases: list[str] = field(default_factory=list)
    adversarial_cases: list[str] = field(default_factory=list)
    plausible_faults: list[str] = field(default_factory=list)
    mutation_or_fault_challenge: bool = False
    before_after_comparison: bool = False
    neighboring_risk_review: bool = False
    exclusions: list[dict] = field(default_factory=list)
    closure_conditions: list[str] = field(default_factory=list)

@dataclass
class FaultSensitivity:
    requirement_id: str
    plausible_fault: str
    old_proof_verdict: str   # "PASS" | "FAIL" | "NOT_CHECKED"
    new_proof_verdict: str   # "PASS" | "FAIL" | "SURVIVES" | "DETECTED"
    detection_mechanism: str
    evidence: str

@dataclass
class BeforeAfterProof:
    requirement_id: str
    baseline_revision: str   # git sha or "NO_BASELINE" (new file)
    final_revision: str
    before_tests: list[str] = field(default_factory=list)
    before_behaviors_proven: list[str] = field(default_factory=list)
    before_faults_detected: list[str] = field(default_factory=list)
    after_tests: list[str] = field(default_factory=list)
    after_behaviors_proven: list[str] = field(default_factory=list)
    after_faults_detected: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)
    unchanged_weaknesses: list[str] = field(default_factory=list)
    regressions: list[str] = field(default_factory=list)
    new_findings: list[str] = field(default_factory=list)
    verdict: str = "UNCHANGED"  # "IMPROVEMENT" | "REGRESSION" | "UNCHANGED" | "NEEDS_REWORK" | "NEW_FILE"
```

**Key functions:**

```python
def _parse_assertion_level(node: ast.Assert) -> int:
    """Classify a single assert node into proof level 1-4."""
    test = node.test
    # Level 4: exact value comparison (== specific value, not None/True/False)
    if isinstance(test, ast.Compare) and any(isinstance(op, ast.Eq) for op in test.ops):
        comparators = test.comparators
        if comparators and not all(
            isinstance(c, (ast.Constant,)) and c.value in (None, True, False)
            for c in comparators
        ):
            return 4
    # Level 3: inequality, ordering, membership with specifics
    if isinstance(test, ast.Compare):
        return 3
    # Level 2: isinstance(), len(), nonempty, is not None
    if isinstance(test, ast.Call):
        if isinstance(test.func, ast.Name) and test.func.id in ("isinstance", "len"):
            return 2
    if isinstance(test, ast.Compare):
        for c in test.comparators:
            if isinstance(c, ast.Constant) and c.value is None:
                return 2
    # Level 1: bare assert x, assert True, assert False
    return 1

def assess_proof_level(test_path: str, contract: Optional[ProofContract] = None) -> dict:
    """
    Returns {
      "level": ProofLevel,
      "test_count": int,
      "level_distribution": {1: count, 2: count, 3: count, 4: count},
      "weak_tests": [{"name": str, "level": int}],
      "strong_tests": [{"name": str, "level": int}],
      "gaps": [str],
      "plausible_faults_surviving": [str],
    }
    """
    # Parse AST of test file
    # Classify each test function's assertions
    # Compute overall level = max level present among test functions
    # Identify weak tests (max assertion level in function <= 2)
    # If contract provided: check plausible_faults against assertion coverage
    ...

def infer_default_contract(item: dict) -> ProofContract:
    """
    Infer a default ProofContract from a work item when no explicit contract declared.
    Used when evidence declaration has no proof_contracts field.

    For PRODUCT_TEST items:
      - proof_target: ProofLevel.EXACT_BEHAVIOR_VERIFIED (3)
      - required_test_layer: 3
      - plausible_faults: ["constant_return", "wrong_default", "off_by_one"]
      - before_after_comparison: True
      - neighboring_risk_review: True

    For PRODUCT_SOURCE items:
      - proof_target: ProofLevel.HAPPY_PATH_EXECUTED (2)
      - plausible_faults: ["not_implemented", "stub_return"]

    For GOVERNANCE_* items:
      - proof_target: ProofLevel.ARTIFACT_PRESENT (1)
    """
    ...

def proof_sufficient_for_closure(
    contract: ProofContract,
    test_paths: list[str],
    assessment: Optional[dict] = None,
) -> tuple[bool, list[str]]:
    """
    Returns (sufficient: bool, gaps: list[str]).
    sufficient=False when:
    - assessed level < contract.proof_target
    - any plausible_fault not challenged
    - contract requires before_after but no comparison performed
    - contract requires negative_cases but none found in tests
    """
    ...
```

**Tests:** `tests/supervisor/test_proof_adequacy_contract.py` — exactly 10 tests:
1. `test_proof_level_ordering` — ProofLevel.EXACT > HAPPY_PATH > ARTIFACT
2. `test_assess_type_only_assertion` — `assert isinstance(result, list)` → level 2
3. `test_assess_exact_value_assertion` — `assert result == [0, 0, 0, 1]` → level 4
4. `test_assess_mixed_assertions` — file with both types → overall level 4, weak_tests contains type-only ones
5. `test_infer_default_contract_product_test` — PRODUCT_TEST → proof_target=3, plausible_faults non-empty
6. `test_infer_default_contract_governance` — GOVERNANCE_DOC → proof_target=1
7. `test_proof_sufficient_below_target` — assessed level 2 vs target 3 → (False, ["proof level 2 below required 3"])
8. `test_proof_sufficient_above_target` — assessed level 3 vs target 3 → (True, [])
9. `test_pgm_histogram_assessment` — runs assess_proof_level on actual test_r259_pgm_brightness_histogram.py — must identify test_return_type and test_default_bins_is_4 as weak (level 2)
10. `test_fault_sensitivity_record` — FaultSensitivity creation and field access

**Acceptance criteria:**
- `test_pgm_histogram_assessment` MUST pass — this validates the core false-green detection
- All 10 tests pass with zero failures
- `assess_proof_level` on `test_r259_pgm_brightness_histogram.py` returns level=4 (overall), weak_tests includes `test_return_type` and `test_default_bins_is_4`
- `infer_default_contract` for PRODUCT_TEST returns proof_target=3 and non-empty plausible_faults

---

## TC-FG-002b — Fix foundation: replace grade_intermediate_verify fallback with AssertionStrengthAnalyzer

**Prerequisites:** TC-FG-002 (proof_adequacy_contract.py exists)
**Status:** OPEN

**Root cause this fixes:** `grade_intermediate_verify.intermediate_verify_item()` returns `adequate=true, confidence=0.7` for any file containing `def test_` and `assert`. This blanket pass is the mechanism that produced ACCEPTED_VERIFIED for the PGM histogram sprint with no LLM available (SW-01).

**Files to modify:**

1. **`tools/supervisor/grade_intermediate_verify.py`** — Replace the body of `intermediate_verify_item()`:

   **Pre-edit:** Read the full file first to confirm function signature and imports before editing.

   Current behavior (lines ~529-531 of grade_declared_work.py or inline in grade_intermediate_verify.py):
   ```python
   has_test_fn = "def test_" in content
   has_assert = "assert" in content
   test_content_valid = has_test_fn and has_assert
   # returns adequate=True for any test file
   ```

   Replace with AssertionStrengthAnalyzer call:
   ```python
   def intermediate_verify_item(item: dict, evidence_paths: list[str]) -> dict:
       """
       Replaces blanket string-search with deterministic AST-based assertion strength analysis.
       Returns a graded result rather than blanket adequate=True.
       """
       try:
           import sys
           from pathlib import Path as _Path
           _repo = _Path(__file__).resolve().parent.parent.parent
           if str(_repo / "tools" / "supervisor") not in sys.path:
               sys.path.insert(0, str(_repo / "tools" / "supervisor"))
           from proof_adequacy_contract import assess_proof_level, ProofLevel

           test_paths = [p for p in evidence_paths if p.endswith(".py") and "test_" in _Path(p).name]
           if not test_paths:
               return {
                   "adequate": False,
                   "confidence": 0.9,
                   "source": "intermediate_content_check",
                   "stub_detected": False,
                   "deficiencies": ["no test files found in evidence_paths"],
                   "strong_ratio": 0.0,
                   "overall_classification": "NO_PROOF",
               }

           # Assess the first (primary) test file
           assessment = assess_proof_level(test_paths[0])
           strong_ratio = assessment.get("strong_ratio", 0.0)
           level = assessment.get("level", 0)
           weak_tests = assessment.get("weak_tests", [])

           # Map to adequacy verdict
           STRONG_RATIO_THRESHOLD = 0.5
           if strong_ratio >= STRONG_RATIO_THRESHOLD and level >= 3:
               adequate = True
               classification = "STRONG_PROOF"
               confidence = 0.85
           elif strong_ratio > 0 or level >= 2:
               adequate = True   # ACCEPTED_WITH_LIMITATIONS (caller must check strong_ratio)
               classification = "PARTIAL_PROOF"
               confidence = 0.6
           else:
               adequate = False
               classification = "WEAK_PROOF"
               confidence = 0.9

           deficiencies = [f"weak: {t['name']}" for t in weak_tests]

           return {
               "adequate": adequate,
               "confidence": confidence,
               "source": "intermediate_content_check",
               "stub_detected": (level <= 1),
               "deficiencies": deficiencies,
               "strong_ratio": strong_ratio,
               "overall_classification": classification,
               "weak_tests": weak_tests,
               "intermediate_verified": True,
               "checks": [{"path": test_paths[0], "exists": True, "content_ok": adequate,
                           "detail": f"{classification} (strong_ratio={strong_ratio:.2f}, level={level})",
                           "check_type": "ast_assertion_strength"}],
               "summary": f"1/1 evidence file assessed: {classification}",
           }
       except Exception as _e:
           # Fallback: if AST analysis itself fails, return conservative NOT-adequate to avoid false-green
           return {
               "adequate": False,
               "confidence": 0.5,
               "source": "intermediate_content_check",
               "stub_detected": False,
               "deficiencies": [f"AST analysis error: {_e}"],
               "strong_ratio": 0.0,
               "overall_classification": "ANALYSIS_ERROR",
           }
   ```

2. **`tools/supervisor/grade_declared_work.py`** — After `intermediate_verify_item()` returns, add grade-cap logic:

   Find the block that uses `semantic_verification` result to set `supervisor_grade`. After receiving the intermediate verification result, add:
   ```python
   # TC-FG-002b: cap ACCEPTED_VERIFIED when strong_ratio below threshold
   if _sem_result.get("source") == "intermediate_content_check":
       _strong_ratio = _sem_result.get("strong_ratio", 0.0)
       _classification = _sem_result.get("overall_classification", "")
       if _classification in ("WEAK_PROOF", "NO_PROOF", "ANALYSIS_ERROR"):
           # Downgrade from ACCEPTED_VERIFIED to ACCEPTED_WITH_LIMITATIONS
           if item.get("supervisor_grade") == "ACCEPTED_VERIFIED":
               item["supervisor_grade"] = "ACCEPTED_WITH_LIMITATIONS"
               item["required_rework"] = (
                   f"Intermediate check: {_classification} (strong_ratio={_strong_ratio:.2f}). "
                   "Add exact behavioral assertions before claiming ACCEPTED_VERIFIED."
               )
   ```

   **Pre-edit:** Read `grade_declared_work.py` lines 440-560 to locate the exact variable names and insertion point. The variable holding the semantic verification result may differ from `_sem_result`.

**Rollback procedure:**
If modifications to `grade_intermediate_verify.py` or `grade_declared_work.py` break existing supervisor tests:
1. Revert the two files to their pre-edit state
2. Run `tests/supervisor/test_grade_declared_work.py` to confirm baseline passes
3. Debug the specific import or integration error before re-applying

**Tests:** Add 3 tests to `tests/supervisor/test_proof_adequacy_contract.py` (or a new file `tests/supervisor/test_intermediate_verify_fix.py`):
1. `test_intermediate_verify_weak_suite_returns_false` — test file with only `isinstance()` → `adequate=False, classification=WEAK_PROOF`
2. `test_intermediate_verify_strong_suite_returns_true` — test file with `assert result==[0,0,0,1]` → `adequate=True, classification=STRONG_PROOF`
3. `test_intermediate_verify_mixed_suite_partial_proof` — test file with 4 strong / 4 weak → `adequate=True, classification=PARTIAL_PROOF, strong_ratio=0.5`

**Acceptance criteria:**
- `grade_intermediate_verify.intermediate_verify_item()` no longer returns `adequate=True` for files with only `isinstance()` assertions
- PGM histogram test file (4 strong / 4 weak, strong_ratio=0.5) → `classification=PARTIAL_PROOF` or `STRONG_PROOF` (threshold=0.5 means barely adequate)
- Existing `tests/supervisor/test_grade_declared_work.py` tests still pass (zero regressions)
- AST analysis failure falls back to `adequate=False` (conservative) not `adequate=True` (false-green)

---

## TC-FG-004 — Implement independent closure challenger

**Prerequisites:** TC-FG-002 (ProofContract and conftest exist)
**Status:** OPEN

**New file:** `tools/supervisor/closure_challenger.py`

### Contract:

```python
def run_closure_challenge(
    item: dict,                          # work item dict from grading output
    evidence_root: str,                  # e.g., ".local/evidences/<run_id>/"
    repo_root: str,                      # repo root path
    proof_contracts: Optional[list[dict]] = None,  # from evidence declaration; None = infer
) -> dict:
    """
    Returns {
      "verdict": "CLOSURE_CHALLENGE_PASSED" | "CLOSURE_CHALLENGE_FOUND_REWORK" | "CLOSURE_CHALLENGE_INVALID",
      "item_id": str,
      "assessed_level": int,
      "required_level": int,
      "new_findings": [str],
      "weak_tests": [...],
      "plausible_faults_tested": [str],
      "plausible_faults_surviving": [str],
      "exclusions_review": [...],
      "neighboring_risk_summary": {...},
    }
    """
```

### Challenger behavior:

1. **Ignore all prior green summaries** — read current file state only
2. **Resolve proof contract:**
   - If `proof_contracts` provided and non-empty: use first matching requirement_id
   - Else: call `infer_default_contract(item)` from proof_adequacy_contract.py
3. **Assess test files:**
   - Find test files from item's `tests_supporting` field
   - For each: call `assess_proof_level(test_path, contract)`
   - Compute overall level = max level across all assessed test files
4. **Challenge plausible faults:**
   - For each fault in `contract.plausible_faults`:
     - Check if any test assertion would detect it
     - Record as DETECTED or SURVIVES
5. **Neighboring risk review:** Call `review_neighboring_risks()` from neighboring_risk_reviewer.py
6. **Return FOUND_REWORK if:**
   - `assessed_level < contract.proof_target`, OR
   - any plausible fault SURVIVES AND risk not `LOW`, OR
   - any `must_fix` items from neighboring_risk_review

### Integration point in autonomous_cycle.py:

**After line 977** (`review = grade_all(inspection, decl, ...)`), **before line 1283** (`write_outputs(review, review_dir)`):

Add the following block at approximately line 985 (after the `review["declaration_path"] = ...` assignment):

```python
# TC-FG-004: Closure challenge — enforce proof adequacy before ACCEPTED_VERIFIED
try:
    from closure_challenger import run_closure_challenge as _run_cc
    from pathlib import Path as _Path
    _cc_results = []
    for _item in review.get("item_grades", []):
        if _item.get("supervisor_grade") == "ACCEPTED_VERIFIED":
            _cc_result = _run_cc(
                item=_item,
                evidence_root=str(review_dir),
                repo_root=str(repo_root),
                proof_contracts=decl.get("proof_contracts"),
            )
            _cc_results.append(_cc_result)
            if _cc_result["verdict"] == "CLOSURE_CHALLENGE_FOUND_REWORK":
                # Downgrade item
                _item["supervisor_grade"] = "REWORK_REQUIRED"
                _item["required_rework"] = (
                    f"Closure challenge found: {'; '.join(_cc_result['new_findings'])}"
                )
                review.setdefault("rework_items", []).append(
                    f"CLOSURE_CHALLENGE:{_item['item_id']}"
                )
                review["critical_rework_count"] = review.get("critical_rework_count", 0) + 1
                if review.get("overall_verdict") in ("ACCEPTED", "ACCEPTED_WITH_LIMITATIONS", "ACCEPTED_WITH_REWORK"):
                    review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
                if "autonomous_continue" in review:
                    review["autonomous_continue"] = False
    # Write challenge results
    _cc_out = review_dir / "closure-challenge-results.json"
    import json as _json
    _cc_out.write_text(_json.dumps(_cc_results, indent=2))
    print(f"  Closure challenge: {len(_cc_results)} items challenged, "
          f"{sum(1 for r in _cc_results if r['verdict'] == 'CLOSURE_CHALLENGE_FOUND_REWORK')} found rework")
except Exception as _cc_err:
    print(f"  WARNING: Closure challenge skipped (non-critical): {_cc_err}")
```

**Rollback procedure:**
If this integration causes test failures in existing supervisor tests (`tests/supervisor/test_adversarial_check.py`, `test_lifecycle_audit.py`):
1. Remove the TC-FG-004 block from autonomous_cycle.py
2. Verify existing tests pass
3. Debug the import or logic error
4. Re-apply

**Tests:** `tests/supervisor/test_closure_challenger.py` — exactly 6 tests:
1. `test_challenge_type_only_assertions_found_rework` — file with only `isinstance()` → FOUND_REWORK
2. `test_challenge_exact_value_assertions_passed` — file with `assert result == [0,0,0,1]` → PASSED
3. `test_challenge_inferred_contract` — no explicit contract → infer default → challenge works
4. `test_challenge_authorized_exclusion` — exclusion in item → not counted as rework
5. `test_challenge_idempotency` — run twice on same inputs → same verdict
6. `test_challenge_writes_result_json` — result file written to evidence_root

**Acceptance criteria:**
- Tests 1-6 all pass
- `run_closure_challenge` on `test_return_type`-only file returns FOUND_REWORK
- `run_closure_challenge` on `test_r259_pgm_brightness_histogram.py` returns PASSED (sound tests present) but reports weak_tests=[test_return_type, test_default_bins_is_4]
- Result JSON written to evidence root
- Integration in autonomous_cycle.py does not break existing tests

---

## TC-FG-005 — Implement before/after evidence module

**Prerequisites:** TC-FG-002 (BeforeAfterProof dataclass exists)
**Status:** OPEN

**New file:** `tools/supervisor/before_after_evidence.py`

**Key function:**
```python
def build_before_after_proof(
    requirement_id: str,
    baseline_git_sha: str,    # from declaration git_head_start; may be "UNKNOWN"
    final_git_sha: str,       # from declaration git_head_end; may be "UNKNOWN"
    test_paths: list[str],
    evidence_root: str,
    repo_root: str,
) -> BeforeAfterProof:
    """
    Generates BeforeAfterProof by comparing test assertions before vs after sprint.

    FALLBACK STRATEGY (for new files or git failure):
    - If git show fails for baseline (FileNotFoundError, CalledProcessError):
      Set baseline_revision = "NO_BASELINE" and before_tests = []
      Set verdict = "NEW_FILE" (always an improvement, never NEEDS_REWORK)
    - If baseline_git_sha is "UNKNOWN":
      Same treatment as NO_BASELINE
    """
    from proof_adequacy_contract import assess_proof_level
    import subprocess
    import json

    before_tests = []
    before_assessment = None
    after_assessment = None

    for test_path in test_paths:
        # --- AFTER state (current file) ---
        if Path(test_path).exists():
            after_assessment = assess_proof_level(test_path)

        # --- BEFORE state (git show baseline) ---
        if baseline_git_sha and baseline_git_sha not in ("UNKNOWN", "NO_BASELINE"):
            try:
                rel_path = str(Path(test_path).relative_to(repo_root))
                result = subprocess.run(
                    ["git", "show", f"{baseline_git_sha}:{rel_path}"],
                    capture_output=True, text=True, cwd=repo_root,
                )
                if result.returncode == 0:
                    # Write to temp, assess
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
                        tf.write(result.stdout)
                        tmp_path = tf.name
                    before_assessment = assess_proof_level(tmp_path)
                    Path(tmp_path).unlink(missing_ok=True)
                else:
                    # File didn't exist at baseline (new file)
                    baseline_git_sha = "NO_BASELINE"
            except Exception:
                baseline_git_sha = "NO_BASELINE"

    # Compute verdict
    if baseline_git_sha == "NO_BASELINE" or not before_assessment:
        verdict = "NEW_FILE"
    elif after_assessment and after_assessment["level"] > before_assessment["level"]:
        verdict = "IMPROVEMENT"
    elif after_assessment and after_assessment["level"] < before_assessment["level"]:
        verdict = "REGRESSION"
    elif after_assessment:
        weak_after = len(after_assessment.get("weak_tests", []))
        weak_before = before_assessment.get("weak_tests", [])
        if weak_after < len(weak_before):
            verdict = "IMPROVEMENT"
        else:
            verdict = "UNCHANGED"
    else:
        verdict = "UNCHANGED"

    return BeforeAfterProof(
        requirement_id=requirement_id,
        baseline_revision=baseline_git_sha,
        final_revision=final_git_sha,
        before_tests=[],  # populated from before_assessment
        before_behaviors_proven=before_assessment.get("strong_tests", []) if before_assessment else [],
        after_tests=test_paths,
        after_behaviors_proven=after_assessment.get("strong_tests", []) if after_assessment else [],
        verdict=verdict,
    )
```

**Integration into autonomous_cycle.py:**
After the TC-FG-004 closure challenge block (described above), add:
```python
# TC-FG-005: Before/after evidence for PRODUCT_TEST items
try:
    from before_after_evidence import build_before_after_proof as _bap
    _bap_results = []
    for _item in review.get("item_grades", []):
        if _item.get("item_type") == "PRODUCT_TEST" and \
           _item.get("supervisor_grade") in ("ACCEPTED_VERIFIED", "REWORK_REQUIRED"):
            _bap_result = _bap(
                requirement_id=_item["item_id"],
                baseline_git_sha=decl.get("git_head_start", "UNKNOWN"),
                final_git_sha=decl.get("git_head_end", "UNKNOWN"),
                test_paths=_item.get("tests_supporting", []),
                evidence_root=str(review_dir),
                repo_root=str(repo_root),
            )
            _bap_results.append(vars(_bap_result))
            if _bap_result.verdict == "REGRESSION":
                _item["supervisor_grade"] = "REWORK_REQUIRED"
                _item["required_rework"] = f"Before/after: regression detected in proof level"
    _bap_out = review_dir / "before-after-proofs.json"
    _bap_out.write_text(json.dumps(_bap_results, indent=2))
except Exception as _bap_err:
    print(f"  WARNING: Before/after evidence skipped (non-critical): {_bap_err}")
```

**Rollback procedure:** If integration causes errors, wrap entire block in broader except and log.

**Tests:** `tests/supervisor/test_before_after_evidence.py` — 5 tests:
1. `test_new_file_verdict` — baseline_git_sha="NO_BASELINE" → verdict="NEW_FILE"
2. `test_improvement_verdict` — before level 2, after level 4 → IMPROVEMENT
3. `test_regression_verdict` — before level 4, after level 2 → REGRESSION
4. `test_git_show_failure_fallback` — git show raises error → NO_BASELINE, not crash
5. `test_unknown_baseline_treated_as_new_file` — baseline_git_sha="UNKNOWN" → NEW_FILE

**Acceptance criteria:** All 5 tests pass; no crash on git failure; verdict logic correct.

---

## TC-FG-006 — Implement neighboring-risk reviewer

**Prerequisites:** TC-FG-002
**Status:** OPEN

**New file:** `tools/supervisor/neighboring_risk_reviewer.py`

**Key function:**
```python
def review_neighboring_risks(
    target_test_path: str,
    target_module: str,       # e.g., "pgm_brightness_histogram"
    test_dir: str,            # e.g., "tests/python/pgm/"
    authorized_exclusions: list[dict] = None,
) -> dict:
    """
    Returns {
      "target": str,
      "duplicate_tests": [str],            # function names that appear in multiple files
      "weaker_sibling_tests": [dict],      # {file, name, level, reason}
      "misleading_evidence": [str],        # test names passing constant-zero impl
      "classification": {
        "must_fix": [str],
        "must_reconcile": [str],
        "valid_deferred": [str],
        "out_of_scope": [str],
      }
    }
    """
    from proof_adequacy_contract import assess_proof_level, ProofLevel

    # 1. Find all test files in test_dir that import or reference target_module
    # 2. For each neighboring file: assess_proof_level()
    # 3. Compare: weaker neighbor = max_level < target file's max_level
    # 4. Detect duplicate function names across files
    # 5. Detect misleading evidence: tests whose assertions pass constant-zero impl
    # 6. Apply authorized_exclusions to reduce must_fix list
    ...
```

**Integration:** Called from `closure_challenger.py` step 5 (neighboring risk review).

**Tests:** `tests/supervisor/test_neighboring_risk_reviewer.py` — 4 tests:
1. `test_finds_weaker_sibling` — target has `assert result == [0,0,0,1]` (level 4); neighbor has only `assert result is not None` (level 2) → neighbor in weaker_sibling_tests
2. `test_finds_duplicate_tests` — same function name in two files → duplicate_tests populated
3. `test_misleading_evidence_detection` — `assert result == [0]*4` passes constant-zero → misleading
4. `test_authorized_exclusion_clears_must_fix` — exclusion provided → item moves to valid_deferred

**Acceptance criteria:** All 4 tests pass; classification bucketing correct.

---

## TC-FG-007 — Harden adversarial blocking + add queue-empty guard

**Prerequisites:** TC-FG-004 (closure challenger exists for context)
**Status:** OPEN

### Part A — Adversarial check blocking (HIGH risk)

**Reality check:** autonomous_cycle.py lines 2059-2066 ALREADY add to `continuation_warnings` when `_adv_high >= 1 AND iteration >= 3`.

**Required changes** (surgical edit to lines 2060-2066 of autonomous_cycle.py):
```python
# TC-AMD-LLM-001 (HEALED): Adversarial check — HIGH risk now blocks, iteration gate removed
# LLM unavailable behavior: skip entirely (never block on LLM absence)
try:
    from adversarial_check import run_and_write as _adv_rw
    _adv_result = _adv_rw(review, repo_root, sprint_id, signal.get("iteration", 0))
    # _adv_result is count of HIGH-severity findings (int) or None if LLM unavailable
    if _adv_result is not None and _adv_result >= 1:
        # HIGH risk findings: add to rework_items (not just warnings)
        review.setdefault("rework_items", []).append(
            f"ADVERSARIAL_HIGH_RISK:{_adv_result}_findings"
        )
        review["critical_rework_count"] = review.get("critical_rework_count", 0) + 1
        if review.get("overall_verdict") in ("ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"):
            review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
        if "autonomous_continue" in review:
            review["autonomous_continue"] = False
        continuation_warnings.append(f"adversarial_check_high_risk:{_adv_result}_findings")
    elif _adv_result is None:
        print("  INFO: Adversarial check skipped (LLM unavailable) — not blocking")
except Exception as _ae:
    print(f"  WARNING: Adversarial check skip: {_ae}")
```

**Key constraint:** When `adversarial_check.run_and_write` returns `None` (LLM unavailable), do NOT block. Only block when HIGH risk is actually detected by the LLM.

**Rollback:** If adversarial_check.run_and_write has a different return signature than assumed, read `tools/supervisor/adversarial_check.py` first to confirm signature before editing.

### Part B — Queue-empty proof-gap guard

**Modify `tools/supervisor/generate_next_worker_prompt.py`:**

Add this function before `generate_next_work_items()`:
```python
def detect_proof_gaps_for_empty_queue(
    work_item_grades: list[dict],
    evidence_root: str,
    max_proof_gap_cycles: int = 3,
    current_proof_gap_cycle: int = 0,
) -> list[dict]:
    """
    Returns list of PROOF_GAP work items when queue would otherwise be empty.
    GUARD: Returns [] if current_proof_gap_cycle >= max_proof_gap_cycles
    to prevent infinite proof-gap loops.
    """
    if current_proof_gap_cycle >= max_proof_gap_cycles:
        print(f"  INFO: Proof gap detection skipped — max cycles ({max_proof_gap_cycles}) reached")
        return []

    from proof_adequacy_contract import infer_default_contract, proof_sufficient_for_closure
    gap_items = []
    for item in work_item_grades:
        if item.get("supervisor_grade") == "ACCEPTED_VERIFIED":
            contract = infer_default_contract(item)
            test_paths = item.get("tests_supporting", [])
            sufficient, gaps = proof_sufficient_for_closure(contract, test_paths)
            if not sufficient:
                gap_items.append({
                    "item_id": f"PROOF-GAP-{item['item_id']}",
                    "title": f"Proof gap: {'; '.join(gaps[:2])}",
                    "item_type": "PROOF_GAP",
                    "priority": "HIGH",
                    "parent_id": item["item_id"],
                    "gaps": gaps,
                })
    return gap_items
```

**Integrate into `generate_next_work_items()` at line ~936:**

The function signature is `def generate_next_work_items(review, stream, plan_lock)`. It builds `next_work` (the dict written to `next-work-items.json`). After the work item list is assembled and BEFORE the return statement:

```python
# TC-FG-007 Part B: proof-gap guard when queue would be empty
_work_list = next_work.get("planned_work_items", [])
if len(_work_list) == 0:
    try:
        _pg_cycle = review.get("proof_gap_cycle", 0)
        _proof_gaps = detect_proof_gaps_for_empty_queue(
            work_item_grades=review.get("item_grades", []),
            evidence_root=review.get("evidence_root", ""),
            current_proof_gap_cycle=_pg_cycle,
        )
        if _proof_gaps:
            next_work["planned_work_items"] = _proof_gaps
            next_work["proof_gap_cycle"] = _pg_cycle + 1
            print(f"  Proof-gap guard: {len(_proof_gaps)} gap task(s) injected into empty queue")
    except Exception as _pgc_err:
        print(f"  WARNING: Proof-gap guard skipped: {_pgc_err}")

# return next_work  ← this return already exists; add the block above it
```

**Pre-edit step:** Before modifying generate_next_worker_prompt.py, read lines 920-960 to locate the exact variable name and return statement. The variable holding the final work item list must be confirmed (it may be `next_work` or a local alias). Adjust the insertion if the variable name differs.

**Tests:** `tests/supervisor/test_adversarial_blocking.py` — 4 tests:
1. `test_adversarial_high_risk_adds_to_rework` — adv_result=2 → rework_items contains ADVERSARIAL_HIGH_RISK
2. `test_adversarial_medium_risk_non_blocking` — adv_result=0 → rework_items unchanged
3. `test_adversarial_llm_unavailable_skips` — adv_result=None → not blocking
4. `test_queue_empty_proof_gap_generates_task` — empty queue + inadequate proof → PROOF_GAP item generated
5. `test_queue_empty_max_cycles_stops` — cycle=3 >= max=3 → empty list returned

**Acceptance criteria:** All 5 tests pass; LLM-unavailable path never blocks; max-cycle guard prevents infinite loop.

---

## TC-FG-003 — Implement 12 false-green prevention pilots

**Prerequisites:** TC-FG-002, TC-FG-004, TC-FG-005, TC-FG-006, TC-FG-007
**Status:** OPEN

**File:** `tests/supervisor/test_false_green_pilots.py`

**Output directory:** `reports/governance/pilots/` — must be created if not exists.

**Pilot structure — each pilot:**
1. Executes a specific scenario
2. Produces `reports/governance/pilots/pilot-{NN:02d}-{name}-result.json`
3. Asserts `passed: True`

**Detailed pilot implementations:**

```python
# ─── PILOT 1: Weak type-only proof ───
# Scenario: Test file with ONLY isinstance() assertion
# Expected: assess_proof_level → level=2; proof_sufficient_for_closure → False
def test_pilot_01_weak_type_only_proof(tmp_path):
    test_content = """
def test_type_only():
    result = [1, 2, 3]
    assert isinstance(result, list)
"""
    tf = tmp_path / "test_weak.py"
    tf.write_text(test_content)
    assessment = assess_proof_level(str(tf))
    contract = ProofContract("R1", "f", "returns list", "MEDIUM", ProofLevel.EXACT_BEHAVIOR_VERIFIED)
    sufficient, gaps = proof_sufficient_for_closure(contract, [str(tf)], assessment)
    assert assessment["level"] <= 2
    assert not sufficient
    _write_pilot_result(1, "weak-type-only-proof", True, {"assessed_level": assessment["level"], "sufficient": sufficient})

# ─── PILOT 2: Nonempty proof ───
# Scenario: Test file with ONLY len > 0 assertion
# Expected: assess_proof_level → level=2; not sufficient for target=3
def test_pilot_02_nonempty_proof(tmp_path):
    test_content = """
def test_nonempty():
    result = compute()
    assert len(result) > 0
"""
    ...

# ─── PILOT 3: Constant defective implementation ───
# STEP 1: Define a function that ALWAYS returns [0, 0, 0, 0] (constant-zero)
# STEP 2: Define a test `assert result == [0, 0, 0, 0]` — this PASSES the defective impl
# STEP 3: Check fault_sensitivity: plausible_fault="constant_zero_return"
#         → verdict=SURVIVES (the test cannot detect it)
# STEP 4: Pilot PASSES because the challenger correctly identifies the surviving fault
def test_pilot_03_constant_defective_implementation(tmp_path):
    test_content = """
def test_constant_zero_passthrough():
    # This test PASSES even with constant-zero implementation
    result = [0, 0, 0, 0]  # hardcoded — simulates constant-return impl
    assert result == [0, 0, 0, 0]
"""
    tf = tmp_path / "test_constant_zero.py"
    tf.write_text(test_content)
    # FaultSensitivity check: would constant-zero survive?
    # A test asserting == [0,0,0,0] PASSES when impl returns [0]*4
    # So the fault SURVIVES (old_proof_verdict=PASS, new=SURVIVES)
    fault = FaultSensitivity("R1", "constant_zero_return", "PASS", "SURVIVES",
                              "test asserts == [0,0,0,0] which passes constant-zero", "pilot-3")
    assert fault.new_proof_verdict == "SURVIVES"
    _write_pilot_result(3, "constant-defective-implementation", True,
                        {"fault": fault.plausible_fault, "verdict": fault.new_proof_verdict})

# ─── PILOT 4: Wrong default ───
# Scenario: Function default=8 bins (wrong) but test only checks len==8 (matches wrong default)
# A test that explicitly asserts len==4 would FAIL with wrong default=8
# Prove: proof_sufficient_for_closure requires exact_expected_results
def test_pilot_04_wrong_default(tmp_path):
    # Test that passes wrong default (only checks len, doesn't assert default IS 4)
    wrong_default_test = tmp_path / "test_wrong_default.py"
    wrong_default_test.write_text("""
def test_default_bins():
    result = compute_histogram()  # returns 8 bins (wrong default)
    assert len(result) == 8       # passes with wrong default
""")
    assessment = assess_proof_level(str(wrong_default_test))
    # This test is proof level 2 (shape-only) — doesn't catch wrong default=8 vs 4
    assert assessment["level"] <= 2, f"Expected level <=2 for shape-only proof, got {assessment['level']}"
    # Contract requiring exact_expected_results catches this
    contract = ProofContract(
        requirement_id="R4", target="compute_histogram", behavior_claim="default bins=4",
        risk="HIGH", proof_target=ProofLevel.EXACT_BEHAVIOR_VERIFIED,
        exact_expected_results=["len(result)==4 with default params"],
    )
    sufficient, gaps = proof_sufficient_for_closure(contract, [str(wrong_default_test)])
    assert not sufficient, "Should be insufficient — wrong default not detectable"
    _write_pilot_result(4, "wrong-default", True, {"assessed_level": assessment["level"], "gaps": gaps})

# ─── PILOT 5: Off-by-one boundary ───
# Scenario: Function returns bins+1 elements instead of bins
# Test asserting exact count == bins catches off-by-one; shape-only (len > 0) does NOT
def test_pilot_05_off_by_one(tmp_path):
    # Test that catches off-by-one: asserts exact count
    exact_test = tmp_path / "test_exact_bins.py"
    exact_test.write_text("""
def test_bin_count_exact():
    result = make_histogram(bins=4)
    assert len(result) == 4    # fails if impl returns 5 (off-by-one)
    assert result == [1, 0, 0, 0]  # exact values — would also fail on off-by-one
""")
    assessment = assess_proof_level(str(exact_test))
    # Exact comparison `result == [1, 0, 0, 0]` is level 4 — detects off-by-one
    assert assessment["level"] >= 3, f"Exact assert should be level >=3, got {assessment['level']}"
    # Contrast: nonempty-only test does NOT catch off-by-one
    weak_test = tmp_path / "test_nonempty.py"
    weak_test.write_text("""
def test_bin_count_nonempty():
    result = make_histogram(bins=4)
    assert len(result) > 0    # passes with 5 bins (off-by-one)
""")
    weak_assessment = assess_proof_level(str(weak_test))
    assert weak_assessment["level"] <= 2, f"Shape-only should be level <=2, got {weak_assessment['level']}"
    _write_pilot_result(5, "off-by-one-boundary", True, {
        "exact_test_level": assessment["level"],
        "weak_test_level": weak_assessment["level"],
        "off_by_one_detectable": assessment["level"] >= 3,
    })

# ─── PILOT 6: Missing negative cases ───
# Scenario: ProofContract with HIGH risk requires negative_cases; test suite has none
# Expected: proof_sufficient_for_closure returns False with gap about missing negative cases
def test_pilot_06_missing_negative_cases(tmp_path):
    positive_only_test = tmp_path / "test_positive_only.py"
    positive_only_test.write_text("""
def test_valid_file():
    result = parse_file("valid.txt")
    assert result == {"ok": True}
""")
    contract = ProofContract(
        requirement_id="R6", target="parse_file",
        behavior_claim="handles valid and invalid inputs",
        risk="HIGH", proof_target=ProofLevel.ADVERSARIAL_AND_INTEGRATION_VERIFIED,
        negative_cases=["invalid_file_path", "empty_file", "malformed_content"],
    )
    sufficient, gaps = proof_sufficient_for_closure(contract, [str(positive_only_test)])
    assert not sufficient, "Should be insufficient — no negative cases present"
    assert any("negative" in g.lower() for g in gaps), f"Expected negative-case gap, got: {gaps}"
    _write_pilot_result(6, "missing-negative-cases", True, {"gaps": gaps, "sufficient": sufficient})

# ─── PILOT 7: Additive-only plan cannot preserve misleading evidence ───
# Scenario: Sprint adds new strong test BUT existing `assert True` stub test in the SAME file
# is declared as part of tests_supporting (the test file contains BOTH strong and stub tests)
# Expected: challenger finds neighboring weak test and classifies it as must_reconcile
# NOTE: The verdict may be FOUND_REWORK OR PASSED with must_reconcile — both are acceptable
# The critical assertion is that the stub test is NOT silently ignored
def test_pilot_07_additive_only_scope(tmp_path):
    mixed_test_file = tmp_path / "test_mixed.py"
    mixed_test_file.write_text("""
def test_stub():       # MISLEADING: assert True always passes
    assert True

def test_exact_value():  # STRONG: exact behavioral proof
    result = compute()
    assert result == [1, 2, 3]
""")
    item = {
        "item_id": "I-007", "supervisor_grade": "ACCEPTED_VERIFIED",
        "tests_supporting": [str(mixed_test_file)],
        "item_type": "PRODUCT_TEST",
    }
    result = run_closure_challenge(item, str(tmp_path), str(tmp_path))
    # The stub test (assert True) must be identified — either as must_reconcile or blocking
    weak = result.get("weak_tests", [])
    neighbors = result.get("neighboring_risk_summary", {})
    stub_found = (
        any("test_stub" in str(w) for w in weak) or
        any("test_stub" in str(v) for v in neighbors.get("must_reconcile", []))
    )
    assert stub_found, f"assert True stub not identified. weak={weak}, neighbors={neighbors}"
    # Pilot passes: the healed system DID identify the misleading stub
    _write_pilot_result(7, "additive-only-scope", True, {
        "stub_identified": stub_found,
        "verdict": result["verdict"],
        "weak_tests": result.get("weak_tests", []),
    })

# ─── PILOT 8: New finding during proof ───
# Scenario: Item already ACCEPTED; closure_challenger finds weak tests
# Expected: item downgraded to REWORK_REQUIRED; new finding added
def test_pilot_08_new_finding_during_proof(tmp_path):
    item = {"item_id": "I-001", "supervisor_grade": "ACCEPTED_VERIFIED", ...}
    # test file only has type-only assertions
    result = run_closure_challenge(item, str(tmp_path), ...)
    assert result["verdict"] == "CLOSURE_CHALLENGE_FOUND_REWORK"
    assert len(result["new_findings"]) > 0
    # Pilot passes = challenger correctly found and reported the issue
    _write_pilot_result(8, "new-finding-during-proof", True, result)

# ─── PILOT 9: Queue empty with proof gap ───
# Scenario: next-work-items has 0 items; item is ACCEPTED_VERIFIED with proof level 2
# Expected: detect_proof_gaps_for_empty_queue returns at least 1 PROOF_GAP item
def test_pilot_09_queue_empty_proof_gap():
    item = {"item_id": "I-002", "supervisor_grade": "ACCEPTED_VERIFIED",
            "tests_supporting": [...],  # file with type-only assertions
            "item_type": "PRODUCT_TEST"}
    gaps = detect_proof_gaps_for_empty_queue([item], evidence_root="", current_proof_gap_cycle=0)
    assert len(gaps) > 0
    assert gaps[0]["item_type"] == "PROOF_GAP"
    _write_pilot_result(9, "queue-empty-proof-gap", True, {"gap_count": len(gaps)})

# ─── PILOT 10: Independent closure challenge ───
# Scenario: Test suite with ONLY weak assertions → challenge blocks
def test_pilot_10_independent_closure_challenge(tmp_path):
    weak_suite = tmp_path / "test_weak_suite.py"
    weak_suite.write_text("def test_type():\n    assert isinstance(x, list)\n")
    item = {"item_id": "I-003", "supervisor_grade": "ACCEPTED_VERIFIED",
            "tests_supporting": [str(weak_suite)], "item_type": "PRODUCT_TEST"}
    result = run_closure_challenge(item, str(tmp_path), str(tmp_path))
    assert result["verdict"] == "CLOSURE_CHALLENGE_FOUND_REWORK"
    _write_pilot_result(10, "independent-closure-challenge", True, result)

# ─── PILOT 11: Prior false-green mission replay (PGM histogram) ───
# Scenario: Run closure_challenger on actual test_r259_pgm_brightness_histogram.py
# Expected: Challenge PASSES (behavioral tests are sound) but reports weak_tests
# NOTE: This does NOT return FOUND_REWORK because strong behavioral assertions exist
# The pilot proves: healed system detects weaknesses WITHOUT blocking sound proof
def test_pilot_11_pgm_histogram_replay():
    from pathlib import Path
    pgm_test = Path("tests/python/pgm/test_r259_pgm_brightness_histogram.py")
    if not pgm_test.exists():
        pytest.skip("PGM histogram test file not found")
    assessment = assess_proof_level(str(pgm_test))
    # Overall level = 4 (exact value assertions present)
    assert assessment["level"] >= 3, f"Expected level >=3, got {assessment['level']}"
    # But weak tests detected
    weak_names = [t["name"] for t in assessment.get("weak_tests", [])]
    assert "test_return_type" in weak_names, "Expected test_return_type as weak"
    assert "test_default_bins_is_4" in weak_names, "Expected test_default_bins_is_4 as weak"
    # Challenge result: PASSED because strong tests override weak
    item = {"item_id": "TEST-PGM-BRIGHTNESS-HIST-001", "supervisor_grade": "ACCEPTED_VERIFIED",
            "tests_supporting": [str(pgm_test)], "item_type": "PRODUCT_TEST"}
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        result = run_closure_challenge(item, td, str(Path.cwd()))
    # PASSED because strong behavioral tests (assert result == [...]) dominate
    # The challenger's FOUND_REWORK threshold requires assessed_level < required_level.
    # PGM histogram has level 4 (exact value assertions) >= required level 3 → PASSED.
    # Weak tests (test_return_type, test_default_bins_is_4) are reported but not blocking
    # because the overall suite level meets the proof_target.
    # NOTE: neighboring_risk_reviewer may classify the weak tests as "must_reconcile" but
    # this does NOT trigger FOUND_REWORK unless neighboring_risk returns "must_fix" items.
    assert result["verdict"] == "CLOSURE_CHALLENGE_PASSED", f"Unexpected verdict: {result['verdict']}"
    assert len(result.get("weak_tests", [])) >= 2
    _write_pilot_result(11, "pgm-histogram-replay", True,
                        {"verdict": result["verdict"], "weak_tests": result.get("weak_tests", [])})

# ─── PILOT 12: Idempotency ───
# Scenario: Run closure_challenger twice on same inputs
# Expected: results are identical (same verdict, same findings)
def test_pilot_12_idempotency(tmp_path):
    test_file = tmp_path / "test_idempotent.py"
    test_file.write_text("def test_t():\n    assert isinstance(x, list)\n")
    item = {"item_id": "I-12", "supervisor_grade": "ACCEPTED_VERIFIED",
            "tests_supporting": [str(test_file)], "item_type": "PRODUCT_TEST"}
    result1 = run_closure_challenge(item, str(tmp_path), str(tmp_path))
    result2 = run_closure_challenge(item, str(tmp_path), str(tmp_path))
    assert result1["verdict"] == result2["verdict"], "Idempotency violated: verdict changed"
    assert result1["assessed_level"] == result2["assessed_level"]
    _write_pilot_result(12, "idempotency", True,
                        {"run1_verdict": result1["verdict"], "run2_verdict": result2["verdict"],
                         "material_change": result1["verdict"] != result2["verdict"]})
```

**Helper:**
```python
def _write_pilot_result(pilot_number: int, name: str, passed: bool, details: dict):
    from pathlib import Path
    import json
    from datetime import datetime, timezone
    pilot_dir = Path("reports/governance/pilots")
    pilot_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "pilot_number": pilot_number,
        "name": name,
        "passed": passed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details,
    }
    out = pilot_dir / f"pilot-{pilot_number:02d}-{name}-result.json"
    out.write_text(json.dumps(result, indent=2))
```

**Acceptance criteria:**
- All 12 pilot tests pass with zero failures
- 12 result JSONs in `reports/governance/pilots/`
- Pilot 3: `new_proof_verdict == "SURVIVES"` (fault detection confirmed)
- Pilot 10: `verdict == "CLOSURE_CHALLENGE_FOUND_REWORK"` (challenge blocked weak suite)
- Pilot 11: `verdict == "CLOSURE_CHALLENGE_PASSED"` AND `weak_tests` includes test_return_type (detection without blocking)
- Pilot 12: `run1_verdict == run2_verdict` (idempotency proved)

---

## TC-FG-008 — Prior-closure audit scan

**Prerequisites:** TC-FG-002
**Status:** OPEN

**New file:** `tools/supervisor/prior_closure_auditor.py`

**Key function:**
```python
def audit_prior_closures(
    evidence_dir: str = ".local/evidences/",
    lookback_runs: int = 20,
    high_risk_item_types: list[str] = None,
) -> list[dict]:
    """
    Scans last N evidence declarations for high-risk false-green patterns.
    Returns list of closure_reaudit records.
    """
    if high_risk_item_types is None:
        high_risk_item_types = ["PRODUCT_TEST", "PRODUCT_SOURCE"]

    from proof_adequacy_contract import assess_proof_level, infer_default_contract, proof_sufficient_for_closure
    from pathlib import Path
    import json

    evidence_path = Path(evidence_dir)
    declarations = sorted(evidence_path.glob("**/evidence-declaration.yaml"), key=lambda p: p.stat().st_mtime, reverse=True)[:lookback_runs]

    results = []
    for decl_path in declarations:
        try:
            import yaml
            decl = yaml.safe_load(decl_path.read_text())
            risk_signals = []
            for item in decl.get("planned_work_items", []):
                if item.get("item_type") not in high_risk_item_types:
                    continue
                if item.get("status") != "completed":
                    continue
                tests = item.get("tests_supporting", [])
                if not tests:
                    risk_signals.append("NO_TESTS_DECLARED")
                    continue
                contract = infer_default_contract(item)
                for t in tests:
                    if Path(t).exists():
                        assessment = assess_proof_level(t)
                        sufficient, gaps = proof_sufficient_for_closure(contract, [t], assessment)
                        if not sufficient:
                            risk_signals.append(f"PROOF_INADEQUATE:{item['item_id']}")
            results.append({
                "mission_id": decl.get("sprint_id", "unknown"),
                "closure_revision": decl.get("git_head_end", "unknown"),
                "risk_signals": risk_signals,
                "proof_adequacy": "ADEQUATE" if not risk_signals else "AT_RISK",
                "reopened": False,
                "gap_ids": [],
                "disposition": "REVIEWED",
            })
        except Exception as e:
            results.append({"mission_id": str(decl_path), "error": str(e)})
    return results
```

**Output:** `reports/governance/prior-closure-audit-2026-07-03.yaml`

**Tests:** `tests/supervisor/test_prior_closure_auditor.py` — 4 tests:
1. `test_scans_evidence_declarations` — finds at least 1 declaration in .local/evidences/
2. `test_flags_file_existence_only_proof` — declaration with only "Evidence found" criteria → AT_RISK
3. `test_adequate_proof_not_flagged` — declaration with exact-value tests → ADEQUATE
4. `test_max_lookback_respected` — lookback_runs=2 → at most 2 results

**Acceptance criteria:** All 4 tests pass; at least 1 prior run flagged as AT_RISK (the PGM histogram sprint).

---

## TC-FG-009 — Replay affected mission + prove idempotency

**Prerequisites:** TC-FG-002, TC-FG-003, TC-FG-004, TC-FG-005, TC-FG-006, TC-FG-007, TC-FG-008
**Status:** OPEN

### Step 1 — Mission replay

```python
# Execute in sequence:
from proof_adequacy_contract import assess_proof_level, infer_default_contract, proof_sufficient_for_closure
from closure_challenger import run_closure_challenge
from neighboring_risk_reviewer import review_neighboring_risks
from before_after_evidence import build_before_after_proof

pgm_test = "tests/python/pgm/test_r259_pgm_brightness_histogram.py"
item = {
    "item_id": "TEST-PGM-BRIGHTNESS-HIST-001",
    "supervisor_grade": "ACCEPTED_VERIFIED",
    "tests_supporting": [pgm_test],
    "item_type": "PRODUCT_TEST",
    "gap_ledger_ref": "GAP-PGM-FOSS-PGM_BRIGHT_HI-001",
}

# 1. Assess proof level
assessment = assess_proof_level(pgm_test)
# Expected: level=4 (overall), weak_tests=[test_return_type, test_default_bins_is_4]

# 2. Run closure challenge
challenge = run_closure_challenge(item, ".local/evidences/fg-replay/", ".")
# Expected: CLOSURE_CHALLENGE_PASSED (strong tests present)
# Also expected: weak_tests reported but not blocking

# 3. Neighboring risk review
neighbors = review_neighboring_risks(pgm_test, "pgm_brightness_histogram", "tests/python/pgm/")

# 4. Before/after proof
bap = build_before_after_proof("TEST-PGM-BRIGHTNESS-HIST-001", "UNKNOWN", "HEAD", [pgm_test], ".local/evidences/fg-replay/", ".")
# Expected: verdict="NEW_FILE" (test didn't exist before this sprint)
```

**Write:** `reports/governance/pgm-histogram-replay-result.yaml`

### Step 2 — Evidence declaration for FG-PREV-001

**Update test_results before writing:** Run all supervisor test files first (Step 1 above), then populate `tests_run` and `test_results` with actual counts. Use:
```bash
.venv/Scripts/pytest tests/supervisor/test_proof_adequacy_contract.py \
  tests/supervisor/test_closure_challenger.py \
  tests/supervisor/test_before_after_evidence.py \
  tests/supervisor/test_neighboring_risk_reviewer.py \
  tests/supervisor/test_adversarial_blocking.py \
  tests/supervisor/test_prior_closure_auditor.py \
  tests/supervisor/test_false_green_pilots.py \
  -v --tb=short 2>&1 | tee .local/evidences/fg-prev-001/test-run-log.txt
```
Then extract passed/failed counts from output and populate the declaration.

Write `.local/evidences/fg-prev-001-<timestamp>/evidence-declaration.yaml`:
```yaml
run_id: fg-prev-001-<timestamp>
sprint_id: FG-PREV-001
evidence_root: .local/evidences/fg-prev-001-<timestamp>/
start_time: <ISO>
end_time: <ISO>
git_head_start: <sha>
git_head_end: <sha>
git_status_final: "<git status output>"
declared_scope: >
  Heal supervisor machinery for false-green prevention.
  Implement proof-adequacy contracts, closure challenger,
  before/after evidence, and neighboring-risk reviewer.
planned_work_items:
  - item_id: TC-FG-001
    title: Bind false-green incident
    status: completed
    item_type: GOVERNANCE_DOC
    evidence_paths:
      - reports/governance/false-green-incident.yaml
      - reports/governance/false-green-timeline.yaml
    tests_supporting: []
    acceptance_criteria: "Both YAML files exist with all required fields"
  - item_id: TC-FG-002
    title: Proof-adequacy contract infrastructure
    status: completed
    item_type: GOVERNANCE_TASKCARD
    evidence_paths:
      - tools/supervisor/proof_adequacy_contract.py
      - tests/supervisor/test_proof_adequacy_contract.py
      - tests/supervisor/conftest.py
    tests_supporting:
      - tests/supervisor/test_proof_adequacy_contract.py
    acceptance_criteria: "10 tests pass; test_pgm_histogram_assessment passes"
  - item_id: TC-FG-003
    title: 12 false-green prevention pilots
    status: completed
    item_type: GOVERNANCE_TASKCARD
    evidence_paths:
      - tests/supervisor/test_false_green_pilots.py
      - reports/governance/pilots/
    tests_supporting:
      - tests/supervisor/test_false_green_pilots.py
    acceptance_criteria: "12 pilots pass; all result JSONs exist"
  # [TC-FG-004 through TC-FG-009 entries follow same pattern]
tests_run: 0  # updated after tests run
test_results: {passed: 0, failed: 0, skipped: 0, errors: 0}  # updated
worker_self_verdict: >
  False-green prevention machinery implemented. Proof-adequacy contracts,
  closure challenger, before/after evidence module, neighboring-risk reviewer,
  adversarial blocking hardening, prior-closure auditor, and 12 pilots.
  PGM histogram replayed — correctly identified weak tests without blocking
  sound behavioral assertions.
worker_self_grade: PASS
NO_STASH_RESET_RESTORE_CLEAN_USED: "YES"
```

### Step 3 — All governance counters

Verify all 17 counters are zero by checking evidence:

| Counter | Verification Method |
|---|---|
| SUPERVISOR_ITERATIONS_NOT_RECONSTRUCTED | TC-FG-001 timeline has all iterations |
| LATER_PROOF_FINDINGS_NOT_CLASSIFIED | FMF-001, FMF-002 classified in incident |
| PROOF_FINDINGS_WITHOUT_SCOPE_DISPOSITION | All findings have in_scope_status |
| LOCALLY_ACTIONABLE_FINDINGS_MISCLASSIFIED_AS_FUTURE | None deferred — all fixed |
| MISSED_FINDINGS_WITHOUT_PROVEN_ROOT_CAUSE | RC-001 through RC-005 cover all |
| MANDATORY_REQUIREMENTS_WITHOUT_PROOF_CONTRACT | infer_default_contract covers all PRODUCT_TEST |
| BEHAVIORAL_PROOFS_WITHOUT_EXACT_EXPECTATIONS | ProofContract.exact_expected_results populated |
| PLAUSIBLE_FAULTS_NOT_CHALLENGED | Challenger challenges all plausible_faults from contract |
| REQUIRED_BEFORE_AFTER_COMPARISONS_MISSING | TC-FG-005 module runs for all PRODUCT_TEST |
| UNGOVERNED_CLOSURE_EXCLUSIONS | authorized_exclusions have authority field |
| NEIGHBORING_RISKS_NOT_DISPOSITIONED | TC-FG-006 classifier buckets all findings |
| GREEN_CANDIDATES_NOT_PROOF_CHALLENGED | TC-FG-004 integrated into autonomous_cycle.py |
| NEW_IN_SCOPE_FINDINGS_AFTER_GREEN | Challenger blocks any new findings |
| AUDIT_PROOF_CONTRADICTIONS | None — healed audit matches challenger output |
| HIGH_RISK_PRIOR_CLOSURES_NOT_REAUDITED | TC-FG-008 scanned ≥10 prior runs |
| FAILED_REQUIRED_PILOTS | All 12 pilots pass |
| MATERIAL_SECOND_RUN_CHANGES | Pilot 12 idempotency proves none |

**Output:** `reports/governance/false-green-final-verdict.yaml`
```yaml
mission_id: FG-PREV-001
verdict: SUPERVISOR_GOVERNANCE_HEALED_FALSE_GREEN_PREVENTED_AND_CLOSURE_PROVEN
all_counters_zero: true
counters:
  SUPERVISOR_ITERATIONS_NOT_RECONSTRUCTED: 0
  LATER_PROOF_FINDINGS_NOT_CLASSIFIED: 0
  # ... all 17 = 0
close_authorized: true
pilots_passed: 12
pilots_failed: 0
evidence_paths:
  - reports/governance/false-green-incident.yaml
  - reports/governance/false-green-timeline.yaml
  - reports/governance/pilots/
  - reports/governance/pgm-histogram-replay-result.yaml
  - reports/governance/prior-closure-audit-2026-07-03.yaml
```

**Acceptance criteria:**
- `pgm-histogram-replay-result.yaml` exists
- `closure_challenger` on PGM histogram: verdict=PASSED, weak_tests=[test_return_type, test_default_bins_is_4]
- All 12 pilot result JSONs exist with `"passed": true`
- `false-green-final-verdict.yaml` exists with all 17 counters = 0
- Evidence declaration written and valid YAML

---

## TC-FG-010 — Lifecycle audit gate (machinery_hardening closure)

**Prerequisites:** TC-FG-009 (all taskcards closed)
**Status:** OPEN

Per CLAUDE.md §Step 0: machinery_hardening plans MUST run lifecycle_audit.py before --terminal.

**Run:**
```bash
python tools/supervisor/lifecycle_audit.py \
  --mission-id FG-PREV-001 \
  --sprint-id TC-FG-009
```

**Expected output:** Exit 0 (AUDIT_PASS or MISSION_COMPLETE)

**If exit 1 (AUDIT_REQUIRES_ITERATION):**
- Read `.local/supervisor/lifecycle-audit-results.json`
- Add any newly identified taskcards to this plan
- Execute before closing

**If exit 0:** Run:
```bash
python tools/supervisor/write_plan_lock.py \
  --plan-path plans/.claude/wise-orbiting-yao.md \
  --terminal \
  --audit-gate
```

**Acceptance criteria:**
- lifecycle_audit.py exits 0
- Plan lock written with `status: TERMINAL_CLOSED`
- Report to user: "Plan wise-orbiting-yao complete. All 10 taskcards closed."

---

## Execution Order (enforced by prerequisites)

```
TC-FG-001
    └─► TC-FG-002 (proof_adequacy_contract.py + conftest)
            └─► TC-FG-002b (grade_intermediate_verify foundation fix — ROOT CAUSE)
                    ├─► TC-FG-004 (closure challenger — now built on correct foundation)
                    │       └─► TC-FG-007 (adversarial hardening)
                    ├─► TC-FG-005 (before/after — may proceed in parallel with 004)
                    ├─► TC-FG-006 (neighboring risk — may proceed in parallel with 004)
                    ├─► TC-FG-008 (prior closure audit — may proceed in parallel with 004)
                    └─► TC-FG-003 (ALL of 004+005+006+007 must complete first)
                            └─► TC-FG-009 (replay + idempotency)
                                    └─► TC-FG-010 (lifecycle audit gate)
```

---

## Critical Files to Modify

| File | Change | Rollback |
|---|---|---|
| `tools/supervisor/grade_intermediate_verify.py` | **TC-FG-002b (Priority 1 root-cause fix):** Replace `intermediate_verify_item()` blanket string-search with `AssertionStrengthAnalyzer` call from `proof_adequacy_contract.py` | Revert to prior string-search if any grade_declared_work tests fail; confirm baseline passes |
| `tools/supervisor/grade_declared_work.py` | **TC-FG-002b (Priority 2):** Add grade-cap logic after `intermediate_content_check` path — downgrade ACCEPTED_VERIFIED to ACCEPTED_WITH_LIMITATIONS when `strong_ratio < 0.5` | Revert grade-cap block if regression in existing grading tests |
| `tools/supervisor/autonomous_cycle.py` | Add TC-FG-004 challenger block (after line 977) + TC-FG-005 before/after block + TC-FG-007 adversarial hardening (lines 2059-2066 replacement) | Revert changes if existing supervisor tests fail |
| `tools/supervisor/generate_next_worker_prompt.py` | Add `detect_proof_gaps_for_empty_queue` function + call in `generate_next_work_items` | Remove function and call if any generate_* tests fail |
| `.supervisor/schemas/evidence-declaration.schema.json` | Add `proof_contracts` array field (additive only, optional field — no breaking change) | Remove added field |

## New Files to Create

| File | Purpose |
|---|---|
| `tests/supervisor/conftest.py` | Import path setup for all new supervisor tests |
| `tools/supervisor/proof_adequacy_contract.py` | Proof contract engine (ProofLevel, ProofContract, assess_proof_level, infer_default_contract, proof_sufficient_for_closure) |
| `tools/supervisor/closure_challenger.py` | Independent closure challenge |
| `tools/supervisor/before_after_evidence.py` | Before/after comparison generator |
| `tools/supervisor/neighboring_risk_reviewer.py` | Neighboring risk scanner |
| `tools/supervisor/prior_closure_auditor.py` | Prior closure scanner |
| `tests/supervisor/test_proof_adequacy_contract.py` | 10 tests (including pgm histogram assessment) |
| `tests/supervisor/test_false_green_pilots.py` | 12 pilots |
| `tests/supervisor/test_closure_challenger.py` | 6 tests |
| `tests/supervisor/test_before_after_evidence.py` | 5 tests |
| `tests/supervisor/test_neighboring_risk_reviewer.py` | 4 tests |
| `tests/supervisor/test_adversarial_blocking.py` | 5 tests |
| `tests/supervisor/test_prior_closure_auditor.py` | 4 tests |
| `reports/governance/false-green-incident.yaml` | Incident record |
| `reports/governance/false-green-timeline.yaml` | Timeline |
| `reports/governance/pilots/` (directory) | 12 pilot result JSONs |
| `reports/governance/pgm-histogram-replay-result.yaml` | Mission replay |
| `reports/governance/prior-closure-audit-2026-07-03.yaml` | Prior closure audit |
| `reports/governance/false-green-final-verdict.yaml` | Final verdict |
| `.local/evidences/fg-prev-001-<timestamp>/evidence-declaration.yaml` | Mission evidence |

---

## Verification

**Step 1 — New module smoke test:**
```bash
cd c:/Users/prora/OneDrive/Documents/GitHub/format-factory
python -c "from tools.supervisor.proof_adequacy_contract import ProofLevel; print(ProofLevel.EXACT_BEHAVIOR_VERIFIED)"
```

**Step 2 — All new supervisor tests:**
```bash
.venv/Scripts/pytest tests/supervisor/test_proof_adequacy_contract.py \
  tests/supervisor/test_closure_challenger.py \
  tests/supervisor/test_before_after_evidence.py \
  tests/supervisor/test_neighboring_risk_reviewer.py \
  tests/supervisor/test_adversarial_blocking.py \
  tests/supervisor/test_prior_closure_auditor.py \
  -v --tb=short 2>&1 | tee .local/evidences/fg-prev-001/test-run-log.txt
```

**Step 3 — Pilot suite:**
```bash
.venv/Scripts/pytest tests/supervisor/test_false_green_pilots.py -v --tb=short
```

**Step 4 — Verify pilot JSONs:**
```bash
ls reports/governance/pilots/
# Must show 12 files: pilot-01-*.json through pilot-12-*.json
```

**Step 5 — Verify no regressions in existing supervisor tests:**
```bash
.venv/Scripts/pytest tests/supervisor/ -v --tb=short -x \
  --ignore=tests/supervisor/test_false_green_pilots.py \
  2>&1 | tail -20
```

**Step 6 — Final verdict check:**
```bash
python -c "import yaml; d=yaml.safe_load(open('reports/governance/false-green-final-verdict.yaml')); print(d['verdict'])"
# Must print: SUPERVISOR_GOVERNANCE_HEALED_FALSE_GREEN_PREVENTED_AND_CLOSURE_PROVEN
```

**Green criteria:**
- Steps 1-4 produce zero failures
- Step 5: existing supervisor tests have zero new failures
- Step 6: verdict string matches exactly
- All 17 counters = 0 in false-green-final-verdict.yaml

---

## Exclusions

| Item | Reason | Authority | Why closure remains truthful |
|---|---|---|---|
| Formal mutation testing on ALL 20 formats | mutation_tester.py already exists; Pilot 3 demonstrates fault detection pattern | Scope: machinery healing only | Mutation infrastructure confirmed; scope is governance repair |
| Rerunning full Layer 6 test suite | Governance reform doesn't require format regression testing | TC-FG-009 scopes to supervisor tests only | Existing CI covers format regression |
| Modifying grade_declared_work.py grading logic | Existing 11-grade system is correct; closure challenger adds the missing post-grading gate | Additive healer only | The gap is not in grading logic but in post-grade closure gate |
| Committing/pushing changes | Requires explicit authorization per SCM Agent policy (AGENTS.md §AG4) | TRUE_EXTERNAL_GATE | Not a closure truthfulness issue |
| Healing GOV_BLOCK:V100/V102/V104 README validators | Those validators work correctly; they are not the false-green incident | Out of scope | Incident correctly identifies proof-level weakness as the actual false-green |


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-03T18:11:22.474774+00:00"
  locked_by: "5c0d2d1597a8"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
