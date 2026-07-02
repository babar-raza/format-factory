# /score-format

Apply the Format Factory scoring model to a format candidate and produce a scoring sheet.

## Usage

```
/score-format <format_id>
```

Example: `/score-format fods`

## What This Command Does

1. **Read format registry** — Load `registry/format-registry.yaml` to find the format entry
2. **Read scoring model** — Load `registry/scoring-model.yaml` for dimension weights and thresholds
3. **Score each dimension** — Apply scoring criteria across: market demand, spec availability, OSS ecosystem, implementation complexity, commercial value, POC tractability
4. **Compute weighted total** — Multiply each dimension score by its weight; sum for final score
5. **Classify tier** — Map final score to tier (TIER-1, TIER-2, TIER-3, HOLD)
6. **Write scoring sheet** — Output to `reports/scoring/<format_id>-scoring-sheet.md`

## Required Inputs

- `format_id` — The format identifier as it appears in `registry/format-registry.yaml`

## Steps

```
1. Read registry/format-registry.yaml → find entry for <format_id>
2. Read registry/scoring-model.yaml → load dimension definitions
3. For each scoring dimension:
   a. Assess current evidence (specs, community, impl complexity)
   b. Assign score 1-5 per dimension rubric
   c. Apply weight → weighted_score
4. Sum weighted_scores → final_score
5. Classify: TIER-1 (≥4.0), TIER-2 (3.0-3.9), TIER-3 (2.0-2.9), HOLD (<2.0)
6. Write reports/scoring/<format_id>-scoring-sheet.md
7. Update registry/format-registry.yaml with tier if changed
```

## Output Format

```
# Scoring Sheet: <FORMAT_ID>
## Final Score: X.X / 5.0 — TIER-N

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| market_demand | 4 | 0.25 | 1.00 |
| ...

## Rationale
...
```

## Validation

Complete when:
- `reports/scoring/<format_id>-scoring-sheet.md` exists
- Score and tier are recorded in `registry/format-registry.yaml`
- All scoring dimensions have justification text

## Allowed Paths

- `registry/ — format registry (read-only unless updating registry)`
- `reports/ — acquisition reports (write)`
- `plans/ — acquisition plans (read/write)`

## Forbidden Paths

- `src/net/**` — no product source mutation during acquisition
- `src/python/**` — no product source mutation during acquisition
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if a scoring sheet cannot be produced
- Stop if any required input field is missing or invalid
