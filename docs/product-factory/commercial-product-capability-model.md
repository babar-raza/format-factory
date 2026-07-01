# Commercial Product Capability Model

**Document type:** Authoritative product requirements
**Authority level:** Normative (referenced by master-plan Rule 12 and docs/gates.md Gate 11)
**Created:** 2026-05-13
**Created by:** Human direction (Babar Raza) — documented by agent sprint

---

## Purpose

This document defines what "commercial product readiness" means for the .NET product track (`src/net/{format}/`). It ensures all agents, sprints, and gate reviews use a shared definition of commercial capability rather than equating Tier 0 parser success with product readiness.

---

## Core Requirement

The commercial .NET product must support **load-edit-save-convert**:

1. **Load** — Build an in-memory document object model from a supported format file that can be inspected and manipulated programmatically.
2. **Edit** — Modify one or more format-specific entities in the document object model (cells, paragraphs, styles, metadata, etc.).
3. **Save** — Write the modified document object model back to the same format with structural and semantic preservation.
4. **Convert** — Export/save the document object model to other formats (PDF, PNG, HTML, and related formats in the same family or type).

---

## What Tier 0 Is (and Is Not)

| Aspect | Tier 0 Reality | Commercial Requirement |
|--------|---------------|----------------------|
| Architecture | Streaming XmlReader (forward-only) | Full document object model (DOM) |
| Read capability | Metadata + structure counting | Full entity graph with relationships |
| Edit capability | None | Programmatic entity modification |
| Save capability | None | Same-format round-trip with fidelity |
| Export capability | None | PDF, PNG, HTML, family-related formats |
| Memory model | No allocation beyond current element | Full document in memory |
| API shape | `Parse(path) -> counts/metadata` | `Load(path) -> Document -> Edit -> Save/Export` |

**Current `src/net/fods/` and `src/net/fodt/` are C4-C6 vertical-slice implementations. They are NOT commercial products.** `commercial_product_ready: false`. Gate 11 NOT approved. Full C7+ capability coverage + Gate 11 human approval required.

---

## Capability Levels

Progress toward full commercial readiness is tracked using capability levels C0 through C10:

| Level | Name | Description | Gate 11 Required |
|-------|------|-------------|-----------------|
| C0 | Detection | Format identification by signature/extension | No |
| C1 | Metadata Read | Extract document properties (title, author, dates) | No |
| C2 | Structure Read | Count and enumerate structural elements (sheets, paragraphs, tables) | No |
| C3 | Full Parse | Complete entity extraction into typed objects | No |
| C4 | Object Model | In-memory document object model with entity relationships | Yes |
| C5 | Read-Only DOM | Navigate and inspect any entity programmatically | Yes |
| C6 | Edit Support | Modify entities in the object model | Yes |
| C7 | Same-Format Save | Serialize modified DOM back to original format | Yes |
| C8 | Round-Trip Fidelity | Load-save preserves all supported features without loss | Yes |
| C9 | Export/Convert | Save to PDF, PNG, HTML, and related formats | Yes |
| C10 | Full Commercial | All C4-C9 at production quality with edge-case coverage | Yes |

**Current FODS .NET source:** C4-C6 vertical slice (FodsDocument.Load/Save + FodsSheet/FodsRow/FodsCell edit; FodsParser.cs Tier 0 streaming retained)
**Current FODT .NET source:** C4-C6 vertical slice (FodtDocument.Load/Save + FodtParagraph.SetText edit; FodtParser.cs Tier 0 streaming retained)

**Gate 11 approval requires:** Minimum C7 demonstrated (load + object model + edit + same-format save). C9-C10 preferred for initial commercial release.

---

## Object Model Requirement

The commercial product MUST include a typed document object model:

- Each format-specific entity (cell, paragraph, table, style, etc.) is represented as a class/struct
- Entities maintain parent-child and reference relationships
- The model supports creation, modification, and deletion of entities
- The model can be serialized back to the source format without structural loss

---

## Same-Format Save Requirement

The product MUST support loading a file and saving it back to the same format:

- Unsupported features are preserved as opaque nodes (no data loss on round-trip)
- Modified entities are serialized correctly
- Document structure, namespaces, and metadata survive round-trip
- Test coverage includes round-trip fidelity checks against reference files

---

## Edit-and-Save Requirement

The product MUST support programmatic editing followed by save:

- At minimum: modify cell values (FODS), modify paragraph text (FODT)
- API must expose typed setters/builders for supported entities
- Edit operations must be observable in the saved output
- Undo/history is NOT required for initial commercial release

---

## Export/Conversion Requirement

The product MUST support export to at least:

- PDF (via rendering or serialization pipeline)
- HTML (structural conversion)
- PNG (page/sheet rendering, may delegate to rendering engine)
- Related formats in the same family (e.g., FODS to ODS, FODT to ODT)

Export fidelity levels and supported feature subsets must be documented per format.

---

## Implications for Gate 11

1. Gate 11 approval MUST NOT proceed based on Tier 0 parser success alone.
2. Gate 11 human review packet MUST reference this capability model and state the achieved level.
3. Gate 11 "full .NET implementation" (per master-plan Rule 12) means C7+ capability, not C0-C2 parsing.
4. Gate 11 publish/release work is paused until the architecture for load-edit-save-convert is designed and vertical slices are implemented.
5. Next implementation goal is NOT packaging or publishing — it is load/save/edit vertical slices.

---

## Relationship to Tier Model

The existing tier model (Tier 0-6 in docs/product-tracks.md) describes feature scope. This capability model describes architectural capability. Both must be satisfied:

- Tier 5-6 features at C7+ capability = commercial readiness
- Tier 0 features at C2 capability = technical baseline only

---

## Binding Authority

This document is referenced by:
- plans/master-plan.md (Rule 12, Gate 11 semantics)
- docs/gates.md (Gate 11 pass criteria)
- AGENTS.md (commercial readiness rules)
- GOVERNANCE.md (commercial capability governance)
- registry/format-registry.yaml (commercial_capability_level field)
