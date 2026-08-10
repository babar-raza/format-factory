# Package Install Proof — All Python Formats

Proves GAP-FORENSIC-001's B9 boundary: wheel build -> pip install into an
ephemeral venv -> import -> primary API smoke on the oracle sample corpus.
Canonical machine-readable source: `proof-manifest.json`. Orchestrator:
`tools/run_package_install_proof.py` via the `/package-install-proof` skill.

| # | Format | Package | Version | Import | API Smoke | Verdict | Deep-import |
|---|--------|---------|---------|--------|-----------|---------|-------------|
| 1 | abw | format-factory-abw | 0.1.0.dev0 | PASS | PASS | **PASS** | 31/33 |
| 2 | csv | format-factory-csv | 0.1.0.dev0 | PASS | PASS | **PASS** | 29/31 |
| 3 | dif | format-factory-dif | 0.1.0.dev0 | PASS | PASS | **PASS** | 0/0 |
| 4 | fodg | format-factory-fodg | 0.1.0.dev0 | PASS | PASS | **PASS** | 32/33 |
| 5 | fodp | format-factory-fodp | 0.1.0.dev0 | PASS | PASS | **PASS** | 28/29 |
| 6 | fods | format-factory-fods | 0.1.0.dev0 | PASS | PASS | **PASS** | 47/49 |
| 7 | fodt | format-factory-fodt | 0.1.0.dev0 | PASS | PASS | **PASS** | 51/52 |
| 8 | gnumeric | format-factory-gnumeric | 0.1.0.dev0 | PASS | PASS | **PASS** | 28/29 |
| 9 | ipynb | format-factory-ipynb | 0.2.0.dev0 | PASS | PASS | **PASS** | 31/31 |
| 10 | mtlx | format-factory-mtlx | 0.1.0.dev0 | PASS | PASS | **PASS** | 21/22 |
| 11 | ndjson | format-factory-ndjson | 0.1.0.dev0 | PASS | PASS | **PASS** | 30/31 |
| 12 | nrrd | format-factory-nrrd | 0.2.0.dev0 | PASS | PASS | **PASS** | 23/23 |
| 13 | ods | format-factory-ods | 0.1.0.dev0 | PASS | PASS | **PASS** | 34/35 |
| 14 | odt | format-factory-odt | 0.1.0.dev0 | PASS | PASS | **PASS** | 31/32 |
| 15 | ora | format-factory-ora | 0.1.0.dev0 | PASS | PASS | **PASS** | 14/14 |
| 16 | pbm | format-factory-pbm | 0.1.0.dev0 | PASS | PASS | **PASS** | 18/18 |
| 17 | pgm | format-factory-pgm | 0.1.0.dev0 | PASS | PASS | **PASS** | 16/16 |
| 18 | ppm | format-factory-ppm | 0.1.0.dev0 | PASS | PASS | **PASS** | 17/17 |
| 19 | qoi | format-factory-qoi | 0.1.0.dev0 | PASS | PASS | **PASS** | 18/18 |
| 20 | safetensors | format-factory-safetensors | 0.2.0.dev0 | PASS | PASS | **PASS** | 21/21 |
| 21 | sylk | format-factory-sylk | 0.1.0.dev0 | PASS | PASS | **PASS** | 31/32 |
| 22 | toml | format-factory-toml | 0.1.0.dev0 | PASS | PASS | **PASS** | 29/30 |
| 23 | tsv | format-factory-tsv | 0.1.0.dev0 | PASS | PASS | **PASS** | 31/32 |
| 24 | ubl | format-factory-ubl | 0.2.0.dev0 | PASS | PASS | **PASS** | 43/43 |
| 25 | xcf | format-factory-xcf | 0.1.0.dev0 | PASS | PASS | **PASS** | 19/19 |
| 26 | xliff | format-factory-xliff | 0.2.0.dev0 | PASS | PASS | **PASS** | 24/24 |
| 27 | zst | format-factory-zst | 0.1.0.dev0 | PASS | PASS | **PASS** | 18/18 |

**27/27 PASS**

## Deep-import findings (non-verdict; converter modules assuming repo layout)

These submodules fail to import from the installed wheel. The B9 verdict
covers package import + primary API; these are registered as a separate gap.

- **abw**: 2/33 failing — abw.abw_to_csv, abw.abw_to_dif
- **csv**: 2/31 failing — ff_csv.csv_to_ods, ff_csv.csv_to_odt
- **fodg**: 1/33 failing — fodg.fodg_to_csv
- **fodp**: 1/29 failing — fodp.fodp_to_csv
- **fods**: 2/49 failing — fods.Compat, fods.fods_to_csv
- **fodt**: 1/52 failing — fodt.fodt_to_csv
- **gnumeric**: 1/29 failing — gnumeric.gnumeric_to_csv
- **mtlx**: 1/22 failing — mtlx.mtlx_to_csv
- **ndjson**: 1/31 failing — ndjson.ndjson_to_csv
- **ods**: 1/35 failing — ods.ods_to_csv
- **odt**: 1/32 failing — odt.odt_to_csv
- **sylk**: 1/32 failing — sylk.sylk_to_csv
- **toml**: 1/30 failing — toml.toml_to_csv
- **tsv**: 1/32 failing — tsv.tsv_to_csv

## Evidence chain

wheel sha256 + complete proof-input digest per format are in `proof-manifest.json`;
junit XML at `.local/package-install-proof-results-*.xml`;
staleness is enforced by the package-install-proof coverage governance validator.
