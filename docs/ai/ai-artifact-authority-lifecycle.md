# AI Artifact Authority Lifecycle

**Version:** 1.0
**Date:** 2026-05-18
**Status:** PLAN — Implementation not yet authorized
**Authority:** docs/ai/ai-platform-operating-model.md

---

## 1. Purpose

Define the state machine governing how AI-generated artifacts progress from draft to authoritative. No AI artifact may skip directly to authoritative status. Every transition requires specific validation.

## 2. States

| State | Description | Who Can Transition |
|-------|-------------|-------------------|
| `ai_draft` | Initial AI output; not validated | Automatic on AI output |
| `schema_validated` | Output conforms to declared Pydantic/JSON schema | Deterministic validator |
| `source_cited` | All claims have source chunk citations | Deterministic validator |
| `source_verified` | Cited chunks confirmed to support claims | Source-support verifier |
| `contradiction_checked` | No contradictions with existing verified facts | Contradiction detector |
| `evaluator_passed` | Golden eval suite passed for this output type | Evaluator runner |
| `accepted_for_planning` | Approved for use in planning/design (not implementation) | Human or delegated review |
| `accepted_for_tests` | Approved for use in test generation | Human or delegated review |
| `accepted_for_source_requirements` | Approved as input to code generation | Human or delegated review + DEC-034 IV |
| `authoritative_after_gate` | Full authority — passed gate review | Human gate approval |
| `rejected` | Failed validation; not usable | Any validator or reviewer |
| `superseded` | Replaced by newer version | New artifact creation |

## 3. State Transition Rules

### 3.1 Valid Transitions

```
ai_draft → schema_validated                (requires: schema validation pass)
schema_validated → source_cited            (requires: citation check pass)
source_cited → source_verified             (requires: source-support verification pass)
source_verified → contradiction_checked    (requires: contradiction detection pass)
contradiction_checked → evaluator_passed   (requires: golden eval pass)
evaluator_passed → accepted_for_planning   (requires: human/delegated review)
accepted_for_planning → accepted_for_tests (requires: human/delegated review)
accepted_for_tests → accepted_for_source_requirements (requires: DEC-034 IV)
accepted_for_source_requirements → authoritative_after_gate (requires: human gate approval)

Any state → rejected                       (on validation failure)
Any state → superseded                     (on new version)
```

### 3.2 Skip Prevention

- No state may be skipped in the forward path
- Each transition requires the specific validation listed
- Attempting to skip a state results in automatic `rejected` transition
- The enforcement mechanism is the authority lifecycle validator in `tools/ai/validators/authority_lifecycle.py`

### 3.3 Backward Transitions

- `rejected` artifacts may be re-submitted as new `ai_draft` (new artifact, new ID)
- `superseded` artifacts are immutable — archived but not reusable
- No backward transition within the forward path (cannot go from `source_verified` back to `schema_validated`)

## 4. Artifact Metadata

Every AI artifact must carry:

```yaml
artifact_id: <unique identifier>
artifact_type: requirement | test_idea | security_finding | summary | strategy | assessment
authority_state: <current state>
state_history:
  - state: ai_draft
    timestamp: <ISO 8601>
    validator: <who transitioned>
    evidence: <validation result reference>
  - state: schema_validated
    timestamp: <ISO 8601>
    validator: schema_validator
    evidence: <schema validation log>
  # ... etc
source_model: <model_id>
model_fingerprint: <fingerprint>
prompt_version: <hash>
input_hashes: [<sha256>]
output_hash: <sha256>
taskcard_id: <linked taskcard>
sprint_id: <sprint>
format: <target format>
created_at: <ISO 8601>
updated_at: <ISO 8601>
```

## 5. Integration with Evidence Bundles

Evidence bundles include:
- Artifact authority state at time of bundle build
- State transition history
- Validation results for each transition
- Count of artifacts by state (summary)

Artifacts in states below `evaluator_passed` SHOULD NOT appear in gate evidence as supporting material. They may appear as "in-progress" artifacts.

## 6. Integration with Existing Systems

### 6.1 Generated Requirements

Generated requirements (`generated-requirements/{format}/`) already follow a review process (AGENTS.md AF13). The authority lifecycle formalizes this:
- AI-generated requirement starts as `ai_draft`
- Schema validation (existing YAML schema check) → `schema_validated`
- Citation to spec sections → `source_cited` → `source_verified`
- Cross-reference check → `contradiction_checked`
- DEC-034 IV → `accepted_for_source_requirements`
- Gate approval → `authoritative_after_gate`

### 6.2 AI Usage Ledger

The existing AI usage ledger (`docs/ai/ai-usage-operating-model.md` Section 6) defines 8 status values. These map to the lifecycle:
- `ai_generated` → `ai_draft`
- `schema_valid` → `schema_validated`
- `citation_verified` → `source_verified`
- `human_reviewed` → `accepted_for_planning` (or higher)
- `accepted` → `accepted_for_source_requirements`
- `rejected` → `rejected`
- `superseded` → `superseded`
- `pending_review` → between `evaluator_passed` and `accepted_for_planning`

## 7. Cross-References

| Document | Relationship |
|----------|-------------|
| `docs/ai/ai-platform-operating-model.md` | Parent platform model |
| `docs/ai/ai-usage-operating-model.md` | Existing status values (mapped) |
| `docs/ai/ai-risk-register.md` | RISK-AI-020 (AI output becoming authority) |
| `AGENTS.md` AF13 | Generated requirements discipline |
| `GOVERNANCE.md` 26.11 | AI-generated requirements rules |
