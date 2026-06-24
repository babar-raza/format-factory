# Lane B — QName Schema and Source Organization Audit
**Plan:** sorted-purring-stardust | **Taskcard:** TC-LANE-B | **Requirement:** REQ-LANE-B

## 1. Schema Definition (shared/qname-registry/schema.yaml)
- **Required fields:** qname, namespace_uri, local_name, canonical_class, spec_fact_ref, status, source_layer
- **Optional fields:** facade_names, python_file, dotnet_file
- **Status lifecycle:** seeded → architecture_only → implementing → implemented → stable → deprecated
- **Source layers:** Spec, Public, Compat, Reading, Writing, Validation, Conversion, Internal

## 2. Registry Coverage (20 formats, 71 total entries)
- **FODS:** 12 entries (11 implemented, 1 implementing) — MOST MATURE
- **FODT:** 9 entries
- **XCF:** 3 entries (all implementing)
- **NDJSON:** 2 entries (implementing)
- **CSV, ZST:** 3 entries each (mixed seeded/implementing)
- **Remaining 14 formats:** 2-3 entries each (mostly seeded)

## 3. Python Format Structure (100% compliance)
All 20 formats have both spec/ and Compat/ subdirectories:
abw, csv, dif, fodg, fodp, fods, fodt, gnumeric, ndjson, ods, odt, pbm, pgm, ppm, qoi, sylk, toml, tsv, xcf, zst

## 4. V44/V45/V48 Wiring
- **V44 (validate_facade_delegates_to_spec):** WIRED, WARN-only. Upgraded from stub 2026-06-21.
- **V45 (validate_qname_class_names):** WIRED. Format-prefixed enforcement.
- **V48 (validate_architecture_only_stub_gate):** WIRED, FAIL for RELEASE_GATE items. Extracted to governance_validators_ext.py for LOC cap.
- **Total validators:** V1-V56 (56 total, not 48 as originally assessed)
- **V49 (validate_qname_structure):** EXISTS at governance_validators.py:3028-3071. WARN-only. Checks spec/ files for spec_qname attribute.

## 5. Key Findings
1. Schema is well-defined with clear lifecycle
2. FODS has the most mature QName mapping (11 implemented)
3. All 20 Python formats have architectural readiness (spec/ + Compat/)
4. V44/V45/V48 all wired and functional
5. V49 ALREADY EXISTS (was believed missing in RC-4 analysis)
6. 56 total validators, not 48 — governance_validators_ext.py holds overflow
