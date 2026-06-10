# R109 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| R108 evidence_quality_score 0.0 blocks ACCEPTED_VERIFIED | High | High | Lane A specifically upgrades all 13 items with raw proof |
| API name collision (already exists) | Medium | Low | Pre-checked: HasSheet, ExportToHtmlFile, Posterize all confirmed absent |
| Context window exhaustion | Medium | Medium | Write reports incrementally, use subagents for parallel work |
| Raw log capture exceeds storage | Low | Low | Capture summary + first/last 50 lines per test run |
| Ledger SHA mismatch | Low | High | Verify SHAs before and after each governed API addition |
