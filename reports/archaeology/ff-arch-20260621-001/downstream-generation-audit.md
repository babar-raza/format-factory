# Downstream Generation Audit — ff-arch-20260621-001

## Summary

**There is NO automated source generation pipeline.** All product source in `src/` was
handwritten by autonomous agents using sprint prompts and skill commands. The machinery
exists at multiple layers but the layers are NOT connected end-to-end.

---

## Current Product Generation Path (as-is)

```
Sprint prompt (next-sprint.md)
  └─> Agent reads sprint task
      └─> Agent calls skill (e.g., /add-python-api)
          └─> Skill prompt tells agent what file to create/modify
              └─> Agent handwrites source code based on skill prompt
                  └─> Agent commits file to src/
```

No spec consultation occurs in this path. No QName validation occurs.
No capability map lookup occurs. No SAL fact retrieval occurs.

---

## What Should Happen (target pipeline)

```
SAL pipeline (run_extraction_pipeline.py)
  └─> Spec facts in sal-facts-latest.json
      └─> Capability compiler (capability_compiler.py)
          └─> Feature IR with spec fact refs
              └─> QName ontology generator (qname_ontology_generator.py)
                  └─> Canonical class names and paths
                      └─> Source generator (MISSING)
                          └─> Generated source in src/{Namespace}/{Element}.cs
                              └─> Spec-aligned, canonical, testable
```

**The source generator is MISSING.** Steps 1-5 exist with varying completeness.
Step 6 (source generator) does not exist.

---

## Skills That Generate Product Source

### /add-python-api (`.claude/commands/add-python-api.md`)
- Tells agent to add a Python function to a format package
- Does NOT require spec_qname reference
- Does NOT require canonical class naming
- Does NOT check qname-to-code-map.yaml
- Produces functions like `fods_sheet_count()` — not spec-aligned classes

### /add-dotnet-api (`.claude/commands/add-dotnet-api.md`)
- Tells agent to add a .NET API to a format package
- Does NOT require spec_qname reference
- Does NOT validate against qname-to-code-map.yaml
- Produces classes like `FodsCell` — not canonical `Table.TableCell`

### /add-python-object-model-feature (`.claude/commands/add-python-object-model-feature.md`)
- Specifically for object model additions
- Status: EXISTS but not deeply audited

### /add-dotnet-object-model-feature (`.claude/commands/add-dotnet-object-model-feature.md`)
- Status: EXISTS but not deeply audited

### /spec-literal-qname-to-code-mapping (`.claude/commands/spec-literal-qname-to-code-mapping.md`)
- Specifically maps spec QNames to code
- This IS the right tool but unclear if it's being used in product deepening sprints

---

## Where Malformed Classes Are Introduced

1. **Sprint prompts tell agents to "add X capability to format Y"** without specifying canonical naming
2. **Agents use format-prefixed names** because no naming validation exists at write time
3. **Skills don't enforce QName compliance** — they produce whatever the agent writes
4. **No pre-commit validator** checks class names against `qname-to-code-map.yaml`
5. **Product deepening rotations** (the old analytics deepening) generate functions in bulk
   without any spec backing — now governed by TC-GUARD-001 but enforcement is recent

---

## Malformed Source Entry Points

| Entry Point | Naming Risk | QName Risk | Can Bypass |
|---|---|---|---|
| /add-python-api skill | HIGH (functions not classes) | HIGH | Yes |
| /add-dotnet-api skill | HIGH (FodsXxx naming) | HIGH | Yes |
| Autonomous product deepening | CRITICAL (bulk generation) | CRITICAL | Yes (until TC-GUARD-001) |
| /add-python-object-model-feature | MEDIUM | MEDIUM | Partially |
| /add-dotnet-object-model-feature | MEDIUM | MEDIUM | Partially |

---

## Same-Format Save Capability

| Product | Save Exists | Round-Trip Tested | Evidence |
|---------|-------------|-------------------|---------|
| .NET FODS | YES | YES | FodsDocument.Save() — Gate evidence |
| .NET FODT | YES | YES | FodtDocument.Save() — Gate evidence |
| Python FODS | YES | YES | write_fods() — tested |
| Python FODT | PARTIAL | PARTIAL | writer.py exists |
| .NET CSV | YES | LIKELY | CsvWriter.cs |
| Python CSV | YES | YES | csv_writer.py |

---

## Export/Conversion Capability

| Product | Export Targets | Status |
|---------|---------------|--------|
| .NET FODS | CSV, HTML, JSON, ODS, PDF, PNG | Active |
| .NET FODT | HTML, Markdown, TXT, PDF, PNG | Active |
| Python FODS | CSV, HTML | Active |
| Python ODS | CSV | Active |
| Others | Limited or none | Prototype |
