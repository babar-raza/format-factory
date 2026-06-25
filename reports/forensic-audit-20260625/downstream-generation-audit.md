# Downstream Product Generation Audit

**Sprint/Run ID:** ff-archaeology-20260625

---

## Summary

The downstream generation pipeline exists and is partially operational. It is NOT
fully automated end-to-end. Source generation is task-driven (per-format, per-sprint)
rather than triggered automatically from spec changes. No template system exists — all
generation is programmatic Python scripts. The critical finding: malformed source no
longer enters from new skills, but the pre-governance monolithic codecs remain as
technical debt.

---

## Spec-to-Code Pipeline (Current State)

```
[Specification Documents]
  ↓ manual workbench review
[SAL Facts] (.local/spec-cache/sal-facts-{format}.json)
  ↓ capability_map_generator.py
[Capability Maps] (reports/capability-layer/unified-capability-map.json)
  ↓ capability_feature_compiler.py
[Next Work Items] (.local/supervisor/product/next-work-items.json)
  ↓ autonomous_cycle.py task selection
[Sprint Task Prompt] (reports/supervisor/next-sprint.md)
  ↓ skill execution (add-python-api, add-dotnet-api, etc.)
[Source Changes] (src/python/ or src/net/)
  ↓ tests + governance validators
[Evidence Declaration]
  ↓ autonomous_cycle.py grading
[Continuation Signal]
```

**Missing links:**
1. `gap_ledger_to_work_items.py` not in the loop (SYSARCH-005)
2. No auto-trigger when SAL facts change
3. No source generation from spec change events
4. No template-based code generation (all ad-hoc script-based)

---

## Source Generation Tools

| Tool | Purpose | Location | Status |
|------|---------|----------|--------|
| `generate_canonical_stubs.py` | Generate architecture-only spec/ skeleton files | `tools/spec/` | ACTIVE |
| `validate_spec_registry.py` | Validate `shared/qname-registry/*.yaml` | `tools/spec/` | ACTIVE |
| `generate_pilot_audit.py` | Generate audit report for a format | `tools/spec/` | ACTIVE |
| `ingest_review_findings.py` | Incorporate external findings | `tools/spec/` | ACTIVE |
| `validate_cross_language_parity.py` | Check .NET/.Python parity | `tools/spec/` | ACTIVE |
| `capability_map_generator.py` | Build capability maps from POC targets + SAL | `tools/capability_layer/` | ACTIVE |
| `capability_feature_compiler.py` | Translate gap-ledger → work items | `tools/supervisor/` | ACTIVE |

**No template library:** All generation is Python-scripted, not Jinja2/T4/ERB based.

---

## Where Malformed Source Enters

### Historical Entry Points (No Longer Active)

1. **Pre-governance era LLM coding (before 2026-06-01):**
   - No skill governance
   - No spec_qname requirement
   - No analytics separation rule
   - Produced monolithic codec files (1,500-4,000+ LOC)
   - Result: `zst_codec.py` was 4,210 LOC, `xcf_parser.py` was 3,997 LOC
   - **Status:** Healed in June 2026 (analytics extracted), caps frozen

2. **Capability-first feature additions (before 2026-06-10):**
   - Capability concepts added without SAL fact reference
   - No V53 enforcement
   - Produced classes without spec_qname
   - **Status:** V53, V18 now block these patterns

### Current Entry Points (ACTIVE RISKS)

1. **DIF/FODG codec classes (HIGH — existing gap):**
   - `dif_parser.py:DifData`, `dif_parser.py:DifCell` — missing spec_qname ClassVar
   - `fodg_codec.py:FodgFrame` — missing spec_qname ClassVar
   - These are EXISTING problems, not from new generation
   - **Mitigation needed:** QNAME-BACKFILL-001, QNAME-BACKFILL-002

2. **New codec class without registry entry (MEDIUM — theoretical):**
   - If a developer adds a new class to a codec file, V53 will catch it at sprint submission
   - No pre-commit hook enforces spec_qname
   - **Mitigation:** V53 at submission time (not perfect but operational)

3. **Analytics masquerade (LOW — deferred):**
   - `gnumeric_workbook_stats.py` named misleadingly
   - GAP-PROD-INV-MASQ-001 tracks this
   - V42 blocks `_mod_N_times_N` pattern but not general masquerade
   - **Mitigation:** Deferred rename (16+ import chain changes required)

---

## Feature Planning Pipeline

**Current feature planning:**
1. Gap-ledger generates open gaps
2. `capability_feature_compiler.py` scores and ranks them
3. `generate_next_worker_prompt.py` creates sprint prompt
4. `autonomous_cycle.py` injects gap_ledger_ref into work items (Step 3a-pre)

**Feature planning quality:**
- All product features trace to a gap-ledger entry
- All gap-ledger entries reference a capability map entry
- All capability map entries reference SAL facts (for ODF formats)
- For non-ODF formats: capability entries exist but SAL fact count is low

---

## Code Generation Gaps

| Gap | Description | Severity | Taskcard |
|-----|-------------|---------|---------|
| No auto-backfill | No script auto-adds spec_qname to codec classes | HIGH | BACKFILL-001 |
| No auto-Compat-gen | No script auto-creates Compat/ facades from registry | MEDIUM | BACKFILL-002 |
| No auto-domain-model-gen | No script auto-creates models.py from spec/ | MEDIUM | BACKFILL-001 |
| No template library | All generation is ad-hoc Python scripts | LOW | — |
| No spec-change trigger | No event that triggers regeneration on spec update | LOW | — |
| No rollback path | No automated rollback for failed generation | LOW | BACKFILL-003 |

---

## Downstream Generation Readiness Rating

| Criterion | Status |
|-----------|--------|
| Generation tools exist | YES |
| Templates exist | NO (scripts only) |
| Malformed source still entering | EXISTING GAPS (DIF/FODG) |
| New malformed source prevented | YES (V53, V18, V42) |
| Feature planning automated | PARTIAL (two compilers, one not wired) |
| Auto-backfill capability | NO |
| Rollback support | NO (git revert only) |

**Overall downstream generation readiness: PARTIAL. Tools exist but not fully automated
or integrated. Malformed source entry is mitigated but 2 formats still have gaps.**
