# /implement-spec-stub

Fill ONE `architecture_only` spec/ stub file with behavioral implementation,
proving equivalence to the existing `models.py` implementation via tests.

**Governed by:** TC-SKILL-003 (taskcards/skill-gaps/TC-SKILL-003-implement-spec-stub.md)
**Skill ID:** implement-spec-stub
**Lane:** F (SRC Healing), D (Missing Skill Workflow)
**V46 enforcement:** This skill produces a PRODUCT_SOURCE item. A skill transcript is REQUIRED.

---

## Step 0 — Execution Manifest (run BEFORE any other step)

```
python -m tools.governance.skills_first.manifest create \
  --task-id <task_id> --agent-type CLAUDE_CODE \
  --operation "<one-line description of this invocation>" \
  --skill implement-spec-stub \
  --allowed-paths src/python/<format_id>/spec/** \
  --write
```

Record the printed `execution_id`. On `ManifestError`, STOP -- do not proceed
until the manifest is created. This is what lets the tool-layer skill gate
(`tools/supervisor/coordination/hooks/skill_gate.py`) recognize this invocation
as `MANIFEST_COVERING` instead of blocking it once `check_mode:skill_resolution`
is promoted to `enforcing` for `src/python/<format_id>/spec/`.

## Required Inputs

| Input | Description |
|-------|-------------|
| `format_id` | Format being healed (e.g., `fodt`) |
| `stub_path` | Relative path to the architecture_only stub (e.g., `src/python/fodt/spec/text/paragraph.py`) |
| `spec_qname` | ODF QName for this spec element (e.g., `text:p`) |
| `behavioral_equivalence_test_path` | Path to the test that proves equivalence (e.g., `tests/python/fodt/test_compat_bootstrap.py`) |

---

## Allowed File Writes

- `src/python/<format_id>/spec/**/*.py` — ONLY the named stub_path (one stub per invocation)
- `src/python/<format_id>/compat.py` — ONLY to activate the stub import AFTER tests pass
- `tests/python/<format_id>/test_compat_bootstrap.py` — equivalence test skeleton/updates

## Forbidden File Writes

- `src/python/<format_id>/models.py` — reference implementation, must NOT change
- `src/python/<format_id>/parser.py` — not in scope
- `src/python/<format_id>/writer.py` — not in scope
- Any file outside the above allowed paths
- Any other spec/ stub not named in `stub_path` (one stub per invocation)

---

## Execution Protocol

### Step 1 — Pre-flight checks (STOP if any fail)

1. Verify `stub_path` exists and contains `# GENERATED — architecture_only` marker.
   - If marker absent: `BLOCKED_NOT_A_STUB` — this file is not a governed stub.
2. Verify `spec_qname` exists in `shared/qname-registry/<format_id>.yaml`.
   - If absent: `BLOCKED_NO_QNAME_RECORD` — register the QName first.
3. Verify `behavioral_equivalence_test_path` exists and the test suite passes for the
   corresponding models.py class BEFORE any changes.
   - If test file absent: create skeleton, STOP, wait for next invocation.
   - If tests fail before changes: `BLOCKED_BASELINE_FAILING` — fix baseline first.

### Step 2 — Implement the stub

Replace `pass` / `# TODO: implement` content with real implementation that:
- Maps to the spec_qname element's attributes and methods
- Delegates to or mirrors the equivalent class in `models.py`
- Removes the `# GENERATED — architecture_only` marker
- Adds `spec_qname = "<qname>"` class attribute

### Step 3 — Verify equivalence (STOP if fails)

Run: `pytest <behavioral_equivalence_test_path> -v`
- If any test fails: `BLOCKED_EQUIVALENCE_FAILURE` — revert stub changes, do NOT proceed.
- `behavioral_regression_count` in transcript MUST equal 0.

### Step 4 — Update compat.py (conditional)

Only update `compat.py` to import from spec/ if ALL of:
- The stub passes equivalence tests
- The stub's spec_qname status is updated to `implemented` in `shared/qname-registry/<format_id>.yaml`
- The bootstrap rule comment in `compat.py` explicitly permits this stub

### Step 5 — Produce transcript

Write transcript to: `reports/skills-r<N>/skill-transcripts/implement-spec-stub-<format_id>-<run_id>.json`

---

## Transcript Schema (Required Fields)

```json
{
  "skill_id": "implement-spec-stub",
  "invocation_id": "implement-spec-stub-<format_id>-<stub_basename>-<timestamp>",
  "mode": "live",
  "result": "PASS",
  "inputs": {
    "format_id": "<format_id>",
    "stub_path": "<stub_path>",
    "spec_qname": "<spec_qname>",
    "behavioral_equivalence_test_path": "<test_path>"
  },
  "actual_files_changed": ["<stub_path>"],
  "allowed_files": ["src/python/<format_id>/spec/...", "tests/python/<format_id>/test_compat_bootstrap.py"],
  "tests_run": ["<behavioral_equivalence_test_path>"],
  "architecture_only_stubs_filled": 1,
  "stub_path": "<stub_path>",
  "spec_qname": "<spec_qname>",
  "architecture_only_before": true,
  "architecture_only_after": false,
  "equivalence_proof_path": "<behavioral_equivalence_test_path>",
  "behavioral_regression_count": 0
}
```

---

## Stop Conditions

| Code | Trigger | Action |
|------|---------|--------|
| `BLOCKED_NOT_A_STUB` | Stub path missing architecture_only marker | Do NOT proceed. File a gap if needed. |
| `BLOCKED_NO_QNAME_RECORD` | spec_qname not in qname-registry | Register QName first via spec-literal-qname-to-code-mapping skill. |
| `BLOCKED_BASELINE_FAILING` | Equivalence tests fail BEFORE stub changes | Fix test baseline. Do NOT modify stub. |
| `BLOCKED_EQUIVALENCE_FAILURE` | Equivalence tests fail AFTER stub changes | Revert stub. Produce transcript with result=FAIL. |

---

## Anti-Overclaim Rules

1. NEVER mark `architecture_only_after: false` without a passing equivalence test run.
2. NEVER claim FODT Bootstrap complete until ALL 11 stubs are implemented and tested.
3. NEVER modify more than one stub per invocation.
4. NEVER update compat.py imports until the stub's equivalence test passes AND qname-registry is updated.
5. NEVER claim stub is implemented if `behavioral_regression_count > 0`.

---

## Execution Order (Recommended)

Lowest complexity first:
1. `spec/meta.py`
2. `spec/settings.py`
3. `spec/manifest.py`
4. `spec/document.py`
5. `spec/body.py`
6. `spec/styles.py`
7. `spec/text/` stubs (paragraph, span)
8. `spec/table/` stubs (table, row, cell)
9. `spec/drawing.py`
10. `spec/formula.py`

## Allowed Paths

- `src/python/<format_id>/ — spec literal source (read/write)`
- `tools/spec/ — healing tools (read-only)`
- `reports/spec/ — healing reports (write)`

## Forbidden Paths

- `src/net/**` — .NET source is out of scope for Python spec healing
- `plans/strategic/**` — strategic plans are read-only

## Output Format

- Structured result written to `reports/` in YAML or JSON format
- Human-readable summary printed to stdout
- Verdict: PASS / FAIL with per-item evidence
