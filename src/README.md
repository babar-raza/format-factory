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
