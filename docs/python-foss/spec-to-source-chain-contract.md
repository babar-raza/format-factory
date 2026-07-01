# Spec-to-Source Authority Chain Contract

## Document Authority
- **Status:** AUTHORITATIVE
- **Origin:** TC-FORENSIC-012, source-realization-forensics-20260625-001
- **Governs:** The complete pipeline from ODF/format specification to consumer-facing source code

---

## The Authority Chain

```
ODF/format specification
        │
        ▼
SAL (Specification Authority Layer) — tools/specification-authority-layer/
  └─ produces: sal-facts-{format}.json (FACT-FORMAT-NNN IDs)
        │
        ▼ (status: CHAIN_BROKEN_AT_SAL for 10/20 formats)
        │
shared/qname-registry/{format}.yaml
  └─ defines: qname, canonical_class, spec_fact_ref, status, python_file, dotnet_file
        │
        ▼
generate_canonical_stubs.py (tools/spec/generate_canonical_stubs.py)
  └─ reads: shared/qname-registry/{format}.yaml
  └─ writes: src/python/{format}/spec/{concept}/{class}.py  (# GENERATED — architecture_only)
  └─ writes: src/net/{format}/Spec/{Concept}/{Class}.cs     (# GENERATED — architecture_only)
        │
        ▼
src/python/{format}/spec/{concept}/{class}.py
  └─ contains: class {CanonicalClass} with spec_qname, spec_fact_ref, authority_only
        │
        ▼
src/python/{format}/Compat/{format}_{class}.py
  └─ contains: class {FormatClass}({CanonicalClass}) with namespace_uri, local_name, facade_names
  └─ format-prefixed names ONLY in this directory
        │
        ▼
src/python/{format}/models.py
  └─ contains: class {FormatDocument} (consumer-facing domain model)
  └─ from_file(), typed properties, to_dict()
  └─ inherits or references spec_qname from Compat/ classes
        │
        ▼
src/python/{format}/__init__.py
  └─ exports: {FormatDocument}, parse_{format}(), parse_{format}_strict(), write_{format}()
  └─ dynamic __all__ with _FF_API_EXCLUDE frozenset
        │
        ▼
Consumer: from {format} import {FormatDocument}; doc = {FormatDocument}.from_file(path)
```

---

## Chain Integrity Status (as of 2026-06-25)

| Format | SAL→Registry | Registry→Stubs | Stubs→Compat | Compat→models.py | models.py→__init__ | Overall |
|--------|-------------|----------------|--------------|-----------------|-------------------|---------|
| FODS | INTACT | INTACT | INTACT | INTACT | INTACT | **INTACT** |
| FODT | INTACT | INTACT | INTACT | INTACT | INTACT | **INTACT** |
| ODS | INTACT | INTACT | INTACT | PARTIAL | INTACT | PARTIAL |
| ODT | INTACT | INTACT | INTACT | PARTIAL | INTACT | PARTIAL |
| FODG | INTACT | INTACT | INTACT | PARTIAL | INTACT | PARTIAL |
| FODP | INTACT | INTACT | INTACT | PARTIAL | INTACT | PARTIAL |
| PBM | INTACT | INTACT | PARTIAL | PARTIAL | INTACT | PARTIAL |
| PGM | INTACT | INTACT | PARTIAL | PARTIAL | INTACT | PARTIAL |
| PPM | INTACT | INTACT | PARTIAL | PARTIAL | INTACT | PARTIAL |
| QOI | INTACT | INTACT | PARTIAL | PARTIAL | INTACT | PARTIAL |
| CSV | BROKEN(SAL) | INTACT | INTACT | INTACT | INTACT | PARTIAL |
| TSV | BROKEN(SAL) | INTACT | INTACT | INTACT | INTACT | PARTIAL |
| NDJSON | BROKEN(SAL) | INTACT | INTACT | INTACT | INTACT | PARTIAL |
| ZST | BROKEN(SAL) | INTACT | INTACT | INTACT | INTACT | PARTIAL |
| TOML | BROKEN(SAL) | INTACT | INTACT | INTACT | INTACT | PARTIAL |
| GNUMERIC | BROKEN(SAL) | INTACT | INTACT | INTACT | INTACT | PARTIAL |
| ABW | BROKEN(SAL) | INTACT | INTACT | INTACT | INTACT | PARTIAL |
| DIF | BROKEN(SAL) | INTACT | PARTIAL | PARTIAL | INTACT | PARTIAL |
| SYLK | BROKEN(SAL) | INTACT | PARTIAL | PARTIAL | INTACT | PARTIAL |
| XCF | BROKEN(SAL) | INTACT | PARTIAL | PARTIAL | INTACT | PARTIAL |

**CHAIN_INTACT (10/20):** ODF and image formats where SAL parsers exist.
**CHAIN_BROKEN_AT_SAL (10/20):** Non-ODF formats where SAL spec parser does not exist.
Breaking at SAL is EXPECTED for non-XML non-ODF formats. The chain from registry onward is intact for all 20.

---

## Validators at Each Chain Link

| Chain Link | Validator | What it checks |
|-----------|-----------|----------------|
| Registry → python_file path | generate_canonical_stubs.py entry guard | Registry YAML must exist before any file creation |
| Registry → status | generate_canonical_stubs.py status check | Only "seeded" files are (re-)generated |
| spec/ classes → spec_qname | V53 | ClassVar[str] spec_qname must exist and match registry |
| Compat/ → spec_qname | V53 | Inherited spec_qname must be present |
| models.py → spec_qname | V53 | Domain model class must expose spec_qname |
| PRODUCT_SOURCE items → registry authority | TC-GUARD-001 | Both gap_ledger_ref AND spec_fact_refs required |
| RELEASE_GATE → no architecture_only stubs | V48 | RELEASE_GATE evidence may not cite spec/ skeleton files |
| __init__.py → no module type leakage | V44 | Public API must not export raw module objects |

---

## Known Chain Gaps

### Gap 1: SAL regeneration never triggered
- **Impact:** `sal-facts-{format}.json` is stale for 17/20 formats (SAL ran once on run030)
- **Root cause:** SAL pipeline has 21 tools; only 3 are regularly invoked
- **Affects:** `spec_fact_ref` values may point to stale FACT IDs
- **Mitigation:** `shared/qname-registry/*.yaml` `spec_fact_ref` fields are manually curated
- **Resolution tracked in:** `plans/strategic/spec-to-feature-radical-correction-plan.md` Lane 1

### Gap 2: FeatureFactory no pre-insertion spec_qname check
- **Impact:** FeatureFactory can insert functions without verifying the target class has spec_qname
- **Root cause:** SYS-001 FeatureFactory has no call to `shared/qname-registry/` before writing
- **Resolution:** TC-SRFA-015 (add spec_qname registry check before insertion)

### Gap 3: generate_canonical_stubs.py not called by automated systems
- **Impact:** Registry additions do not automatically produce skeleton classes
- **Root cause:** No CI/CD step or autonomous_cycle step invokes generate_canonical_stubs.py
- **Resolution:** TC-SRFA-019 (wire generate_canonical_stubs to registry change detection)

### Gap 4: V53 ClassVar detection limitation
- **Impact:** V53 AST parser cannot distinguish `spec_qname: ClassVar[str]` from `spec_qname: str`
- **Root cause:** Both produce AST.Assign or AST.AnnAssign nodes; type annotation not fully checked
- **Resolution:** TC-SRFA-028 (add ast.AnnAssign inspection to V53)

### Gap 5: FeatureFactory anchor loss is silent
- **Impact:** When anchor function not found, code appended to EOF with no error
- **Root cause:** `_find_insertion_point()` returns `len(content)` silently when no match
- **Resolution:** TC-SRFA-029 (raise FeatureFactoryError when anchor specified but not found)

---

## Correct Usage Pattern for Adding a New Format

1. Add entry to `shared/qname-registry/{format}.yaml` with status: "seeded"
2. Run `python tools/spec/generate_canonical_stubs.py {format}` → creates `spec/` skeleton
3. Implement `Compat/{format}_{class}.py` facades (inherit from spec class)
4. Implement `{format}_parser.py` or `{format}_codec.py` (core parsing)
5. Create `models.py` with domain model class (from_file, typed properties, to_dict)
6. Create `{format}_analytics.py` with derived analytics functions
7. Update `__init__.py` with dynamic `__all__`
8. Add gap entry to `reports/capability-layer/gap-ledger.json`
9. Add skill-attributed work item to ensure TC-GUARD-001 compliance
10. Write tests: spec_qname compliance, round-trip, malformed input, consumer proof

**Do NOT** skip step 1-3 and hand-write spec/ or Compat/ classes — this breaks chain traceability.
**Do NOT** skip step 8 — PRODUCT_SOURCE items without gap_ledger_ref are blocked by TC-GUARD-001.
