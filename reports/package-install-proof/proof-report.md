# Package Install Proof — All Python Formats

Proves GAP-FORENSIC-001's B9 boundary: wheel build -> pip install into an
ephemeral venv -> import -> primary API smoke on the oracle sample corpus.
Canonical machine-readable source: `proof-manifest.json`. Orchestrator:
`tools/run_package_install_proof.py` via the `/package-install-proof` skill.

| # | Format | Package | Version | Import | API Smoke | Verdict | Deep-import |
|---|--------|---------|---------|--------|-----------|---------|-------------|
| 1 | abw | format-factory-abw | 0.1.0.dev0 | PASS | PASS | **PASS** | 35/36 |
| 2 | csv | format-factory-csv | 0.1.0.dev0 | FAIL | FAIL | **FAIL** | 0/0 |
| 3 | dif | format-factory-dif | 0.1.0.dev0 | PASS | PASS | **PASS** | 32/33 |
| 4 | fodg | format-factory-fodg | 0.1.0.dev0 | PASS | PASS | **PASS** | 31/32 |
| 5 | fodp | format-factory-fodp | 0.1.0.dev0 | PASS | PASS | **PASS** | 31/32 |
| 6 | fods | format-factory-fods | 0.1.0.dev0 | PASS | PASS | **PASS** | 85/88 |
| 7 | fodt | format-factory-fodt | 0.1.0.dev0 | PASS | PASS | **PASS** | 54/55 |
| 8 | gnumeric | format-factory-gnumeric | 0.1.0.dev0 | PASS | PASS | **PASS** | 30/31 |
| 9 | ipynb | format-factory-ipynb | 0.2.0.dev0 | PASS | PASS | **PASS** | 28/28 |
| 10 | mtlx | format-factory-mtlx | 0.1.0.dev0 | PASS | PASS | **PASS** | 21/22 |
| 11 | ndjson | format-factory-ndjson | 0.1.0.dev0 | PASS | PASS | **PASS** | 32/33 |
| 12 | nrrd | format-factory-nrrd | 0.2.0.dev0 | PASS | PASS | **PASS** | 16/16 |
| 13 | ods | format-factory-ods | 0.1.0.dev0 | PASS | PASS | **PASS** | 36/37 |
| 14 | odt | format-factory-odt | 0.1.0.dev0 | PASS | PASS | **PASS** | 34/35 |
| 15 | pbm | format-factory-pbm | 0.1.0.dev0 | PASS | PASS | **PASS** | 18/18 |
| 16 | pgm | format-factory-pgm | 0.1.0.dev0 | PASS | PASS | **PASS** | 16/16 |
| 17 | ppm | format-factory-ppm | 0.1.0.dev0 | PASS | PASS | **PASS** | 17/17 |
| 18 | qoi | format-factory-qoi | 0.1.0.dev0 | PASS | PASS | **PASS** | 18/18 |
| 19 | safetensors | format-factory-safetensors | 0.2.0.dev0 | PASS | PASS | **PASS** | 21/21 |
| 20 | sylk | format-factory-sylk | 0.1.0.dev0 | PASS | PASS | **PASS** | 33/34 |
| 21 | toml | format-factory-toml | 0.1.0.dev0 | PASS | PASS | **PASS** | 32/33 |
| 22 | tsv | format-factory-tsv | 0.1.0.dev0 | PASS | PASS | **PASS** | 32/33 |
| 23 | ubl | format-factory-ubl | 0.1.0.dev0 | PASS | PASS | **PASS** | 16/18 |
| 24 | xcf | format-factory-xcf | 0.1.0.dev0 | PASS | PASS | **PASS** | 18/18 |
| 25 | xliff | format-factory-xliff | 0.1.0.dev0 | PASS | PASS | **PASS** | 16/18 |
| 26 | zst | format-factory-zst | 0.1.0.dev0 | PASS | PASS | **PASS** | 17/17 |

**25/26 PASS**

## Failures

- **csv**: import=FAIL: AssertionError: csv resolved to C:\Python313\Lib\csv.py, not to site-packages C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\worktrees\ff-six-python-production\.local\package-install-p smoke=FAIL: ModuleNotFoundError: No module named 'csv.csv_parser'; 'csv' is not a package

## Deep-import findings (non-verdict; converter modules assuming repo layout)

These submodules fail to import from the installed wheel. The B9 verdict
covers package import + primary API; these are registered as a separate gap.

- **abw**: 1/36 failing — abw.abw_to_csv
- **dif**: 1/33 failing — dif.dif_to_csv
- **fodg**: 1/32 failing — fodg.fodg_to_csv
- **fodp**: 1/32 failing — fodp.fodp_to_csv
- **fods**: 3/88 failing — fods.Compat, fods.fods.Compat, fods.fods_to_csv
- **fodt**: 1/55 failing — fodt.fodt_to_csv
- **gnumeric**: 1/31 failing — gnumeric.gnumeric_to_csv
- **mtlx**: 1/22 failing — mtlx.mtlx_to_csv
- **ndjson**: 1/33 failing — ndjson.ndjson_to_csv
- **ods**: 1/37 failing — ods.ods_to_csv
- **odt**: 1/35 failing — odt.odt_to_csv
- **sylk**: 1/34 failing — sylk.sylk_to_csv
- **toml**: 1/33 failing — toml.toml_to_csv
- **tsv**: 1/33 failing — tsv.tsv_to_csv
- **ubl**: 2/18 failing — ubl._build_backend, ubl.ubl_to_csv
- **xliff**: 2/18 failing — xliff._build_backend, xliff.xliff_to_csv

## Evidence chain

wheel sha256 + complete proof-input digest per format are in `proof-manifest.json`;
junit XML at `.local/package-install-proof-results-*.xml`;
staleness is enforced by the package-install-proof coverage governance validator.
