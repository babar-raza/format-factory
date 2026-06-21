# Backfill Facility Design — Format Factory Machinery Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52

## Prior Design (from 23d1333 audit)

A backfill facility design was produced in the prior audit but all phases were not_started.
This document updates the design and prioritizes the immediate work.

## Current State

Backfill tooling: NOT BUILT (confirmed by live repo inspection)
Backfill design: EXISTS (prior audit's backfill-facility-design.md)
Production code in src/: Uses format-prefixed names NOT spec-shaped names

## What Backfill Must Do

For each format product:
1. INVENTORY: Scan src/{format}/ for all class definitions and their names
2. MAP: Match existing names to spec qnames where possible (e.g., FodsCell → table:table-cell)
3. PLAN: Determine migration path (rename, move, or add spec_qname attribute)
4. ASSESS: Identify API-breaking changes (class renaming breaks public API)
5. MIGRATE: Implement changes in a governed sprint
6. VERIFY: Run tests; produce evidence

## Compatibility Strategy

For public API continuity:
- Keep format-prefixed names in Compat/ (e.g., FodsCell) as facades
- Move canonical logic to spec/ hierarchy (Table.TableCell)
- Compat/ facades delegate to canonical — zero behavior change
- This is exactly the pattern already implemented for FODS Compat/ (FodsDocument, FodsCell)

This strategy means: backfill = add facade delegation, not rename

## Priority Order

1. FODS Python (highest priority — most mature, closest to Gate 11)
2. FODT Python
3. FODS .NET
4. FODT .NET
5. Others (deferred — no spec backing)

## Immediate Required Tool: backfill_inventory.py

Purpose: Scan src/{format}/ and produce a YAML inventory of:
- All class definitions
- Current name
- Suggested spec_qname
- Suggested spec/ path
- API surface (public vs. private)
- Migration type (add_attribute | move_to_spec | create_facade)

This is TC-BACKFILL-001. Required input to any migration sprint.

## What NOT to Do

- Do NOT bulk-rename classes before the inventory is complete
- Do NOT run backfill on formats without spec/ stubs
- Do NOT break existing public API (neutral_model.py functions are public API)
- Do NOT run product backfill while a product sprint is active for the same format

## Status

All backfill phases: NOT_STARTED
Recommended: Start with TC-BACKFILL-001 (FODS inventory only) in next machinery sprint.
