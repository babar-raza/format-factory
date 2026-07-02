# /sync-readmes

Run the preservation-first README sync pipeline for all per-format READMEs.

## What This Command Does

1. Collects format metadata from registries, package manifests, QName registries, and test/source file counts.
2. Splices generated README blocks between `<!-- BEGIN:README-* -->` markers.
3. Preserves maintained README prose, examples, frontmatter, warnings, limitations, and references.
4. Validates README markers and generated package claims.
5. Confirms no timestamp-stripped drift remains.

## Command

```bash
python tools/readme_sync/run_sync.py --mode full
```

## Validation

```bash
python tools/readme_sync/run_sync.py --mode validate
python tools/readme_sync/run_sync.py --mode drift-only
python -m pytest tests/tools/test_readme_sync.py -q
```

## skill_id

sync-readmes

## Required Inputs

- `dry_run` — if `true`, print planned changes without writing (default: `false`)

## Allowed Paths

- `tools/readme_sync/run_sync.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no product source mutation
- `src/python/**` — no product source mutation
- `plans/strategic/**` — strategic plans are read-only
- `.supervisor/skill-registry.yaml` — skill registry is read-only here

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid

## Output Format

- Summary of items synced, added, removed, or unchanged
- Report file at `reports/` confirming final state
- Exit code 0 on success; non-zero with error message on failure
