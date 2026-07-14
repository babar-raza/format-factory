# Source Code

Product source code for all Format Factory libraries.

## Contents

- **`python/`** — Python FOSS libraries (20 format modules + `_shared/`)
- **`net/`** — .NET commercial libraries (6 core formats + utility export targets)
- **`format_factory_*.egg-info/`** — Package metadata (generated, do not edit)

## Format Coverage

Python has 20 format implementations: abw, csv, dif, fodg, fodp, fods, fodt, gnumeric, ndjson, ods, odt, pbm, pgm, ppm, qoi, sylk, toml, tsv, xcf, zst.

.NET has 6 core formats: csv, fods, fodt, ndjson, tsv, zst — plus utility targets (html, markdown, netpbm, txt).

4 registered formats have no implementation yet: ora, pam, xpm, zpaq.

## Governance

- **Classification:** CORE_PRODUCT
- **Layer:** L06 (Product Source)
- **Producers:** developers, source generators, spec-parity tools
- **Consumers:** tests, packaging, oracle, supervisor, examples
- **Manual editing:** Yes — this is authoritative source code
- **Registry:** `registry/repository-root-folders.yaml`

## Agent Navigation

**Purpose of this folder:** All product implementation source code lives here. Created by
developers and spec-parity tools following the spec-to-feature correction plan.

**To add a new format (Python):** Create `src/python/<format_id>/` with `__init__.py`,
`parser.py`, `neutral_model.py`. Register the format in `registry/format-registry.yaml`.
Run `python tools/supervisor/governance_validators_root_struct.py` to confirm no governance
gaps. Add tests in `tests/python/<format_id>/`.

**To add a new format (.NET):** Create `src/net/<format_id>/` with the .cs source files.
Run `python .venv/Scripts/pytest tests/ -q` after changes to confirm no regressions.

**Key constraint:** `source-structure-baseline.json` tracks LOC caps per file. Never raise
`baseline_loc_cap` — only add new files. Run `check-source-loc` skill if near the cap.
