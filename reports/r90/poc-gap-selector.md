---
visibility: generated
generated_by: codex
---

# R90 POC Gap Selector

Implemented by `tools/supervisor/select_poc_gaps.py`.

The selector reads `product-capability-matrix/poc-targets.yaml` and writes:

- `.local/supervisor/selected-product-gaps.json`
- `reports/supervisor/product-gap-selection.md`

Ranking rules:

1. Product capabilities that close POC behavior gaps rank above external approval blockers.
2. Missing writers and dogfood exports receive the highest POC-impact scores.
3. Repeatable work is annotated `GOVERNED_SKILL_REQUIRED`.
4. Uncovered work is annotated `GOVERNED_HANDOFF_REQUIRED`.
5. Human approvals remain visible as `EXTERNAL_GATE_ESCALATION`; they are never autonomous lanes.

The generated JSON is the machine-readable supervisor input. The generated Markdown report is the
operator-facing projection of the same ordered list.
