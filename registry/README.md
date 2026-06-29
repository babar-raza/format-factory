# Registry

Canonical registries, baselines, and ledgers for format governance.

## Contents

- **`format-registry.yaml`** - Canonical format registry (25 formats)
- **`repository-root-folders.yaml`** - Root folder catalog (this directory's own governance)
- **`source-structure-baseline.json`** - Source LOC/function baselines with violation tracking
- **`product-deepening-ledger.yaml`** - Product deepening task ledger
- **`format-completion-matrix.yaml`** - Format completion status
- **`parity-matrix.yaml`** - Spec parity status
- **`known-failure-ledger.yaml`** - Known test failure tracking
- **`candidates/`** - Format candidates under evaluation

## Governance

- **Classification:** GOVERNANCE_INFRA
- **Producers:** developers, sync tools, governance validators
- **Consumers:** all tools, supervisor, validators, agents
- **Manual editing:** Partially - registries are authored, baselines have write-once fields
- **Registry:** `registry/repository-root-folders.yaml`
