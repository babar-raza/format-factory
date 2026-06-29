# Oracle

Oracle test execution framework — canonical test case definitions and executors per format.

## Contents

- **`formats/`** — Per-format oracle test packages (20 formats)
- **`registry/`** — Oracle case registry
- **`reports/`** — Per-format oracle run summaries
- **`schema/`** — Oracle case schema definitions
- **`shared/`** — Shared oracle utilities

## Format Coverage

All 20 product formats have oracle test definitions. 4 formats excluded (ora, pam, xpm, zpaq — no product implementations).

## Governance

- **Classification:** CORE_PRODUCT
- **Layer:** L05 (Oracle)
- **Producers:** developers, oracle tools
- **Consumers:** tests, supervisor, certification
- **Registry:** `registry/repository-root-folders.yaml`
