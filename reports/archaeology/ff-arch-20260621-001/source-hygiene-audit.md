# Source Hygiene Audit — ff-arch-20260621-001

## Summary

Source hygiene is POOR. Build artifacts, duplicate package nesting, and committed
temporary files all pollute the source inventory and risk corrupting import resolution.

## Issues Found

### 1. 21 .egg-info directories committed to git (HIGH SEVERITY)

All Python package egg-info directories are tracked in git:
- `src/python/format_factory_abw.egg-info/`
- `src/python/format_factory_csv.egg-info/`
- ... (19 more)

**Impact**: Pollutes git status; risks outdated metadata; non-reproducible builds.
**Fix**: Add `*.egg-info/` to `.gitignore` and remove from tracking.

### 2. `src/format_factory_dev.egg-info/` at root of src/ (HIGH SEVERITY)

Development install artifact at top level of src/. Not source code.
**Fix**: Remove from git tracking.

### 3. `src/src.zip` — source archive artifact (MEDIUM SEVERITY)

A ZIP of the source tree committed alongside the source. Stale artifact.
**Fix**: Remove from git. Use git archives for distribution.

### 4. FODS triple package nesting (BLOCKER)

```
src/python/fods/
src/python/fods/fods/
src/python/fods/fods/fods/
```

All three levels contain the same `__init__.py`, `parser.py`, `writer.py`, etc.
- Creates ambiguous import paths
- Installed package may resolve to wrong level
- Makes source-level audits unreliable (unclear which level is canonical)

**Fix**: Flatten to `src/python/fods/{module}.py` only. Remove duplicate `fods/fods/` nesting.

### 5. `__pycache__/` directories present (LOW SEVERITY)

Multiple `__pycache__` directories found throughout `src/` and `tools/`.
Should be in `.gitignore` and not tracked.

### 6. Committed `.local/` outputs mixed into evidence discussion

`.local/` directory contains session state, spec cache, evidence bundles.
These are correctly NOT tracked (in `.gitignore` presumably) but are referenced
extensively from committed files, creating broken paths in committed reports.

## Recommendation Summary

| Issue | Severity | Action |
|-------|----------|--------|
| 21 egg-info dirs | HIGH | gitignore + rm from tracking |
| src/format_factory_dev.egg-info | HIGH | gitignore + rm |
| src/src.zip | MEDIUM | rm from git |
| FODS triple nesting | BLOCKER | flatten package structure |
| __pycache__ dirs | LOW | confirm in .gitignore |
| Stale generated code | MEDIUM | audit per format |

## Impact on Audits

**Source audits are partially polluted.** When counting Python source files, the
`fods/fods/fods/` nesting artificially triples the FODS file count. When Python
resolves imports, the egg-info metadata determines which package root is used —
meaning the outer `src/python/fods/__init__.py` may NOT be the one executed.

All metrics in this audit account for this pollution and report on the canonical
(innermost or egg-info-resolved) package where discernible.
