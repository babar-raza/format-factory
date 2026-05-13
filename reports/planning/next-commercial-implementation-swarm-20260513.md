# Next Commercial Implementation Swarm Design
# Sprint: COMMERCIAL-PRODUCT-DIRECTION-RESET-SWARM-001
# Lane H — Next Implementation Swarm Design
# Date: 2026-05-13

## Recommended Next Swarm

**COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001**

This is the exact next implementation swarm. It must not execute until:
1. Human accepts this rebaseline plan
2. Human approves the capability model (G11-A)
3. Human authorizes COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001 explicitly

---

## Swarm Goals

1. FODS: no-edit roundtrip (load FODS → save FODS → verify structural equivalence)
2. FODS: edit-one-cell vertical slice (load → edit cell → save → reload → verify)
3. FODT: no-edit roundtrip (load FODT → save FODT → verify structural equivalence)
4. FODT: edit-one-paragraph vertical slice (load → edit paragraph → save → reload → verify)
5. Golden fixtures and oracle comparison for both formats
6. Package hygiene and docs update
7. Memory/governance sync

---

## Proposed Swarm Lanes

### Lane A: Shared Object Model Decision and Source Layout
- Decide: shared FormatFactory.Core or format-local only?
- Create or confirm source layout under src/net/fods/ and src/net/fodt/
- Create Model/ subdirectory stubs
- Deliverables: decision record, updated source layout docs

### Lane B: FODS Load/Save No-Edit Roundtrip
- Implement FodsDocument.cs with Load() + basic DOM builder
- Implement FodsWriter.cs with Save()
- No-edit roundtrip: load → save → verify
- Tests: all 4 FODS sample fixtures pass roundtrip
- Deliverables: FodsDocument.cs, FodsWriter.cs, 4+ roundtrip tests

### Lane C: FODS Edit-One-Cell Save Vertical Slice
- Extends Lane B
- Implement typed FodsCellValue (string, number)
- Mutable cell setter
- Edit cell → save → reload → verify
- Tests: 4+ edit tests, LibreOffice oracle comparison
- Deliverables: Cell.cs, CellValue.cs, 4+ edit tests, oracle report

### Lane D: FODT Load/Save No-Edit Roundtrip
- Implement FodtDocument.cs with Load() + basic DOM builder
- Implement FodtWriter.cs with Save()
- No-edit roundtrip: load → save → verify
- Tests: all 4 FODT sample fixtures pass roundtrip
- Deliverables: FodtDocument.cs, FodtWriter.cs, 4+ roundtrip tests

### Lane E: FODT Edit-One-Paragraph Save Vertical Slice
- Extends Lane D
- Implement FodtParagraph with mutable text
- Edit paragraph → save → reload → verify
- Tests: 4+ edit tests, LibreOffice oracle comparison
- Deliverables: Paragraph.cs, Run.cs, 4+ edit tests, oracle report

### Lane F: Golden Fixtures and Oracle Comparison
- Create golden round-trip fixtures for both formats
- Run LibreOffice oracle on saved files
- Comparison report
- Deliverables: golden fixtures, oracle comparison report, DEC-034 IV

### Lane G: Package Hygiene and Docs
- Verify .gitignore excludes new Model/ build artifacts
- Update README.md for both formats
- Update tier-map.yaml to note C7 requirement
- Deliverables: updated docs, hygiene check

### Lane M: Memory and Governance Sync
- Update memory/21 (or new file) with swarm outcomes
- Update master-plan.md with new sub-gate statuses
- Deliverables: memory update, master-plan update

---

## Prerequisites Before Executing This Swarm

- [ ] Human accepts COMMERCIAL-PRODUCT-DIRECTION-RESET-SWARM-001 rebaseline plan
- [ ] Human accepts docs/commercial-product-capability-model.md (G11-A accepted)
- [ ] Human authorizes COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001 explicitly
- [ ] Shared core decision made (Lane A of next swarm)
- [ ] .NET SDK 10.0.204 confirmed installed (already done)

---

## What This Swarm Produces (After Execution)

If successful:
- G11-B partially satisfied (object model for basic entities)
- G11-C satisfied (no-edit roundtrip for both formats)
- G11-D satisfied for minimum slice (edit one entity and save)
- Commercial capability level advances from C2 → C7 (minimum)

---

## Lane H Verdict
LANE_H_PASS
