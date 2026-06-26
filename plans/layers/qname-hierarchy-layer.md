# QName Hierarchy Authority Layer

```yaml
layer_metadata:
  layer_id: L02
  canonical_name: QName Hierarchy Authority
  canonical_slug: qname-hierarchy-layer
  permanent_plan_path: plans/layers/qname-hierarchy-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: GOVERNED_OPERATIONAL
  health: HEALTHY
  maturity_current: 3
  maturity_target: 4
  current_stage: GOVERNED_OPERATION
  current_owner: null
  session_id: "923e237958c1"
  active_taskcards: []
  ready_taskcards: [TC-QN-001]
  blocked_taskcards: []
  completed_taskcards: []
  dependencies: [L01]
  upstream_layers: [L01]
  downstream_layers: [L03, L06]
  skill_ids: [qname-backfill, spec-literal-qname-to-code-mapping]
  command_ids: [qname-backfill, spec-literal-qname-to-code-mapping]
  evidence_paths:
    - reports/qname-coverage-20260626.json
    - reports/sal-qname-gap-20260626.json
  last_updated_at: "2026-06-26"
  last_verified_at: "2026-06-26"
  last_verified_revision: "a7744cf6"
  next_task_id: TC-QN-001
  next_action: "Add QName entries for ora/pam/xpm/zpaq; close intentional gap fodt:office:body"
```

---

## 1-4. Identity, Authority, Scope, Non-Scope

**Authority:** The canonical mapping from specification QName identifiers to
Python/C# class hierarchies. Governs the rule:
`Spec QName → Canonical Class (e.g., Table.TableCell) → Facade in Compat/ only (e.g., FodsCell)`

**Scope:** `shared/qname-registry/{format}.yaml` (one file per format)

**Non-Scope:** Does NOT own spec facts (L01), capabilities (L03), or product source (L06).

## 5. Owned Decisions

- Canonical class name for each QName
- Compat/ facade naming convention
- Coverage target (current: 99.4%, 1 intentional gap)

## 6-7. Upstream Inputs / Downstream Consumers

- **Upstream:** L01 SAL facts confirm spec QName terminology
- **Downstream:** L03 Capability uses QNames to generate capability records; L06 Product implements canonical classes

## 8. Ideal Production Design

1. One YAML file per format with all spec QNames and their canonical classes
2. 100% coverage (all active QNames mapped)
3. Automated V49-V55 validator checks
4. Canonical names used in product source `spec_qname: ClassVar[str]` declarations

## 9. Verified Current Implementation

- 79 entries across `shared/qname-registry/`
- 75 implemented, 3 verified, 1 architecture_only
- 99.4% coverage (65/66 active entries)
- 1 intentional gap: `fodt:office:body` (documented)
- QName coverage report: `reports/qname-coverage-20260626.json`
- Validators V49-V55 operational (WARN-only)
- V73 (.NET): `SpecQName` constant required in Spec/*.cs files

## 10-11. Stage / Maturity

**GOVERNED_OPERATION** / **LEVEL 3 — OPERATIONAL**

Gap preventing L4: fodt:office:body intentional gap; 4 formats (ora/pam/xpm/zpaq) not yet registered.

## 14. Gap Register

| Gap ID | Severity | Current | Target | Taskcards |
|--------|----------|---------|--------|-----------|
| QN-GAP-001 | LOW | fodt:office:body intentional gap | Close or document formally | TC-QN-001 |
| QN-GAP-002 | LOW | ora/pam/xpm/zpaq not in registry | Add when products exist | TC-QN-001 |

## 29. Active Taskcards

| Task ID | Title | Status |
|---------|-------|--------|
| TC-QN-001 | Add QName entries for 4 new formats; close intentional gap | TODO |

## 34. Work Log

```yaml
- log_id: WL-L02-001
  layer_id: L02
  task_id: TC-LP-001
  session_id: "923e237958c1"
  timestamp: "2026-06-26T00:00:00Z"
  event_type: LAYER_FILE_CREATED
  summary: "Created qname-hierarchy-layer.md"
  current_stage: GOVERNED_OPERATION
```

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L02-001
  layer_id: L02
  permanent_layer_plan: plans/layers/qname-hierarchy-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  repository_revision: a7744cf6
  current_status: GOVERNED_OPERATIONAL
  maturity_current: 3
  exact_next_task: TC-QN-001
  why_this_is_next: >
    Coverage is 99.4% (missing fodt:office:body and 4 no-product formats).
    TC-QN-001 closes the gap and brings coverage to 100% for active formats.
  allowed_paths: [shared/qname-registry/]
  forbidden_paths: [src/python/, src/net/]
  required_verification: ["reports/qname-coverage-{date}.json shows 100%"]
  resume_instructions: >
    QName registry is healthy. Coverage 99.4%. Next work is TC-QN-001.
    Use /qname-backfill skill. Verify V49-V55 validators pass after changes.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file |
