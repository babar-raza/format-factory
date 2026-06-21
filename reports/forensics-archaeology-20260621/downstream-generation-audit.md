# Downstream Generation Audit

**Sprint:** forensics-archaeology-20260621

---

## Where Product Code Enters the System

### Generation Pathways (current)

```
1. Direct sprint work → product source files edited by agent
2. Capability compiler → generates taskcards (not source directly)
3. Skills (add-python-api etc.) → prompts agent to write specific code
4. Autonomous product deepening → agent selects from next-sprint.md tasks
5. Plan-based execution → agent follows taskcard from per-chat plan
```

**Critical observation:** There is NO code generator that writes Python or .NET source files
programmatically. All source generation is done by the LLM following skill prompts. This means:
- Quality is bounded by skill prompt quality
- Repeatability depends on skill enforcement
- A bad sprint can introduce malformed code that passes tests but violates spec

### Where Malformed Classes Enter

Malformed classes (no spec_qname, wrong names) enter at Step 1 and 3 when:
- The skill prompt doesn't require spec_qname
- The agent uses format-prefixed names instead of canonical names
- The governance validators don't check for this
- The supervisor grades the sprint as PASS based on tests alone

**Evidence:** 106 classes in src/python/ have no spec_qname. These were generated in sprints
where spec_qname was either not required or not enforced.

---

## Feature Planning → Code Generation Flow

```
SAL facts → capability gaps → gap ledger → task generation → sprint prompt → code generation
```

**Current state of each step:**

| Step | Status | Problem |
|------|--------|---------|
| SAL facts | PARTIAL — ODF formats only | 0 facts for 8+ formats |
| Capability gaps | 958 entries | severity=unknown; no fact_refs |
| Gap ledger → task generation | PARTIALLY WIRED | advisory_only may still be true |
| Task generation → sprint prompt | ACTIVE | uses next-sprint.md + next-work-items.json |
| Sprint prompt → code generation | ACTIVE | but no spec_qname enforcement |

---

## Same-Format Save Assessment

| Format | Python Write | .NET Write |
|--------|-------------|-----------|
| FODS | PARTIAL (writer.py exists, status unknown) | YES (FodsWriter.cs verified) |
| FODT | PARTIAL (parser only, unclear) | YES (FodtWriter.cs verified) |
| ODS | YES (ods_writer.py) | NO |
| CSV | YES (csv_writer.py) | YES (CsvWriter.cs) |
| NDJSON | YES (ndjson_codec.py) | YES (NdjsonWriter.cs) |
| TSV | NO (tsv_parser.py only) | YES (TsvWriter.cs) |
| Others | NO | NO |

---

## Export / Conversion Assessment

| Format | Python Export | .NET Export |
|--------|--------------|------------|
| FODS | CSV (csv_exporter.py) | CSV, HTML, JSON, PDF, ODS, PNG |
| FODT | none visible | HTML, TXT, Markdown, PDF, PNG |
| ODS | CSV (ods_csv_exporter.py) | NO |
| NDJSON | none | CSV (NdjsonCsvExporter.cs) |
| TSV | none | CSV (TsvCsvExporter.cs) |
| Netpbm | cross-format (pbm→pgm, etc.) | NO |

---

## Governance / Validation in Generation Loop

| Check | When Applied | By What |
|-------|-------------|---------|
| LOC cap | Post-sprint | source_structure_validator.py (V35) |
| Function count | Post-sprint | source_structure_validator.py (V35) |
| Analytics skill required | Post-sprint | deepening_suspension_validator (V42) |
| Monolith detection | Post-sprint | monolith_detection_validator (V43) |
| spec_qname presence | NEVER | Not wired |
| Overclaim detection | NEVER | Not wired |
| SAL fact reference | NEVER | Not wired |
| Lane compliance | NEVER (prompt-only) | Not wired |

**Verdict:** The generation loop has partial governance (LOC, function count, analytics
suspension) but lacks the critical spec_qname enforcement. Code can be generated and
pass all current governance checks while violating the spec-to-feature pipeline.

---

## Downstream Generation Readiness

| Component | Status |
|-----------|--------|
| Code generator (LLM-based) | ACTIVE |
| Skill enforcement | WEAK — no spec_qname requirement |
| Governance checks on generation | PARTIAL — LOC/function caps enforced |
| Spec-literal generation | NOT PRESENT — no template from SAL to code |
| Regeneration safety | NOT PRESENT — no spec-version tracking |
| Backfill of malformed code | NOT PRESENT — no facility |

**Rating:** Red for repeatability. Orange for current safety (LOC/function caps do catch
some issues). Green for operational continuity (system works day-to-day).
