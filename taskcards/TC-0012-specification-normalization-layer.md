# TC-0012 — Specification Normalization Layer

**Taskcard ID:** TC-0012
**Phase:** 2+ (Foundation Layer — supports all phases)
**Gate:** Supports Gates 3–8 (required before Gate 4)
**Status:** completed (2026-06-18 — all Phase 1/2 artifacts verified; master-plan.md updated)
**Created:** 2026-05-05 (run024)
**Last updated:** 2026-05-05 (run025)
**Created by:** claude-sonnet-4-6 (run024)

---

## Artifact Front Matter

```yaml
artifact_id: TC-0012-specification-normalization-layer
artifact_type: taskcard
path: taskcards/TC-0012-specification-normalization-layer.md
format_id: null
product_family: null
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-05"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Specification Normalization Layer taskcard. Created run024. Policy and tools created run024. Full pdfminer.six extraction completed run025: text.txt (2.2 MB), pages.jsonl (782 pages), citations.yaml (194 section refs, 35 external refs). G-NORM-001 resolved. parser-requirements.yaml pending (Gate 4 prerequisite)."
```

---

## Purpose

Define, implement, and validate the Specification Normalization Layer: the tooling and policy for converting immutable cached specification PDFs into local-only machine-readable derived artifacts for use in Gate 3–8 work.

The normalization layer sits between the specification cache layer (TC-0007) and the evidence pack layer (acquisition-packs/). It is a local-only working layer — its artifacts are never committed.

---

## Background

The FODS/ODF 1.3 Part 3 PDF (24.27 MB) was acquired in run021 and verified in run022. The spec cache layer (TC-0007) stores the immutable source. However, agents cannot efficiently work with a raw 24 MB PDF for structured reasoning, parser requirement extraction, or oracle comparison.

The normalization layer adds a derived working material layer:

```
.local/spec-cache/fods/1.3/
├── OpenDocument-v1.3-os-part3-schema.pdf  ← immutable source (TC-0007)
├── spec-index.yaml                         ← provenance metadata (TC-0007)
└── normalized/                             ← derived materials (TC-0012)
    ├── source-manifest.yaml
    ├── text.txt                            (requires pdfminer.six)
    ├── pages.jsonl                         (requires pdfminer.six)
    ├── sections.jsonl                      (future)
    ├── page-map.yaml                       (future)
    ├── citations.yaml                      (build_citation_map.py)
    ├── parser-requirements.yaml           (manual or future tool — Gate 4 required)
    ├── verified-facts.yaml                 (manual — Gate 5 useful)
    └── extraction-report.md
```

---

## Scope

1. **Policy document** (`docs/python-foss/specification-normalization.md`) — 15-section governing policy.
2. **Tool: `normalize_pdf.py`** — PDF → text.txt + pages.jsonl extraction with hash verification; graceful fallback to metadata-only if no extraction library installed.
3. **Tool: `build_citation_map.py`** — citations.yaml from pages.jsonl or text.txt (section refs + external refs).
4. **Tool: `validate_normalized_spec.py`** — validates normalized directory for gate readiness, checks source hash currency.
5. **Governance integration** — AGENTS.md Section W, GOVERNANCE.md Section 16, gates.md Gate 3/4 normalization notes, specification-cache.md Normalization Layer section.
6. **Local normalization run** — dry-run or full extraction on `.local/spec-cache/fods/1.3/` to produce at minimum `source-manifest.yaml` and `extraction-report.md`.

---

## Acceptance Criteria

- [x] `docs/python-foss/specification-normalization.md` exists with full 15-section policy
- [x] `tools/spec-normalize/_readme.md` exists with tool orientation
- [x] `tools/spec-normalize/normalize_pdf.py` exists — graceful fallback to metadata-only
- [x] `tools/spec-normalize/build_citation_map.py` exists
- [x] `tools/spec-normalize/validate_normalized_spec.py` exists
- [x] AGENTS.md Section W exists with 10 normalization rules
- [x] GOVERNANCE.md Section 16 exists with 6 normalization governance rules
- [x] `docs/gates.md` Gate 3 and Gate 4 updated with normalization dependencies
- [x] `docs/python-foss/specification-cache.md` references normalization layer
- [x] Local normalization run completed on `.local/spec-cache/fods/1.3/` — full extraction with pdfminer.six (run025)
- [x] `source-manifest.yaml` present under `.local/spec-cache/fods/1.3/normalized/` showing SHA-256 MATCH
- [x] `extraction-report.md` present in normalized directory
- [x] `master-plan.md` updated with TC-0012 record (Section 25, 2026-06-18)

---

## Implementation Record

### Phase 1 (run024): Policy and tooling

| Item | Status | Notes |
|---|---|---|
| `docs/python-foss/specification-normalization.md` | DONE | 15 sections, created run024 |
| `tools/spec-normalize/_readme.md` | DONE | Created run024 |
| `tools/spec-normalize/normalize_pdf.py` | DONE | Full skeleton with graceful fallback |
| `tools/spec-normalize/build_citation_map.py` | DONE | Section + external ref extraction |
| `tools/spec-normalize/validate_normalized_spec.py` | DONE | Gate readiness validation |
| AGENTS.md Section W | DONE | 10 rules |
| GOVERNANCE.md Section 16 | DONE | 6 rules |
| gates.md updates | DONE | Gate 3 and Gate 4 normalization notes |
| specification-cache.md updates | DONE | Normalization Layer section added |
| Local normalization dry-run | PENDING | Requires run024 completion |

### Phase 2 (run025): Full extraction

| Item | Status | Notes |
|---|---|---|
| Install pdfminer.six | DONE | `pip install --user pdfminer.six` (run025); version 20260107 |
| Run full normalize_pdf.py on FODS spec | DONE | run025; text.txt 2,160,370 chars; pages.jsonl 782 pages |
| Verify text.txt and pages.jsonl | DONE | run025; output quality confirmed; G-NORM-001 resolved |
| Run build_citation_map.py | DONE | run025; 194 section refs; 35 external refs; citations.yaml + citation-report.md |
| Run validate_normalized_spec.py | DONE | run025; 7 PASS, 1 WARN (parser-requirements.yaml), 0 FAIL, 3 SKIP |
| Add requirements.txt | DONE | run025; tools/spec-normalize/requirements.txt created |
| Manual `parser-requirements.yaml` draft | PENDING | Gate 4 prerequisite — deferred to Gate 4 execution |
| Manual `verified-facts.yaml` starter | PENDING | Gate 5 useful — deferred |

---

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| TC-0007 (Spec Cache) | COMPLETED | FODS spec cached run021 |
| pdfminer.six | INSTALLED | version 20260107, installed run025 |
| Gate 2 PASSED | DONE | Babar Raza, 2026-05-05 |

---

## Gaps

| Gap ID | Description | Severity | Blocking |
|---|---|---|---|
| G-NORM-001 | PDF extraction library unavailable until pdfminer.six installed | ~~Medium~~ **RESOLVED run025** | Resolved — pdfminer.six 20260107 installed; full extraction succeeded |

---

## Notes

- The normalization layer is local-only. Its artifacts are never committed to git.
- The cached spec SHA-256 (`sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066`) must match before normalization proceeds.
- This taskcard covers the infrastructure layer. Format-specific extraction quality review is out of scope and should be tracked via a separate gate-3/gate-4 taskcard.
- `parser-requirements.yaml` is the Gate 4 hard dependency. It may be produced manually (agent reading cached spec) rather than automatically. TC-0012 does not require the automated tool to produce it — only that it exists in normalized/ before Gate 4 begins (or a waiver is logged).

---

## Related Files

- `docs/python-foss/specification-normalization.md`
- `docs/python-foss/specification-cache.md`
- `tools/spec-normalize/` (normalize_pdf.py, build_citation_map.py, validate_normalized_spec.py, _readme.md)
- `AGENTS.md` Section W
- `GOVERNANCE.md` Section 16
- `docs/gates.md` Gates 3 and 4
- `taskcards/TC-0007-specification-cache.md`
- `taskcards/TC-0010-fods-gate3-sample-corpus-planning.md`
