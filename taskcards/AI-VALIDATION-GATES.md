# Taskcard: AI-VALIDATION-GATES

**Status:** not_started
**Created:** 2026-05-13

## Purpose

Ensure AI output is validated before becoming authority. Define concrete validation gates that AI-generated code, tests, documentation, and evidence must pass before acceptance.

## Scope

- Define validation gate checklist for each AI output type (code, tests, docs, evidence)
- Integrate with existing evidence bundle validation (`tools/evidence/validate_evidence_bundle.py`)
- Define CI-ready validation steps for AI-generated C# code (`dotnet build`, `dotnet test`)
- Define validation steps for AI-generated Python code (`pytest`)
- Define citation validation for AI-generated spec claims
- Ensure DEC-034 IV requirement applies to AI-generated gate evidence

## Non-Goals

- Building a new validation framework (reuse existing tools)
- Replacing deterministic tests with AI validation
- Authorizing AI to approve validation results

## Acceptance Criteria

- [ ] Code validation gate defined: `dotnet build` + `dotnet test` + round-trip test
- [ ] Spec claim validation gate defined: citation verified against local spec text
- [ ] Documentation validation gate defined: cross-reference check + coordinator review
- [ ] Evidence validation gate defined: `BUNDLE_VALIDATION: PASS` + DEC-034 IV
- [ ] AI output status workflow integrated (PROPOSED → ACCEPTED/REJECTED)
- [ ] Validation gate checklist added to coordinator sprint checklist
- [ ] DEC-034 requirement confirmed as applicable to AI-generated gate evidence

## Evidence Requirements

- Checklist document created
- Existing tool references (validate_evidence_bundle.py, dotnet test) verified

## Files Allowed

- docs/ai-validation-gates.md (create if needed, else update existing)
- AGENTS.md (narrow addition only if validation gate rule is missing)

## Prohibited Actions

- No AI approval of validation results
- No bypassing `dotnet test` or `pytest` with AI claims
- No removing DEC-034 requirement

## Validation Required

- Consistency with AGENTS.md §V (DEC-034 independent verification)
- Consistency with tools/evidence/validate_evidence_bundle.py behavior

## Next Dependency

- NEXT-COMMERCIAL-IMPLEMENTATION-SWARM (enforces these gates)
