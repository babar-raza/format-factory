**Document type:** Directory Orientation
**Last reviewed:** 2026-06-29

# Shared Resources

## Purpose

Shared QName registry — active authority for spec QName-to-class mappings across all formats.

## Contents

- **`qname-registry/`** — Per-format QName YAML files (21 formats) + `schema.yaml`. **Active authority** used by supervisor and spec-parity tools.

## Governance

- **Classification:** SHARED_LIBRARY
- **Producers:** developers, qname tools
- **Consumers:** supervisor, spec-parity tools, validators
- **Manual editing:** Guided — QName files follow schema.yaml

## Relationships

- Registry entry: `registry/repository-root-folders.yaml`
