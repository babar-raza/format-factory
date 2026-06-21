# Machinery Repair Plan — ff-arch-20260621-001

## Priority Order

### Phase 1: Source Hygiene (Do First — Blocks All Else)

**TC-HYGIENE-FODS-001**: Fix FODS Python triple package nesting
- Duration: 1 sprint
- Prerequisite: None
- Risk: Medium (import resolution change)

**TC-HYGIENE-GITIGNORE-001**: Remove build artifacts from git
- Duration: 1 sprint (part of Phase 1)
- Prerequisite: TC-HYGIENE-FODS-001

---

### Phase 2: QName Authority (Establishes What "Correct" Means)

**TC-QNAME-CANONICAL-001**: Create canonical spec class stubs for FODS
- Duration: 1-2 sprints
- Creates: src/net/fods/Spec/{Table,Office}/ stubs
- Creates: shared/qname-registry/fods.yaml

**TC-GOV-QNAME-VALIDATOR-001**: Add V43 QName class name validator
- Duration: 1 sprint
- Prevents future violations from entering source

**TC-SKILL-QNAME-ENFORCE-001**: Update /add-python-api and /add-dotnet-api skills
- Duration: 1 sprint
- Prevents violations from skill output

---

### Phase 3: Backfill (Correct Existing Violations)

**TC-QNAME-BACKFILL-FODS-001**: Move FodsCell to Compat/; create canonical TableCell
- Duration: 2-3 sprints
- Depends on: Phase 2

**TC-QNAME-FODT-SPEC-IMPL-001**: Implement FODT spec/ stubs; switch compat.py
- Duration: 2-3 sprints
- Depends on: Phase 2

---

### Phase 4: SAL and Compiler Integration

**TC-SAL-OUTPUT-001**: Run SAL pipeline; produce sal-facts-latest.json
- Duration: 1 sprint

**TC-FEATURE-COMPILER-CODEGEN-001**: Add source generation to capability compiler
- Duration: 2-3 sprints
- Depends on: TC-SAL-OUTPUT-001

---

### Phase 5: Pilot Demonstration

**TC-PILOT-FODT-SPEC-TO-LIBRARY-001**: FODT end-to-end spec-to-library proof
- Duration: 1-2 sprints
- Depends on: All Phase 3 completions

---

## What Must Be Fixed Before Product Deepening Resumes

The following blockers must be resolved (from system-gap-matrix.yaml):

1. **GAP-ARCH-001**: FODS triple nesting (SOURCE-HYGIENE — BLOCKER)
2. **GAP-ARCH-008**: QName enforcement in skills (SKILL-HARDENING — HIGH)
3. **GAP-ARCH-009**: V43 QName class name validator (QNAME-VALIDATORS — HIGH)

Product deepening may resume for .NET FODS and FODT after these three gaps are closed,
with the additional constraint that all new product source references canonical names
or declared facades only.

---

## Machinery Readiness Checklist

Before calling machinery "ready to produce professional format libraries":

- [ ] Single canonical package level per Python format (no nesting)
- [ ] V43 validator active and blocking non-canonical class names
- [ ] Skills updated with QName enforcement prompts
- [ ] FODS spec/ stubs created (canonical Table.TableCell etc.)
- [ ] FODT spec/ stubs implemented (not architecture_only)
- [ ] SAL pipeline producing sal-facts-latest.json
- [ ] Capability compiler producing source stubs (not just taskcards)
- [ ] Lane order check in check_continuation.py
- [ ] Backfill evidence: FodsCell is a facade, TableCell is canonical
- [ ] Pilot: FODT spec-to-library-to-export demonstrated end-to-end
