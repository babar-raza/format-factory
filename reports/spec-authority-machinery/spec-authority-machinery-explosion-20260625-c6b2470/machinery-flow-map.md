# Machinery Flow Map — Spec Authority Pipeline
## Run ID: spec-authority-machinery-explosion-20260625-c6b2470

---

## Diagram 1: Intended Spec Authority Acquisition Flow

```
External Source (OASIS PDF / RFC / Community Spec)
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │  T3 Authorization Gate                               │
 │  - Legal category verified                           │
 │  - Redistribution policy confirmed                   │
 │  - Canonical URL locked                              │
 │  - Version pinned                                    │
 │  - Operator sign-off recorded                        │
 │  - Format registered in qname-registry               │
 └───────────────────────┬──────────────────────────────┘
                         │ AUTHORIZED
                         ▼
               acquire_spec.py
               (download + SHA-256 hash)
                         │
                         ▼
          .local/spec-cache/{format}/{version}/
          ├── spec-index.yaml         ← source manifest
          ├── raw/                    ← original PDF/RFC/HTML
          └── normalized/
              ├── text.txt            ← full text extraction
              ├── sections.jsonl      ← section boundaries
              ├── chunks.jsonl        ← retrieval chunks
              ├── page-map.yaml       ← page → section map
              └── citations.yaml     ← cross-references
                         │
                         ▼
               run_extraction_pipeline.py
               (fact extraction from normalized text)
                         │
                         ▼
          workbench/
          ├── candidate-facts.yaml   ← machine-extracted candidates
          ├── verified-facts.yaml    ← human/tool-verified facts
          ├── requirement-packs/     ← grouped requirements
          │   ├── FACT-{FMT}-001.yaml
          │   └── ...
          └── task-packets/          ← work items per fact
                         │
                         ▼
          sal-facts-{format}.json    ← canonical FACT-{FMT}-NNN registry
                         │
                         ▼
          authority_gate_validation.py
          → P-level classification (P0→P6)
          → product_expansion_allowed flag
```

---

## Diagram 2: Actual FODS Flow (Production-Quality Path)

```
OpenDocument-v1.3-os-part3-schema.pdf
[CACHED: .local/spec-cache/fods/1.3/raw/]
        │
        ▼
normalized/text.txt          ← 4988 fact candidates extracted
normalized/sections.jsonl    ← ODF 1.3 section boundaries
normalized/chunks.jsonl      ← retrieval-ready chunks
        │
        ▼
workbench/verified-facts.yaml
        4348 verified facts
        ├── FACT-FODS-001: office:document element (P6 COMPLETE)
        ├── FACT-FODS-002 through FACT-FODS-010: needs_review
        └── (4978 remaining facts at draft/needs_review)
        │
        ▼
sal-facts-fods.json
        4988 FACT-FODS-NNN canonical IDs
        │
        ▼
Compat/fods_document.py    ← "Spec authority: FACT-FODS-001, ODF 1.3 §3.1"
Compat/fods_sheet.py       ← "Spec authority: FACT-FODS-004, ODF 1.3 §9.1"
Compat/fods_cell.py        ← "Spec authority: FACT-FODS-006, ODF 1.3 §9.5"
        │
        ▼
tests/python/fods/test_r125_fact_traceability.py
        ← Behavioral assertions: QN_DOCUMENT value, namespace URI, mimetype
        ← Cites: FACT-FODS-001
        │
        ▼
authority-conveyor-20260608/fods-p6-proof-graph.yaml
        ← COMPLETE for FACT-FODS-001 ONLY
        ← Explicit scope: "P6 claimed ONLY for FACT-FODS-001"
        │
        ▼
authority_gate_validation.py → P6
        ⚠️  BUG: _check_code_citations() uses rglob("*.py")
            includes build/ artifacts → false P6 for other facts
        ⚠️  SCOPE: P6 is 1/4988 facts (0.02% coverage)

────────────────── ENFORCEMENT PATH ──────────────────

PRODUCT_SOURCE sprint item submitted
        │
        ▼
V13 (validate_spec_fact_refs_wired)
    IF spec_fact_refs PROVIDED AND INVALID → FAIL (blocks_sprint=True)
    IF spec_fact_refs ABSENT → NO ENFORCEMENT ← CRITICAL GAP
    IF exception_classification present → PASS
        │
        ▼
TC-GUARD-001 (autonomous_cycle.py Step 2d3)
    IF gap_ledger_ref OR capability_ref OR spec_fact_refs → PASS
    ← gap_ledger_ref ALONE bypasses spec_fact_refs requirement
```

---

## Diagram 3: Actual Gnumeric Flow (Schema-Only — Designed Bypass)

```
No published Gnumeric XML specification
        │
        ▼
XSD Schema (gnumeric-stf-2.0.xsd available via GNOME)
        │
        ▼
.local/spec-cache/gnumeric/v10/
├── spec-index.yaml
│   ├── source_type: schema_xsd_only
│   ├── normalized_text_cached: false    ← NO text extraction
│   └── no_spec_text_reason: "No formal narrative spec available"
└── workbench/
    └── verified-facts-review.yaml
        ├── FACT-GNUMERIC-001: <gnm:Workbook> root element  (structural)
        ├── FACT-GNUMERIC-002: <gnm:Sheets> container      (structural)
        └── FACT-GNUMERIC-003: <gnm:Sheet> element         (structural)
        ← 3 facts from XSD inspection, NOT from narrative spec text
        │
        ▼
authority_gate_validation.py → P1
        ← SCHEMA_ONLY_FORMATS frozenset includes "gnumeric"
        ← product_expansion_allowed: FALSE (P1 < MIN=P4)
        │
        ▼ ← BYPASS PATH ──────────────────────────────────────────┐
product_task_selector.py                                           │
    _get_format_authority_status()                                 │
    Checks poc-targets.yaml membership ONLY                       │
    Does NOT call authority_gate_validation.py                    │
    Gnumeric IN poc-targets → ALLOWED ← BUG (ignores P1)         │
        │                                                         │
        ▼                                                         │
_CANDIDATE_CATALOG (hard-coded task list)                         │
        ├── "gnumeric:read_workbook"                              │
        ├── "gnumeric:get_sheet_count"                            │
        └── "gnumeric:get_cell_value"                            │
    ← Tasks emitted WITHOUT P4 authority gate                    │
        │                                                         │
        ▼                                                         │
generate_next_worker_prompt.py                                    │
    READ_BEFORE_EXECUTION: [poc-targets, gap-ledger, skill-reg]  │
    ← NO spec facts injected (none to inject at P1)             │
    ← NO requirement pack referenced                             │
        │                                                         │
        ▼                                                         │
Worker executes Gnumeric task                                     │
    Code: gnumeric_codec.py                                       │
    ← No FACT-GNUMERIC-* citations in code                       │
        │                                                         │
        ▼                                                         │
Evidence declaration:                                             │
    gap_ledger_ref: GAP-GNUMERIC-*                               │
    spec_fact_refs: null  ← ABSENT, NOT ENFORCED               │
    exception_classification: schema_authority_available          │
        │                                                         │
        ▼                                                         │
V13: exception_classification → PASS ← designed bypass          │
TC-GUARD-001: gap_ledger_ref → PASS ← designed bypass           │
Sprint ACCEPTED ──────────────────────────────────────────────────┘
```

---

## Diagram 4: Intended Autonomous Execution Flow (Design Target)

```
Gap Ledger Entry (GAP-{FORMAT}-*)
        │
        ▼
product_task_selector.py
    ← Calls authority_gate_validation.py
    ← Checks: authority_level >= MIN_PRODUCT_EXPANSION_LEVEL (P4)
    ← BLOCKED if P < 4 AND no exception_classification
        │ P >= 4 (or exception approved)
        ▼
generate_next_worker_prompt.py
    ← Injects: authority_level, top-N verified facts, requirement_pack_path
    ← READ_BEFORE_EXECUTION includes: sal-facts-{format}.json,
                                      workbench/requirement-packs/{FACT}.yaml,
                                      workbench/verified-facts.yaml
        │
        ▼
Worker prompt contains:
    "The following spec facts must be cited in code:
     FACT-{FMT}-NNN: [requirement text from §X.Y]"
        │
        ▼
Worker generates code with citations:
    # Spec authority: {element} (FACT-{FMT}-NNN, {Spec} §{section})
        │
        ▼
Tests cite fact IDs:
    """Behavioral assertion per FACT-{FMT}-NNN:
       - Element <{tag}> MUST appear exactly once at root
       - Namespace MUST be {namespace_uri}"""
        │
        ▼
Evidence declaration:
    spec_fact_refs: ["FACT-{FMT}-NNN", "FACT-{FMT}-NNN+1"]
    gap_ledger_ref: GAP-{FORMAT}-*
        │
        ▼
V13: spec_fact_refs present + valid → PASS
TC-GUARD-001: spec_fact_refs present → PASS
authority_integration_fabric.py called → updates proof graph
        │
        ▼
Proof graph extended:
    spec.pdf → FACT-{FMT}-NNN → code_file → test_file → evidence
        │
        ▼
authority_gate_validation.py advances format P-level
Product ledger records authority_level at sprint close
```

---

## Diagram 5: Actual Autonomous Execution Flow (Current Reality)

```
Gap Ledger Entry (GAP-{FORMAT}-*)
        │
        ▼
product_task_selector.py
    ← _get_format_authority_status() checks poc-targets.yaml ONLY
    ← Binary: IN poc-targets → ALLOWED, else BLOCKED
    ← Does NOT check authority_gate_validation.py P-level ← BUG
    ← _BLOCKED_AUTHORITY_STATES frozenset defined but never populated
        │ "ALLOWED" (any format in poc-targets)
        ▼
generate_next_worker_prompt.py
    READ_BEFORE_EXECUTION: [poc-targets, gap-ledger, skill-registry,
                            unified-capability-map, ...]
    ← sal-facts-{format}.json NOT in list
    ← workbench/ artifacts NOT in list
    ← requirement-packs NOT in list
    ← authority_level NOT injected ← CRITICAL GAP
        │
        ▼
Worker prompt contains:
    "Format: {format}. Gap: GAP-{FORMAT}-*. Implement {capability}."
    ← No spec facts
    ← No requirement pack reference
    ← No behavioral requirements derived from spec
        │
        ▼
Worker generates code WITHOUT citations:
    def get_sheet_count(model): ...  ← no FACT-* comment
        │
        ▼
Tests check happy-path only:
    assert get_sheet_count(model) >= 0  ← no fact citation
    assert GnumericWorkbook.spec_fact_ref == "FACT-GNUMERIC-001"
    ← identifier test, NOT behavioral proof
        │
        ▼
Evidence declaration:
    gap_ledger_ref: GAP-{FORMAT}-*   ← satisfies TC-GUARD-001
    spec_fact_refs: null              ← absent = NOT ENFORCED
    exception_classification: {valid exception}  ← bypasses V13
        │
        ▼
TC-GUARD-001:
    gap_ledger_ref present → PASS (OR logic bypass)
    ← spec_fact_refs NOT required when gap_ledger_ref present
V13:
    spec_fact_refs absent → NO ENFORCEMENT (only fires if present+invalid)
    exception_classification present → PASS anyway
        │
        ▼
Sprint ACCEPTED
        │
        ▼
authority_integration_fabric.py → NOT CALLED (unwired)
Proof graph → NOT UPDATED (disconnected from sprint)
Product ledger → authority_level NOT RECORDED
authority_gate_validation.py P-level → NOT ADVANCED
        │
        ▼
System state: No spec authority advancement despite ACCEPTED sprint
```

---

## Summary: Actual vs. Intended Gap Table

| Stage | Intended | Actual | Gap |
|-------|----------|--------|-----|
| Task selection | P-level gate via authority_gate_validation.py | poc-targets binary check | MISSING_GATE |
| Prompt injection | Spec facts + requirement packs | No spec data in prompt | MISSING_INJECTION |
| Code citation | FACT-* in code comments | None (ODF Compat only) | MISSING_CITATION |
| Test citation | Facts cited in assertions | Identifier-only tests | WEAK_TEST |
| Evidence | spec_fact_refs mandatory | spec_fact_refs absent=no-op | MISSING_ENFORCEMENT |
| Gate | AND(gap_ref, fact_refs OR exception) | OR(gap_ref, fact_refs) | BYPASS_LANE |
| Proof graph | Updated per sprint | Never updated | DISCONNECTED |
| P-level advance | Per format, per sprint | Never advances autonomously | STATIC |
| Integration fabric | Called at sprint start | Never called | UNWIRED |
