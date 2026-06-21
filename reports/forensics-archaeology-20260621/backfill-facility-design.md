# Backfill Facility Design

**Sprint:** forensics-archaeology-20260621

---

## Is a Backfill Facility Currently Present?

**Answer: NO — not as a systematic, governed facility.**

Partial backfill work has been done:
- FODS: spec stubs created (`src/python/fods/spec/`), Compat/ facade started
- FODT: spec stubs created (`src/python/fodt/spec/`), no Compat/ yet
- These were created by autonomous sprint work (commit 8ca43a12) — not by a backfill tool

There is no:
- `tools/backfill/` directory
- `backfill-spec-stubs.py` script
- Migration plan for existing non-spec source classes
- Rollback mechanism for backfill operations
- Per-format backfill tracking ledger

---

## Why Backfill Is Needed

18 of 20 Python packages and 9 of 11 .NET packages contain domain classes without `spec_qname`.
These classes cannot participate in the spec-to-feature pipeline. They will remain orphaned
as the pipeline matures unless systematically backfilled.

The backfill problem has two dimensions:
1. **Naming compliance:** DifDocument → should be mapped to a governed canonical class
2. **Spec coverage:** OdsCell → should gain `spec_qname = "table:table-cell"` and link to FACT-ODS-NNN

---

## Proposed Backfill Subsystem Design

### Phase 1: Inventory Tool (2-3 day effort)

```python
# tools/backfill/inventory_source.py
# Scans src/python/ and src/net/
# For each class:
#   - File path
#   - Class name
#   - Has spec_qname? (yes/no)
#   - Candidate spec_qname (from name analysis)
#   - Candidate SAL fact reference
#   - Migration action: add_spec_qname | create_spec_stub | rename_class | quarantine
# Outputs: backfill-inventory.yaml
```

### Phase 2: Spec Stub Generator (3-5 day effort)

```python
# tools/backfill/generate_spec_stub.py
# Given: format, namespace (e.g. "table"), element_name (e.g. "table-cell")
# Creates: src/python/{format}/spec/{namespace}/{element_name}.py
# Populates: spec_qname, spec_fact_ref, namespace_uri, local_name, facade_names
# Validates: SAL fact exists for spec_fact_ref
# Does NOT modify existing code
```

### Phase 3: Backfill Applicator (per format, 1-2 day effort per format)

For each format package:
1. Run inventory to identify classes needing backfill
2. For ODF formats (ods, odt, fodg, fodp): generate spec stubs based on FODS/FODT pattern
3. For non-XML formats (dif, sylk, csv, zst, xcf etc.): create governed canonical names
4. Add `spec_qname` attribute to existing domain classes (non-breaking addition)
5. Add `spec_fact_ref` attribute where SAL fact exists
6. Create Compat/ facade pointing to canonical stub (if format has package-level API)
7. Run tests to verify no regression

### Phase 4: Migration Tracking

```yaml
# registry/backfill-status.yaml
formats:
  - format_id: ods
    status: pending
    domain_classes_needing_backfill: [OdsDocument, OdsSheet, OdsRow, OdsCell]
    spec_stubs_needed: [table:table, table:table-row, table:table-cell, office:document]
    sal_facts_available: true (1066 facts)
    estimated_effort: 2 days
    risk: low (ODS is 80% same namespace as ODS but different container)
```

---

## ODF Format Backfill Priority (Easy Wins)

ODS and ODT share 80% of FODS/FODT's namespace. Their domain classes can be backfilled
by creating spec stubs that reference the SAME ODF namespaces:

| ODS Class | Spec QName | Existing Spec Stub? |
|-----------|-----------|-------------------|
| OdsDocument | office:document | YES (fods/spec/office/document.py) — REUSE |
| OdsSheet | table:table | YES (fods/spec/table/table.py) — REUSE |
| OdsRow | table:table-row | YES (fods/spec/table/table_row.py) — REUSE |
| OdsCell | table:table-cell | YES (fods/spec/table/table_cell.py) — REUSE |

**Easy win:** ODS and ODT domain classes can gain spec_qname attributes immediately by
referencing the FODS spec stubs. This is a 1-day effort.

---

## Non-XML Format Canonical Naming

For binary/text formats without XML namespaces, create a canonical naming registry:

```yaml
# registry/format-canonical-names.yaml
formats:
  - format_id: dif
    governed_names:
      - class_name: DifDocument
        canonical_name: DIF.Document
        spec_ref: "DIF specification §2.1 — TABLE record"
        fact_ref: FACT-DIF-001 (pending creation)
        qname_equivalent: "dif:document"
      - class_name: DifCell
        canonical_name: DIF.Cell
        spec_ref: "DIF specification §2.3 — DATA record"
        qname_equivalent: "dif:cell"
```

---

## Backfill Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Breaking existing public API | spec_qname is an additive attribute — never breaks |
| Breaking tests | Run full test suite before/after each format backfill |
| Wrong spec_qname mapping | Validate against SAL facts before applying |
| Missing SAL facts | Create minimal SAL facts for non-ODF formats before backfill |
| Conflicting class names | Compat/ facades absorb the format-prefixed names |

**Overall risk: LOW** — `spec_qname` addition is purely additive. No public API changes.
No behavior changes. Tests should not be affected.

---

## Recommended Action

Create `tools/backfill/` with inventory + generator scripts. Target ODS first (2 days,
low risk, reuses FODS spec stubs). Then ODT (1 day). Then DIF + SYLK (2 days each,
need canonical naming registry first). Binary formats (XCF, ZST, PBM/PGM/PPM, QOI) last
(most work, need SAL facts first).
