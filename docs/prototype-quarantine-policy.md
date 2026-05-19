# Prototype Quarantine and Promotion Policy

**Document type:** Policy
**Created:** R32 (2026-05-19)
**Authority:** Defines when code may be promoted from prototypes/ to src/python/, and when formats in src/python/ should be classified as probe-quality despite their location.

---

## Problem Statement

R32 investigation found that prototype parsers were copied from `prototypes/by-format/` to `src/python/` without enrichment. Four formats (FODP, FODG, Gnumeric, ABW) exist in `src/python/` at Gate 10 with 141-217 LOC, no neutral model, no write capability, and no export. Their location in `src/python/` implies library quality they do not possess.

---

## Definitions

- **Prototype:** Exploratory code that proves a format can be parsed. Lives in `prototypes/by-format/{format}/`. No quality bar. May be throwaway.
- **Source track:** Production-intent code in `src/python/{format}/` or `src/net/{format}/`. Expected to meet source-track-maturity-policy standards.
- **Probe:** A parser that reads header/metadata only, or extracts shallow features without a formal model. Valid as a prototype (G4) but not as a library.
- **Quarantine marker:** A metadata flag in format-completion-matrix.yaml indicating that code in src/python/ does not meet source-track expectations. The code is not physically moved, but its maturity class signals its true state.

---

## Promotion Rules: prototypes/ to src/python/

Code may be promoted from `prototypes/by-format/{format}/` to `src/python/{format}/` when ALL of the following are true:

1. **Gate 5 passed** — neutral model exists and is populated by the parser.
2. **At least 30 test methods** exist in tests/python/{format}/.
3. **Parser extracts at least 5 format features** beyond header/probe.
4. **__init__.py** defines public API surface.
5. **exceptions.py** or equivalent error handling exists.
6. **File size guard** is present.

Promotion does NOT require write/export capability. But promotion to src/python/ without write/export limits the format to `read_only_library_foundation` maturity class and caps it at Gate 9 under the new gate quality criteria.

---

## Quarantine: Formats Already in src/python/

Formats currently in `src/python/` that do not meet promotion criteria are NOT physically moved in this sprint. Instead:

1. Their `actual_maturity_class` in format-completion-matrix.yaml is set to `probe_only` or `read_only_prototype`.
2. Their `evidence_backed_gate` is set to the gate their source actually supports (typically G4).
3. A DRIFT-* taskcard is created documenting the gap.
4. Future sprints must either:
   - (a) Deepen the code to meet promotion criteria, OR
   - (b) Physically move the code back to prototypes/ if deepening is not planned.

Physical movement (option b) requires:
- A dedicated taskcard
- Test path updates
- Import path updates
- Registry/pack.yaml updates
- Git history preservation (move, not delete+recreate)
- Human approval

---

## When Physical Quarantine Is Allowed

A future sprint may physically move code from `src/python/{format}/` back to `prototypes/by-format/{format}/` when:

1. A DRIFT-* taskcard documents the rationale.
2. All tests are updated to reflect the new path.
3. All imports and references are updated.
4. The move is a git mv (preserves history), not delete+recreate.
5. The registry and pack.yaml are updated.
6. The sprint prompt explicitly authorizes the move.

---

## Preventing Future Premature Promotion

1. New code in `src/python/` must pass the promotion checklist above.
2. Sprint prompts that create `src/python/{format}/` must reference this policy.
3. The evidence validator (`test_source_track_maturity.py`) checks that formats in src/python/ with probe_only maturity have a DRIFT-* taskcard.

---

## History Preservation

When code is promoted or quarantined:
- Use `git mv` for file moves.
- Do not delete and recreate files.
- Record the move in the sprint report with old and new paths.
- Update all references (tests, pack.yaml, registry, memory).
