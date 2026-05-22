# R51 AI Acceleration Pilot

**Sprint:** FORMAT-FACTORY-R51-INSTALLED-ARTIFACT-BASELINE-AND-AI-ACCELERATION-001
**Run:** R51
**Date:** 2026-05-22

---

## Purpose

R51 AI acceleration pilot (round 2). R50 ran the first live call for object-model gap priority analysis. R51 targets formula preservation design — the highest-priority gap confirmed by R50's AI analysis.

---

## Call Record

| Field | Value |
|-------|-------|
| Model | recommended (via llm.professionalize.com) |
| Endpoint | llm.professionalize.com (GPT_OSS_ENDPOINT) |
| Purpose | FODS formula preservation design: neutral model schema + parser + writer changes |
| Prompt tokens | 148 |
| Completion tokens | 400 |
| Total tokens | 548 |
| finish_reason | length (max_tokens=400 hit) |
| Status | LIVE_AI_CALL_R51: PASS |

---

## AI Response (ai_draft — not authoritative)

The AI recommended a 3-part approach:

### 1. Neutral model schema change
Add optional `formula` key to cell dict:
```python
cell = {"value": 12.34, "value_type": "float", "formula": "of:=SUM([.A1:.A5])"}
```

### 2. Parser change
Extract the `table:formula` attribute from `<table:table-cell>` elements:
```python
formula = cell_elem.get('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}formula')
if formula:
    cell_dict['formula'] = formula
```

### 3. Writer change
Emit formula attribute if present:
```python
if cell.get('formula'):
    attribs['{...}formula'] = cell['formula']
```

---

## Verification Status

AI output is `ai_draft`. Verification against ODF spec required before implementation.
- TC-0054 (formula preservation FODS) targets this implementation
- Priority: HIGHEST (confirmed both by human review and R50 AI analysis)

---

## Limitations

- finish_reason was `length` — response was truncated at max_tokens=400
- Full technical detail on namespace handling was cut off
- Next step: expand max_tokens and request complete implementation spec in dedicated AI call

---

## Conclusion

AI confirmed the 3-part approach (schema + parser + writer) is the correct minimal path. This aligns with the R50 AI analysis that formula preservation is the highest-priority gap for data integrity (formulas affect correctness of computed data).

`LIVE_AI_CALL_R51: PASS`
