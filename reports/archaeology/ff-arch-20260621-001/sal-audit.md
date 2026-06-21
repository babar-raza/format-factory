# SAL Audit — ff-arch-20260621-001

## SAL (Specification Authority Layer) Summary

**Status: EXISTS but DISCONNECTED from product generation**

The SAL has significant machinery built, a spec cache populated with facts, and integration
tests. However, the pipeline from SAL output → capability → source generation is NOT
automated and NOT enforced.

---

## SAL Files Present (tools/specification-authority-layer/)

| File | Purpose | Status |
|------|---------|--------|
| spec_parser.py | Parse spec vault snapshots into ParsedSpec sections | EXISTS |
| spec_normalizer.py | Normalize spec content for extraction | EXISTS |
| spec_indexer.py | Build searchable index of spec sections | EXISTS |
| spec_digestor.py | Digest spec content into facts | EXISTS |
| spec_governance_runtime.py | Runtime governance checks | EXISTS |
| spec_source_registry.py | Registry of spec sources | EXISTS |
| spec_vault_ingest.py | Ingest spec content into vault | EXISTS |
| spec_verifier.py | Verify extracted facts against source | EXISTS |
| requirement_extractor.py | Extract requirements from spec | EXISTS |
| requirement_graph.py | Build requirement dependency graph | EXISTS |
| run_extraction_pipeline.py | Run full extraction pipeline | EXISTS |
| run_fact_verification.py | Verify facts against spec | EXISTS |
| sal_master_runner.py | Master runner for SAL pipeline | EXISTS |
| context_pack_builder.py | Build context packs from spec facts | EXISTS |
| fact_coverage_report.py | Report on fact coverage | EXISTS |

**16 SAL modules exist. This is substantial machinery.**

---

## Spec Cache (`.local/spec-cache/`)

Spec facts are cached for 15 formats:
abw, csv, dif, fodg, fodp, fods, fodt, gnumeric, ods, odt, pbm, pgm, ppm, tsv, zst

Evidence: `.local/spec-cache/fods/1.3/` and `.local/spec-cache/fodt/odf-1.3/` exist.

**SAL facts exist and are being maintained.**

---

## SAL Integration into Gap Ledger

The gap ledger (`reports/capability-layer/gap-ledger.json`) references spec facts:
```json
"spec_facts": ["FACT-FODS-001", "FACT-FODS-003", ..., "FACT-FODS-032"]
```

This means SAL facts ARE being used to annotate capability gaps.
**The SAL → capability link exists and is populated.**

---

## SAL Integration into Product Source

**NONE.** No product source file in `src/` contains a machine-generated spec fact reference
that traces back to SAL output. The spec references in `FodsDocument.cs` comments are manually
written (e.g., "ODF 1.3 §9.4.5") not SAL-generated references.

The `capability_compiler.py` in `tools/supervisor/` attempts to load SAL facts:
```python
SAL_OUTPUT_PATH = REPO_ROOT / ".local" / "sal-output" / "sal-facts-latest.json"
```
But `.local/sal-output/sal-facts-latest.json` was not found in the repo.

**Gap: SAL pipeline does not produce the `sal-facts-latest.json` file that the capability compiler expects.**

---

## SAL Determinism Assessment

The SAL extracts facts from spec vault snapshots. Determinism depends on:
1. Stable spec vault content — YES (cache is content-addressed)
2. Deterministic parser — LIKELY (spec_parser.py uses regex, not AI)
3. Stable fact IDs — UNCERTAIN (fact IDs like FACT-FODS-001 are sequential; re-running may change order)
4. Negative tests (rejection of non-spec authority) — UNKNOWN (not audited in depth)

**SAL is SEMI-deterministic. Needs negative test coverage to confirm authority rejection.**

---

## SAL Gaps

| Gap | Severity | Fix |
|-----|----------|-----|
| SAL output not connected to capability compiler | BLOCKER | Run SAL pipeline to produce sal-facts-latest.json |
| No automated SAL → source generation | BLOCKER | Build source generation step in pipeline |
| Fact IDs may not be stable across re-runs | HIGH | Add stable fact ID policy |
| No negative tests (reject non-spec authority) | HIGH | Add rejection tests to SAL |
| Manual spec references in source (not SAL-generated) | MEDIUM | Migrate to SAL fact refs |
| SAL facts exist but FODT context pack not complete | MEDIUM | Extend SAL to cover all FODT elements |
