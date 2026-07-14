---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: "Supervisor approval"
skill_type: ATOMIC_SKILL
idempotency: "Same failing CI run + same Diagnosis Map produce the same job identification and the same local-reproduction command selection; the `gh run list`/`gh run view --log-failed` calls are read-only and repeatable without side effects"
loc_budget: "0 lines of executable code (prompt-driven diagnosis map + local-repro command table only; no bundled script)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the manual scan proof recorded under TC-EXT-020-03"
product_track: infrastructure
created-by: TC-EXT-020
risk_level: MEDIUM
---

# /gh-fix-ci

Diagnose a failing CI job: read its real failure log via `gh run view
--log-failed`, map the job name to its exact local-reproduction command, run
that command locally, and — if the fix requires a `src/**` change — delegate
to the applicable already-governed mutation skill rather than editing
`src/**` directly. This skill diagnoses and reproduces locally; it never
mutates product source itself.

## Origin

FF-original skill — no upstream project was verified during this session's
external-skill-adoption research to cite as a source (see
`plans/.claude/yes-my-earlier-answer-humming-waffle.md` §7.3, TC-EXT-020:
"FF-original — no upstream name verified in this session's research"). There
is no upstream commit or license to cite, and this file carries no
`external_skill_*` provenance fields.

## Purpose

This repository's CI pipeline (`.github/workflows/ci.yml`) runs multiple
independent jobs on every push/PR. When a job goes red, the fastest reliable
path to a fix is: (1) read the actual failure output rather than guessing
from the job name, (2) reproduce the same failure locally using the exact
command CI itself runs, (3) iterate on the fix locally (fast, no CI-queue
round-trip), and (4) route any `src/**` change through the correct governed
mutation skill (EP-3) instead of hand-editing product source from a CI-repair
context. This skill owns steps 1-3 and the routing decision in step 4; it
never itself performs a `src/**` write.

## When to Use

- A CI job shows a red X in `gh pr checks` or `gh run list`.
- Before re-deriving `.github/workflows/ci.yml`'s job list from scratch —
  use the Diagnosis Map below as the current source of truth, but re-verify
  it (Mandatory Validations, `diagnosis_map_freshness_checked`) if
  `.github/workflows/ci.yml` has changed since this file's `last-updated`.

## CI Job Diagnosis Map (re-derived from `.github/workflows/ci.yml` HEAD, 2026-07-14)

`.github/workflows/ci.yml` at HEAD defines **14** jobs — not 13. (This
skill's own originating taskcard, TC-EXT-020, assumed "13 jobs" in its
summary count, but the named list it enumerated already correctly listed
all 14 job names; only the summary count label was stale by one. This table
is the corrected, re-derived version.)

| Job | Trigger | Local reproduction command(s) |
|---|---|---|
| lint | push, pull_request | `ruff check src/ tests/ tools/ --output-format=github` |
| security | push, pull_request | `bandit -r src/ -ll -q --skip B314` (B314 skipped intentionally — see `docs/governance/security.md`) |
| test-fast | pull_request only | `python tools/test_runner.py --layer 3 --known-failures registry/known-failure-ledger.yaml --json-out .local/test-results/ci-fast.json` |
| skill-attribution-check | push, pull_request | `python tools/governance/ci_skill_attribution_check.py --base-ref HEAD~1 --head-ref HEAD --allow-pre-policy --output .local/ci-skill-attribution-report.json` |
| governance-check | push, pull_request | `python tools/validators/source_structure_validator.py` → `python tools/governance/run_ci_governance_check.py` → `.venv/Scripts/pytest tests/governance/test_capability_parity.py -v` → `python tools/supervisor/check_component_register.py` → `python tools/supervisor/check_extension_budget.py` (run in this order; any step failing is the diagnosis target) |
| readme-drift | push, pull_request | `python tools/readme_sync/generate_root_status.py --mode drift-only` |
| dotnet-build | push, pull_request | `dotnet restore <proj>` for each `src/net/*/FormatFactory.*.csproj` and `tests/net/*/FormatFactory.*.Tests.csproj` that exists, then `dotnet build src/net/<fmt>/FormatFactory.*.csproj --configuration Release --no-restore` for `fmt` in `csv html txt markdown fods fodt ndjson tsv netpbm zst` (in that dependency order), then `dotnet test tests/net/<fmt>/FormatFactory.*.Tests.csproj --configuration Release` for each test project |
| test-full | push to `main` only, matrix `python-version: [3.10, 3.11, 3.12]` | `.venv/Scripts/pytest --cov=src/python --cov-report=xml --cov-report=term-missing` → `.venv/Scripts/pytest tests/playbook/ -q --tb=short` → `coverage report --fail-under=85` |
| oracle-obligations | push, pull_request | `python tools/oracle/validate_oracle_obligations.py` |
| capability-parity | push, pull_request (advisory — `continue-on-error: true`, WARN only) | `python tools/capability_sync/detect_drift.py --output capability-drift.json` |
| oracle-depth-check | push, pull_request | inline Python block reading `oracle/formats/*/reports/oracle-run-summary.json` for any `format_depth_score == "D0"` — copy the exact inline block from `.github/workflows/ci.yml`'s `oracle-depth-check` job step and run it via `python -c "..."` |
| release-phase-validation | push, pull_request | `python tools/supervisor/gate_executor.py --format fods --gates G1,G2 --dry-run` |
| count-drift-detection | push, pull_request | `python tools/readme_sync/generate_root_status.py --mode drift-only` (identical underlying command to `readme-drift` — two CI job names guarding the same check) |
| agent-parity-drift | push, pull_request (PRs touching agent configs, skill registry, capability registry, or `inventory_capabilities.py`) | inline Python block invoking `governance_validators_agent_parity.{validate_agent_opt_in_not_default, validate_kilo_column_in_registry, validate_canonical_contract_integrity, validate_agent_bundles_current}` — copy the exact inline block from `.github/workflows/ci.yml`'s `agent-parity-drift` job step |

## Steps

1. **Identify the failing job**: `gh run list --branch <branch> --limit 5` to
   find the run, then `gh run view <run_id> --log-failed` to read the real
   failure output for the specific job(s) that failed. Never guess the cause
   from the job name alone.
2. **Map to local reproduction**: look up the failing job name in the
   Diagnosis Map above. If `.github/workflows/ci.yml` has changed since this
   table was last re-derived, re-read the workflow file in full before
   trusting the table (see Mandatory Validations).
3. **Run locally**: execute the mapped command(s) exactly as CI runs them
   (same flags, same working directory assumption — repo root). Confirm the
   local run reproduces the same failure. If it does not reproduce, treat
   that itself as a finding (e.g. Python/.NET version drift between the
   matrix and the local environment, a matrix-only failure, or a stale
   `.local/`/cache artifact) rather than concluding "already fixed."
4. **Route the fix**:
   - Confined to `tests/**`, a local diagnostic script, or CI-config
     *understanding* (not a CI-config edit) — this skill may state the fix
     directly.
   - Requires any `src/**` change — STOP. Delegate to the applicable
     governed mutation skill (`/product-source-task`, `/add-python-api`,
     `/add-dotnet-api`, `/format-feature-expansion`, etc., per EP-3
     "Skill-Driven Architecture" in CLAUDE.md). This skill creates no direct
     `src/**` mutation pathway of its own.
   - Reveals a governance/validator defect rather than a code bug (e.g. a
     stale count baseline, a validator that should have caught this earlier)
     — route through `/systematic-debugging`'s FF-Specific Escalation into
     `/found-issue-ownership`.
5. **Record the diagnosis**: write a diagnosis record to
   `reports/ci-diagnosis/<run_id>-<job>.md` — job name, failing step, local
   command used, local result, root cause (if confirmed), and the routing
   decision (self-contained fix / delegated to skill X / routed to
   `/found-issue-ownership`).

## Mandatory Validations

- `real_log_read_before_diagnosis` — `gh run view <run_id> --log-failed` (or
  equivalent) output is read before any local-reproduction command is
  selected; the job name alone is never treated as sufficient diagnosis.
- `diagnosis_map_freshness_checked` — before trusting the Diagnosis Map
  above, confirm `.github/workflows/ci.yml`'s last-modified state does not
  postdate this file's `last-updated` frontmatter field; re-derive the map
  from the live file if it does.
- `no_direct_src_mutation` — any fix requiring a `src/**` change is delegated
  to a named governed mutation skill (EP-3); this skill's own write surface
  never includes `src/**`.
- `diagnosis_recorded` — every invocation writes a diagnosis record under
  `reports/ci-diagnosis/`.

## Allowed Paths

- `.github/workflows/ci.yml` — read only (source of the Diagnosis Map)
- Any file under `src/`, `tests/`, `tools/` — read only, for local
  reproduction and root-cause tracing
- `gh run list`, `gh run view <run_id> --log-failed` — external read-only
  network calls (no write-side GitHub API call of any kind)
- The local reproduction commands from the Diagnosis Map — executed as
  ordinary local processes; no CI configuration mutation
- `reports/ci-diagnosis/` — write (diagnosis records only)

## Forbidden Paths

- `src/**` — no direct write; any required fix is delegated to a governed
  mutation skill (EP-3)
- `.github/workflows/*.yml` — read only; this skill diagnoses CI, it does
  not edit CI configuration
- `.supervisor/skill-registry.yaml`, `registry/format-registry.yaml` — this
  skill does not alter governance or gate authority
- Any `gh api`/`gh pr`/`gh issue` write call (comment posting, label
  changes, merges) — out of scope; see `/gh-address-comments` (TC-EXT-021)
  for the PR-comment-posting case, a separate HIGH-risk,
  SCM-POLICY-CHECK-001-gated skill

## Stop Conditions

- Stop and delegate if the fix requires any `src/**` change — never edit
  `src/**` directly from this skill.
- Stop and re-derive the Diagnosis Map if `.github/workflows/ci.yml` has
  changed since this file's `last-updated`.
- Stop and route through `/found-issue-ownership` if the failure indicates a
  governance/validator defect rather than an ordinary code bug.

## Idempotency Contract

Given the same failing CI run and the same Diagnosis Map (this file),
re-running this skill's diagnosis steps identifies the same failing job,
selects the same local-reproduction command, and reaches the same routing
decision. The `gh run list`/`gh run view --log-failed` calls are read-only
and safe to repeat.

## Output Format

```
## CI Diagnosis: <job name> (<run_id>)

### Step 1 — Failing job identified
- Run: <run_id>, Job: <job name>, Trigger: <push|pull_request>
- Failure log excerpt: <key lines from --log-failed>

### Step 2-3 — Local reproduction
- Command: <mapped command(s) from Diagnosis Map>
- Local result: <matches CI failure | does not reproduce — CI-environment-only, explain why>

### Step 4 — Routing decision
- <self-contained fix (tests/** or diagnostic only) | delegated to /<skill> (src/** change) | routed to /found-issue-ownership (governance defect)>

### Step 5 — Diagnosis record
- Written to: reports/ci-diagnosis/<run_id>-<job>.md
```

## Governance Note

FF-original skill, built under TC-EXT-020 of the external-skill-adoption
plan (`plans/.claude/yes-my-earlier-answer-humming-waffle.md` §7.3). No
upstream project was verified during this session's research to cite as a
source — this is not an external import and carries no `external_skill_*`
provenance fields. Cleared by `/skill-scanner` before registration
(TC-EXT-020-03), consistent with every other skill imported/authored under
the TC-EXT-0XX family.
