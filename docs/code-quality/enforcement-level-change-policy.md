# Enforcement Level Change Policy

**Authority:** TC-CQGA2-R5B (mutable-exploring-hellman / CQGA-002)
**Effective:** 2026-07-12
**Replaces:** Ad-hoc practice (CI-pressure demotions in commit messages)

---

## Problem

V87 (`validate_dotnet_constant_return_public_api`) was demoted from `blocks_sprint=True`
to `blocks_sprint=False` in a CI-fix commit (`147b63fa`). No gap entry was created.
No policy rationale was recorded. The commit message ("readme freshness") was unrelated
to the actual change. This is a governance anti-pattern.

Root cause: there was no policy requiring documentation before demoting an enforcement level.
This document establishes that policy.

---

## Rules

### ELP-001: Gap Entry Required Before Demotion

Any change that reduces a validator's enforcement level — specifically:
- `blocks_sprint=True` → `blocks_sprint=False`
- `severity: FAIL` → `severity: WARN`
- Removing a validator from the `STRUCTURAL_GOV_BLOCKS` registry

...MUST be preceded by a gap ledger entry with:

```yaml
gap_id: CQG-NNN
validator_id: V<N>
change_type: ENFORCEMENT_LEVEL_DEMOTION
disposition: ACKNOWLEDGED_BY_DESIGN
rationale: "<why this demotion is intentional and safe>"
evidence: "<what compensating control exists>"
authorized_by: "<who approved — 'Babar Raza' for commercial controls, 'agent' for machinery>"
commit_reference: "<to be filled in at commit time>"
```

The gap entry must be committed in the **same commit** as the demotion.

### ELP-002: No CI-Pressure Demotions

A validator MUST NOT be demoted from FAIL to WARN solely because CI is failing.
CI failures are signals that the product has a real quality problem. The correct
response is to fix the product — not to weaken the validator.

If a CI failure is a false positive (validator fires incorrectly): fix the validator
logic, not its enforcement level. Create gap entry CQG-NNN with
`disposition: VALIDATOR_FALSE_POSITIVE_FIX`.

### ELP-003: STRUCTURAL_GOV_BLOCKS Are Immutable Without Architecture Review

Items in `tools/supervisor/governance_block_registry.py::STRUCTURAL_GOV_BLOCKS` produce
hard-stop continuation failures. Removing or renaming a structural block requires:
1. An architecture review section in the relevant plan
2. A gap entry with `disposition: STRUCTURAL_BLOCK_RETIRED` and evidence that the
   root cause the block was protecting against is permanently resolved
3. Update to `CLAUDE.md §GOV_BLOCK Exception`

---

## Acknowledged Historical Violations

| Gap ID | Validator | Violation | Status |
|--------|-----------|-----------|--------|
| CQG-017 | V87 `validate_dotnet_constant_return_public_api` | Demoted FAIL→WARN in CI-fix commit `147b63fa` without gap entry or rationale | RETROACTIVELY_ACKNOWLEDGED |

**CQG-017 retroactive gap entry:**
```yaml
gap_id: CQG-017
validator_id: V87
change_type: ENFORCEMENT_LEVEL_DEMOTION
disposition: ACKNOWLEDGED_BY_DESIGN
rationale: >
  V87 fires on all constant-return public methods including intentional read-only
  properties in .NET DTOs. The false-positive rate was blocking CI without providing
  actionable quality signal for the formats in scope at the time.
evidence: >
  V87 still fires at WARN level — detection is preserved; only the sprint-blocking
  behavior was reduced. Product quality for .NET constant-return is tracked via
  gate_executor.py G1 (source readiness) and via certification tests.
authorized_by: agent (machinery fix — no commercial impact)
commit_reference: "147b63fa (retroactive — policy not in place at time of change)"
```

---

## Related

- `tools/supervisor/governance_block_registry.py` — STRUCTURAL_GOV_BLOCKS canonical list
- `reports/product-quality/` — gap ledger location
- CLAUDE.md §GOV_BLOCK Exception — agent-facing operational summary
