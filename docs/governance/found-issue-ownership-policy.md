# Found-Issue Ownership Policy

**Policy ID:** FIO-POL-001
**Version:** 1.0
**Date:** 2026-07-04
**Mission:** FOUND-ISSUE-OWNERSHIP-MVP-001
**Status:** ACTIVE

---

## §1 — Purpose

This policy governs how the format-factory autonomous supervisor and its agents handle
**found issues** — any defect, failure, regression, or incorrect behavior discovered
during or after sprint execution.

The governing rule:

```
FOUND IT → OWN IT → INVESTIGATE IT → HEAL IT → VERIFY IT → PREVENT ITS RETURN
```

Every found issue must be registered, classified, traced to root cause, taskcarded for
repair, healed, and verified before it may be closed. Silent disposal — marking something
as pre-existing, unrelated, or outside scope without evidence — is **never acceptable**.

---

## §2 — Scope

This policy applies to:
- All autonomous sprint executions
- All worker declarations in `.local/evidences/`
- All validator runs via `governance_validator_runner.py`
- All human-initiated repairs in the repository

---

## §3 — issue_types

Every found issue must be classified as exactly one of:

| Type | Description |
|---|---|
| `failed_test` | A test that was passing and now fails, or was never passing |
| `broken_fixture` | A test fixture, parametrize list, or data file that references invalid state |
| `missing_fixture` | Expected test infrastructure is absent |
| `incorrect_implementation` | Code that compiles/runs but produces wrong output |
| `stale_output` | Generated artifact that no longer reflects its source |
| `schema_violation` | YAML/JSON/Python structure deviates from declared schema |
| `import_error` | A Python or .NET import fails at runtime |
| `package_failure` | An installed package is missing, wrong version, or inconsistent |
| `regression` | A previously-passing capability no longer works |
| `dead_code` | Code that can never be reached or has no consumers |
| `unsupported_claim` | A declaration or comment asserts something not evidenced in code |
| `missing_provenance` | No traceable origin for a spec fact, QName, or domain model field |

---

## §4 — lifecycle_states

Every issue in `registry/found-issue-register.yaml` must advance through this lifecycle:

```
discovered → classified → taskcarded → in_repair → verified → closed
```

Or reach one of the valid final states via disposition (see §6).

| State | Meaning |
|---|---|
| `discovered` | Issue logged; not yet root-caused |
| `classified` | issue_type, severity, and reproducibility assigned |
| `taskcarded` | A healing taskcard exists and is referenced via `healing_taskcard_id` |
| `in_repair` | Active repair work is in progress |
| `verified` | Repair complete; test or evidence confirms resolution |
| `closed` | Issue closed; disposition set to one of the 6 valid values |
| `invalid` | Disposition = INVALID_FINDING_WITH_PROOF |
| `duplicate` | Disposition = DUPLICATE_OF_ACTIVE_ISSUE |
| `governed_exclusion` | Disposition = VALID_GOVERNED_EXCLUSION |
| `blocked_external` | Disposition = BLOCKED_TRUE_EXTERNAL_DEPENDENCY |
| `waiting_gate_11` | Disposition = WAITING_VALID_GATE_11_AUTHORIZATION |

---

## §5 — priority_map

| Priority | Label | Description |
|---|---|---|
| `P0` | CRITICAL | Blocks sprint immediately; data loss or security risk |
| `P1` | HIGH | Blocks autonomous continuation; governance validator FAIL |
| `P2` | MEDIUM | Fails tests in CI; causes regressions in governed suite |
| `P3` | LOW | Advisory; WARN-level; does not block sprint |
| `P4` | INFORMATIONAL | Tracked for visibility only; no repair urgency |

---

## §6 — valid_dispositions

Exactly 6 valid closing dispositions for issues in `registry/found-issue-register.yaml`:

### HEALED_AND_VERIFIED
The defect was repaired, a test or evidence confirms the fix, and the issue is closed.
**Requires:** `verification_verdict` field with evidence path.

### DUPLICATE_OF_ACTIVE_ISSUE
This issue is identical to an existing open issue. The duplicate is closed; the canonical
issue continues.
**Requires:** `duplicate_of: FI-NNN` field pointing to the canonical issue.

### INVALID_FINDING_WITH_PROOF
The reported behavior is actually correct, or the issue does not exist.
**Requires:** Written proof in `evidence` field explaining why the finding was invalid.

### VALID_GOVERNED_EXCLUSION
The behavior is intentionally unsupported, the artifact is outside governance scope,
or an explicit governance exception has been granted.
**Requires:** Reference to governing policy section or exception grant document.
**NOT valid for:** LOC cap violations in product files (those are always governed).
**NOT valid for:** Test failures that block autonomous continuation.

### BLOCKED_TRUE_EXTERNAL_DEPENDENCY
Repair requires action from an external party (e.g., package maintainer, infrastructure
team) that is genuinely outside the agent's scope.
**Requires:** Named blocker, evidence that internal options are exhausted.

### WAITING_VALID_GATE_11_AUTHORIZATION
Issue resolution requires Gate 11 commercial execution approval by Babar Raza.
**Requires:** Gate 11 requirement clearly stated in `evidence`.

---

## §7 — invalid_dismissals

The following dismissals are **categorically invalid** and will be caught by V142:

| Invalid Dismissal | Why It Is Rejected |
|---|---|
| `pre-existing` | Age does not exempt an issue from ownership |
| `unrelated` | Proximity does not excuse responsibility |
| `not caused by me` | Causal distance does not transfer ownership |
| `outside current task` | Found issues belong to the finder regardless of task scope |
| `follow-up recommended` | Deferred without a taskcard is abandonment |
| `warning only` | WARN-level issues still require classification |
| `probably harmless` | Probability without evidence is not a disposition |
| `no time` | Workload is not a valid governance disposition |

---

## §8 — existing_infrastructure

Agents MUST use the following existing infrastructure for found-issue management:

| Asset | Path | Purpose |
|---|---|---|
| Found-issue register | `registry/found-issue-register.yaml` | Primary lifecycle tracking |
| Root-cause register | `registry/root-cause-register.yaml` | Systemic root-cause analysis |
| Fixture analysis register | `registry/fixture-analysis-register.yaml` | Broken/stale fixture tracking |
| Blast radius register | `registry/blast-radius-register.yaml` | Impact scope analysis |
| Failure memory store | `tools/supervisor/failure_memory.py` | Persistent failure capture |
| Rework orchestrator | `tools/supervisor/rework_orchestrator.py` | Healing loop management |
| Bounded repair engine | `tools/supervisor/bounded_repair_engine.py` | Max-attempt enforcement |
| Known-failure ledger | `registry/known-failure-ledger.yaml` | Pre-existing issue baseline |
| Validator runner | `tools/supervisor/governance_validator_runner.py` | V139-V142 enforcement |

---

## §9 — Enforcement Validators

| Validator | ID | Scope | blocks_sprint |
|---|---|---|---|
| found_issue_register_present | V139 | When tests fail, register must have entries | WARN |
| issue_accounting_reconciles | V140 | All register statuses must map to accounting buckets | FAIL |
| no_prose_only_findings | V141 | Dismissal language in verdict or notes | WARN |
| validate_invalid_ownership_disposition | V142 | No issue may use an invalid_dismissal as disposition | FAIL |

---

## §10 — Command

Use `/found-issue-ownership` (`.claude/commands/found-issue-ownership.md`) to execute
the found-issue capture, classification, healing, and closure workflow.
