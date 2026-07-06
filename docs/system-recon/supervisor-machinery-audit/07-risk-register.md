# 07 - Risk Register

## R-001: Consolidation Breaks Dynamic Invocation Path

| Field | Value |
|---|---|
| risk_id | R-001 |
| title | Removing "zero-import" files may break subprocess/CLI invocation paths |
| category | consolidation_risk |
| related_problems | P-003, P-005 |
| likelihood | MEDIUM |
| impact | HIGH — sprint execution fails silently |
| mitigation | Before quarantining any file: search all YAML, JSON, MD, and shell files for the filename; check CLAUDE.md, AGENTS.md, .claude/commands/, .supervisor/skill-registry.yaml, CI workflows |
| evidence | 142 files have `if __name__ == '__main__'` guards; 56 subprocess call sites in tools/supervisor/; 50 skill-registry references to supervisor/ |

## R-002: Governance Validator Restructuring Creates Regression

| Field | Value |
|---|---|
| risk_id | R-002 |
| title | Restructuring 18 validator files may break test mappings and import paths |
| category | consolidation_risk |
| related_problems | P-004 |
| likelihood | MEDIUM |
| impact | HIGH — governance validation silently stops running validators |
| mitigation | Dual execution: run old + new validator structure and compare results before switching; test_governance_validators.py (3,270 LOC) must be updated simultaneously |
| evidence | governance_validator_runner.py discovers validators dynamically from files matching governance_validators*.py pattern |

## R-003: Capability Map Regeneration Non-Determinism

| Field | Value |
|---|---|
| risk_id | R-003 |
| title | Moving capability maps to gitignored build output may produce different maps across environments |
| category | consolidation_risk |
| related_problems | P-007 |
| likelihood | LOW |
| impact | MEDIUM — different environments see different capabilities |
| mitigation | Verify deterministic regeneration by comparing outputs from two independent runs at same commit |

## R-004: Report Archival Breaks Historical References

| Field | Value |
|---|---|
| risk_id | R-004 |
| title | Archiving old reports may break references from plans, evidence declarations, and MEMORY.md |
| category | consolidation_risk |
| related_problems | P-006 |
| likelihood | HIGH |
| impact | LOW — historical references are informational, not functional |
| mitigation | Only archive reports older than a threshold (e.g., 30 sprints); keep a manifest of archived reports; don't delete, compress to separate branch |

## R-005: Machinery Consolidation Slows Product Progress

| Field | Value |
|---|---|
| risk_id | R-005 |
| title | Time spent on machinery consolidation diverts from product deepening |
| category | opportunity_cost |
| related_problems | All |
| likelihood | HIGH |
| impact | MEDIUM — each consolidation sprint is one fewer product sprint |
| mitigation | Prioritize highest-ROI consolidation (P-002 evidence writers = 11K LOC savings for minimal risk); defer complex consolidation (P-004 validators) until low-hanging fruit proves the approach |

## R-006: Accretive Growth Resumes After Consolidation

| Field | Value |
|---|---|
| risk_id | R-006 |
| title | Without structural prevention, the same growth patterns will recur |
| category | regrowth |
| related_problems | P-003, P-004, P-006 |
| likelihood | HIGH |
| impact | MEDIUM — consolidation benefits erode over time |
| mitigation | Implement regrowth prevention: file count budget per directory, duplicate-name detection in CI, migration-completion checks, deprecation policy |

## R-007: Investigation Conclusions Based on Static Analysis Only

| Field | Value |
|---|---|
| risk_id | R-007 |
| title | All "SUSPECTED_GHOST" classifications are based on static grep analysis, not runtime tracing |
| category | investigation_limitation |
| related_problems | P-003, P-005 |
| likelihood | MEDIUM |
| impact | HIGH — false ghost classification leads to removing active code |
| mitigation | Add observability (call tracing) before any removal; run characterization tests; check git log for recent invocations |

## Risk Summary

| Risk | Likelihood | Impact | Priority | Mitigation Effort |
|---|---|---|---|---|
| R-001 Dynamic invocation | MEDIUM | HIGH | P1 | Low (search before remove) |
| R-002 Validator regression | MEDIUM | HIGH | P1 | High (dual execution) |
| R-005 Opportunity cost | HIGH | MEDIUM | P2 | Low (prioritize ROI) |
| R-006 Regrowth | HIGH | MEDIUM | P2 | Medium (CI checks) |
| R-007 Static analysis only | MEDIUM | HIGH | P1 | Medium (add observability) |
| R-003 Map non-determinism | LOW | MEDIUM | P3 | Low (verify) |
| R-004 Report references | HIGH | LOW | P3 | Low (threshold) |
