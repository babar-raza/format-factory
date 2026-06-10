# Mainstream Gap Priority Table

## Sprint
`FORMAT-FACTORY-SUPERVISOR-PRODUCT-TRAFFIC-CONTROLLER-INTEGRATION-001`

## Source
`.local/supervisor/selected-product-gaps.json` — 8 mainstream gaps

## Priority-Ordered Gap Table

| Rank | Priority | Gap ID | Format | Track | Type | Skill |
|------|----------|--------|--------|-------|------|-------|
| 1 | 125 | commercial-net-fods-dogfood-status-fods-to-csv-dotnet | FODS | commercial_net | dogfood CSV export | governed-dogfood-export |
| 2 | 125 | commercial-net-fods-dogfood-status-fods-to-html-dotnet | FODS | commercial_net | dogfood HTML export | governed-dogfood-export |
| 3 | 125 | commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet | FODT | commercial_net | dogfood Markdown export | governed-dogfood-export |
| 4 | 125 | commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet | FODT | commercial_net | dogfood TXT export | governed-dogfood-export |
| 5 | 110 | foss-reduced-sylk-python-status-installed-workflow | SYLK | foss_reduced | installed workflow | governed-installed-workflow-verification |
| 6 | 90 | foss-reduced-netpbm-blockers-1 | Netpbm | foss_reduced | FOSS proof | governed-dogfood-export |
| 7 | 90 | foss-reduced-sylk-blockers-1 | SYLK | foss_reduced | writer not implemented | governed-dogfood-export |
| 8 | 90 | foss-reduced-zst-blockers-1 | ZST | foss_reduced | dependency resolution | governed-dependency-resolution-review |

## Families in Next Sprint (Target 3+)

For CLEAN_PASS, Mainstream must touch 3+ format families. Recommended combination:

**Option A (highest priority):** FODS + FODT + Netpbm
- Covers 3 families (all commercial_net or foss_reduced)
- FODS: 2 dogfood gaps (CSV + HTML) — priority 125 each
- FODT: 2 dogfood gaps (Markdown + TXT) — priority 125 each
- Netpbm: 1 FOSS proof gap — priority 90

**Option B (broader):** FODS + FODT + SYLK + ZST
- Covers 4 families
- Includes ZST dependency resolution

**Recommended: Option A** — highest priority score per gap, governed skills available for all.

## CLEAN_PASS Requirements Checklist

For next Mainstream sprint to achieve CLEAN_PASS:
- [ ] families_touched ≥ 3 (currently 2 → need +1)
- [ ] source_diffs ≥ 3 (currently 2 → need +1)
- [ ] governed_transcripts ≥ 3 (currently 0 → need Skills consumption)
- [ ] raw_logs ≥ 3 (currently 0)
- [ ] capability_matrix_deltas ≥ 3 (currently 0)
- [ ] repair_items < product_items (currently 0 < 8 ✓)
