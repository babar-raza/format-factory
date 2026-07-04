# /found-issue-ownership

## Purpose

Governed workflow for capturing, classifying, root-causing, healing, and closing
issues discovered during or after sprint execution.

**Rule:** `FOUND IT → OWN IT → INVESTIGATE IT → HEAL IT → VERIFY IT → PREVENT ITS RETURN`

## Trigger Conditions

Use this command when you discover any of:
- A failing or newly-broken test
- A `FileNotFoundError` or `ImportError` in test execution
- A fixture or parametrize list referencing a deleted/renamed file
- A file exceeding its `baseline_loc_cap`
- A domain model class missing `spec_qname: ClassVar[str]`
- An unstaged or uncommitted change that causes test failures
- A governance validator WARN or FAIL
- Contradictory evidence in declarations

## Required Inputs

- `issue_id`: Next available `FI-NNN` from `registry/found-issue-register.yaml`
- `issue_type`: One of the 12 types in `docs/governance/found-issue-ownership-policy.md §3`
- `severity`: P0–P4
- `observed_behavior`: What actually happens
- `expected_behavior`: What should happen
- `affected_paths`: List of files involved

## Workflow Steps

### Step 1 — Capture
Write a new entry to `registry/found-issue-register.yaml` with:
- `status: discovered`
- `discovered_at: <ISO8601>`
- `discovering_task_id: <current mission or sprint id>`
- All required fields above

### Step 2 — Classify
Assign `issue_type`, `severity`, `reproducibility`. Update `status: classified`.

### Step 3 — Root Cause
Investigate to find the first failing boundary. If systemic, write entry to
`registry/root-cause-register.yaml` and set `root_cause_id` on the issue.

### Step 4 — Blast Radius
For regressions and schema violations, write `registry/blast-radius-register.yaml`
entry. Scan all surfaces using the `search_pattern`.

### Step 5 — Taskcard
Create a healing taskcard (or reference existing plan entry). Set
`healing_taskcard_id` and `status: taskcarded`.

### Step 6 — Heal
Execute the repair. Set `status: in_repair` at start. After repair, run the
specific test or validator to confirm fix.

### Step 7 — Verify
Run the relevant test. On PASS: set `status: verified`, `verification_verdict`
with evidence path.

### Step 8 — Close
Set `status: closed` and `disposition` to one of the 6 valid values:

| Disposition | When to use |
|---|---|
| `HEALED_AND_VERIFIED` | Repair confirmed by passing test |
| `DUPLICATE_OF_ACTIVE_ISSUE` | Same defect as existing FI-NNN |
| `INVALID_FINDING_WITH_PROOF` | Behavior is actually correct (with written proof) |
| `VALID_GOVERNED_EXCLUSION` | Intentionally unsupported; outside governance scope |
| `BLOCKED_TRUE_EXTERNAL_DEPENDENCY` | Requires external party action |
| `WAITING_VALID_GATE_11_AUTHORIZATION` | Requires Babar Raza Gate 11 sign-off |

## Invalid Dispositions (V142 blocks these)

Never use as the sole disposition:
- `pre_existing`, `unrelated`, `not_caused_by_me`, `ignored`, `outside_current_task`

## Integration

- Register: `registry/found-issue-register.yaml`
- Root causes: `registry/root-cause-register.yaml`
- Fixtures: `registry/fixture-analysis-register.yaml`
- Blast radius: `registry/blast-radius-register.yaml`
- Governance validators: V139 (register presence), V140 (accounting), V141 (no prose dismissal), V142 (valid disposition)
- Policy: `docs/governance/found-issue-ownership-policy.md`
