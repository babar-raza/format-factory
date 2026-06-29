**Document type:** Directory Orientation
**Last reviewed:** 2026-06-29

# Test Drivers

## Purpose

Test generation templates (`.py.tmpl`) for format-specific test scaffolding.

## Contents

- **`python/`** — Python test templates (append_test, export_csv_test, getter_test, probe_test, roundtrip_test)

## Governance

- **Classification:** SHARED_LIBRARY
- **Producers:** developers
- **Consumers:** `tools/supervisor/test_drivers.py`, `tools/supervisor/libforge_pattern_registry.py`
- **Manual editing:** Yes — templates are authored

## Relationships

- Registry entry: `registry/repository-root-folders.yaml`
