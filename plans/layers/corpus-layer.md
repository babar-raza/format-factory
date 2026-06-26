# Sample Corpus Layer

```yaml
layer_metadata:
  layer_id: L04
  canonical_name: Sample Corpus Layer
  canonical_slug: corpus-layer
  permanent_plan_path: plans/layers/corpus-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: NOT_ASSESSED
  health: UNKNOWN
  maturity_current: 2
  maturity_target: 3
  current_stage: DISCOVERY
  current_owner: null
  session_id: "923e237958c1"
  active_taskcards: []
  ready_taskcards: [TC-CORP-001]
  blocked_taskcards: []
  completed_taskcards: []
  dependencies: []
  upstream_layers: []
  downstream_layers: [L05, L06, L07]
  skill_ids: []
  command_ids: []
  evidence_paths: []
  last_updated_at: "2026-06-26"
  last_verified_at: null
  next_task_id: TC-CORP-001
  next_action: "Audit samples/by-format/ — verify coverage for all 24 formats; add governance"
```

---

## 2. Authority and Purpose

Owns the sample files used by oracle (L05), tests (L07), and format development (L06).
Current location: `samples/by-format/` (177 files, no governance).

## 3. Scope

- `samples/by-format/{format}/` — format sample files
- Coverage: 177 files across active formats

## 8. Ideal Production Design

1. One `samples/by-format/{format}/` directory per registered format
2. Minimum coverage: 3 samples per format (valid, minimal, edge case)
3. Sample manifest: `samples/by-format/{format}/manifest.yaml` with format, version, description
4. Governance: samples validated against oracle at every sprint
5. Provenance: samples cite source spec or generation method

## 9. Verified Current Implementation

- 177 files exist (per forensic audit)
- No manifest files
- No governance validators for corpus
- Oracle uses samples without validation of sample quality
- FODT sample path: `samples/by-format/fodt/minimal-document.fodt` (NOT in valid/)

## 14. Gap Register

| Gap ID | Severity | Current | Target | Taskcards |
|--------|----------|---------|--------|-----------|
| CORP-GAP-001 | MEDIUM | No corpus governance | Governed manifest per format | TC-CORP-001 |
| CORP-GAP-002 | MEDIUM | Coverage unknown for all formats | All 24 formats covered | TC-CORP-001 |

## 29. Active Taskcards

| Task ID | Title | Status |
|---------|-------|--------|
| TC-CORP-001 | Audit samples/by-format/; add manifests; close coverage gaps | TODO |

## 34. Work Log

```yaml
- log_id: WL-L04-001
  layer_id: L04
  task_id: TC-LP-001
  session_id: "923e237958c1"
  timestamp: "2026-06-26T00:00:00Z"
  event_type: LAYER_FILE_CREATED
  summary: "Created corpus-layer.md"
```

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L04-001
  layer_id: L04
  permanent_layer_plan: plans/layers/corpus-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  repository_revision: a7744cf6
  current_status: NOT_ASSESSED
  maturity_current: 2
  exact_next_task: TC-CORP-001
  allowed_paths: [samples/]
  forbidden_paths: [src/python/, src/net/]
  important_decisions:
    - "FODT sample: samples/by-format/fodt/minimal-document.fodt (not in valid/)"
  resume_instructions: >
    Corpus has not been assessed. First: list all samples/by-format/ directories.
    Check coverage per format. Create TC-CORP-001 to add missing samples.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file |
