# Mainstream Replan Brief

**Date:** 2026-06-03
**Lane:** Mainstream Product
**Latest reviewed:** R112

## Current State

R112 accepted with evidence repair + FODS GetUsedRange progress, but product breadth is weak. Direct source changes were mainly in FODS .NET. FODT .NET, Netpbm .NET, and all FOSS products received insufficient attention.

## Problem

Mainstream has been producing narrow product output (one format per sprint) instead of broad capability growth across all 6 POC targets.

## Replan Goals

### R113+ Immediate Priorities

**Commercial .NET (must each get at least 1 new capability per sprint):**
1. FODS .NET: Continue object model expansion (edit, save, export). Target: 3+ new APIs.
2. FODT .NET: Expand beyond paragraph read. Target: edit/save/export path. 2+ new APIs.
3. Netpbm .NET: Expand beyond pixel operations. Target: format conversion, merge. 2+ new APIs.

**Reduced/FOSS (must each get at least 1 new capability per sprint):**
4. ZST: Verify package proof, add streaming workflow example.
5. Python Netpbm (PBM/PGM/PPM): Add missing writer/export paths, installed proof.
6. SYLK/DIF: Add CSV export round-trip, installed proof.

### Hard PASS Quota
- Minimum 6 new product capabilities per Mainstream sprint (1 per product track).
- Tests for every new capability.
- Capability matrix update.

### Success Criteria
- All 6 product tracks show measurable progress in capability matrix.
- No product track has zero progress for 2 consecutive Mainstream sprints.
- Package proof exists for every product with a wheel/package.

## Dependencies

- Needs Skills for governed execution of repetitive product changes.
- Needs Acceleration-B for AI-assisted test generation if available.
- Does NOT wait for machinery unless machinery is removing a product blocker.
