# Test Suite Layering — Format Factory

## Layer Model

| Layer | Name | Scope | Expected Time | Command |
|-------|------|-------|---------------|---------|
| L0 | Structural | Health check, import smoke | <5s (+ collection) | `pytest -m layer0` |
| L1 | Focused | Single-format unit tests | <30s | `pytest -m "layer0 or layer1" tests/python/{format}/` |
| L2 | Family | Related format group | <60s | `pytest -m "layer0 or layer1" tests/python/{fmt1}/ tests/python/{fmt2}/ ...` |
| L3 | Integration | Supervisor, governance, evidence, capability | ~varies | `pytest -m "layer0 or layer1 or layer2 or layer3"` |
| L4 | Golden | Roundtrip, cross-format, export, dogfood | ~varies | `pytest -m "layer0 or layer1 or layer2 or layer3 or layer4"` |
| L5 | Broad | All python + supervisor + evidence + packaging + skills + ai | ~varies | `pytest -m "layer0 or layer1 or layer2 or layer3 or layer4 or layer5"` |
| L6 | Full | Entire test suite | Full duration | `pytest` (no -m flag) |

Layers are **cumulative**: requesting layer N runs layers 0 through N.

## Quick Reference

```bash
# Structural sanity (every iteration)
python tools/test_runner.py --layer 0

# Format-specific work (most common)
python tools/test_runner.py --layer 1 --format tsv

# Family expansion (e.g., PBM change tests PBM+PGM+PPM)
python tools/test_runner.py --layer 2 --format pbm

# Supervisor/governance change
python tools/test_runner.py --layer 3

# Auto-detect from git diff
python tools/test_runner.py --auto

# Full suite, sharded
python tools/test_runner.py --layer 6 --shard 1/4
python tools/test_runner.py --layer 6 --shard 2/4
python tools/test_runner.py --layer 6 --shard 3/4
python tools/test_runner.py --layer 6 --shard 4/4

# Dry-run (see command without executing)
python tools/test_runner.py --layer 3 --dry-run

# JSON output for evidence declarations
python tools/test_runner.py --layer 1 --format tsv --json-out .local/test-results/result.json
```

## Change-Impact Matrix

| Changed File Pattern | Min Layer | Closeout Layer | Full Suite Required? |
|---------------------|-----------|---------------|---------------------|
| `docs/**`, `reports/**`, `plans/**`, `*.md` | L0 | L0 | No |
| `src/python/{format}/**` | L1 | L2 | No |
| `tests/python/{format}/**` | L1 | L1 | No |
| `tools/supervisor/**` | L3 | L3 | No |
| `tools/ai/**` | L3 | L3 | No |
| `tests/supervisor/**` | L3 | L3 | No |
| `tests/evidence/**` | L3 | L3 | No |
| `tests/capability_layer/**` | L3 | L3 | No |
| `registry/**` | L3 | L3 | No |
| `schemas/**` | L3 | L3 | No |
| `tools/*` (non-supervisor, non-ai) | L5 | L5 | No |
| `tests/python/conftest.py` | L5 | L5 | No |
| `src/net/**` | L5 | L5 | No |
| `pyproject.toml` | L6 | L6 | Yes |
| `.github/**` | L6 | L6 | Yes |
| `tests/conftest.py` (root) | L6 | L6 | Yes |
| Unrecognized file | L6 | L6 | Yes (fail-safe) |

Machine-readable version: `registry/test-layer-manifest.yaml`

## Agent Guidance

### Choosing the Right Layer

1. **Every iteration**: Run at least L0 (structural sanity).
2. **Format source change**: Run L1 for the changed format, L2 at closeout.
3. **Supervisor/governance change**: Run L3.
4. **Shared infrastructure**: Run L5.
5. **Build/CI config**: Run L6 (full suite).
6. **Docs only**: L0 is sufficient.

### Prohibited Claims

- **Do NOT claim full verification after running only L0-L5.** If full suite was not run, state `full_suite_run: false` in evidence.
- **Do NOT skip L0.** It must pass before any higher layer.
- **Do NOT claim a format is fully tested if only L1 was run.** L2 (family) catches cross-format regressions.
- **If unsure, escalate.** Running a higher layer is always safe.

### Evidence Requirements

Include in evidence-declaration.yaml:
```yaml
test_layer: 3
test_layer_name: "integration"
test_layer_reason: "tools/supervisor/governance_validators.py changed"
full_suite_required: false
full_suite_run: false
test_results:
  passed: 1234
  failed: 0
  skipped: 5
  errors: 0
```

## Full-Suite Policy

The full suite is **mandatory** when:
- `pyproject.toml` changes
- `.github/workflows/` changes
- `tests/conftest.py` (root) changes
- Release candidate gating
- Explicit human or governance request
- Unrecognized file patterns (fail-safe)

The full suite is **authoritative**: no partial run can replace it for release confidence.

## Sharding Commands (Layer 6)

| Shard | Scope | Command |
|-------|-------|---------|
| 1/4 | Format codecs (tests/python/) | `python tools/test_runner.py --layer 6 --shard 1/4` |
| 2/4 | Supervisor (tests/supervisor/) | `python tools/test_runner.py --layer 6 --shard 2/4` |
| 3/4 | Evidence (tests/evidence/) | `python tools/test_runner.py --layer 6 --shard 3/4` |
| 4/4 | Everything else | `python tools/test_runner.py --layer 6 --shard 4/4` |

Each shard produces a separate JSON result. Partial shard completion is clearly labeled — do not claim full-suite pass from partial shards.

## Collection Optimization

The runner uses **fast-path collection** for L0 and L1/L2 with `--format`:

| Scenario | Method | Collection Time |
|----------|--------|----------------|
| `--layer 0` | Explicit file paths (no `-m` marker) | ~2s |
| `--layer 1 --format tsv` | L0 files + format directory (no `-m` marker) | ~4s |
| `--layer 1` (no format) | `-m "layer0 or layer1"` (full collection) | ~25s |
| `--layer 3` and above | `-m` marker expression (full collection) | ~25s |

The fast-path bypasses pytest's full-tree discovery by passing explicit file/directory paths instead of using marker filters. Layers remain cumulative: L1+format includes both L0 files and the format directory.

For L3 and above, full collection overhead (~25s) is unavoidable due to pytest's architecture.

## Known Environment-Dependent Test Failures

Some tests at L3 (integration) may fail due to environment conditions, not code regressions:

| Test | Trigger | Root Cause | Workaround |
|------|---------|-----------|------------|
| `tests/evidence/test_auto_proof_bundle.py` | Dirty git working tree | Validates that evidence bundles are built from a clean tree. Fails when uncommitted changes exist. | Commit or stash changes before running L3. |
| SSL/network-dependent tests | No internet or slow connectivity | Some supervisor and evidence tests make network calls that may timeout. | Ensure internet connectivity, or run L1 (format-only) to avoid these tests. |

These are **not layering regressions**. The marker assignment is correct — these tests belong at L3. The failures are pre-existing and environment-dependent.

**Runner reliability flag**: When pytest exits non-zero but produces no test results (e.g., due to early failure before junitxml is written), the runner sets `test_results_reliable: false` in the JSON output and prints a stderr warning. Always check this field before using test_results in evidence declarations.

## Known Limitations

1. **Collection overhead for L3+**: Layers 3–6 still require ~25s for pytest to collect all 14,500+ tests before marker filtering. This is a pytest architectural limitation. L0 and L1+format bypass this via the fast-path above.
2. **Layer 2 (Family)**: Not assigned as a marker — the runner handles family expansion by adding multiple directory paths to L1's marker expression.
3. **No parallel execution**: pytest-xdist is not installed. Tests run sequentially.
4. **Auto-detection scope**: `--auto` uses `git diff HEAD` + staged + unstaged changes. In CI, use `--base-ref` to compare against the target branch.
5. **--auto on dirty repos**: On repos with many untracked files not in the manifest, `--auto` selects L6 (fail-safe). Use explicit `--layer N` on dirty branches.
6. **test_layer schema enforcement**: The `test_layer`, `full_suite_required`, and `full_suite_run` fields in evidence-declaration.yaml are ADVISORY ONLY. The supervisor schema does not enforce them. Agents must self-enforce these rules.

## Taskcard State Machine

Taskcards use these states to track validation progress:

| State | Description |
|-------|-------------|
| `backlog` | Not yet started |
| `ready` | Prerequisites met; can start |
| `active` | Currently in progress |
| `blocked` | Waiting on external dependency |
| `LAYER0_VALIDATING` | Running L0 structural tests |
| `FOCUSED_VALIDATING` | Running L1 format-focused tests |
| `COMPONENT_VALIDATING` | Running L2 family tests |
| `INTEGRATION_VALIDATING` | Running L3 supervisor/governance tests |
| `BROAD_VALIDATING` | Running L5 broad infrastructure tests |
| `FULLSUITE_VALIDATING` | Running L6 full suite (all shards) |
| `EVIDENCE_PACKAGING` | Writing evidence-declaration.yaml |
| `ACCEPTED_VERIFIED` | All tests passed; evidence accepted |
| `ACCEPTED_WITH_REWORK` | Accepted with documented limitations |
| `REJECTED_NEEDS_REWORK` | Failed; rework required before re-submission |

**Transition rules:**
1. No taskcard may move to `ACCEPTED_VERIFIED` without test evidence at or above its required layer.
2. No product-behavior taskcard (`item_type=PRODUCT_SOURCE`) may close with docs-only validation (L0 only).
3. No shared-infrastructure taskcard may close with single-family test only (L1 only).
4. No full-suite claim without all 4 shards completing at `exit_code=0`.
5. Any timeout or incomplete execution keeps the taskcard in its current VALIDATING state.
6. Pre-existing known failures (in `registry/known-failure-ledger.yaml`) do not block closure; new failures do.
7. Advisory-only evidence (dry-run output, prose summaries) does NOT satisfy a VALIDATING state.

## Known-Failure vs New-Failure Handling

Pre-existing failures are tracked in `registry/known-failure-ledger.yaml`.

**Classification procedure:**
1. After running tests, collect the list of failing test IDs.
2. Look up each failing test ID in `registry/known-failure-ledger.yaml`.
3. If found → PRE-EXISTING: document in evidence but do not require rework.
4. If NOT found → NEW FAILURE: investigate before declaring the taskcard complete.

**Known pre-existing failures (as of 2026-06-18):**
- `tests/evidence/test_auto_proof_bundle.py` — fails on dirty working tree. Mitigation: `--no-state` flag.
- Unmarked supervisor network tests — timeout-dependent. Mitigation: `--timeout=N` per test.

Use `--known-failures registry/known-failure-ledger.yaml` with `tools/test_runner.py` (after HEAL-003)
to get automatic classification of new vs pre-existing failures in JSON output.

## Slow Test Policy

Slow tests are defined as individual tests consistently exceeding **5 seconds**.

**Detection:** Use `pytest --durations=10 tests/python/{fmt}/` to find the 10 slowest tests.
No extra dependency required — `--durations` is a built-in pytest flag.

**Registration:** Slow tests are registered in `registry/slow-test-ledger.yaml`.

**@pytest.mark.slow strategy:**
- Marker is informational only — slow tests are NOT auto-skipped.
- Slow tests run in full suite (L6) and in L1+format runs.
- Developers may exclude them locally: `pytest tests/python/{fmt}/ -m "not slow" -q`.
- CI always includes slow tests.

**Slow format threshold:** A format directory with L1 runtime >60 seconds is a slow-format candidate.

## Flaky Test Policy

A test is flaky if it fails non-deterministically across identical runs.

**Confirmation:** 3-run rule — must fail in 2 of 3 identical runs.

**Quarantine:** Apply `@pytest.mark.skip(reason="QUARANTINE: {cause}. Owner: {owner}. Review by: {date}")`.
Register in `registry/slow-test-ledger.yaml` under the `flaky_tests` section.

**Expiry:** Quarantined tests older than 30 days without a fix are escalated to deletion review.

## Evidence Declaration — Required Test Layer Fields

Include these fields in every sprint's `evidence-declaration.yaml`:

```yaml
# Test layer fields (advisory — not schema-enforced as of 2026-06-18)
test_layer: 3                          # int: highest layer run (0–6)
test_layer_name: "integration"         # str: layer name
test_layer_reason: "tools/supervisor/ changed"  # str: why this layer was chosen
full_suite_required: false             # bool: was L6 mandatory for this sprint?
full_suite_run: false                  # bool: was L6 actually run?
full_suite_reason: "Change scope is docs/tools/registry — no L6-triggering files modified"
full_suite_shards_run: []             # list: shard IDs completed (e.g., [1, 2])
full_suite_shards_not_run: [1,2,3,4]  # list: shard IDs not run
# Failure fields
known_failures: []                     # list: pre-existing failures from ledger
new_failures: []                       # list: failures not in known ledger (require rework)
# Slow/flaky tracking
slow_tests_identified: []              # list: tests flagged as slow this sprint
flaky_tests_identified: []            # list: tests confirmed flaky this sprint
```
