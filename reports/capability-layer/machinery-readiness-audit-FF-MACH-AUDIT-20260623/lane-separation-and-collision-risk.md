# Lane Separation and Collision Risk
**Plan:** sorted-purring-stardust | **Taskcard:** TC-SOL-001-04 | **Requirement:** REQ-SOL-001

## Lane Boundary Map

| Lane | Owns | May Read | Must NOT Touch |
|------|------|----------|---------------|
| MACHINERY | tools/supervisor/**, tools/backfill/**, tools/validators/** | src/** (read-only), shared/** | src/python/**/*, src/net/**/*, tests/python/**/*, tests/net/**/* |
| PRODUCT | src/python/**, src/net/**, tests/python/**, tests/net/** | tools/** (read-only), shared/** | tools/supervisor/**, .supervisor/** |
| INFRASTRUCTURE | .supervisor/**, registry/**, shared/** | everything | src/python/**, src/net/** |
| PLANNING | plans/**, reports/**, docs/** | everything | src/**, tools/supervisor/** (code) |

## Shared-File Risk Map

### HIGH RISK — Files touched by multiple lanes
| File | Touched By | Collision Risk |
|------|-----------|---------------|
| governance_validators.py | MACHINERY (V49-V56 additions), PRODUCT (evidence validation) | HIGH — sequential execution required |
| autonomous_cycle.py | MACHINERY (lane guard, SAL), PRODUCT (runtime) | HIGH — shared write lock needed |
| gap-ledger.json | MACHINERY (stub entries), PRODUCT (gap closure) | MEDIUM — append-only, no conflicts |
| source-structure-baseline.json | MACHINERY (cap updates), PRODUCT (new files) | MEDIUM — field-level isolation |

### LOW RISK — Lane-exclusive files
| File | Owner Lane | Risk |
|------|-----------|------|
| capability_compiler.py | MACHINERY | LOW — exclusive |
| failure_memory.py | MACHINERY | LOW — exclusive |
| tools/backfill/** | MACHINERY | LOW — new directory |
| src/python/{format}/** | PRODUCT | LOW — exclusive |

## Contamination/Collision Risk Matrix

| Scenario | Current State | Risk Level | Mitigation |
|----------|--------------|------------|------------|
| MACHINERY sprint modifies src/python/ | Undetected until Step 2e (post-grade) | HIGH | TC-MACH-LANE-001: Step 1b guard |
| PRODUCT sprint modifies tools/supervisor/ | Undetected until Step 2e (post-grade) | HIGH | TC-MACH-LANE-001: Step 1b guard |
| Two sprints modify governance_validators.py | File lock prevents parallel | MEDIUM | ECL-I sequential execution |
| Gap-ledger append during product sprint | Append-only, no structural conflict | LOW | JSON append is safe |
| SAL refresh during product sprint | Read-only SAL check | LOW | Non-blocking by design |

## Preventive Lane Guard Design
See [lane-guard-design.md](lane-guard-design.md) for full specification.

**Key points:**
- Injection at Step 1b (before grading)
- MACHINERY + src/ → exit 3 (LANE_CONFLICT_DETECTED)
- PRODUCT + tools/supervisor/ → exit 3
- Grace period via .supervisor/policies.yaml
- 5 test cases covering all scenarios

## Required Supervisor Changes
1. **autonomous_cycle.py:** Add check_lane_conflict() call at Step 1b
2. **.supervisor/policies.yaml:** Add lanes_grace_period_until field
3. **lane_enforcement_validator.py:** Keep existing post-hoc check as backup (belt + suspenders)
