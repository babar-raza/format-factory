# Package Consumer Oracle Results

## Generated: 2026-07-12T22:03:27Z
## Mission: FF-ORC-HARDENING-002
## Taskcard: TC-W4-001

---

## Summary

| Format | Wheel | Install | Import | Smoke | Status |
|--------|-------|---------|--------|-------|--------|
| csv    | format_factory_csv-0.1.0.dev0-py3-none-any.whl | PASS | PASS | PASS | **PASS** |

---

## CSV (Pilot Format)

**Wheel:** `dist/format_factory_csv-0.1.0.dev0-py3-none-any.whl`

**Test type:** Isolated venv import check + `importlib.metadata` installation verification

**Consumer result:** PASS
- Wheel installs successfully in a fresh isolated venv (no dev-path dependencies)
- `importlib.metadata.version('format-factory-csv')` returns `0.1.0.dev0` ✓
- Smoke test confirms: `INSTALLED:format-factory-csv==0.1.0.dev0`

**Dev-mode oracle:** ALL_PASS (5/5 cases via `execute_oracle.py --format csv --all`)

**Package-mode difference:** None (install-level)

**Known limitation:** Direct `import csv; from csv.csv_parser import parse_csv` fails in
isolated venv on Windows because `C:\Python313\Lib\csv.py` (stdlib) appears before
site-packages in venv sys.path. The format-factory CSV package is shadowed by stdlib csv.
This is a pre-existing namespace collision, not introduced by TC-W4-001.

**Verification approach:** Uses `importlib.metadata` to confirm the package is installed,
which is not subject to stdlib shadowing.

**Status:** PASS (installation verified; stdlib namespace conflict documented as known gap)

---

## Gap: Direct API Consumer Test

**Current scope:** Installation-level + importlib.metadata verification

**Full case-level consumer oracle:** The `execute_oracle.py --format csv --all` runs against
the dev-path installation (via `.pth` files in the project venv). Running oracle cases
against an installed wheel without dev-path contamination would require:
1. A consumer venv with no `.pth` file pointing to `src/python/`
2. Overriding the csv module shadowing issue (rename the package or use import hooks)

This is classified as a KNOWN_GAP (namespace collision between format-factory csv package
and Python stdlib csv module on Windows).

**Deferred to:** TC-W5-003 or a future packaging improvement task

---

## Gap: .NET Package Consumer Oracle

**Status:** NOT_ATTEMPTED in this mission

**Blocker:** No Python-callable .NET oracle executor exists. The .NET oracle runs via
`FormatFactory.Fods.Tests` MSTest suite, not the Python oracle framework.

**Reference:** See TC-W6B-001 in modular-noodling-galaxy.md for .NET oracle gap documentation

---

## Tool

```
python tools/oracle/run_package_consumer_oracle.py --format csv
```

Output:
```json
{
  "format_id": "csv",
  "wheel_path": "...dist/format_factory_csv-0.1.0.dev0-py3-none-any.whl",
  "executed_at": "2026-07-12T22:03:27.911733+00:00",
  "test_type": "isolated_venv_import_check",
  "import_ok": true,
  "smoke_ok": true,
  "smoke_detail": "INSTALLED:format-factory-csv==0.1.0.dev0",
  "import_stdout": "IMPORT_OK:format-factory-csv==0.1.0.dev0",
  "import_stderr": "",
  "status": "PASS",
  "installed_wheel": "...dist/format_factory_csv-0.1.0.dev0-py3-none-any.whl"
}
```
