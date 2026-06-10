---
version: "1.1"
last-updated: "2026-06-03"
phase-available: "3+"
gate-required: null
generated_by: claude
visibility: generated
---

# /package-install-proof

Prove that a Format Factory Python package can be installed and imported successfully.

## Usage

```
/package-install-proof
```

## What This Skill Does

1. **List packages**: Reads `packaging/` directory for available wheel/sdist
2. **Install**: Runs `pip install <wheel>` in the active venv
3. **Import test**: Runs `python -c "import <package>; print(<package>.__version__)"`
4. **API smoke test**: Calls the core API (e.g., `parse_fods()`, `write_csv()`)
5. **Write proof**: Creates `reports/r<n>/package-install-proof.md` with results

## Constraints

- Must install from a physical wheel file (not `pip install -e .`)
- Must verify `import <format>` works (not `import aspose_format_factory_<format>`)
- If wheel doesn't exist, report WHEEL_MISSING and stop
- If import fails, report INSTALL_FAIL with error message

## Evidence Required

- Package name and version
- Wheel file path
- Install command output
- Import test result
- API smoke test result: PASS | FAIL | SKIP

## Output Format

```
| Package | Wheel | Import | API Smoke |
|---------|-------|--------|-----------|
| fods    | 0.1.0.dev0 | import fods: OK | workbook_to_csv: OK |
| fodt    | 0.1.0.dev0 | import fodt: OK | document_to_text: OK |
```

## Allowed Paths

- `packaging/` (read-only, wheel source)
- `reports/r<n>/` (proof output)

## Forbidden Paths

- `src/**` (no source edits)
- `registry/format-registry.yaml` (gate authority)
- `plans/master-plan.md` (operational authority)

## Rollback

1. Remove proof report `reports/r<n>/package-install-proof.md`
2. Uninstall the package if needed: `pip uninstall <package>`

## Validation

Complete when: wheel installs, import succeeds, and API smoke test result is documented (PASS, FAIL, or SKIP).

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, format_id, package_name, wheel_path, import_result, smoke_result, verdict.

## Changelog

- 1.0 (2026-06-02): Initial version
- 1.1 (2026-06-03): Added frontmatter, allowed/forbidden paths, rollback, changelog (Skills R99)
- 1.2 (2026-06-03): Added validation, transcript requirement (Skills R101).
