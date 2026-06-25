# SAL Verification Plan
**Mission:** spec-auth-inv-20260625-001
**Date:** 2026-06-25

## Verification Gates

### VG-001: Fact Count Increase
**Trigger:** After any SAL parser addition or fact expansion
**Method:** `python -c "import json; d=json.loads(open('.local/spec-cache/sal-facts-latest.json').read()); print(d['spec_facts_total'])"`
**Expected:** Fact count increases monotonically with each SAL healing sprint

### VG-002: V13 Gate Hardened
**Method:** `pytest tests/supervisor/test_governance_validators.py -k spec_fact_refs_wired -v`
**Expected:** V13 returns FAIL (not WARN) when spec toolchain unavailable

### VG-003: Chain Status Improved
**Method:** Re-run this investigation mission after each SAL healing sprint
**Expected:** CHAIN_BROKEN_AT_SAL list shrinks as parsers are added

### VG-004: No V47 Regressions
**Method:** `pytest tests/supervisor/test_governance_validators.py -k spec_fact_refs_in_sal_output -v`
**Expected:** V47 PASS for all existing fact references (new facts don't break old ones)

### VG-005: Evidence Schema Backward Compatible
**Method:** Run `sprint_executor_validate.py --repair` on existing declarations
**Expected:** Existing declarations still validate after schema additions

## Pilot Rerun Checklist

After each healing sprint:
- [ ] VG-001: Fact count increased
- [ ] VG-002: V13 gate hardened (if H1 was executed)
- [ ] VG-003: Chain status report updated
- [ ] VG-004: V47 no regressions
- [ ] Full governance test suite passes (109+ tests)
