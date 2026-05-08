# Taskcard S-F2F-05: ODF-Flat Family Playbook

## 1. Taskcard ID and Title
S-F2F-05: ODF-Flat Family Playbook

## 2. Status
proposed_pending_human_approval

## 3. Purpose
Create the ODF-flat family playbook that documents reusable acquisition operations across
the ODF flat format family (FODS, FODT, FODP, FODG, FODB). The family playbook proposes
reuse_level classifications for each operation type and provides per-format override guidance.
It does NOT approve any gate, does NOT create per-format playbook.yaml files (those require
separate authorization), and does NOT inherit gate passes from FODS to other formats.

## 4. Phase
S5 — ODF-Flat Family Playbook
NOTE: Can run after S-F2F-01 (schema). Does NOT require S-F2F-02, S-F2F-03, or S-F2F-04.
S5 can run in parallel with S2/S3/S4 if MAIN SPRINT allows.

## 5. Scope
- acquisition-packs/_families/odf-flat/playbook.yaml (family-level reuse proposals)
- acquisition-packs/_families/odf-flat/reuse-policy.md (governance for family inheritance)
- acquisition-packs/_families/odf-flat/format-overrides.yaml (per-format exception table)

## 6. Out of Scope
- acquisition-packs/fods/playbook.yaml (not in this sprint — requires separate auth)
- acquisition-packs/fodt/playbook.yaml (not in this sprint — requires separate auth)
- Any inherited gate approval (explicitly prohibited)
- Any new format acquisition packs
- Any format registry changes
- Any product source

## 7. Inputs
- schemas/playbook/acquisition-playbook.schema.json (from S-F2F-01)
- docs/odf-flat-family-reuse-strategy.md (existing reuse strategy)
- acquisition-packs/fods/ (FODS gate operations as reuse reference)
- acquisition-packs/fodt/ (FODT gate operations)

## 8. Outputs
- acquisition-packs/_families/odf-flat/playbook.yaml
- acquisition-packs/_families/odf-flat/reuse-policy.md
- acquisition-packs/_families/odf-flat/format-overrides.yaml

## 9. Exact Files Allowed
- acquisition-packs/_families/odf-flat/playbook.yaml
- acquisition-packs/_families/odf-flat/reuse-policy.md
- acquisition-packs/_families/odf-flat/format-overrides.yaml
- tools/evidence/contracts/s-f2f-05-family-playbook.yaml (sprint contract)
- memory/ (if updated)
- .claude/settings.json (allow-list add: acquisition-packs/_families/**)

## 10. Exact Files Forbidden
- acquisition-packs/fods/playbook.yaml
- acquisition-packs/fodt/playbook.yaml
- acquisition-packs/fodp/** (not yet acquired)
- acquisition-packs/fodg/** (not yet acquired)
- registry/format-registry.yaml (no gate changes)
- schemas/product/**
- src/python/**, src/net/**

## 11. Validation Commands
```bash
# Family playbook validates against schema
python tools/playbook/validate_playbook.py --format-id odf-flat \
  acquisition-packs/_families/odf-flat/playbook.yaml
# Confirm reuse-policy.md explicitly prohibits inherited approval
grep -n "inherited" acquisition-packs/_families/odf-flat/reuse-policy.md
grep -n "independent.*DEC-034" acquisition-packs/_families/odf-flat/reuse-policy.md
# Confirm no per-format playbook.yaml files were created
ls acquisition-packs/fods/playbook.yaml 2>/dev/null && echo "FAIL: fods playbook exists" || echo "OK"
python tools/evidence/validate_evidence_bundle.py \
  --bundle .local/evidence-bundles/s-f2f-05-*.zip \
  --contract tools/evidence/contracts/s-f2f-05-family-playbook.yaml \
  --check-no-pending
```

## 12. Evidence Requirements
Sprint-specific contract: tools/evidence/contracts/s-f2f-05-family-playbook.yaml
BUNDLE_VALIDATION: PASS required

## 13. Rollback
Delete acquisition-packs/_families/ directory.
Revert commit. No other changes to undo.

## 14. MAIN SPRINT Non-Deviation Rule
This sprint does not modify any existing acquisition pack. It creates a NEW _families/
directory only. No gate states changed. No registry modified. MAIN SPRINT is unaffected.

## 15. Format-Agnostic Requirement
The family playbook must cover ALL 5 ODF flat formats: FODS, FODT, FODP, FODG, FODB.
Operations must use format_id parameter, not hardcode any single format.
FODP/FODG/FODB stubs may be marked "not_started" but must be present.

## 16. Approval Required Before Execution
Human authorization prompt must explicitly name "S-F2F-05 ODF-Flat Family Playbook."
Separate authorization required for any per-format playbook.yaml files.

## 17. Dependencies
- S-F2F-01: completed (schema exists for validation)
- S-F2F-02: NOT required (can validate with Python jsonschema directly if tool not available)

## 18. Done Definition
DONE when:
- acquisition-packs/_families/odf-flat/playbook.yaml: validates against schema; covers 5 formats
- acquisition-packs/_families/odf-flat/reuse-policy.md: explicitly prohibits inherited approval
- acquisition-packs/_families/odf-flat/format-overrides.yaml: present with FODS, FODT entries
- ZERO per-format playbook.yaml files created in acquisition-packs/{fods,fodt}/
- BUNDLE_VALIDATION: PASS
- Git status: clean after commit
