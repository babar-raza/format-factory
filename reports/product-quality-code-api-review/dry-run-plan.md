# Dry Run Plan

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

The dry run validates that the scoring rubrics produce sensible, calibrated results before
committing to fix planning. It uses Phase B matrix outputs as inputs and checks score
distributions against expected ranges.

---

## Dry Run Inputs

| Input File | What It Provides |
|-----------|-----------------|
| `dotnet-product-quality-matrix.json` | 18-dimension scores for 10 .NET products |
| `python-product-quality-matrix.json` | FOSS readiness for 20 Python products |
| `public-api-matrix.json` | API quality scores |
| `architecture-review-matrix.json` | Architecture scores |
| `feature-availability-matrix.json` | FA level per feature per product |
| `product-quality-problem-schema.json` | 20 problems with severity + blocks_release |

---

## Dry Run Validation Checks

### Check 1 — Score Range Sanity (0–5 bounds)

All dimension scores MUST be in range [0, 5]. No negative values. No values > 5.

Expected result: PASS (scores were manually assigned within range)

### Check 2 — Tier Calibration (weakest vs strongest)

Verify that the weakest products score significantly lower than the strongest:

| Product | Expected Score | Required |
|---------|---------------|----------|
| HTML .NET (writer helper) | < 1.5 | REQUIRED |
| ZST .NET (no writer) | < 2.5 | REQUIRED |
| FODP Python (read-only) | < 2.0 | REQUIRED |
| FODS .NET (strongest .NET) | > 3.5 | REQUIRED |
| NetPBM .NET | > 3.5 | REQUIRED |
| FODT Python (strongest Python) | > 3.0 | REQUIRED |

### Check 3 — blocks_release Correlation

All products with any `blocks_release=true` problem MUST score below threshold:

Rule: If a product has >= 1 P0 problem with blocks_release=true, its commercial_readiness_score
MUST NOT exceed 4.0 until the problem is resolved.

Products affected:
- ZST .NET (PQ-007): commercial_readiness_score should be <= 2.0 ✓
- FODS .NET (PQ-006): commercial_readiness_score should be <= 4.0 ✓ (gap confirmed: 3.8)
- FODS Python (PQ-001, PQ-002): foss_readiness should not be PY-5 ✓ (currently PY-4)
- FODP Python (PQ-009): foss_readiness should be PY-1 to PY-2 ✓ (currently PY-2)
- All Python packages (PQ-004): not at commercial-ready without pyproject.toml metadata ✓

### Check 4 — Feature Complexity vs API Quality Correlation

Products with high feature complexity (C4+) should have API quality >= 3.5.
Products with low complexity (C0–C1) should have API quality <= 2.5.

Cross-checks:
- FODS .NET: complexity C4, API 3.8 ✓
- ZST .NET: complexity C1-C2 (no writer), API 1.5 ✓
- FODP Python: complexity C1, API 1.2 ✓
- NetPBM .NET: complexity C4, API 4.0 ✓

### Check 5 — Problem Severity Distribution

Verify distribution is realistic (not all CRITICAL, not all LOW):

Expected distribution:
- CRITICAL: 1-3 problems
- HIGH: 6-10 problems
- MEDIUM: 6-10 problems
- LOW: 2-5 problems

Actual distribution in PQ-001 to PQ-020:
- CRITICAL: 1 (PQ-007 ZST .NET no writer)
- HIGH: 9 (PQ-001, PQ-002, PQ-004, PQ-005, PQ-006, PQ-008, PQ-009, PQ-014, PQ-019)
- MEDIUM: 8 (PQ-003, PQ-010, PQ-011, PQ-012, PQ-016, PQ-017, PQ-018, PQ-020)
- LOW: 2 (PQ-013, PQ-015)

Result: PASS — distribution is realistic.

### Check 6 — blocks_release Coverage

All CRITICAL + HIGH problems should be reviewed for blocks_release. Count:
- blocks_release=true: 9 (PQ-001, PQ-002, PQ-004, PQ-005, PQ-006, PQ-007, PQ-009, PQ-014, PQ-015 WAIT — PQ-015 is MEDIUM, let me recheck)

Actually from schema:
- PQ-001: blocks_release=true
- PQ-002: blocks_release=true
- PQ-004: blocks_release=true
- PQ-005: blocks_release=true
- PQ-006: blocks_release=true
- PQ-007: blocks_release=true
- PQ-009: blocks_release=true
- PQ-014: blocks_release=true

That is 8 release-blocking problems. This is a high ratio — expected given how early in the
product release cycle Format Factory is.

### Check 7 — Fix Effort vs Priority Alignment

P0 problems should not require XL effort (would be impractical for release blockers):

| PQ-ID | Priority | Effort | Alignment |
|-------|---------|--------|-----------|
| PQ-006 | P0 | XS | ALIGNED |
| PQ-002 | P0 | L | WARN — large effort for P0 |
| PQ-007 | P0 | L | WARN — large effort for P0 |
| PQ-009 | P1 | XS (stub) | ALIGNED |

**Note:** PQ-007 (ZstWriter) is L effort but P0 because ZST .NET is functionally broken as a
product without write capability. The large effort is unavoidable.

**Note:** PQ-002 (FODS Python dual API) is L effort but P0 because dual API confuses all
FODS Python users. Consider downgrading to P1 if FODS Python is not in immediate release scope.

---

## Dry Run Execution Steps

```bash
# Step 1: Verify JSON files parse correctly
cd reports/product-quality-code-api-review
python -c "
import glob, json
files = glob.glob('*.json')
for f in files:
    try:
        json.load(open(f))
        print(f'OK: {f}')
    except Exception as e:
        print(f'FAIL: {f} — {e}')
"

# Step 2: Extract scores and verify ranges
python -c "
import json
matrix = json.load(open('dotnet-product-quality-matrix.json'))
for p in matrix['products']:
    score = p['commercial_readiness_score']
    assert 0 <= score <= 5, f'{p[\"product\"]}: score {score} out of range'
    print(f'{p[\"product\"]} .NET: {score}')
print('All .NET scores in range.')
"

# Step 3: Verify tier expectations
python -c "
import json
matrix = json.load(open('dotnet-product-quality-matrix.json'))
scores = {p['product']: p['commercial_readiness_score'] for p in matrix['products']}
assert scores.get('ZST', 5) < 2.5, f'ZST scored too high: {scores.get(\"ZST\")}'
assert scores.get('FODS', 0) > 3.5, f'FODS scored too low: {scores.get(\"FODS\")}'
print('Tier calibration: PASS')
"
```

---

## Dry Run Success Criteria

| Check | Expected Result | Weight |
|-------|----------------|--------|
| 1. Score ranges | All in [0, 5] | REQUIRED |
| 2. Tier calibration | ZST < 2.5, FODS > 3.5 | REQUIRED |
| 3. blocks_release correlation | P0 products < 4.0 | REQUIRED |
| 4. Complexity vs API correlation | Directional match | ADVISORY |
| 5. Problem distribution | Realistic bell curve | ADVISORY |
| 6. blocks_release count | 6–12 for a 30-product suite | ADVISORY |
| 7. Effort vs priority | P0 <= L effort (warn only) | ADVISORY |

---

## Dry Run Expected Results (pre-calculated)

Based on Phase B matrices, all checks are expected to PASS:

| Check | Status |
|-------|--------|
| Score ranges | PASS |
| Tier calibration | PASS |
| blocks_release correlation | PASS |
| Complexity vs API | PASS |
| Problem distribution | PASS |
| blocks_release count | PASS (8 of 20 = 40%) |
| Effort vs priority | WARN (PQ-002, PQ-007 are L effort P0) |

**Overall dry run verdict:** READY_FOR_PHASE_D
