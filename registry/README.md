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

## Agent Navigation

**Purpose of this folder:** Canonical registries and baselines for format governance.
Created and maintained by developers, sync tools, and governance validators.

**To register a new format:** Add an entry to `registry/format-registry.yaml` under `formats:`.
Include `format_id`, display name, scoring data, and gate fields. Run `python tools/capability_sync/run_sync.py` afterward.

**To register a new root folder:** Add an entry to `registry/repository-root-folders.yaml` under `folders:`.
Required fields: `folder_path`, `retention` (RETAIN/DELETED/EXEMPT), `readme_required`.
Validation command: `python tools/supervisor/governance_validators_root_struct.py`

**Key write-once rule:** `source-structure-baseline.json` fields `baseline_loc_cap` and
`baseline_functions_cap` are write-once. Run `python tools/validators/source_structure_validator.py`
to validate compliance. Never increase existing caps.

**Producer:** Developers author registries. `tools/capability_sync/run_sync.py` updates
derived fields. `tools/supervisor/governance_validators_root_struct.py` validates the root-folder registry.
