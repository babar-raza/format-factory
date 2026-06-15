# /spec-parity-verification

**Skill ID:** spec-parity-verification
**Registry Version:** 2.0
**Track:** spec_parity
**Status:** active

## Purpose

Run spec-parity validators and produce a structured verification report.
Required before any product model taskcard is declared complete.

## Validators

1. **SpecParityQNameValidator** — verifies every product class has a `spec_qname`
2. **NamespaceTreeValidator** — verifies namespace hierarchy matches QName map
3. **SkeletonProgressValidator** — verifies spec concepts have non-skeleton implementations
4. **SkillWiringValidator** — verifies skills are registered and command files exist

## Required Inputs

- `format_id` — format to verify
- `evidence_root` — where to write verification reports

## Invocation

```
python tools/supervisor/qname_ontology_generator.py \
  --format <FORMAT_ID> \
  --output-dir <evidence_root>/qname/

python tools/supervisor/validate_skill_registry.py

python tools/supervisor/governance_validators.py
```

## Evidence

- `spec-parity-verification-report.yaml` — structured results
- `qname-coverage-<format>.json` — per-format QName coverage
- `skill-registry-validation.log` — skill registry check
- `governance-validators.log` — governance check results

## Acceptance Criteria

- SkillWiringValidator: 0 missing command files (excluding deferred)
- SpecParityQNameValidator: 0 flat-class violations for declared scope
- NamespaceTreeValidator: namespace tree exists and is valid JSON
- All mandatory_validations items report PASS or ACCEPTABLE_EXCEPTION

## Mandatory Validations

1. `spec_parity_qname_validator_run` — generator must complete
2. `namespace_tree_validator_run` — namespace tree must exist
3. `skeleton_progress_validator_run` — governance validators must run
4. `skill_wiring_validator_run` — validate_skill_registry.py must exit 0
5. `verification_report_written` — report must be written to evidence_root

## Allowed Paths

- `tools/supervisor/qname_ontology_generator.py`
- `tools/supervisor/validate_skill_registry.py`
- `tools/supervisor/governance_validators.py`
- `.local/evidences/<run_id>/`
- `reports/supervisor/`

## Forbidden Paths

- No direct edits to `src/` source files
- No Gate 11 self-approval
- No edits to `registry/format-registry.yaml` without supervisor authorization

## Stop Conditions

- Stop if `qname_ontology_generator.py` exits non-zero
- Stop if skill registry validation reports missing command files for active skills
- Stop if governance validators report `blocks_sprint=True` for current sprint scope
- Stop if evidence_root does not exist and cannot be created

## Gate 11

This skill prepares spec-parity evidence for Gate 11 readiness packets.
Actual Gate 11 EXECUTION approval requires Babar Raza.
