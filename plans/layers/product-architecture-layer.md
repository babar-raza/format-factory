# Product Architecture Layer

```yaml
layer_metadata:
  layer_id: L06
  canonical_name: Product Architecture Layer
  canonical_slug: product-architecture-layer
  permanent_plan_path: plans/layers/product-architecture-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: EXECUTION_IN_PROGRESS
  health: HEALTHY
  maturity_current: 4
  maturity_target: 5
  current_stage: IMPLEMENTATION
  current_owner: null
  session_id: "923e237958c1"
  active_taskcards: []
  ready_taskcards: []
  blocked_taskcards: [TC-PROD-001]
  completed_taskcards: []
  dependencies: [L01, L02, L03, L14]
  upstream_layers: [L01, L02, L03, L14]
  downstream_layers: [L05, L07, L08, L16, L19]
  skill_ids:
    - add-python-api
    - add-dotnet-api
    - add-dotnet-object-model-feature
    - add-python-object-model-feature
    - add-same-format-writer-feature
    - decompose-monolithic-codec
  command_ids:
    - add-python-api
    - add-dotnet-api
    - add-dotnet-object-model-feature
    - add-python-object-model-feature
  evidence_paths:
    - registry/source-structure-baseline.json
    - docs/code-quality/production-library-standard-v2.md
    - reports/r90/product-code-change-ledger.json
  last_updated_at: "2026-06-26"
  last_verified_at: "2026-06-26"
  last_verified_revision: "a7744cf6"
  next_task_id: TC-PROD-001
  next_action: "Continue .NET deepening S141+; Gate 11 execution requires Babar Raza"
```

---

## 1-4. Identity, Authority, Scope, Non-Scope

**Authority:** The primary product deliverable — format packages for Python (FOSS)
and .NET (commercial). Governed by Production Library Standard v2.

**Scope:**
- `src/python/{format}/` — 20+ Python format packages
- `src/net/{format}/` — 10+ .NET format packages
- `registry/source-structure-baseline.json` — LOC caps (write-once)
- `docs/code-quality/production-library-standard-v2.md` — governing standard

**Non-Scope:** Tests (L07), evidence (L08), oracle (L05), capabilities (L03).

## 5. Owned Decisions

- 8-layer file structure per format (Spec, Domain, Parser, Writer, Analytics, Export, Compat, Public API)
- LOC caps per file (baseline_loc_cap in source-structure-baseline.json — write-once, never increase)
- spec_qname: ClassVar[str] required in every domain model class
- Analytics overflow splits PERMANENTLY FORBIDDEN (*_analytics_extra.py)

## 8. Ideal Production Design

Every format package follows the 8-layer structure:

```
src/python/{format}/
  spec/           # Spec-literal stubs with spec_qname ClassVars
  models/         # Domain models with spec_qname
  parser/         # Parse-only (no write operations)
  writer/         # Write-only (no parse operations)
  {format}_analytics.py  # Analytics (spec-fact-traced only)
  export/         # {format}_to_{target}.py transformations
  Compat/         # Compat/{format}_{class}.py facades only
  __init__.py     # Public API (≤100 LOC)
  exceptions.py   # Format-specific exceptions
```

Governance:
- V35: LOC cap enforcement (baseline_loc_cap write-once)
- V66: single responsibility (one layer per file)
- V73: .NET SpecQName constant
- V75/V76: dependency direction + error hierarchy

## 9. Verified Current Implementation

- 20 Python packages: fods, fodt, ods, odt, fodg, fodp, xcf, zst, ndjson, toml, csv, tsv, abw, dif, gnumeric, sylk, qoi, pbm, pgm, ppm
- 10+ .NET packages: FODS, FODT, Netpbm, CSV, NDJSON, ZST, and others
- 1,609 tests passing (combined Python + .NET)
- Latest sprint: ff-gates-advancement-20260625 (S140 .NET deepening)
- FODS Gate 11: 8/31 criteria. G11-G APPROVED by Babar Raza.
- FODT: Customer-readiness ALL 8 PASS.

## 10-11. Stage / Maturity

**IMPLEMENTATION** / **LEVEL 4 — GOVERNED**

Gate 11 execution blocked (Babar Raza sign-off needed).

## 14. Gap Register

| Gap ID | Severity | Current | Target | Taskcards |
|--------|----------|---------|--------|-----------|
| PROD-GAP-001 | CRITICAL | Gate 11 not executed | Babar Raza sign-off | BLOCKED_EXTERNAL |
| PROD-GAP-002 | MEDIUM | .NET deepening at S140 | S160+ target | TC-PROD-NET-001 |
| PROD-GAP-003 | MEDIUM | Some formats lack exceptions.py | All formats have exceptions.py (V76) | TC-PROD-EXC-001 |

## 20. Skills and Commands

| Skill | Purpose | SAL-aware |
|-------|---------|----------|
| /add-python-api | Add Python format API method | Yes (spec_qname required) |
| /add-dotnet-api | Add .NET format API method | Yes (SpecQName required) |
| /add-dotnet-object-model-feature | Add .NET object model class | Yes |
| /add-python-object-model-feature | Add Python object model class | Yes |
| /add-same-format-writer-feature | Add writer feature | Yes |
| /decompose-monolithic-codec | Break monolithic codec into layers | No |

## 21. Validators and Enforcement

- V35: LOC cap (baseline_loc_cap write-once, never increase)
- V44: facade delegates to spec (WARN-only)
- V45: QName class names (canonical naming)
- V49: spec_qname structure required in spec/ classes
- V66: single responsibility per file
- V69: analytics naming enforced
- V73: .NET SpecQName constant
- V74: ledger continuation gate
- V75: dependency direction (WARN existing, FAIL new)
- V76: error hierarchy (WARN existing, FAIL new)

## 29-31. Taskcards

Active: None (sprint S140 complete)
Ready: .NET deepening S141+ (see reports/supervisor/next-sprint.md)
Blocked: Gate 11 execution (TRUE_EXTERNAL_GATE — Babar Raza)

## 34. Work Log

```yaml
- log_id: WL-L06-001
  layer_id: L06
  task_id: TC-LP-001
  session_id: "923e237958c1"
  timestamp: "2026-06-26T00:00:00Z"
  event_type: LAYER_FILE_CREATED
  summary: "Created product-architecture-layer.md"
```

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L06-001
  layer_id: L06
  permanent_layer_plan: plans/layers/product-architecture-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  repository_revision: a7744cf6
  current_status: EXECUTION_IN_PROGRESS
  maturity_current: 4
  exact_next_task: "Continue .NET deepening S141+ per reports/supervisor/next-sprint.md"
  why_this_is_next: >
    Product deepening continues after each sprint. The general ledger (next-sprint.md)
    drives selection when no per-chat plan is active.
  blocked_tasks: [TC-PROD-001]
  allowed_paths: [src/python/, src/net/, tests/python/, tests/net/]
  forbidden_paths: []
  important_decisions:
    - "Gate 11 G11-G APPROVED for FODS/FODT/Netpbm — but G11 EXECUTION needs Babar Raza"
    - "LOC caps are write-once: baseline_loc_cap NEVER increases"
    - "Analytics overflow splits PERMANENTLY FORBIDDEN"
    - "Product deepening uses /add-python-api or /add-dotnet-api skills"
  unresolved_findings:
    - "Gate 11 execution blocked on Babar Raza commercial decision"
  resume_instructions: >
    READ reports/supervisor/next-sprint.md for current sprint prompt.
    Use /add-dotnet-api or /add-python-api skills.
    Check source-structure-baseline.json for LOC caps before adding functions.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file |
