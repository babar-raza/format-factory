# /add-python-object-model-feature

Add a new object-model feature to a Python FOSS product (fods, fodt, pbm, pgm, ppm, sylk, zst).

## Usage

```
/add-python-object-model-feature
```

## What This Skill Does

1. **Pre-flight**: Reads `.supervisor/skill-registry.yaml` and `reports/r90/product-code-change-ledger.json`
2. **Plan**: Determines the target Python module and feature to add
3. **Implement**: Adds the feature to `src/python/<format>/` following existing patterns
4. **Test**: Creates a test in `tests/python/<format>/test_r<run>_<feature>.py`
5. **Ledger**: Adds a `GOVERNED_PRODUCT_CHANGE` entry to `reports/r90/product-code-change-ledger.json`
6. **Verify**: Runs `python -m pytest tests/python/<format>/test_r<run>_<feature>.py -v`

## Constraints

- One feature at a time
- Must add or modify Python source in `src/python/`
- Must create at least 4 new test functions
- Must add ledger entry with SHA-256 before and after
- No direct src edits without this skill or explicit execution handoff

## Evidence Required

- Source file path
- Pre-change SHA-256
- Post-change SHA-256
- Test file path
- Test count and pass result
- Ledger entry ID

## Ledger Entry Format

```json
{
  "entry_id": "R<N>-GOVERNED-PYTHON-<FORMAT>-<FEATURE>-001",
  "sprint": "R<N>",
  "classification": "GOVERNED_PRODUCT_CHANGE",
  "skill_used": "/add-python-object-model-feature",
  "source_files": [{"path": "src/python/<format>/...", "sha256_before": "...", "sha256_after": "..."}],
  "tests_added": ["tests/python/<format>/test_r<n>_<feature>.py"],
  "test_count": <n>,
  "description": "<feature> added to <format>"
}
```
