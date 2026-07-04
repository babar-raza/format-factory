---
version: "1.0"
last-updated: "2026-07-04"
phase-available: "all"
gate-required: null
created-by: sparkling-waddling-narwhal
spec_qname_required: "false"
overflow_split_allowed: "false"
product_track: "packaging"
---

# /sync-installed-packages

## Purpose

Audit and repair the Python editable-install environment for all 20 Format Factory
FOSS packages. Detects stale module directories in `.venv/Lib/site-packages/` that
defeat editable installs, removes them, creates PTH files where missing, runs all 20
consumer roundtrip scripts, and captures dated execution evidence.

Resolves the dual-code-identity problem: imports serving stale installed code instead
of current `src/python/` source.

## When to Use

- After adding new source files to `src/python/{format}/` that are not reflected in the installed package
- After any sprint that modifies PRODUCT_SOURCE items in `src/python/`
- When `V137 validate_no_stale_installed_packages` fires in governance validators
- When consumer proof scripts pass but tests are failing (indicates code divergence)
- As a periodic environment health check
- After cloning the repo in a new environment

## Steps

### Phase 1: Staleness Audit

1. **Find site-packages dir**: locate `.venv/Lib/site-packages/` (Windows) or
   `.venv/lib/python*/site-packages/` (Linux/macOS)

2. **For each of the 20 formats** (`abw csv dif fodg fodp fods fodt gnumeric
   ndjson ods odt pbm pgm ppm qoi sylk toml tsv xcf zst`):

   a. Check if `site-packages/{fmt}/` directory exists (module dir = potential stale copy)
   b. If module dir exists AND `src/python/{fmt}/` also exists: stale copy confirmed
   c. For each `.py` file present in both: compute MD5 checksum — diverged = stale file
   d. For files in site-packages but NOT in source: ghost file (deleted from source)
   e. Record: format, stale_count, ghost_count, total_sp_files

3. **Check for PTH editable markers**: list `site-packages/__editable__*{fmt}*.pth`
   and `site-packages/__editable__*format_factory_dev*.pth`

4. **Print staleness summary table**:
   ```
   Format    Module dir?   Stale files   Ghost files   PTH exists?   Status
   fods      YES           8             2             YES           STALE_COPY_DEFEATING_EDITABLE
   abw       no            N/A           N/A           YES           EDITABLE_OK
   ```

### Phase 2: Repair

For each format in STALE_COPY state:

1. **Delete the stale module directory**: `shutil.rmtree(site-packages/{fmt}/)` — this
   re-activates any existing PTH-based editable install for that format

2. **If no PTH file exists for this format**: create one:
   ```
   Path(site-packages / f"__editable__.format_factory_{fmt}-0.1.0.dev0.pth")
       .write_text(str(repo_root / "src" / "python") + "\n")
   ```

3. **Verify the repair**: run `.venv/Scripts/python -c "import {fmt}; print({fmt}.__path__[0])"`
   — confirm output contains `src/python`

4. **Special case — CSV**: `import csv` always resolves to Python stdlib `csv.py`. The
   PTH file is created (enables submodule imports like `from csv.csv_parser import ...`)
   but `csv.__path__` will not be accessible via plain `import csv`. Document as
   VALID_DEFERRED in the repair log.

### Phase 3: Consumer Proof Evidence Capture

1. Run `tools/consumer_proof_runner.py`:
   ```
   .venv/Scripts/python tools/consumer_proof_runner.py
   ```

2. Captures stdout from each `examples/python/{fmt}/consumer_roundtrip.py` to
   `.local/evidences/consumer-proof-{fmt}.txt`

3. Writes `.local/evidences/consumer-proof-manifest.json` with per-format:
   `{pass: bool, timestamp: ISO8601, returncode: int, output_file: path}`

4. Required result: `20/20 PASS` (or document any failures with root cause)

### Phase 4: Obligation Register Update

For any format whose evidence was newly captured or updated:

1. Read `reports/all-format-deepening/all-format-obligation-register.yaml`
2. Find the entry for that format (key: `obligation_id: ALLF-{FMT}-PY`)
3. Ensure `evidence_paths` includes both:
   - `examples/python/{fmt}/consumer_roundtrip.py`
   - `.local/evidences/consumer-proof-{fmt}.txt`
4. Write back if any entries were missing the captured evidence path

### Phase 5: Emit Skill Transcript

Write skill invocation transcript to `reports/skills-r<N>/skill-transcripts/`:
```json
{
  "skill_id": "sync-installed-packages",
  "invoked_at": "<ISO8601>",
  "formats_audited": 20,
  "stale_dirs_found": <n>,
  "stale_dirs_removed": <n>,
  "pth_files_created": <n>,
  "editable_verified": <n>,
  "consumer_proof_pass": <n>,
  "consumer_proof_fail": <n>,
  "manifest_path": ".local/evidences/consumer-proof-manifest.json",
  "verdict": "PASS | PARTIAL | FAIL",
  "csv_status": "VALID_DEFERRED_STDLIB_COLLISION"
}
```

## Required Inputs

None — the skill is self-contained. It reads the environment and acts.

Optional:
- `--formats abw,fods,fodt` — restrict to specific formats (default: all 20)
- `--dry-run` — audit only, no deletions or PTH creation

## Required Evidence

- Staleness audit table (before state)
- List of stale dirs removed
- List of PTH files created
- Import verification output for each repaired format (`{fmt}.__path__[0]` → `src/python`)
- `consumer_proof_runner.py` output (20/20 PASS required)
- Updated `consumer-proof-manifest.json` (all 20 entries with timestamps)

## Allowed Paths

- `.venv/Lib/site-packages/` — delete stale module dirs, create PTH files
- `.local/evidences/` — write consumer proof output files and manifest
- `reports/all-format-deepening/all-format-obligation-register.yaml` — update evidence paths
- `reports/skills-r<N>/skill-transcripts/` — skill transcript output

## Forbidden Paths

- `src/python/**` — no source edits
- `tests/**` — no test modification
- `plans/master-plan.md` — no master plan edits
- `registry/format-registry.yaml` — gate authority, read-only
- `.venv/Lib/site-packages/{fmt}/__init__.py` — never edit installed files, only delete dirs

## Constraints

- The PTH file content must be the absolute path to `src/python/` + newline
- Never delete a module dir without first verifying `src/python/{fmt}/` exists
- Never delete the `__editable__.format_factory_dev-0.0.0.pth` file (adds entire src/)
- CSV is a permanent exception — document VALID_DEFERRED, never fail the skill for CSV
- If `tools/consumer_proof_runner.py` exits non-zero: record failing formats, do NOT abort — capture partial evidence

## Stop Conditions

Stop and report `BLOCKED` if:
- `.venv/` directory does not exist (environment not set up)
- `src/python/` directory does not exist (repo structure broken)
- All 20 formats are already in EDITABLE_OK state AND manifest is fresh (< 24h) — report `NO_ACTION_NEEDED`

## Rollback

If anything goes wrong during Phase 2:
1. Reinstall the stale package: `pip install --force-reinstall packaging/python/{fmt}/dist/{fmt}-*.whl`
   OR
2. Re-create the module dir from source: `cp -r src/python/{fmt}/ .venv/Lib/site-packages/{fmt}/`

## Validation

Skill is complete when:
- V137 `validate_no_stale_installed_packages({changed_files: all_formats})` returns PASS
- V138 `validate_consumer_proof_evidence_exists({})` returns PASS
- Transcript written with `verdict: PASS`
- 19/20 import verifications confirm `src/python` in `__path__` (CSV is VALID_DEFERRED)

## Changelog

- 1.0 (2026-07-04): Initial version — sparkling-waddling-narwhal plan.
  Wraps TC-CPR-001 through TC-CPR-006: editable install audit+repair, consumer
  proof evidence capture, obligation register update.
