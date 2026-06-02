---
version: "1.0"
last-updated: "2026-06-02"
phase-available: "3+"
generated_by: r92-worker
---

# /add-installed-package-example

Add a standalone example that demonstrates a format's public API as if the package
were installed from PyPI/NuGet (no PYTHONPATH or project reference needed).

## Required Inputs

- `format_id`
- `language` (dotnet | python)
- `example_name` — descriptive name
- `capability_shown` — what the example demonstrates
- exact example file path

## Steps

1. Confirm sprint prompt names this skill and exact paths.
2. Write an example file that:
   - Uses only the public API (no internal imports)
   - Has a main() or equivalent entry point
   - Shows the full load → [edit] → save/export flow
   - Includes inline comments explaining each step
3. Write a smoke test (optional) that runs the example and verifies it exits 0.
4. Update examples/python/<format_id>/ or examples/net/<format_id>/ as appropriate.
5. Do not add to src/; examples are docs-adjacent.

## Allowed Paths

- `examples/python/<format_id>/**`
- `examples/net/<format_id>/**`

## Forbidden Paths

- `src/**`
- Gate/release state files

## Stop Conditions

- Example uses internal imports that bypass installed-package behavior
- Example does not run (syntax error or missing sample file)

## Output

Report example file path, capability shown, and whether smoke test passes.
