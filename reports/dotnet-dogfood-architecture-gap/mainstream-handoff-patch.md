# Mainstream Handoff Patch — TASK-009..012 Architecture Block

**Sprint:** FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
**Lane:** G — Prompt and Handoff Guardrails
**Date:** 2026-06-05

---

## Before / After Text for TASK-009..012

### TASK-009 — BEFORE

```
- [pending] TASK-009: Product deepening: commercial-net-fods-dogfood-status-fods-to-csv-dotnet — dogfood_status.fods_to_csv_dotnet
```

### TASK-009 — AFTER

```
- [architecture_blocked] TASK-009: [ARCHITECTURE_BLOCKED — DO NOT INVOKE /add-dogfood-export]
  Gap: commercial-net-fods-dogfood-status-fods-to-csv-dotnet
  Root cause: No Format Factory target writer library exists for .NET CSV (format-factory-csv-dotnet).
  Decision: ISSUE_001_ACCEPTED_AS_ARCHITECTURE_GAP_FOR_THIS_SPRINT
  Evidence: reports/dotnet-dogfood-architecture-gap/architecture-gap-decision-record.md
  Alternative work: See reports/dotnet-dogfood-architecture-gap/actionable-gap-replacement-candidates.json
  Candidate future sprint: CREATE-DOTNET-CSV-WRITER-001
```

---

### TASK-010 — BEFORE

```
- [pending] TASK-010: Product deepening: commercial-net-fods-dogfood-status-fods-to-html-dotnet — dogfood_status.fods_to_html_dotnet
```

### TASK-010 — AFTER

```
- [architecture_blocked] TASK-010: [ARCHITECTURE_BLOCKED — DO NOT INVOKE /add-dogfood-export]
  Gap: commercial-net-fods-dogfood-status-fods-to-html-dotnet
  Root cause: No Format Factory target writer library exists for .NET HTML (format-factory-html-dotnet).
  Note: This requires a SEPARATE format-factory-html .NET writer — NOT unblocked by the CSV writer.
  Decision: ISSUE_001_ACCEPTED_AS_ARCHITECTURE_GAP_FOR_THIS_SPRINT
  Evidence: reports/dotnet-dogfood-architecture-gap/architecture-gap-decision-record.md
  Alternative work: See reports/dotnet-dogfood-architecture-gap/actionable-gap-replacement-candidates.json
  Candidate future sprint: CREATE-DOTNET-HTML-WRITER-001
```

---

### TASK-011 — BEFORE

```
- [pending] TASK-011: Product deepening: commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet — dogfood_status.fodt_to_markdown_dotnet
```

### TASK-011 — AFTER

```
- [architecture_blocked] TASK-011: [ARCHITECTURE_BLOCKED — DO NOT INVOKE /add-dogfood-export]
  Gap: commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet
  Root cause: No Format Factory target writer library exists for .NET Markdown (format-factory-markdown-dotnet).
  Decision: ISSUE_001_ACCEPTED_AS_ARCHITECTURE_GAP_FOR_THIS_SPRINT
  Evidence: reports/dotnet-dogfood-architecture-gap/architecture-gap-decision-record.md
  Alternative work: See reports/dotnet-dogfood-architecture-gap/actionable-gap-replacement-candidates.json
  Candidate future sprint: CREATE-DOTNET-MARKDOWN-WRITER-001
```

---

### TASK-012 — BEFORE

```
- [pending] TASK-012: Product deepening: commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet — dogfood_status.fodt_to_txt_dotnet
```

### TASK-012 — AFTER

```
- [architecture_blocked] TASK-012: [ARCHITECTURE_BLOCKED — DO NOT INVOKE /add-dogfood-export]
  Gap: commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet
  Root cause: No Format Factory target writer library exists for .NET TXT (format-factory-txt-dotnet).
  Decision: ISSUE_001_ACCEPTED_AS_ARCHITECTURE_GAP_FOR_THIS_SPRINT
  Evidence: reports/dotnet-dogfood-architecture-gap/architecture-gap-decision-record.md
  Alternative work: See reports/dotnet-dogfood-architecture-gap/actionable-gap-replacement-candidates.json
  Candidate future sprint: CREATE-DOTNET-TXT-WRITER-001
```

---

## generate_next_worker_prompt.py Status: IMPLEMENTED

The file `tools/supervisor/generate_next_worker_prompt.py` was modified as follows:

### Change 1 — Added BLOCKED_ARCHITECTURE_GAPS frozenset (after TRAIN_LETTERS)

```python
BLOCKED_ARCHITECTURE_GAPS: frozenset = frozenset({
    "commercial-net-fods-dogfood-status-fods-to-csv-dotnet",
    "commercial-net-fods-dogfood-status-fods-to-html-dotnet",
    "commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet",
    "commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet",
})
```

### Change 2 — Added filter in G5 dogfood train synthesis

In `synthesize_trains()`, the `actionable_dogfood` list comprehension now excludes gaps whose `id` or `gap_id` field matches any entry in `BLOCKED_ARCHITECTURE_GAPS`:

```python
actionable_dogfood = [
    g for g in dogfood_gaps
    if g.get("suggested_sprint", "HOLD") != "HOLD"
    and g.get("current_status") != "IMPLEMENTED"
    and g.get("id", g.get("gap_id", "")) not in BLOCKED_ARCHITECTURE_GAPS
]
```

### py_compile result

```
COMPILE_OK
```

`.local/venv/Scripts/python -m py_compile tools/supervisor/generate_next_worker_prompt.py` exited 0.

---

## How Agents Reading next-sprint.md Will Now Behave Differently

Previously, TASK-009..012 appeared as `[pending]` items. An agent reading next-sprint.md would see these as actionable product-deepening tasks and might invoke `/add-dogfood-export` or attempt to implement the export path directly in `.NET`, leading to wasted effort or a fabricated export chain with no real FF writer library backing it.

After this patch:

1. Each task is explicitly tagged `[architecture_blocked]` — agents that check status tags before acting will skip these automatically.
2. The inline text `[ARCHITECTURE_BLOCKED — DO NOT INVOKE /add-dogfood-export]` is unambiguous: even agents that do not parse status tags will read the prohibition.
3. Each task names the root cause (missing writer library), the decision record for traceability, and a candidate future sprint ID — giving agents a clear reroute path rather than a dead end.
4. The `generate_next_worker_prompt.py` BLOCKED_ARCHITECTURE_GAPS filter ensures that if these gap IDs appear in a fixture file with a non-HOLD sprint suggestion, they will still be excluded from G5 dogfood train generation in future prompt regenerations.
