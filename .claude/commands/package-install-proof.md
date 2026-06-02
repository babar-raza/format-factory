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
