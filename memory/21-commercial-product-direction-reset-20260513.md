# Memory 21: Commercial Product Direction Reset (2026-05-13)

## Event

Human (Babar Raza) clarified full commercial product requirements for the .NET product track on 2026-05-13. The clarification revealed that current Tier 0 .NET parsers (`src/net/fods/`, `src/net/fodt/`) are technical baselines only, not commercial products.

## Human Requirements (Verbatim Intent)

1. The product must be able to **load** a supported format and **save** it back with or without editing.
2. Loading means building an **in-memory document object model** that can be inspected and manipulated.
3. Editing means modifying one or more format-specific entities in the document object model.
4. The product must be able to **save/export/convert** to other formats (PDF, PNG, HTML, related family formats).
5. Current Tier 0 streaming parsers are **not enough** for commercial readiness.
6. Current `src/net/fods/` and `src/net/fodt/` should be treated as **Tier 0 parser prototypes or technical baselines**, not commercial products.
7. Future commercial implementation must move toward **load-edit-save-convert architecture**.
8. Gate 11 approval/publishing must not proceed until the repo clearly distinguishes Tier 0 parser readiness from full commercial product readiness.

## Actions Taken

- Created `docs/commercial-product-capability-model.md` — C0-C10 capability levels; commercial = C7+
- Created `docs/commercial-dotnet-architecture.md` — expected API, object model, save/export pipelines
- Updated `plans/master-plan.md` — Rule 12 references capability model; next-action states Gate 11 deferred
- Updated `registry/format-registry.yaml` — FODS/FODT gate_11: commercial_capability_level: C2, commercial_product_ready: false
- Updated `AGENTS.md` — AF9-AF11 (commercial readiness rules)
- Updated `GOVERNANCE.md` — 26.8-26.9 (commercial governance)
- Created 10 commercial taskcards for implementation roadmap
- Created governance sync reports

## Key Facts for Future Agents

- **Current .NET source is C2** (streaming metadata extraction). NOT commercial product ready.
- **Commercial readiness = C7+** (load + object model + edit + same-format save).
- **Gate 11 is deferred/rebaselined** until capability model requirements are met.
- **Agents must NOT equate parser/count extraction with commercial product readiness.**
- **Next implementation direction:** load-edit-save-convert vertical slices, not packaging/publishing.
- **Controlled swarm execution** is preferred for larger work, but product direction must be preserved.
- **docs/commercial-product-capability-model.md** is the authoritative reference for C-levels.

## Files Created/Updated

| File | Action |
|------|--------|
| docs/commercial-product-capability-model.md | CREATED |
| docs/commercial-dotnet-architecture.md | CREATED |
| plans/master-plan.md | UPDATED (Rule 12, next-action) |
| registry/format-registry.yaml | UPDATED (gate_11 for FODS + FODT) |
| AGENTS.md | UPDATED (AF9-AF11) |
| GOVERNANCE.md | UPDATED (26.8-26.9) |
| 10 taskcards in taskcards/ | CREATED |
| reports/governance/commercial-requirements-local-doc-sync-20260513.md | CREATED |
| reports/governance/commercial-requirements-local-doc-sync-20260513.yaml | CREATED |
