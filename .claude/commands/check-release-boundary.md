# /check-release-boundary

Verify that no commercial artifacts are in the OSS release scope (Phase 3+ governance).

## Usage

```
/check-release-boundary
```

No arguments required. Scans the full repository.

## What This Command Does

1. **Load commercial format list** — Identify all formats with `commercial_product_ready: true` or commercial .NET source
2. **Scan OSS-designated paths** — Check `src/python/`, `examples/python/`, `tests/python/` for commercial leakage
3. **Check license headers** — Confirm no proprietary license headers in OSS-scoped files
4. **Check packaging manifests** — Verify commercial packages are not listed in OSS wheel configurations
5. **Report violations** — List any boundary violations found

## Release Boundary Rules

### OSS-Safe (can be in any release):
- `src/python/` — Python FOSS codecs/parsers
- `examples/python/` — Python usage examples
- `tests/python/` — Python test files
- `packaging/python/` — Python wheel build scripts

### Commercial-Only (must NOT appear in OSS release):
- Any file in `src/dotnet/` or `src/csharp/`
- Any file with `commercial_allowed: true` and `open_source_allowed: false`
- NuGet package specs
- Gate 11 commercial API implementations

## Steps

```
1. Load registry/format-registry.yaml → identify commercial formats
2. Load product-capability-matrix/poc-targets.yaml → identify commercial_product_ready: true
3. Scan packaging/python/ → confirm no commercial deps in Python wheel manifests
4. Scan src/python/ → confirm no .NET/commercial code imports
5. Check .gitignore and .claude/settings.json → confirm commercial paths are excluded
6. For each violation found:
   - File path
   - Violation type (license, import, manifest)
   - Recommended action
7. Write reports/release-boundary-check-<date>.md
```

## Output Format

```
# Release Boundary Check
**Date:** <date>
**Status:** CLEAN / VIOLATIONS_FOUND

## OSS-Safe Paths: PASS / FAIL
- src/python/: CLEAN (no commercial leakage)
- examples/python/: CLEAN

## Violations (if any)
| File | Violation | Action |
|------|-----------|--------|
...

## Commercial Paths (correctly excluded)
...
```

## Validation

Complete when:
- `reports/release-boundary-check-<date>.md` exists
- All paths scanned (no UNKNOWN status)
- Violations listed (even if zero)

## Allowed Paths

- `registry/ — format registry (read-only unless updating registry)`
- `reports/ — acquisition reports (write)`
- `plans/ — acquisition plans (read/write)`

## Forbidden Paths

- `src/net/**` — no product source mutation during acquisition
- `src/python/**` — no product source mutation during acquisition
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid
