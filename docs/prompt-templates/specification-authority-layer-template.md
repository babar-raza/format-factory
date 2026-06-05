# Specification Authority Layer Execution Template

**Added:** 2026-06-04
**Sprint ID pattern:** FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-<PHASE>-<N>
**Reference:** docs/governance/specification-authority-layer.md

## Prerequisites

This template should only be used when the plan has verdict `SPEC_AUTH_HEALING_PLAN_REPAIRED_READY_FOR_SINGLE_GO_EXECUTION`.

Current plan status: PLAN_NEEDS_REPAIR
Repair prompt ID: `FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-HEALING-PLAN-REPAIR-001`

## Mission

Build the Specification Authority Layer architecture and pilot (ZST + Netpbm + DIF minimum).

NOT: product source implementation / gate approval / external tool install.

## Hard Prohibitions
- No src/net/* or src/python/* edits
- No registry/format-registry.yaml mutation
- No .vscode/mcp.json changes
- No gate approval
- No push/commit/publish
- No external tool install

## Allowed Paths
- tools/spec_authority/** (new — spec authority tooling)
- requirements-authority/** (if shared with Req/Cap layer)
- .local/spec-usage-ledger/** (usage ledger)
- tests/supervisor/test_specification_authority_*.py
- reports/specification-authority-layer-production-healing/**
- .local/evidences/specification-authority-layer-<N>/**
- .local/supervisor/reviews/specification-authority-layer-<N>/**

## Required Subsystems (Phase 1 minimum)

Build at minimum:
1. SpecSourceRegistry (schema + store)
2. SpecVault (raw snapshot storage with provenance/checksum)
3. SpecParser (section tree output)
4. ContextPackBuilder (deterministic, with manifest.sha256)
5. SpecGovernanceRuntime (anti-bypass enforcement)
6. Usage Ledger (append-only JSONL)

## Pilot Formats
- ZST
- Netpbm
- DIF

For each pilot format:
- Register source in SpecSourceRegistry
- Fetch/store raw snapshot in SpecVault
- Parse to section tree
- Build context pack (with manifest.sha256)
- Log usage record

## Evidence Closeout
1. `.local/venv/Scripts/python tools/supervisor/autonomous_cycle.py --declaration .local/evidences/specification-authority-layer-<N>/evidence-declaration.yaml`
2. `.local/venv/Scripts/python tools/supervisor/build_declaration_review_package.py --declaration .local/evidences/specification-authority-layer-<N>/evidence-declaration.yaml`

## Allowed Verdicts
- `SPEC_AUTHORITY_LAYER_PHASE1_COMPLETE`
- `SPEC_AUTHORITY_LAYER_PHASE1_PARTIAL`
- `SPEC_AUTHORITY_LAYER_PHASE1_BLOCKED`

## Final Response Contract
- Exact verdict
- Subsystems built
- Pilot formats processed
- Context packs produced (with manifest.sha256)
- Test count: passed/failed/skipped
- Evidence declaration path
- Review package absolute path: C:\Users\prora\...\
- Review package SHA-256
- Explicit: no product source edits, no gate approval, no push, no commit
