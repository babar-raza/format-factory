# Incident Runbook — Format Factory

## Overview

This runbook covers operational incidents for the Format Factory format acquisition pipeline.
All incident handling follows the authority model defined in [AGENTS.md](../../AGENTS.md) and
the security threat model in [docs/governance/security.md](../governance/security.md).

---

## Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|--------------|---------|
| P0 | Production data corruption, security breach | Immediate | XXE injection, path traversal |
| P1 | Parser crash on valid input, data loss | < 1 hour | Unhandled exception in FODS/FODT parser |
| P2 | Test suite regression > 5%, CI red | < 4 hours | Coverage drop, new failures |
| P3 | Governance validator failure | < 1 day | Anti-skip check blocks sprint |
| P4 | Documentation staleness, style violations | Next sprint | Ruff violations, outdated docs |

---

## P0 — Security Incident

**Trigger:** XML External Entity (XXE) injection, path traversal, or Billion Laughs attack detected.

**Response steps:**
1. **Isolate** — Do not merge or deploy the affected parser version.
2. **Identify** — Determine if `defusedxml` is active (check `parser.py` import: `try: import defusedxml.ElementTree`).
3. **Verify** — Run security tests: `python -m pytest tests/python/security/ -v`
4. **Escalate** — Open a Gate 8 security review (requires human approval per [AGENTS.md](../../AGENTS.md)).
5. **Reference** — See [docs/governance/security.md](../governance/security.md) for full threat model and mitigations.

**Key files:**
- `src/python/fods/parser.py` — FODS XML parser with defusedxml protection
- `src/python/fodt/fodt_parser.py` — FODT XML parser with defusedxml protection
- `docs/governance/security.md` — Threat categories and mitigations
- `tests/python/security/test_xml_security.py` — Behavioral security tests

**Gate 8 authority:** Human approval required before production release of any format that
processes external XML/ZIP content. See `registry/format-registry.yaml` for gate status.

---

## P1 — Parser Crash on Valid Input

**Trigger:** `FodsParseError`, `FodtParseError`, or unhandled exception on a valid format file.

**Response steps:**
1. **Capture** — Save the failing file (ensure no sensitive data).
2. **Reproduce** — Run `parse_fods_strict(file_path)` or equivalent locally.
3. **Diagnose** — Check for size limit violations (`MAX_FILE_BYTES`), unsupported features,
   or encoding issues. Review constants in `src/python/fods/constants.py`.
4. **Fix** — Add a regression test first, then fix the parser.
5. **Validate** — Run: `python -m pytest tests/python/fods/ tests/python/fodt/ -v`
6. **Gate** — If the fix changes parser behavior, increment minor version and note in CHANGELOG.md.

**Escalation:** @prora (see [CODEOWNERS](../../CODEOWNERS))

---

## P2 — Test Suite Regression

**Trigger:** CI test-full job fails, coverage drops below 85%, or > 10 new failures appear.

**Response steps:**
1. **Triage** — Distinguish test failures from collection errors.
   - Collection errors: usually import failures → check `sys.path` and package installs
   - Test failures: run locally with `python -m pytest <failing-test> -v --tb=long`
2. **Evidence tests** — Evidence tests in `tests/evidence/` are skipped in CI (they require
   `.local/` artifacts). If they fail locally, run `python tools/supervisor/build_declaration_review_package.py` to populate `.local/`.
3. **Supervisor tests** — Tests in `tests/supervisor/` are integration tests against
   supervisor tools. If they fail, check `tools/supervisor/` imports and dependencies.
4. **Coverage drop** — If coverage < 85%, identify uncovered new code and add tests.
5. **Fix and rerun** — Fix the regression, run `python -m pytest tests/ -x` locally.

**Non-blocking known state:**
- `tests/evidence/` tests: skipped in CI (require `.local/` artifacts). Run locally.
- Oracle tool errors (`tools/oracle/`): excluded from ruff checks (legacy Python 3.9 compat issue).

---

## P3 — Governance Validator Failure

**Trigger:** `python tools/supervisor/autonomous_cycle.py` exits with code 3, or
`run_all_governance_validators()` returns `blocks_sprint=True`.

**Response steps:**
1. **Read output** — Identify which of the 11+ validators failed.
2. **Common causes:**
   - `validate_adoption`: declaration has `item_type: PRODUCT_SOURCE` without `exemption_reason`
   - `validate_anti_skip`: evidence files referenced in declaration don't exist
   - `validate_evidence_quality`: evidence quality score < threshold
   - `validate_declaration_schema`: missing required YAML fields
3. **Fix declaration** — Edit `.local/evidences/<run_id>/evidence-declaration.yaml`
4. **Rerun** — `python tools/supervisor/autonomous_cycle.py --declaration <path>`
5. **Reference** — `docs/automation/supervisor-worker-contract.md` for full field list.

---

## Escalation Chain

| Scenario | Owner | Contact |
|----------|-------|---------|
| Security incident (P0) | @prora | Gate 8 approval required |
| Production parser failure | @prora | File GitHub issue |
| Gate 11 approval needed | Babar Raza | Commercial readiness gate |
| CI/CD pipeline failure | @prora | Check GitHub Actions logs |
| Governance validator failure | @prora | Check supervisor pipeline |

All authority decisions follow the gate model in `registry/format-registry.yaml`.
No format advances past Gate 8 (security) or Gate 11 (commercial) without human approval.

---

## Post-Mortem Template

Use this template after any P0 or P1 incident.

```
## Incident: <title>
**Date:** YYYY-MM-DD
**Severity:** P0/P1
**Duration:** <from detection to resolution>

### Timeline
- HH:MM — Detection
- HH:MM — Initial triage
- HH:MM — Root cause identified
- HH:MM — Fix deployed
- HH:MM — Resolved

### Root Cause
<What caused the incident>

### Impact
<Which formats, which users, which tests affected>

### Resolution
<What was changed to fix it>

### Prevention
<What was added to prevent recurrence: test, validator, CI check, doc>

### Files Changed
<List of changed files and their purpose>
```

---

## Observability

- **Structured logging:** `tools/supervisor/logging_config.py` — JSON-formatted logs for supervisor pipeline
- **Health check:** `python tools/health_check.py` — validates project health (imports, registry, governance)
- **Test runner:** `python tools/test_runner.py --layer 3` — layer-filtered test execution
- **Governance check:** `python -c "from governance_validators import run_all_governance_validators; ..."`
- **CI artifacts:** GitHub Actions uploads `coverage.xml` and test results per run

See [docs/operations/observability-guide.md](observability-guide.md) for more.
