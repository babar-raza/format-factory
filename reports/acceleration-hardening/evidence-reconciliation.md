# Evidence-to-Implementation Reconciliation

**Sprint:** FORMAT-FACTORY-ACCELERATION-HARDENING-IV-AND-CONSUMPTION-CONTRACT-001
**Date:** 2026-06-04

---

## What Was Claimed vs. What Was Built

### Claimed: 4 directly-consumable Mainstream packets
### Found: 4 packets with fixture_error and missing schema fields

| Packet | Claimed Status | Actual Status | Blocking? |
|--------|---------------|---------------|-----------|
| FODS CSV | directly_consumable | fixture_error in ai_rationale; test_plan_path=null; missing 8 fields | YES |
| FODT Markdown | directly_consumable | fixture_error in ai_rationale; test_plan_path=null; missing 8 fields | YES |
| Netpbm export | directly_consumable | fixture_error in ai_rationale; test_plan_path=null; missing 8 fields | YES |
| SYLK CSV | directly_consumable (foss) | fixture_error in ai_rationale; test_plan_path=null; missing 8 fields | YES |

**Root cause:** Packets were generated using system Python which lacks `pydantic`. The gateway call
inside `_gateway_rationale()` catches the ImportError and writes `[fixture_error]`. The packet
still writes to disk but the ai_rationale is degraded.

**Secondary issue:** `test_plan_path` uses pattern `{capability_path.replace('.', '-')}-test-plan.json`
but actual files are named `{format}-{short_gap}-test-plan.json` (e.g. `fods-dogfood-csv-test-plan.json`).

### Claimed: 58 tests passing
### Found: 58 tests passing — CONFIRMED

### Claimed: All 8 tools import OK
### Found: System Python: pydantic missing (caught by fixture_error). Venv Python: all OK.

---

## Non-Blocking Evidence Caveats

| Item | Caveat | Impact |
|------|--------|--------|
| agentic_low_risk passes | status=skipped (correct per spec) | Pre/mid/final passes non-authoritative |
| Source patterns: corpus_empty may be true for some formats | ai_pattern_summary uses fixture if corpus empty | Low impact — lexical patterns still present |
| Healing docs: 11 files written | Not schema-validated | Advisory only |

---

## Blocking Verification Gaps

| Gap | Severity | Fix in Lane |
|-----|----------|-------------|
| ai_rationale = [fixture_error] in all 4 packets | BLOCKING | B |
| test_plan_path = null in all 4 packets | BLOCKING | B/C |
| 8 schema fields missing from all packets | BLOCKING | C |
| No deterministic replay proof | NON-BLOCKING | D |
| No Skills/Supervisor compatibility packets | NON-BLOCKING | E |
