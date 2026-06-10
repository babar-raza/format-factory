# ABW No-Public-Spec Downgrade — TCA-FULL-012

## Spec Availability Check

- abisource.com: BLOCKED_SERVER_DOWN (server not responding at time of investigation)
- No formal ISO/OASIS specification for ABW format
- No DTD/XSD schema available
- `exception_classification: no_public_spec_available` — CONFIRMED CORRECT

## ABW Cache State

Spec cache check: .local/spec-cache/abw/ — has spec-index.yaml indicating BLOCKED_SERVER_DOWN
No spec document cached locally for ABW.

## Classification: no_public_spec_available (CORRECT)

- ABW is an AbiWord XML format with no retrievable public spec
- `no_public_spec_available` is the correct classification
- This is in DEBT_ONLY_EXCEPTIONS — ABW cannot claim READINESS or RELEASE_GATE

## Can ABW Claim Readiness Without Authority?

**NO.** Validator result for READINESS + no_public_spec_available:
→ REJECTED with grade_impact: reject
→ "debt/grace classification cannot be used with item_type=READINESS"

(Verified in existing tests: test_no_public_spec_available_cannot_claim_release_gate)

## Pilot Declaration Test

- PRODUCT_SOURCE + `no_public_spec_available` → ACCEPTED with authority debt
- READINESS + `no_public_spec_available` → REJECTED ✓
- RELEASE_GATE + `no_public_spec_available` → REJECTED ✓

## Proof Level Classification

| Component | Present? |
|-----------|----------|
| Spec document | ✗ (no public spec available) |
| Schema (XSD/DTD) | ✗ |
| Verified facts | ✗ |
| Code | ✓ (src/python/abw/abw_codec.py implemented) |
| Tests | ✓ (tests/python/abw/ — multiple test files) |

**Proof Level: P0** — no authority document accessible; all code is legacy backfill

## Current ABW in poc-targets.yaml

ABW has `authority_status` not set → defaults to ALLOWED via product_task_selector.
If ABW should be blocked from new product work: add `authority_status: BLOCKED_MISSING_SPEC` to poc-targets.yaml entry.
This is a governance decision — not done autonomously.

## Honest Assessment

ABW has working code and passing tests but no accessible spec authority.
All current ABW code is pre-existing backfill work.
No new ABW product source changes should claim spec authority without `no_public_spec_available` exception.
Readiness/release gating is correctly blocked.
