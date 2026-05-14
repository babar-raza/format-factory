---
document_type: template_model_report
sprint: CONWAY-R1R2-ACCELERATED-FOUNDATION-SWARM-001
lane: G
title: "Evidence Contract Template Model Report"
date: "2026-05-13"
visibility: internal
publish_allowed: false
---

# Evidence Contract Template Model Report — Lane G

**Sprint:** CONWAY-R1R2-ACCELERATED-FOUNDATION-SWARM-001
**Date:** 2026-05-13

---

## Summary

`templates/evidence/base-commercial-sprint.contract.yaml` has been created as a reusable
template model. No generator tool was created. Existing contract system is preserved.

**EVIDENCE_CONTRACT_TEMPLATE_STATUS: COMPLETE**

---

## Section 1: What Was Created

**File:** `templates/evidence/base-commercial-sprint.contract.yaml`

**Design pattern:** Template (fill-in-the-blank), not a generator tool.
Sprint coordinators instantiate this template by replacing `{{PLACEHOLDER}}` values.

**Template sections:**
1. **Template header** — sprint_id, format_id, date, coordinator
2. **Authority chain metadata** — AGENTS.md sections, GOVERNANCE.md sections, master_plan_version
3. **Requirements pipeline metadata** — requirements_authority_status, accepted_count, verifier_result, iv_status, stale_check
4. **Evidence bundle configuration** — inherits from base-run v1.4; adds commercial-sprint semantic checks
5. **AI usage metadata** — model_tool, session_type, ai_proposal_count
6. **Semantic checks** — requirements_schema_validation_result, verifier_review_present, iv_status, accepted_requirement_ids_referenced, no_stale_requirements

---

## Section 2: Relationship to Existing Contract System

| Existing component | Status | Relationship |
|-------------------|--------|--------------|
| `tools/evidence/contracts/base-run.yaml` | PRESERVED | Template inherits its philosophy |
| `tools/evidence/build_evidence_bundle.py` | PRESERVED | Still the authoritative builder |
| `tools/evidence/validate_evidence_bundle.py` | PRESERVED | Still validates all bundles |
| `tools/evidence/contracts/gate-approval.yaml` | PRESERVED | Unchanged |
| `tools/evidence/contracts/independent-verification.yaml` | PRESERVED | Unchanged |

**No existing contracts were modified. No generator tool was created.**

---

## Section 3: Semantic Checks Added

The commercial-sprint template adds checks beyond base-run:

| Check | Required value | Purpose |
|-------|---------------|---------|
| `requirements_schema_validation_result` | PASS | Confirms validator ran before sprint |
| `verifier_review_present` | true | Confirms verifier-review.yaml exists |
| `iv_status` | ESTABLISHED | Confirms DEC-034 IV completed |
| `accepted_requirement_ids_referenced` | >= 1 | Confirms requirements consumed |
| `no_stale_requirements` | manual attestation | Manual until automation exists |

---

## Section 4: Future Work

These checks are currently manual attestations in the template:
- `no_stale_requirements` — will become automated when `--check-stale` is fully implemented
- `verifier_review_hash` — should reference hash of verifier-review.yaml for tamper detection

---

**LANE_G_STATUS: COMPLETE**
**CONTRACT_TEMPLATE_CREATED: YES**
**GENERATOR_TOOL_CREATED: NO (by design — template model only)**
**EXISTING_CONTRACT_SYSTEM: PRESERVED**
