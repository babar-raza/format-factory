# Risk Register — Canary Shadow Promotion

## Purpose

Risk assessment for promoting canary shadow components from shadow-only mode to
primary-with-fallback mode. Generated for CT-INV-001 (clever-tickling-island).

## Risk Assessment

| Risk ID | Description | Likelihood | Impact | Mitigation | Status |
|---------|-------------|------------|--------|------------|--------|
| RISK-CAN-001 | Shadow grader diverges from primary due to LLM non-determinism | HIGH | LOW | Log only; never change primary grade based on shadow | ACCEPTED |
| RISK-CAN-002 | Shadow continuation check incorrectly signals CONTINUE when primary says STOP | LOW | HIGH | Shadow result is logged only; primary verdict is authoritative | ACCEPTED |
| RISK-CAN-003 | canary_shadow_ingestor.py writing to control-index.db corrupts primary index | MEDIUM | MEDIUM | Shadow writes only to temp DB; production DB unchanged | MITIGATED |
| RISK-CAN-004 | Hash pre-computation for CAN-005 triggers file reads on PROMOTED_STABLE entries mid-sprint | LOW | MEDIUM | Read-only hashing; no file mutations | ACCEPTED |
| RISK-CAN-005 | Schema migration shadow (CAN-006) incorrectly predicts lock write status | LOW | HIGH | Lock write shadow is dry-run only; production lock write unchanged | ACCEPTED |
| RISK-CAN-006 | Canary adds 10-20s to sprint overhead per shadowed stage | HIGH | LOW | Canary runs async where possible; best-effort only | ACCEPTED |
| RISK-CAN-007 | Shadow divergence alerts create alert fatigue if high divergence frequency | MEDIUM | MEDIUM | Rate-limit alerts; group by divergence type | PLANNED |

## Promotion Criteria

Before promoting any canary from SHADOW-ONLY to PRIMARY-WITH-FALLBACK:

1. Shadow must run for >= 10 consecutive sprints without production impact
2. Divergence rate < 5% (measured over last 20 shadow runs)
3. Unit tests for the shadow component: >= 5 assertions covering PASS, FAIL, DIVERGE paths
4. Code review by at least 1 independent agent (adversarial verify)

## Current Status

| Component | Shadow Runs | Divergence Rate | Promotion Ready |
|-----------|-------------|-----------------|-----------------|
| validator_promotion.py | 0 | N/A | NO — needs 10+ runs |
| compilation_diff.py | 0 | N/A | NO — needs 10+ runs |
| grader_promotion.py | 0 | N/A | NO — needs 10+ runs |
| canary_shadow_ingestor.py | 0 | N/A | NO — needs 10+ runs |

## Decision Authority

Promotion from SHADOW-ONLY to PRIMARY-WITH-FALLBACK:
- Decision owner: Babar Raza (product authority)
- Evidence required: shadow run log + divergence analysis
- Blockers: none (not a TRUE_EXTERNAL_GATE for shadow operation itself)

## Risk Register FINALIZED: 2026-07-13
