# Repair + Advancement Plan — R105

## Repairs (GROUP 1-2)
1. Package identity contamination: FIXED (builder restructured, validator added)
2. Stale gap contamination: FIXED (fresh acceleration gaps generated with R105 sprint ID)
3. Dirty state unclassified: FIXED (dirty_state_classification field added)
4. Global state mislabeled: FIXED (global-state/ prefix in builder)

## Advancement (GROUP 3)
1. Package identity validator: NEW tool (16 tests)
2. Anti-skip checker: 9->11 detectors (8 new tests)
3. Prompt quality validator: NEW tool (7 tests)
4. Builder identity fix: restructured packaging (6 existing tests still pass)

## Balance
- 4 repairs + 4 advancements
- Repair is packaging/identity focused (not product code)
- Advancement is real acceleration tooling (not just evidence packaging)
