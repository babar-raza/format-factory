# AI-Assisted Commercial Development Patterns

**Document type:** Implementation patterns
**Authority level:** Normative (implementation guidance for `src/net/{format}/`)
**Created:** 2026-05-13
**Applies to:** FODS, FODT commercial .NET implementation (and future formats)

---

## Purpose

This document defines specific patterns for using AI to accelerate commercial .NET product development while preserving product direction, evidence standards, and gate integrity.

---

## Governing Requirements

All AI-assisted commercial development must remain aligned with:
- **Capability model:** `docs/commercial-product-capability-model.md` (target C7+)
- **Architecture:** `docs/commercial-dotnet-architecture.md`
- **AI operating model:** `docs/ai-usage-operating-model.md`
- **Spec retrieval:** `docs/spec-retrieval-and-rag-policy.md`

---

## Pattern A: Spec-to-Requirements Extraction

**Purpose:** Extract structured requirements from ODF spec sections for a specific capability.

**Steps:**
1. Retrieve relevant spec section (local normalized text via `tools/spec-normalize/`)
2. Prompt AI with: spec section text + target capability level (e.g., "C4: object model for FODS cells")
3. AI produces: list of structured requirements with spec citations
4. Validate: each requirement cites spec file path + page/section reference
5. Schema-validate: requirements become entries in a `requirements-*.yaml`
6. Human/coordinator review: reject unsourced claims before proceeding

**AI output status:** `PROPOSED` → `ACCEPTED_AFTER_VALIDATION` (after citations verified)

**Prohibited:** AI may not invent spec behavior. Every requirement needs a spec citation or a product decision record (DEC-NNN).

---

## Pattern B: Requirements-to-Object-Model Draft

**Purpose:** Translate validated requirements into a C# object model skeleton.

**Steps:**
1. Feed validated requirements YAML + `docs/commercial-dotnet-architecture.md` to AI
2. AI produces: C# class/record definitions (properties, constructors, relationships)
3. Validate: model compiles with `dotnet build`
4. Validate: model structure matches architecture document expectations
5. Review: coordinator checks entity relationships against neutral model schemas
6. Tests: write unit tests for construction and basic manipulation before accepting

**AI output status:** `PROPOSED` → `ACCEPTED_AFTER_VALIDATION` (after compile + tests)

---

## Pattern C: Object-Model-to-Code Draft

**Purpose:** Implement parse, save, and edit operations from object model skeleton.

**Steps:**
1. Feed object model classes + requirements + architecture doc to AI
2. AI produces: parser implementation, writer implementation, edit operations
3. Validate: `dotnet build` passes
4. Validate: `dotnet test` passes (all existing tests still green)
5. New tests: write tests for new operations (don't rely on AI to write all tests)
6. Round-trip test: load reference FODS/FODT file, save, compare structure

**AI output status:** `PROPOSED` → `ACCEPTED_AFTER_VALIDATION` (after compile + test + round-trip)

**Prohibited:** AI-generated code that passes no tests must not be committed.

---

## Pattern D: Test Generation

**Purpose:** Generate comprehensive test coverage for commercial implementation.

**Test types AI may propose:**
- Positive: valid inputs, expected outputs
- Negative: malformed XML, oversized files, empty documents
- Edge: empty sheets, empty paragraphs, nested tables, Unicode
- Adversarial: XXE attempts, extremely long strings, circular references
- Round-trip: load → save → reload → structural comparison
- Edit: modify entity → save → verify in output

**Steps:**
1. AI generates test code stubs with scenario descriptions
2. Developer/agent fills implementation details
3. Tests must be deterministic (same input → same output, always)
4. Tests must fail on broken implementation where possible (not trivially passing)
5. Add to `tests/net/{format}/`

**Prohibited:** Flaky or nondeterministic tests must not be committed.

---

## Pattern E: Adversarial Review

**Purpose:** AI reviews implementation proposals against requirements and capability model.

**Steps:**
1. Feed proposed code + capability model + relevant requirements to AI
2. AI classifies findings:
   - `REAL_GAP` — functionality missing from spec requirement
   - `REAL_BUG` — code does not match spec behavior
   - `FALSE_POSITIVE` — AI misread spec or requirement
   - `FUTURE_SCOPE` — valid but out of current capability level
3. Only `REAL_GAP` and `REAL_BUG` findings become code changes
4. All findings logged in sprint report

**Prohibited:** AI adversarial findings without spec citation are `FALSE_POSITIVE` by default.

---

## Pattern F: Evidence Summarization

**Purpose:** AI drafts human review packets and sprint summaries.

**Steps:**
1. AI reads test results, implementation files, and capability level
2. AI drafts: gate human review packet, sprint summary
3. Coordinator verifies: all claims match actual test results and file state
4. Any overstatement of capability level → `REJECTED_FALSE_POSITIVE`

**Prohibited:** AI-drafted review packets must not claim C-level advancement without test evidence. No fabricated pass counts.

---

## Commercial Product Direction Guard

Before each AI-assisted implementation sprint, verify:

1. **Target capability level:** What C-level is this sprint moving toward?
2. **Architecture alignment:** Does the proposed code match `docs/commercial-dotnet-architecture.md`?
3. **No premature claims:** Does any AI output claim `commercial_product_ready: true` without C7+ evidence?
4. **Load-edit-save-convert:** Does the sprint advance at least one axis of the load-edit-save-convert pipeline?
5. **Test coverage:** Are there deterministic tests for every new API surface?

---

## Format-Specific Notes

### FODS (FormatFactory.Fods)

- Streaming parser (`FodsParser.cs`) exists at C2 — must be extended or replaced with DOM-builder
- Target entity types: `FodsDocument`, `FodsSheet`, `FodsRow`, `FodsCell`, `FodsStyle`
- Spec: ODF 1.3 Part 3 (cached at `.local/spec-cache/fods/1.3/`)
- Reference samples: `samples/by-format/fods/`

### FODT (FormatFactory.Fodt)

- Streaming parser (`FodtParser.cs`) exists at C2 — must be extended or replaced with DOM-builder
- Target entity types: `FodtDocument`, `FodtParagraph`, `FodtList`, `FodtTable`, `FodtStyle`
- Spec: ODF 1.3 Part 3 (same spec, different element namespace)
- Reference samples: `samples/by-format/fodt/`
