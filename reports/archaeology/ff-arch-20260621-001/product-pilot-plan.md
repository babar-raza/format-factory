# Product Pilot Plan — ff-arch-20260621-001

## Pilot Selection Rationale

Best candidates for demonstrating spec-to-library-to-export:

1. **FODT (both .NET and Python)** — closest to spec-aligned; compat.py bridge ready
2. **FODS .NET** — most feature-complete; DOM-backed; only needs canonical refactor

---

## Pilot 1: FODT Python — Full Spec Migration

**Goal**: Demonstrate that Python FODT operates through a spec-aligned object model

### Prerequisites
- [ ] FODT spec/ stubs implemented (TC-QNAME-FODT-SPEC-IMPL-001)
- [ ] compat.py switched to spec/ imports
- [ ] test_compat_bootstrap.py proves behavioral equivalence

### Demonstration Steps

1. Load a FODT file → get list of `Text.Paragraph` objects (not `FodtParagraph`)
2. Edit a paragraph via `Text.Paragraph.set_text()`
3. Save the modified document
4. Reload and verify text changed
5. Export to HTML via spec-aligned path
6. Run `test_spec_qname_stubs.py` to verify QName identity on objects

### Evidence Required
- `fodt-pilot-1-spec-migration.log` — run log
- `pytest tests/python/fodt/ -v` — all tests passing
- `tests/python/fodt/test_compat_bootstrap.py` — behavioral equivalence proof
- `tests/python/fodt/test_fodt_semantic_roundtrip.py` — roundtrip through spec model

---

## Pilot 2: FODS .NET — Canonical Refactor

**Goal**: Demonstrate that .NET FODS uses canonical `Table.TableCell` as primary class

### Prerequisites
- [ ] TC-QNAME-CANONICAL-001 (FODS Spec/ stubs created)
- [ ] TC-QNAME-BACKFILL-FODS-001 (FodsCell is facade)

### Demonstration Steps

1. Load FODS file → get `Table.TableCell` objects (not `FodsCell`)
2. Edit via `Table.TableCell.SetText()`
3. Save → reload → verify
4. Also test via `FodsCell` facade → same behavior
5. Verify namespace: `FormatFactory.Fods.Spec.Table.TableCell`

### Evidence Required
- Integration test in `tests/net/fods/test_canonical_object_model.cs`
- `FodsCell` facade test proving delegation to `TableCell`

---

## Pilot 3: FODT .NET — Spec Layer Activation

**Goal**: Demonstrate .NET FODT uses `Spec/Text/Paragraph.cs` as primary class

### Prerequisites
- [ ] FODT Spec/ stubs implemented (not architecture_only)

### Demonstration Steps

1. Load FODT → get `FormatFactory.Fodt.Spec.Text.Paragraph` objects
2. Verify `Paragraph.QName == "text:p"`
3. Verify `Paragraph.SpecFactRef == "FACT-FODT-003"`
4. Edit paragraph text via Paragraph API
5. Verify `FodtParagraph` facade delegates to `Paragraph`

---

## Pilot Success Criteria

A pilot is "successful" when:
1. Spec-derived class names are in the production code path
2. Facade pattern delegates to canonical class
3. All existing tests pass through the facade
4. At least one new test exercises canonical class directly
5. QName constants are verified in test output
6. Evidence bundle created and accepted by supervisor
