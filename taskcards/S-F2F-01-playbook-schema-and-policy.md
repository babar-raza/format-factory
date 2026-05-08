# Taskcard S-F2F-01: Playbook Schema and Policy

## 1. Taskcard ID and Title
S-F2F-01: Playbook Schema and Policy

## 2. Status
completed_pending_independent_verification
executed: 2026-05-08
evidence_bundle: secondary-sf2f01-playbook-schema-policy-YYYYMMDD-HHMMSS.zip
artifacts_created:
  - schemas/playbook/acquisition-playbook.schema.json
  - schemas/playbook/review-queue.schema.json
  - docs/playbook-layer.md
  - docs/examples/acquisition-playbook-fods-documentation-example.yaml

## 3. Purpose
Create the foundational JSON schemas for acquisition playbooks and review queue items,
plus a policy document explaining what playbooks are and are not in format-factory. This
is the minimal viable first implementation step for the Full2Foss-inspired playbook system.
No executable tools are created; only schemas and a policy document.

## 4. Phase
S1 — Playbook Schema and Policy

## 5. Scope
- schemas/playbook/acquisition-playbook.schema.json (JSON schema draft-7)
- schemas/playbook/review-queue.schema.json (JSON schema draft-7)
- docs/playbook-layer.md (policy document)
- Example YAML snippet (embedded in docs/playbook-layer.md; NOT in acquisition-packs/)
No tools. No replay engine. No actual playbook.yaml files in acquisition-packs/.

## 6. Out of Scope
- tools/playbook/ (not in this sprint)
- acquisition-packs/fods/playbook.yaml (not in this sprint)
- acquisition-packs/fodt/playbook.yaml (not in this sprint)
- acquisition-packs/_families/ (not in this sprint)
- tests/playbook/ (not in this sprint)
- Any replay or apply mode capability
- Any gate status changes
- Any product source

## 7. Inputs
- plans/secondary/full2foss-inspired-system-strengthening-plan-v2.md (Layer 1 schema spec)
- plans/secondary/full2foss-inspired-plan-repair-review.md (corrected YAML examples)
- tools/evidence/contracts/base-run.yaml (contract baseline)

## 8. Outputs
- schemas/playbook/acquisition-playbook.schema.json
- schemas/playbook/review-queue.schema.json
- docs/playbook-layer.md

## 9. Exact Files Allowed
- schemas/playbook/acquisition-playbook.schema.json
- schemas/playbook/review-queue.schema.json
- docs/playbook-layer.md
- tools/evidence/contracts/s-f2f-01-playbook-schema.yaml (sprint contract)
- memory/ (if updated)
- .claude/settings.json (allow-list add: schemas/playbook/**, docs/playbook-layer.md)

## 10. Exact Files Forbidden
- tools/playbook/**
- acquisition-packs/fods/playbook.yaml
- acquisition-packs/fodt/playbook.yaml
- acquisition-packs/_families/**
- tests/playbook/**
- schemas/product/**
- tools/product/**
- src/python/**, src/net/**
- Any parser, neutral model, sample, or gate evidence file
- registry/format-registry.yaml (no gate changes)

## 11. Validation Commands
```bash
# Validate schemas are valid JSON
python -c "import json; json.load(open('schemas/playbook/acquisition-playbook.schema.json'))"
python -c "import json; json.load(open('schemas/playbook/review-queue.schema.json'))"
# Validate example YAML validates against schema
python -c "import jsonschema, yaml, json; jsonschema.validate(yaml.safe_load(open('docs/playbook-layer.md').read().split('```yaml')[1].split('```')[0]), json.load(open('schemas/playbook/acquisition-playbook.schema.json')))"
python tools/evidence/validate_evidence_bundle.py \
  --bundle .local/evidence-bundles/s-f2f-01-*.zip \
  --contract tools/evidence/contracts/s-f2f-01-playbook-schema.yaml \
  --check-no-pending
```

## 12. Evidence Requirements
Sprint-specific contract: tools/evidence/contracts/s-f2f-01-playbook-schema.yaml
Base: tools/evidence/contracts/base-run.yaml v1.2
BUNDLE_VALIDATION: PASS required

## 13. Rollback
Delete schemas/playbook/ (directory and all files).
Delete docs/playbook-layer.md.
Revert commit: `git revert <hash>`. No other changes to undo.

## 14. MAIN SPRINT Non-Deviation Rule
This sprint creates new schema and doc files only. It does not:
- Modify registry/format-registry.yaml
- Change any gate status
- Touch any MAIN SPRINT taskcard or acquisition pack gate field
MAIN SPRINT is unaffected.

## 15. Format-Agnostic Requirement
The schemas must use generic field names (format_id, not fods_id).
The policy doc must describe the system in format-neutral terms.
The example YAML must show format_id as a required parameter, not hardcoded.

## 16. Approval Required Before Execution
Human authorization prompt must explicitly name "S-F2F-01 Playbook Schema and Policy."
Generic continuation prompts are not sufficient.

## 17. Dependencies
- S-F2F-00: completed_by_plan_repair (this sprint is complete)
- plan-v2 schema specification: plans/secondary/full2foss-inspired-system-strengthening-plan-v2.md Section 11, Layer 1

## 18. Done Definition
DONE when:
- schemas/playbook/acquisition-playbook.schema.json: valid JSON, validates example YAML
- schemas/playbook/review-queue.schema.json: valid JSON, validates example review item YAML
- docs/playbook-layer.md: present, >= 4 sections, example YAML embedded
- ZERO tool files in tools/playbook/
- ZERO playbook.yaml in acquisition-packs/
- BUNDLE_VALIDATION: PASS
- Git status: clean after commit
