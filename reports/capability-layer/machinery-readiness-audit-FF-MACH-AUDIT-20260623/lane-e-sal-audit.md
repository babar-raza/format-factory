# Lane E — SAL (Specification Authority Layer) Audit
**Plan:** sorted-purring-stardust | **Taskcard:** TC-LANE-E | **Requirement:** REQ-LANE-E

## 1. SAL Tool Inventory
| Tool | LOC | Status | Purpose |
|------|-----|--------|---------|
| refresh_check.py | 297 | ACTIVE | Staleness scanner (exit 0=current, 1=stale). Read-only. |
| acquire_spec.py | 397 | ACTIVE | Network downloader + indexer. Requires --allow-network. |
| spec_index.py | 372 | ACTIVE (library) | YAML parsing library for spec-index.yaml management. |
| propagate_source_hash.py | 98 | ACTIVE (utility) | Hash propagator for post-download content hashes. |

All 4 tools are ACTIVE — none dormant.

## 2. SAL Output Statistics
- **File:** .local/sal-output/sal-facts-latest.json
- **generated_at:** 2026-06-21T14:44:45 (2 days old — FRESH)
- **formats_processed:** 23
- **spec_facts_total:** 14,309
- **workbench_verified:** 14,284 (99.8% verified)
- **FODS facts:** 4,991 in verified-facts-review.yaml

## 3. Step 0a-Refresh Wiring
- **Location:** autonomous_cycle.py lines 272-330
- **Behavior:** Checks sal-facts-latest.json age. If >7 days: runs sal_master_runner.py --all --from-cache-only (timeout=300s). On success: triggers capability_map_generator.py refresh. On failure: WARNING only (non-blocking).
- **Policy:** Completely non-blocking per Supreme Directive.

## 4. Fact Quality Assessment (FODS sample)
- Each fact has: qname (e.g., FACT-FODS-001), section, description, authority, verification_status
- verified-facts-review.yaml shows detailed provenance (spec page, extraction method, SHA256)
- Quality: HIGH (99.8% verified)

## 5. Staleness Handling Classification
- **Current:** ADVISORY (warning only, non-blocking)
- **RC-7 assessment:** SAL staleness is warn-only. Sprint can proceed with stale facts.
- **Recommendation:** Escalate to SPRINT-BLOCKING when >7 days AND sprint_type is product (not machinery:sal_repair)
- **Design decision:** Advisory vs blocking — recommend BLOCKING for product sprints only
