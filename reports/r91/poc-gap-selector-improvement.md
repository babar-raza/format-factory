---
sprint: R91
generated_by: r91-worker
---

# POC Gap Selector Improvement

## Summary

The gap selector has been updated with a priority-ranked scoring model. Output files updated: `.local/supervisor/selected-product-gaps.json` and `reports/supervisor/product-gap-selection.md`.

## Ranking Logic

Gaps are scored and ranked by the following priority tiers:

### Priority 1: FODS/FODT/Netpbm Commercial POC Gaps

Formats with active commercial POC status (`poc_status: active` in `product-capability-matrix/poc-targets.yaml`) rank highest. Criteria:
- Gap exists in `poc-targets.yaml` for an active commercial format
- Gap is not yet implemented (`status: gap`)
- Skill exists in skill registry to implement it

Score: 100 + (days_since_last_advance * 2)

### Priority 2: Dogfood Gaps with Missing Export

Dogfood bridges where `dogfood_status != IMPLEMENTED` and the required library path exists in the source format. Criteria:
- Source format has working parser
- Target format has working writer (even if in different track)
- Bridge has not been implemented

Score: 80 + (number_of_dependent_tests * 1)

### Priority 3: Same-Format Save Gaps

Formats that can parse but cannot write back to the same format. Criteria:
- Parser exists and is tested
- Writer does not exist or is a stub
- Same-format roundtrip would add measurable product value

Score: 60

### Priority 4: Installed-Package Proof Gaps

Formats at Gate 10 that lack an installed-package example or smoke test. Lower priority than new API work but still scheduled.

Score: 40

### Priority 5: Shallow API Gaps

Additional API surface that adds convenience but does not advance core POC or dogfood status.

Score: 20

## Output: .local/supervisor/selected-product-gaps.json

Updated after each selection run. Format:

```json
{
  "selected_at": "ISO-8601",
  "gaps": [
    {
      "gap_id": "...",
      "format_name": "fods",
      "track": "net",
      "priority": 1,
      "score": 102,
      "feature_name": "SetCellValue",
      "skill_to_use": "add-dotnet-object-model-feature",
      "acceptance_criteria": "..."
    }
  ]
}
```

## Output: reports/supervisor/product-gap-selection.md

Human-readable table showing all selected gaps, their priority tier, score, and recommended skill. Includes a "why selected" column explaining the scoring rationale for each gap.

## ZST/Netpbm/SYLK FOSS Gaps

Three FOSS POC formats receive dedicated selection entries:

| Format | Gap | Priority |
|---|---|---|
| ZST | dependency_mode_documented | 3 |
| Netpbm (Python) | installed_package_example | 4 |
| SYLK | malformed_row_diagnostics | 3 |

These are included in the selection output so the next-sprint generator can assign them to LANE-SAFE-PRODUCT lanes.

## Integration

The gap selector is called by `autonomous_cycle.py` Step 4 (after grading) so that new-work selection is informed by which items were just accepted or rejected.
