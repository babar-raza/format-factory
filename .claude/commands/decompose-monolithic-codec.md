# /decompose-monolithic-codec

Move arithmetic/analytical functions from a format's main codec/parser file into
`<format_id>_analytics.py`, reducing the main file's LOC below its baseline cap.

**Governed by:** TC-SKILL-004 (taskcards/skill-gaps/TC-SKILL-004-decompose-monolithic-codec.md)
**Skill ID:** decompose-monolithic-codec
**Lane:** F (SRC Healing)
**V46 enforcement:** This skill produces a PRODUCT_SOURCE item. A skill transcript is REQUIRED.

---

## Required Inputs

| Input | Description |
|-------|-------------|
| `format_id` | Format being healed (e.g., `fodg`) |
| `source_file` | Main codec/parser file path (e.g., `src/python/fodg/fodg_codec.py`) |
| `analytics_target_file` | Analytics destination file (e.g., `src/python/fodg/fodg_analytics.py`) |
| `functions_to_move` | List of function names to extract from source to analytics target |

---

## Allowed File Writes

- `src/python/<format_id>/<format_id>_analytics.py` — functions moved here

## Allowed File Modifications

- `src/python/<format_id>/<format_id>_codec.py` or `<format_id>_parser.py` — remove extracted functions, add delegation imports

## Forbidden File Writes

- Any other file in `src/python/`
- `__init__.py` files (unless the analytics file import is not yet wired)
- `tests/` files (backward compat tests may be run but not modified)

---

## Execution Protocol

### Step 1 — Pre-flight checks (STOP if any fail)

1. Measure LOC of `source_file` using V35 method:
   ```python
   sum(1 for _ in Path(source_file).open(encoding='utf-8', errors='replace'))
   ```
   Record as `source_loc_before`.

2. Check `analytics_target_file` LOC against its `baseline_loc_cap` in
   `registry/source-structure-baseline.json`.
   - If at or above cap: `BLOCKED_CAP_REACHED` — analytics file cannot receive more functions.

3. Verify the test suite for this format passes BEFORE any changes:
   ```
   pytest tests/python/<format_id>/ -v --tb=short
   ```
   - If tests fail before changes: `BLOCKED_BASELINE_FAILING` — fix baseline first.

### Step 2 — Extract functions

For each function in `functions_to_move`:
1. Copy function definition to `analytics_target_file`
2. In `source_file`, replace the function body with a delegation import:
   ```python
   from .<format_id>_analytics import <function_name>
   ```
   OR add at bottom of source file (if not already present):
   ```python
   try:
       from .<format_id>_analytics import *
   except ImportError:
       pass
   ```

### Step 3 — Verify backward compatibility (STOP if fails)

Run the format test suite again:
```
pytest tests/python/<format_id>/ -v --tb=short
```
- If any tests fail: `BLOCKED_NO_BACKWARD_COMPAT` — revert changes. All public function
  signatures must remain callable with the same arguments.

### Step 4 — Measure LOC reduction

Measure `source_file` LOC after extraction (V35 method). Must be less than before.
- If `source_loc_after >= source_loc_before`: `BLOCKED_NO_LOC_REDUCTION` — extraction
  failed to reduce main file. Do NOT claim reduction without measurement.

### Step 5 — Update baseline

After confirmed reduction, update `registry/source-structure-baseline.json`:
```
python tools/supervisor/update_source_baseline.py --path <source_file>
```
Note: `baseline_loc_cap` is write-once — only `loc` field is updated.

### Step 6 — Produce transcript

Write transcript to: `reports/skills-r<N>/skill-transcripts/decompose-monolithic-codec-<format_id>-<run_id>.json`

---

## Transcript Schema (Required Fields)

```json
{
  "skill_id": "decompose-monolithic-codec",
  "invocation_id": "decompose-monolithic-codec-<format_id>-<timestamp>",
  "mode": "live",
  "result": "PASS",
  "inputs": {
    "format_id": "<format_id>",
    "source_file": "<source_file>",
    "analytics_target_file": "<analytics_target_file>",
    "functions_to_move": ["<fn1>", "<fn2>"]
  },
  "actual_files_changed": ["<source_file>", "<analytics_target_file>"],
  "allowed_files": ["src/python/<format_id>/<format_id>_analytics.py", "<source_file>"],
  "tests_run": ["tests/python/<format_id>/"],
  "functions_moved": 5,
  "source_loc_before": 3176,
  "source_loc_after": 2950,
  "loc_reduction": 226,
  "backward_compat_verified": true,
  "codec_tests_pass": true
}
```

---

## Stop Conditions

| Code | Trigger | Action |
|------|---------|--------|
| `BLOCKED_CAP_REACHED` | analytics_target_file LOC ≥ its baseline_loc_cap | Do NOT move functions to this target. File a gap to increase the cap or find alternate target. |
| `BLOCKED_BASELINE_FAILING` | Tests fail BEFORE changes | Fix baseline tests first. Do NOT extract. |
| `BLOCKED_NO_BACKWARD_COMPAT` | Tests fail AFTER extraction | Revert changes. Produce transcript with result=FAIL. |
| `BLOCKED_NO_LOC_REDUCTION` | LOC not reduced after extraction | Function likely called by other functions in main file. Revert, document, stop. |

---

## Anti-Overclaim Rules

1. NEVER claim LOC reduction without measuring BEFORE and AFTER using V35 method.
2. NEVER move a function that is called by other functions in the main codec file
   (unless you also move all callers or redirect them to the analytics import).
3. NEVER mark `codec_tests_pass: true` without running the test suite after changes.
4. NEVER mark `backward_compat_verified: true` if any tests failed.
5. `loc_reduction` in transcript must be a measured integer, not an estimate.

---

## Format Status Reference

| Format | Main File | Current LOC | Cap | Analytics File | Status |
|--------|-----------|-------------|-----|---------------|--------|
| FODG | `fodg_codec.py` | 3176 | 3176 | `fodg_analytics.py` | AT CAP — monitor |
| XCF | `xcf_parser.py` | 1301 | 3997 | `xcf_analytics.py` | HEALED (2026-06-18) |
| ZST | `zst_codec.py` | 1558 | 4210 | `zst_analytics.py` | HEALED (2026-06-18) |

## Allowed Paths

- `.supervisor/ — skill registry and governance config (read/write as needed)`
- `.governance/ — governance rules and policies (read-only)`
- `.claude/commands/ — command files (read-only unless updating commands)`
- `reports/ — governance reports (write)`

## Forbidden Paths

- `src/net/**` — no .NET product source mutation
- `src/python/**` — no Python product source mutation
- `plans/strategic/**` — strategic plans are read-only

## Output Format

- PASS / FAIL / PARTIAL verdict printed to stdout
- Per-item findings list with skill_id, issue, and severity
- Report file at `reports/` with structured YAML findings
