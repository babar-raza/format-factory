# Specification Authority Layer

```yaml
layer_metadata:
  layer_id: L01
  canonical_name: Specification Authority Layer
  canonical_slug: specification-authority-layer
  permanent_plan_path: plans/layers/specification-authority-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: HARDENING_REQUIRED
  health: DEGRADED
  maturity_current: 2
  maturity_target: 4
  current_stage: FORENSIC_RECON
  current_owner: null
  agent_type: null
  session_id: "923e237958c1"
  active_sprint: "lp-bootstrap"
  active_taskcards: []
  ready_taskcards: [TC-SAL-001]
  blocked_taskcards: []
  completed_taskcards: []
  dependencies: []
  upstream_layers: []
  downstream_layers: [L02, L03, L14]
  skill_ids: [ingest-spec-sal, sal-pipeline-heal]
  command_ids: [ingest-spec-sal, sal-pipeline-heal]
  evidence_paths:
    - plans/snoopy-juggling-seal.md
    - reports/layer-audit-2026-06-26/forensic-layer-discovery-report.md
  last_started_at: "2026-05-06"
  last_progress_at: "2026-06-26"
  last_updated_at: "2026-06-26"
  last_verified_at: null
  last_verified_revision: null
  next_task_id: TC-SAL-001
  next_action: "Activate 17 dormant SAL tools; run spec extraction for all 20 Python FOSS formats"
  handoff_id: null
```

---

## 1. Layer Metadata

See YAML block above.

## 2. Authority and Purpose

The Specification Authority Layer (SAL) is the **upstream source of all authoritative
specification facts**. It is responsible for:

- Extracting specification facts from format specifications (OASIS ODF, IETF RFCs, etc.)
- Normalizing spec text into structured FACT-{FORMAT}-NNN entries
- Making spec facts available to downstream layers (L02-QName, L03-Capability)
- Providing the V13 AND rule evidence: `spec_fact_refs` must cite real FACT-* entries

**Critical state:** SAL is the most critical underperforming layer. Only 5-6 of 20
Python FOSS formats have real spec facts. The chain
EXTERNAL SPEC → LOCAL SNAPSHOT → PARSED FACTS → QNAME → CAPABILITY → FEATURE
is broken at the first link for 14+ formats.

**Active plan:** `plans/snoopy-juggling-seal.md` (SAL forensics plan — do NOT use
for general plan amendments; it is the SAL forensics plan specifically)

## 3. Scope

- `tools/specification-authority-layer/` (24 tools total)
  - 3 active: spec_source_registry, context_pack_builder, spec_governance_runtime
  - 17 dormant: spec_parser, spec_normalizer, spec_indexer, requirement_extractor,
    spec_verifier, and 12 others
- `.local/sal-output/` — output directory for SAL facts
- `shared/spec-snapshots/` — local spec snapshot files (if any)

## 4. Explicit Non-Scope

- Does NOT own QName entries (that is L02)
- Does NOT own capabilities (that is L03)
- Does NOT own product source (that is L06)
- Does NOT download specs without governance (all downloads through spec_source_registry)

## 5. Owned Decisions

- Which specs are canonical for each format (OASIS ODF 1.3, etc.)
- Fact ID namespace convention: FACT-{FORMAT}-NNN
- Fact extraction frequency (currently: once, 2026-05-06)
- Spec snapshot storage location
- Which formats get real facts vs. exception_classification

## 6. Upstream Inputs

- External format specifications (OASIS, IETF, etc.) — downloaded via spec_source_registry
- `registry/format-registry.yaml` — format metadata including spec_body and spec_version

## 7. Downstream Consumers

| Consumer | What it needs |
|----------|--------------|
| L02 QName | Spec fact IDs to confirm canonical class names |
| L03 Capability | spec_fact_refs in capability records |
| L08 Evidence | V13 validator checks spec_fact_refs in declarations |
| L12 Validation | V-NEW-001/002 SAL validators |

## 8. Ideal Production Design

The ideal SAL pipeline:

1. **spec_source_registry** — knows canonical spec URL + version for all 20+ formats
2. **spec_downloader** — downloads + caches spec at spec-snapshots/{format}/
3. **spec_parser** — parses spec XML/HTML/PDF into normalized text blocks
4. **spec_normalizer** — produces normalized spec lines (57,803 lines already generated for FODS/FODT)
5. **spec_indexer** — builds searchable index from normalized text
6. **requirement_extractor** — identifies spec requirements (MUST, SHOULD, SHALL)
7. **fact_generator** — creates FACT-{FORMAT}-NNN entries with section refs, page refs
8. **fact_verifier** — verifies facts against spec text
9. **sal_facts_exporter** — writes `.local/sal-output/sal-facts-latest.json`
10. **coverage_reporter** — reports fact count and coverage per format

**Trigger:** SAL pipeline runs at minimum once per format, ideally on every spec version update.

## 9. Verified Current Implementation

```yaml
current_layer_implementation:
  implementation_paths:
    - tools/specification-authority-layer/sal_master_runner.py
    - tools/specification-authority-layer/spec_source_registry.py  # ACTIVE
    - tools/specification-authority-layer/context_pack_builder.py   # ACTIVE
    - tools/specification-authority-layer/spec_governance_runtime.py  # ACTIVE
    - tools/specification-authority-layer/spec_parser.py            # DORMANT
    - tools/specification-authority-layer/spec_normalizer.py        # DORMANT
    - tools/specification-authority-layer/spec_indexer.py           # DORMANT
    - tools/specification-authority-layer/requirement_extractor.py  # DORMANT
    - tools/specification-authority-layer/spec_verifier.py          # DORMANT
    # + 12 more dormant tools
  active_components:
    - spec_source_registry (knows spec URLs)
    - context_pack_builder (builds context packs)
    - spec_governance_runtime (runtime governance)
  partially_implemented_components:
    - sal_facts_json: exists for FODS (10 initial facts), FODT, ODS, ODT, FODG, FODP (via merge)
  missing_components:
    - spec_parser: not running (DORMANT)
    - spec_normalizer: not running (DORMANT)
    - fact_generator: not running (DORMANT)
    - fact_verifier: not running (DORMANT)
  stale_components:
    - fact_extraction_run030: ran 2026-05-06, produced 10 FODS facts, then stopped
  bypass_paths:
    - Formats use exception_classification instead of spec_fact_refs (approved for Tier 2)
  contradictions: []
```

## 10. Current Execution Stage

**FORENSIC_RECON** — The SAL pipeline has been forensically analyzed. Root causes known.
17 tools are dormant. Last extraction run: 2026-05-06.

## 11. Current Maturity Assessment

**LEVEL 2 — PARTIAL**

Justification:
- Infrastructure exists (24 tools, tool directory)
- 3 tools are active
- 14,441 total facts exist (mostly FODS/FODT/ODS/ODT area)
- `/ingest-spec-sal` and `/sal-pipeline-heal` skills registered (2026-06-26)

But:
- 17 of 24 tools dormant
- 14 of 20 Python formats have ZERO spec facts
- Last real extraction: 2026-05-06
- Fact extraction pipeline is effectively frozen

## 12. Target Maturity

**LEVEL 4 — GOVERNED**

Required:
- All 20 Python FOSS formats have ≥1 real spec fact
- Fact extraction runs automatically on schedule
- Facts cited in V13 AND rule for PRODUCT_SOURCE items
- spec_parser, spec_normalizer, fact_generator operational

## 13. Current Strengths

- `/ingest-spec-sal` skill registered (TC-LA-004)
- `/sal-pipeline-heal` skill registered
- 14,441 facts for 6 formats (FODS/FODT/ODS/ODT/FODG/FODP cover the major ODF formats)
- spec_source_registry knows canonical spec URLs
- 57,803 normalized spec lines already exist for FODS/FODT

## 14. Gap Register

| Gap ID | Severity | Current State | Target State | Root Cause | Taskcards |
|--------|----------|---------------|--------------|------------|-----------|
| SAL-GAP-001 | CRITICAL | 14 formats have 0 facts | All 20 formats have ≥1 fact | Extraction ran once 2026-05-06, then stopped | TC-SAL-001 |
| SAL-GAP-002 | HIGH | 17 tools dormant | All tools active | No automated trigger for extraction | TC-SAL-001 |
| SAL-GAP-003 | HIGH | Facts not wired to V13 AND rule for many items | All PRODUCT_SOURCE items cite spec_fact_refs | Facts not available to cite | TC-SAL-001 |
| SAL-GAP-004 | MEDIUM | No schedule for fact extraction | Periodic extraction (quarterly) | Architecture gap | TBD |

## 15. Root-Cause Register

- **SAL-GAP-001/002:** The fact extraction pipeline was implemented, ran once (run030, 2026-05-06,
  produced 10 FODS facts), and then was never triggered again. The 17 dormant tools have code but
  no automated trigger. The `/ingest-spec-sal` skill (TC-LA-004) is the activation path but
  has not been executed for the remaining 14 formats.

- **SAL-GAP-003:** V13 AND rule requires BOTH gap_ref AND spec_auth. For formats without real SAL
  facts, workers use `exception_classification` (approved for Tier 2 formats). For Tier 1 formats
  with facts, workers must cite specific FACT-* IDs. The chain is incomplete because fact IDs
  for most formats don't exist yet.

## 16. Repair Architecture

**TC-SAL-001:**
1. Run `/ingest-spec-sal` skill for CSV, TSV, NDJSON, TOML, ABW, DIF, GNUMERIC, SYLK, XCF, QOI, PBM, PGM, PPM (13 formats)
2. For each: download spec snapshot → parse → normalize → extract facts → generate FACT-{FORMAT}-NNN entries
3. For formats with no public spec (ABW, SYLK, DIF, GNUMERIC, TSV): use `schema_authority_available` exception classification
4. Update `.local/sal-output/sal-facts-latest.json` with all new facts
5. Run tools/specification-authority-layer/sal_master_runner.py to rebuild coverage report
6. Verify V13 passes for all updated format declarations

## 17. Schemas and Contracts

- FACT-{FORMAT}-NNN naming convention
- `spec_fact_refs: ["FACT-CSV-001"]` field in PRODUCT_SOURCE declarations
- `exception_classification: schema_authority_available` for Tier 2 formats
- `provenance_chain` field (SAL-HEAL-B001): fact_id + section_ref + page_ref + source_sha256

## 18. Producers

- `/ingest-spec-sal` skill invocation starts the pipeline
- `sal_master_runner.py` orchestrates all tools

## 19. Consumers

- L02 QName: confirms class name choices against spec terminology
- L03 Capability: capability records cite spec facts
- L08 Evidence: V13 validator checks `spec_fact_refs` presence
- L12 Validation: V-NEW-001 (capability_fact_ratio), V-NEW-002 (spec_fact_provenance)

## 20. Skills and Commands

| Skill | Purpose |
|-------|---------|
| /ingest-spec-sal | Run SAL pipeline for one or more formats |
| /sal-pipeline-heal | Repair dormant SAL tools and re-run extraction |

## 21. Validators and Enforcement

- V13: `spec_fact_refs_wired` — BOTH gap_ref AND spec_auth required for PRODUCT_SOURCE
- V-NEW-001: `capability_fact_ratio` — warn if capabilities/verified_facts > 10
- V-NEW-002: `spec_fact_provenance` — warn if READINESS items lack provenance_chain

## 22. Tests and Negative Controls

- Positive: run `/ingest-spec-sal` for CSV → verify FACT-CSV-NNN entries appear in sal-facts-latest.json
- Negative: declare PRODUCT_SOURCE for CSV with `spec_fact_refs: ["FACT-CSV-999"]` (non-existent) → V13 should FAIL

## 23. Evidence and Observability

- `.local/sal-output/sal-facts-latest.json` — all facts
- `reports/layer-audit-2026-06-26/forensic-layer-discovery-report.md` — coverage report
- SAL coverage metric: 6/20 formats with real facts (30%)

## 24. Recovery and Rollback

- Fact extraction is additive (new facts append, existing preserved)
- If extraction fails for a format: `exception_classification` approved fallback
- Roll back by deleting FACT-{FORMAT}-NNN entries from sal-facts-latest.json

## 25. Security and Compliance

- All spec downloads go through spec_source_registry (URL validation)
- Spec snapshots stored locally (no external dependencies at runtime)

## 26. Cross-Layer Handoffs

| Handoff | From | To | Artifact |
|---------|------|----|---------|
| HO-001 | L01 | L02 | .local/sal-output/sal-facts-latest.json |
| HO-002 | L01 | L03 | .local/sal-output/sal-facts-latest.json |

## 27. Migration and Backfill

For formats using `exception_classification`, backfill path:
1. Run `/ingest-spec-sal` to generate real facts
2. Update declarations to use `spec_fact_refs` instead
3. Remove exception_classification entries (if Tier 1)
4. Tier 2 formats keep exception_classification permanently

## 28. Effort and Dependencies

- TC-SAL-001: ~8 hours (13 formats × 30 min per format pipeline run)
- No upstream dependencies (SAL is the root of the spec chain)
- Unblocks: TC-QN-001, TC-CAP-001, TC-FEAT-001

## 29. Active Taskcards

| Task ID | Title | Status | Priority |
|---------|-------|--------|---------|
| TC-SAL-001 | Activate 17 dormant SAL tools; run extraction for all 20 formats | TODO | P0 |

## 30. Ready Taskcards

TC-SAL-001 — READY (no dependencies).

## 31. Completed Taskcards

(None in this session)

## 32. Blocked and Waiting Work

- SAL-GAP-004 (scheduled extraction) — requires architecture decision.

## 33. Decision Log

| Decision | Date | Rationale |
|----------|------|-----------|
| Tier 2 formats use exception_classification | Pre-existing | No public spec available |
| SAL facts use FACT-{FORMAT}-NNN naming | Pre-existing | Consistent with V13 convention |
| plans/snoopy-juggling-seal.md is SAL forensics plan | Pre-existing | Do NOT use for general amendments |

## 34. Work Log

```yaml
- log_id: WL-L01-001
  layer_id: L01
  task_id: TC-LP-001
  session_id: "923e237958c1"
  sprint_id: lp-bootstrap
  timestamp: "2026-06-26T00:00:00Z"
  event_type: LAYER_FILE_CREATED
  summary: "Created specification-authority-layer.md permanent plan file"
  repository_revision: a7744cf6
  changed_paths: [plans/layers/specification-authority-layer.md]
  current_stage: FORENSIC_RECON
  status: IN_PROGRESS
  next_action: "Execute TC-SAL-001 via /ingest-spec-sal skill"
```

## 35. Verification Log

```yaml
- verification_id: VER-L01-001
  layer_id: L01
  task_id: null
  repository_revision: a7744cf6
  contracts_verified:
    - "24 tools exist in tools/specification-authority-layer/"
    - "3 tools are active (spec_source_registry, context_pack_builder, spec_governance_runtime)"
    - "14,441 total facts in .local/sal-output/ (mostly FODS/FODT/ODS area)"
    - "/ingest-spec-sal and /sal-pipeline-heal skills registered"
  focused_result: PARTIAL  # 6/20 formats have real facts
  integration_result: PARTIAL  # V13 passes for most items via exception_classification
  verdict: VERIFIED_WITH_EXPLICIT_LIMITATION
  limitation: "14 of 20 Python FOSS formats have ZERO spec facts"
  verified_at: "2026-06-26"
  verifier: forensic-layer-discovery-report.md
```

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L01-001
  layer_id: L01
  permanent_layer_plan: plans/layers/specification-authority-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  repository_revision: a7744cf6
  current_status: HARDENING_REQUIRED
  current_stage: FORENSIC_RECON
  maturity_current: 2
  exact_next_task: TC-SAL-001
  why_this_is_next: >
    SAL is the most critical underperforming layer. 14 of 20 formats have ZERO
    spec facts, breaking the EXTERNAL SPEC → LOCAL SNAPSHOT → PARSED FACTS →
    QNAME → CAPABILITY → FEATURE chain. TC-SAL-001 activates 17 dormant tools
    and runs extraction for all 14 missing formats.
  ready_tasks: [TC-SAL-001]
  blocked_tasks: []
  required_skills: [ingest-spec-sal, sal-pipeline-heal]
  required_commands: [ingest-spec-sal, sal-pipeline-heal]
  allowed_paths:
    - tools/specification-authority-layer/
    - .local/sal-output/
    - shared/spec-snapshots/
  forbidden_paths:
    - src/python/
    - src/net/
  required_verification:
    - "All 20 formats have ≥1 entry in sal-facts-latest.json"
    - "V13 passes for all PRODUCT_SOURCE items (or has valid exception_classification)"
  important_decisions:
    - "plans/snoopy-juggling-seal.md is SAL FORENSICS PLAN — do not use for general amendments"
    - "Tier 2 formats (ABW/SYLK/DIF/GNUMERIC/TSV) use exception_classification permanently"
  unresolved_findings:
    - "SAL-GAP-001: 14 formats have 0 facts"
    - "SAL-GAP-002: 17 tools dormant"
    - "SAL-GAP-004: no scheduled extraction"
  known_risks:
    - "Without real SAL facts, V13 relies on exception_classification — reduces spec parity"
    - "57,803 normalized spec lines for FODS/FODT exist but are unused"
  resume_instructions: >
    READ this file §16 Repair Architecture.
    EXECUTE: python tools/specification-authority-layer/sal_master_runner.py
    OR use /ingest-spec-sal skill for each missing format.
    Verify .local/sal-output/sal-facts-latest.json gets entries for 14 new formats.
```

## 37. Exact Next Actions

1. Run `/sal-pipeline-heal` skill — checks which tools are dormant and attempts activation
2. For each of 14 missing formats (CSV, TSV, NDJSON, TOML, ABW, DIF, GNUMERIC, SYLK, XCF, QOI, PBM, PGM, PPM): run `/ingest-spec-sal --format {format}`
3. Verify `.local/sal-output/sal-facts-latest.json` has new FACT-{FORMAT}-NNN entries
4. Update this file §9 `active_components` with newly activated tools
5. Transition status from `FORENSIC_RECON` to `IMPLEMENTATION`

## 38. Layer Completion Gate

```yaml
sal_layer_completion_gate:
  permanent_plan_exists: true
  all_formats_have_facts: false  # 14/20 missing
  pipeline_tools_active: false  # 17/24 dormant
  facts_cited_in_declarations: false  # V13 uses exception_classification for most
  scheduled_extraction: false  # no automation
  overall: HARDENING_REQUIRED
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (bootstrap TC-LP-001) |
