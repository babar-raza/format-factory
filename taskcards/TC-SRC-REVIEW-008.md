# TC-SRC-REVIEW-008: Governance Validators V43/V44 and Pilot Audit Gate

**Lane**: SRC-REVIEW
**Status**: backlog
**Owner**: autonomous agent
**Prerequisites**: TC-SRC-REVIEW-007 COMPLETE
**item_type**: GOVERNANCE_ASSET
**gap_ledger_ref**: GAP-QNAME-FODT-006

## Objective

Verify V43 and V44 governance validators pass against the pilot state. Produce the machine-readable
fodt-pilot-audit.md that is the gate before FODS pilot can begin.

## Execution Steps

1. Run `python tools/validators/source_structure_validator.py` → PASS
2. Run existing governance validator suite → V43 PASS, V44 WARN (expected)
3. Create `reports/spec-registry/fodt-pilot-audit.md` with:
   - Registry: 9/9 QNames seeded → architecture_only; 0 implemented (expected)
   - Source manifests: 5 classes mapped (3 Python + 2 .NET; FodtDocument as public_facade)
   - Python stubs: 8 created; 4 __init__.py files confirmed
   - compat.py: bootstrap mode (imports from models.py) — confirmed by test_compat_bootstrap PASS
   - Tests: all passing
   - Cross-language parity: 8/9 PASS; 1 PARTIAL (office:body by design)
   - Idempotency: generate_canonical_stubs.py run twice → identical output
   - Governance: V43 PASS, V44 WARN (expected), V35 PASS
   - Overall gate: PASS or FAIL

## Gate Logic

- Any FAIL (not PARTIAL) item in parity check → FAIL gate, retry from Phase 1
- V43 FAIL → FAIL gate
- V44 WARN → OK (expected in bootstrap)
- All else → PASS gate

## Validation

`reports/spec-registry/fodt-pilot-audit.md` exists with OVERALL: PASS verdict

## Evidence Required

- fodt-pilot-audit.md content
- V43 validator output showing PASS

## Completion Criteria

Audit report exists with OVERALL PASS; ready to proceed to FODS pilot
