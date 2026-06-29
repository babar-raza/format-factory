**Document type:** Directory Orientation
**Last reviewed:** 2026-06-29

# Product Capability Matrix

## Purpose

System of record for POC capability tracking. `poc-targets.yaml` is the canonical authority file — referenced by 90+ tools across the supervisor system.

## Contents

- **`poc-targets.yaml`** — Master POC authority (30+ KB)
- **`dotnet-fods-fodt.yaml`** — .NET FODS/FODT extended matrix
- **`fods.yaml`**, **`fodt.yaml`**, **`netpbm.yaml`** — Per-format matrices

## Governance

- **Classification:** PIPELINE_ARTIFACT
- **Producers:** developers, capability tools
- **Consumers:** supervisor, sprint executor, task generators, evidence tools
- **Manual editing:** Guided — poc-targets.yaml is the master authority

## Relationships

- Registry entry: `registry/repository-root-folders.yaml`
- Referenced by: `tools/supervisor/`, `tools/evidence/`, `tools/ai/`
