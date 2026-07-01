# Prototypes

**Document type:** Directory Orientation — Phase 0 Foundation
**Last reviewed:** 2026-05-03

---

## Purpose

This directory contains prototype parsers — minimal working implementations that demonstrate parsing feasibility for a format. Prototypes are internal-only reference implementations. They are never promoted directly to `src/`. Product code is written from scratch in Phase 4+, using the prototype as a design reference.

---

## Directory Structure

```
prototypes/
+-- _readme.md              This file
+-- by-format/              One subdirectory per format (created Phase 3, Gate 4)
    +-- fods/               FODS prototype (Phase 3)
        +-- README.md       Prototype documentation (required for Gate 4)
        +-- parser.py       Main parser module
        +-- tests/          Prototype-level tests
```

The `by-format/` subdirectory is created in Phase 3 when Gate 4 work begins for the pilot format (FODS).

---

## Prototype Rules

Prototypes must follow these rules:

1. **Internal only.** All prototype files have `visibility: internal`. They are never included in any release.
2. **Python only.** Prototypes are written in Python (the faster iteration language). .NET prototype implementations are not required.
3. **Security baseline required.** The prototype README must document which threat categories from `docs/governance/security.md` apply and what mitigations are in place. A prototype that does not address XXE or entity expansion for XML formats does not pass Gate 4.
4. **Corpus coverage required.** The prototype must correctly parse all samples in the Gate 3 sample corpus without crashing. Data loss on core data structures is a Gate 4 failure.
5. **No promotion.** Prototype code is never copied or moved to `src/`. The prototype demonstrates feasibility; the product implementation is independent.

---

## Prototype README Requirements (Gate 4)

Every prototype directory must contain a `README.md` that documents:
- Parsing approach and key decisions
- Libraries used and why (especially security-relevant choices)
- Known limitations and out-of-scope features
- Security mitigations applied (mapped to `docs/governance/security.md` threat categories)
- How to run the prototype and what output to expect

---

## Visibility

All prototype files are `visibility: internal`. Prototypes are never released to users. They are internal reference implementations.

---

## Relationship to Other Documents

- `docs/governance/security.md` — threat categories that must be addressed in prototype README
- `docs/gates.md` — Gate 4 (prototype) pass criteria
- `docs/python-foss/acquisition-workflow.md` — Stage 4: Prototype Development
- `acquisition-packs/_template/parser-notes.md` — parser strategy document that informs prototype design
