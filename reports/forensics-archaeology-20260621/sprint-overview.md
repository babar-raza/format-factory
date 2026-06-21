# Format Factory — Generation Archaeology Sprint Overview

**Sprint / Run ID:** `forensics-archaeology-20260621`
**Date:** 2026-06-21
**Branch:** main
**HEAD:** 827f5a52915f1ee3b285bf13965b5f65f3532a469
**Investigator Role:** Senior software archaeologist, spec engineer, format-library architect

---

## Purpose

Full forensic investigation to answer: *Is Format Factory currently able to convert specifications
into professional, repeatable, qname/spec-hierarchy-aligned, testable, maintainable .NET and
Python format libraries?*

This is NOT a shallow code review. It is an evidence-driven assessment of whether the current
machinery can repeatably produce Gate 11–ready products.

---

## Scope

- 20 Python format packages (`src/python/`)
- 11 .NET format packages (`src/net/`)
- SAL (Specification Authority Layer) infrastructure
- Capability Layer and gap-ledger
- Downstream product generation machinery
- 40+ registered skills
- Autonomous supervisor and continuation system
- QName compliance across all products
- Generation archaeology (Waves 1-4)
- Source hygiene audit
- Backfill facility assessment

---

## Key Findings Summary

| Area | Status | Severity |
|------|--------|----------|
| FODS Python (spec stubs + Compat/) | Generation 3 — partial | Yellow |
| FODT Python (spec stubs, no Compat/) | Generation 3 — partial | Yellow |
| 18 other Python packages | Generation 1-2 — format-prefixed, no spec_qname | Red |
| .NET FODS (DOM-backed + Spec/) | Generation 3-4 — usable prototype | Yellow |
| .NET FODT (DOM-backed + Spec/) | Generation 3-4 — usable prototype | Yellow |
| 9 other .NET packages | Generation 1-2 — stubs/monoliths | Orange-Red |
| SAL (FODS, FODT) | 4987 / 4933 facts — partially operational | Yellow |
| SAL (CSV, XCF, TOML, NDJSON) | 0 facts — not operational | Red |
| Capability Layer | 958 gaps, all severity=unknown | Orange |
| Capability-to-Feature Compiler | Exists, partially wired | Orange |
| QName compliance (overall) | 29/135 classes (21%) | Red |
| Build artifact hygiene | Recursive build/ + 20+ egg-info in repo | Orange |
| Skills | 40+ registered, few enforce spec_qname | Orange |
| Autonomous supervisor | Operational (MODE 4) | Green |

---

## Final Verdict

**READY_AFTER_TARGETED_MACHINERY_REPAIRS**

FODS and FODT are close to a repeatable spec-to-library proof. The other 18+ formats need
machinery repairs before product deepening can be safely resumed.

---

## Reports in This Bundle

See `evidence-index.md` for the complete file listing.
