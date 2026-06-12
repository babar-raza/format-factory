# Compliance Posture — Format Factory

## Overview

Format Factory operates under a structured 11-gate acquisition pipeline with automated
governance enforcement. This document maps the project's governance controls to standard
compliance dimensions: access control, audit trail, policy-as-code, and change governance.

---

## Governance Architecture

### 11-Gate Acquisition Pipeline

Every format acquired by Format Factory must pass 11 sequential gates before commercial release:

| Gate | Name | Authority | Automated |
|------|------|-----------|-----------|
| G1 | Spec Research | Registry | Partial |
| G2 | Format Analysis | Registry | Partial |
| G3 | Prototype | Registry + Tests | Yes |
| G4 | Prototype Proof | Registry + Evidence | Yes |
| G5 | FOSS Source | Registry | Yes |
| G6 | FOSS Proof | Tests + Evidence | Yes |
| G7 | Test Depth | CI Coverage | Yes |
| G8 | Security Review | **Human Required** | No |
| G9 | API Stability | Registry + Tests | Yes |
| G10 | Release Manifest | Registry + Docs | Partial |
| G11 | Commercial Readiness | **Human Required** | No |

**Policy:** No format advances past Gate 8 or Gate 11 without explicit human approval.
Gate status is tracked in `registry/format-registry.yaml` (single source of truth).

---

## Policy-as-Code Controls

### Automated Governance Validators (11 validators)

Location: `tools/supervisor/governance_validators.py`

| Validator | Purpose |
|-----------|---------|
| `validate_declaration_schema` | Enforces evidence declaration structure |
| `validate_evidence_artifacts` | Verifies all referenced files exist |
| `validate_anti_skip` | Prevents skip of governance checks |
| `validate_adoption_compliance` | Enforces product source adoption rules |
| `validate_prompt_quality` | Validates supervisor prompt quality (Check 8) |
| `validate_skill_registry` | Checks skill registry consistency |
| `validate_spec_fact_refs` | Enforces spec-fact reference citations |
| `validate_state_machine` | Validates taskcard state transitions |
| `validate_cross_stream` | Enforces cross-stream isolation rules |
| `validate_evidence_quality` | Scores evidence quality (0.0–1.0) |
| `validate_package_manifest` | Validates package manifest completeness |

Validators run automatically in every supervisor cycle and in CI (`governance-check` job).

### CI Quality Gates

Defined in `.github/workflows/ci.yml`:
- **Lint gate:** `ruff check` hard-fail (no `continue-on-error`)
- **Security scan:** `bandit -r src/ -ll` (B314 intentionally skipped; see `docs/security.md`)
- **Test coverage gate:** `coverage report --fail-under=85` (hard-fail)
- **Governance smoke test:** imports `governance_validators` and validates the module loads

---

## Audit Trail

### Sprint Evidence Bundles

Every sprint produces a signed evidence bundle:
- Location: `.local/supervisor/reviews/<run_id>/declaration-review-package.zip`
- Contents: evidence declaration, changed files manifest, test logs, governance validator output
- Integrity: SHA-256 hash recorded in sprint memory and supervisor cycle output
- Retention: All bundles retained in `.local/supervisor/reviews/` (gitignored; operator-retained)

### Supervisor Cycle Reports

Location: `reports/supervisor/` — persisted to git for every sprint:
- `session-resume.md` — current state summary
- `evidence-review.md` — detailed evidence assessment
- `work-item-grades.yaml` — graded work items with accept/reject/rework verdicts
- `latest-cycle-summary.md` — sprint closeout summary

### Format Registry

Location: `registry/format-registry.yaml` — authoritative gate status for all formats.
Updated only through governed sprint cycles; each change is traceable to a sprint declaration.

---

## Access Control

### Repository Ownership

Defined in `CODEOWNERS`:
- All source code: `@prora`
- Supervisor tools: `@prora`
- Registry: `@prora`
- Tests and docs: `@prora`

**Gate authority:** Gate 11 (commercial readiness) additionally requires approval from Babar Raza.

### Agent Operating Boundaries

Defined in `AGENTS.md`:
- Agents may NOT commit, push, or publish without explicit human authorization
- Agents may NOT approve Gate 8 or Gate 11 themselves
- Agents may NOT deploy, release, or modify production systems
- Agents MUST record evidence for every product source change
- Agents MUST follow the supervisor-worker contract (`docs/automation/supervisor-worker-contract.md`)

---

## Security Controls

### Parser Security (Threat Model in `docs/security.md`)

| Threat | Mitigation | Verified By |
|--------|------------|-------------|
| XXE injection | `defusedxml` library used for XML parsing | `tests/python/security/test_xml_security.py` |
| DTD entity expansion | `defusedxml` blocks entity expansion | Security tests |
| Resource exhaustion | File size limits (`MAX_FILE_BYTES`) | Parser unit tests |
| Path traversal | No archive extraction in FODS/FODT parsers | N/A (flat XML formats) |
| Malformed input | `FodsParseError`/`FodtParseError` on bad input | Parser negative tests |

### CI Security Scanning

- `bandit -r src/ -ll -q` runs on every push/PR
- B314 (xml.etree): intentionally skipped; see `docs/security.md` for justification
- Security gate (Gate 8): human review required before production

---

## Change Governance

### Product Source Changes

Every product source change (code in `src/`) must be:
1. Declared in an evidence declaration YAML (`evidence-declaration.yaml`)
2. Referenced to a taskcard with `taskcard_id`
3. Accompanied by tests proving the change works
4. Graded by the supervisor pipeline (VERIFIED, ACCEPTED, or ACCEPTED_WITH_LIMITATIONS)
5. Traceable to a capability reference (`capability_refs`)

Governed by: `tools/supervisor/validate_product_code_ledger.py`

### Supervisor Pipeline Integrity

The autonomous supervisor pipeline enforces:
- No autonomous git push or commit (hard stop)
- No self-approval of Gate 8 or Gate 11 (hard stop)
- No package publication without human authorization (hard stop)
- Evidence quality scoring on every sprint declaration
- Contradiction detection and mandatory resolution before continuation

---

## Compliance Readiness Status

| Dimension | Status | Evidence |
|-----------|--------|---------|
| Access control | Active | `CODEOWNERS`, `AGENTS.md` authority model |
| Audit trail | Active | Sprint evidence bundles, supervisor reports |
| Policy-as-code | Active | 11 governance validators, CI gates |
| Change governance | Active | Supervisor-worker contract, product ledger |
| Security review (Gate 8) | Pending | Requires human approval per format |
| Commercial readiness (Gate 11) | Pending | Requires Babar Raza approval |
| Package publication | Not started | Awaiting Gate 11 approval |
| Incident response | Defined | `docs/operations/incident-runbook.md` |

**Note:** Gates 8 and 11 are hard-stops requiring human authorization. No autonomous
agent or automated process can advance a format past these gates.
