# GAP-FORENSIC-013b: spec_qname ClassVar Backfill — Remaining 18 Formats

## Taskcard Status Summary

| TC-ID | Status |
|---|---|
| TC-GF013B-001 | CLOSED |
| TC-GF013B-002 | CLOSED |
| TC-GF013B-003 | CLOSED |
| TC-GF013B-004 | CLOSED |
| TC-GF013B-006 | CLOSED |
| TC-GF013B-007 | CLOSED |
| TC-GF013B-008 | CLOSED |
| TC-GF013B-005 | CLOSED |
| TC-GF013B-COMMIT-001 | CLOSED |

**Execution evidence (2026-07-16):**

- **TC-GF013B-001** (ndjson): 6 files (5 planned + `ndjson_codec.py`, discovered mid-execution — see Change Log). Restored-and-reapplied to isolate from unrelated FACT→SAL drift. 2218 passed, 5 pre-existing unrelated failures (dirty test files expecting the other session's in-progress rename, confirmed via git-HEAD comparison).
- **TC-GF013B-002** (batch A: dif, fodg, fodp, pgm, ppm): 21 files (19 planned + pgm_parser.py/ppm_parser.py). Restored-and-reapplied (21/21 files had unrelated drift). 6501 passed, 11 pre-existing unrelated failures (same pattern, confirmed).
- **TC-GF013B-003** (batch B: odt, pbm, qoi, sylk): 26 files (24 planned + pbm_parser.py/qoi_parser.py). Restored-and-reapplied (25/26 flagged, all confirmed genuine). odt/pbm/qoi: 7 pre-existing unrelated failures. sylk: 21 failures, root-caused to two distinct pre-existing unrelated causes — FACT→SAL metadata drift (dirty test files) AND unrelated WIP changes to `sylk_writer.py`/`sylk_value_analytics.py` (never touched by this plan) that break a value-type roundtrip; confirmed via direct trace (`write_sylk` imported from the dirty `sylk_writer.py`) since neither file was touched by this plan.
- **TC-GF013B-004** (batch C: ods, xcf): 15 files as planned. xcf_parser.py/image_document.py confirmed class-level only (not module-level) per the plan's own note. Restored-and-reapplied (15/15). 4439 passed, 15 pre-existing unrelated failures (same pattern).
- **TC-GF013B-006** (batch D: ipynb, nrrd, safetensors): 14 files as planned. No pre-existing drift found. 700 passed, 0 failures.
- **TC-GF013B-007** (batch E: xliff, ubl): 14 files as planned. No pre-existing drift found. 405 passed, 0 failures.
- **TC-GF013B-008** (batch F: mtlx): 12 files as planned. No pre-existing drift found. 266 passed, 0 failures.
- **TC-GF013B-005** (cross-format verification): Whole-tree AST scan across all 18 formats confirmed 0/103 bare declarations AND 0 typed-but-not-ClassVar declarations remain. Full 18-format regression run twice due to a large number of other concurrently active agent sessions in this repo (confirmed via the coordination hook) altering unrelated files between runs: first run 48 failed/19440 passed, second run (minutes later) 15 failed/19473 passed — the failure count itself fluctuated while this plan's own diff stayed static, which is independent confirmation that all remaining failures are externally caused, not caused by this plan's changes. Final state: 15 failures, all in sylk (root-caused above), 0 failures anywhere else.
- **TC-GF013B-COMMIT-001**: Built a 109-file intended list (108 source/tool files + this plan file), staged via `git add --pathspec-from-file`, verified staged-set == intended-set exactly (109/109, 0 discrepancy) before committing. Committed as `320033d39821490fefab115d609da82b6972d7fc`. Post-commit: 0/109 intended files remain dirty.

## Context

GAP-FORENSIC-013 (spec_qname ClassVar backfill for abw, csv, fods, fodt, gnumeric, toml, tsv, zst) was executed and TERMINAL_CLOSED this session — commits `f81f1a8b`, `5fac6038`, `25238b3b`; all 6 taskcards CLOSED; `lifecycle_audit.py` returned `AUDIT_PASS`. Its own plan file now carries a `mutation_policy: "no further plan/hardening/execution writes"` marker, so this is a **successor plan**, not a reopening.

A comprehensive, definitive AST scan of all 26 real format directories under `src/python/` (run during this planning session, superseding an earlier, narrower, partially-incorrect draft of this same plan) found:

- **`ndjson`'s `models.py` was also fully bare** and was never in the original 8-format scope — it needs the same full treatment (models.py + Compat + spec).
- **17 other formats** already have `ClassVar` on their top-level `models.py`, but still have bare `spec_qname = "..."` on their `Compat/`/`spec/` **sub-element** classes: dif, fodg, fodp, ipynb, mtlx, nrrd, ods, odt, pbm, pgm, ppm, qoi, safetensors, sylk, ubl, xcf, xliff.

**Correction to an earlier draft of this plan:** An initial pass (based on a stale inference from GAP-FORENSIC-013's own research phase) incorrectly assumed 6 of these 17 formats (ipynb, mtlx, nrrd, safetensors, ubl, xliff) were "already fully covered" because a few of their files matched a `ClassVar` grep. Re-verification with the same live AST scan used for the other formats found this was wrong — all 6 have multiple spec-element classes per format (e.g. mtlx has 6: look, material, nodedef, nodegraph, propertyset, typedef) and only some were annotated. This correction is recorded here per this plan's own Anti-Overclaim Rules, and the scope below reflects the corrected, fully-verified count.

**Scale (verified, not inferred):** 18 formats, 103 bare `spec_qname` declarations across 103 files (one class per spec/Compat file in this architecture, so declaration count and file count coincide here).

**Reused from GAP-FORENSIC-013 (do not rebuild):** `tools/backfill/classvar_annotation_backfill.py` already handles all 3 import-mutation categories and 7 attribute types needed here — it is format-agnostic and was validated idempotent against the DIF top-level pattern. No new transformation logic is required, only new `--format` invocations.

**Migration note (per CLAUDE.md Step 0):** On approval, migrate this plan to `plans/.claude/gap-forensic-013b-classvar-compat-spec-backfill.md` (a **new** filename — do NOT write into the closed `plans/.claude/gap-forensic-013-spec-qname-classvar-snappy-waffle.md`), then run `write_plan_lock.py --plan-path plans/.claude/gap-forensic-013b-classvar-compat-spec-backfill.md`.

---

## Plan File Hardening Change Log

- 2026-07-15 (draft 1): Initial plan covering 12 formats (63 declarations), based on GAP-FORENSIC-013's own documented Exclusions list plus a live AST scan for those 12.
- 2026-07-15 (draft 2, approved): Ran a comprehensive scan across **all 26** real format directories (not just the 12 already flagged) before finalizing. Found the draft-1 scope had incorrectly excluded 6 formats (ipynb, mtlx, nrrd, safetensors, ubl, xliff — 40 more declarations, 40 more files) based on a stale, unverified inference. Corrected scope: 18 formats, 103 declarations, 103 files.
- 2026-07-15 (execution correction, mid TC-GF013B-001): The original AST scan classified any `AnnAssign` on `spec_qname` as "already correct," without checking whether the annotation was actually `ClassVar[...]` vs a bare type like `str`. A dry-run of `classvar_annotation_backfill.py --format ndjson` surfaced `ndjson/ndjson_codec.py` — a `@dataclass`-decorated class where `spec_qname: str = "..."` is a genuine per-instance dataclass field (not a shared class attribute at all — a functional bug, not just a missing annotation). A corrected whole-tree scan distinguishing `BARE` / `TYPED_NOT_CLASSVAR` / `PROPER_CLASSVAR` found 4 more instances of this same pattern: `pbm/pbm_parser.py`, `pgm/pgm_parser.py`, `ppm/ppm_parser.py`, `qoi/qoi_parser.py`. The original 103-bare count is unchanged and confirmed accurate (this is an additive, distinct finding, not a correction to the 103 count). These 5 files are added to the Allowed Paths of their respective taskcards (TC-GF013B-001 for ndjson_codec.py; TC-GF013B-002 for pgm_parser.py/ppm_parser.py; TC-GF013B-003 for pbm_parser.py/qoi_parser.py) rather than triggering a new planning cycle, since the existing tool already detects and correctly fixes this case (confirmed via the ndjson dry-run) and all 5 files fall within formats already in scope. None of the 8 GAP-FORENSIC-013 formats exhibit this pattern (confirmed clean).

## Audit Findings Incorporated

| Finding | Source | Disposition |
|---|---|---|
| ndjson/models.py bare, omitted from original 8-format scope | Live AST scan, this session | `new_plan_item_required` — TC-GF013B-001 |
| 11 formats' Compat/spec sub-element classes bare (58 declarations) | Live AST scan, this session; originally flagged in GAP-FORENSIC-013 Exclusions | `new_plan_item_required` — TC-GF013B-002/003/004 |
| 6 more formats (ipynb, mtlx, nrrd, safetensors, ubl, xliff) incorrectly assumed complete; actually 40 bare declarations | Live AST scan, this session, correcting this plan's own draft 1 | `new_plan_item_required` — TC-GF013B-006/007/008 |
| GAP-FORENSIC-013's own L1-002/L2-001 (uncommitted work + unrelated-file commit-scoping risk) | GAP-FORENSIC-013 stage1-issue-model.json | `governance_change_required` — folded into this plan's Gate Contract and Repair Loop from the start, not left as an end-of-plan surprise |
| V51 validator tolerates bare + ClassVar equally | GAP-FORENSIC-013 L3-001 | `rejected_with_reason` — carried forward unchanged, still out of scope |
| 3 pre-existing fods/zst test failures (FACT citation gaps) | GAP-FORENSIC-013 L2-002 | `rejected_with_reason` — unrelated, owned by another session, unaffected by this plan's target formats |

## Resolved / Preserved Work

- `tools/backfill/classvar_annotation_backfill.py` — built and validated in GAP-FORENSIC-013, reused as-is.
- The format-by-format, smallest-first execution pattern with restore-and-reapply isolation (for pre-existing unrelated uncommitted drift) — proven effective, reused.
- The file-list-precise commit discipline (`git add --pathspec-from-file`, staged-set-vs-intended-set cross-reference) — proven necessary in GAP-FORENSIC-013's own closure; built into this plan's taskcards from taskcard 1, not bolted on at the end.

## Unresolved Work Register

| Item | Status | Owner |
|---|---|---|
| ndjson full ClassVar backfill | not_attempted | this plan, TC-GF013B-001 |
| 11-format Compat/spec ClassVar backfill (dif, fodg, fodp, ods, odt, pbm, pgm, ppm, qoi, sylk, xcf) | not_attempted | this plan, TC-GF013B-002/003/004 |
| 6-format Compat/spec ClassVar backfill (ipynb, mtlx, nrrd, safetensors, ubl, xliff) | not_attempted | this plan, TC-GF013B-006/007/008 |
| V51 validator annotation-style enforcement | not_attempted, deliberately out of scope | future governance sprint |
| 3 pre-existing fods/zst FACT-citation test failures | not_attempted, deliberately out of scope | unrelated session that performed the FACT→SAL rename |

---

## Taskcard Register

Shared pattern for all TC-GF013B-00N implementation taskcards (stated once, applies to all):
- **Required work:** Run `python tools/backfill/classvar_annotation_backfill.py --format {fmt}` for each format in the batch; if pre-existing unrelated uncommitted drift is discovered mid-run in a target file, restore that file to its committed HEAD state and reapply the backfill in isolation (do not carry forward unrelated changes).
- **Required verification:** `.venv/Scripts/pytest tests/python/{fmt}/ -x -q` for every format in the batch; AST scan confirming 0 bare class-level `spec_qname` remain in the batch's formats.
- **Required evidence:** pytest pass counts per format; AST scan output; `git diff` hunk-level review confirming ClassVar-only changes (no value drift) — reuse the verification script pattern from GAP-FORENSIC-013's own audit.
- **Stop conditions:** If any format's test suite shows a new failure not attributable to a pre-existing, HEAD-confirmed unrelated cause, stop and root-cause before continuing to the next format in the batch.
- **Forbidden actions:** No `git add -A` or directory-wildcard staging at any point (see TC-GF013B-COMMIT-001). No edits to module-level `spec_qname` (analytics/parser-level bare module attributes are out of scope — same exclusion as GAP-FORENSIC-013).

### TC-GF013B-001 — ndjson full backfill
- **Title:** Add ClassVar annotations to ndjson (models.py + Compat + spec) — the omitted 9th format
- **Source audit finding:** Live AST scan, this session (models.py:23 confirmed bare)
- **Why it matters:** ndjson has the exact same defect class as the original 8 formats, just missed from the original gap report.
- **Current status:** not_attempted
- **Priority:** HIGH (identical defect class to already-fixed formats; correctness/consistency gap)
- **Lane owner:** product-source-task
- **Acceptance criteria:** 0/5 bare `spec_qname` assignments remain in ndjson; full ndjson test suite passes.
- **Allowed paths:** `src/python/ndjson/models.py`, `src/python/ndjson/Compat/ndjson_field.py`, `src/python/ndjson/Compat/ndjson_record.py`, `src/python/ndjson/spec/record/field.py`, `src/python/ndjson/spec/record/record.py`, `src/python/ndjson/ndjson_codec.py` (added mid-execution — dataclass field `spec_qname: str` missing `ClassVar[]`, see Change Log)
- **Dependencies:** none
- **Closeout rules:** Mark CLOSED only after both the AST scan and the ndjson pytest suite pass.

### TC-GF013B-002 — Batch A: dif, fodg, fodp, pgm, ppm (19 files)
- **Title:** Compat/spec ClassVar backfill, batch A
- **Current status:** not_attempted
- **Priority:** MEDIUM
- **Lane owner:** product-source-task
- **Acceptance criteria:** 0 bare `spec_qname` remain in dif, fodg, fodp, pgm, ppm; all 5 formats' test suites pass.
- **Allowed paths:** `src/python/dif/Compat/{dif_datum,dif_header,dif_vector}.py`; `src/python/fodg/{Compat/fodg_document,Compat/fodg_page,spec/draw/page,spec/office/document}.py`; `src/python/fodp/{Compat/fodp_document,Compat/fodp_page,spec/draw/page,spec/office/document}.py`; `src/python/pgm/{Compat/pgm_graymap,Compat/pgm_header,spec/graymap/graymap,spec/graymap/header,pgm_parser}.py`; `src/python/ppm/{Compat/ppm_header,Compat/ppm_pixmap,spec/pixmap/header,spec/pixmap/pixmap,ppm_parser}.py` (pgm_parser.py/ppm_parser.py added mid-execution, see Change Log)
- **Dependencies:** none
- **Closeout rules:** Mark CLOSED only after AST scan + all 5 format test suites pass.

### TC-GF013B-003 — Batch B: odt, pbm, qoi, sylk (24 files)
- **Title:** Compat/spec ClassVar backfill, batch B
- **Current status:** not_attempted
- **Priority:** MEDIUM
- **Lane owner:** product-source-task
- **Acceptance criteria:** 0 bare `spec_qname` remain in odt, pbm, qoi, sylk; all 4 formats' test suites pass.
- **Allowed paths:** `src/python/odt/{Compat/odt_document,Compat/odt_heading,Compat/odt_paragraph,spec/office/document,spec/text/heading,spec/text/paragraph}.py`; `src/python/pbm/{Compat/pbm_bitmap,Compat/pbm_header,Compat/pbm_raster,spec/bitmap/bitmap,spec/bitmap/header,spec/bitmap/raster,pbm_parser}.py`; `src/python/qoi/{Compat/qoi_chunk,Compat/qoi_end_marker,Compat/qoi_header,spec/chunk/chunk,spec/chunk/end_marker,spec/chunk/header,qoi_parser}.py`; `src/python/sylk/{Compat/sylk_cell,Compat/sylk_header,Compat/sylk_row,spec/row/cell,spec/row/header,spec/row/row}.py` (pbm_parser.py/qoi_parser.py added mid-execution, see Change Log)
- **Dependencies:** none
- **Closeout rules:** Mark CLOSED only after AST scan + all 4 format test suites pass.

### TC-GF013B-004 — Batch C: ods, xcf (15 files)
- **Title:** Compat/spec ClassVar backfill, batch C (includes non-Compat/spec parser-level files for xcf)
- **Why it matters:** xcf additionally has 2 bare declarations outside the Compat/spec layer (`xcf/image_document.py`, `xcf/xcf_parser.py`) — verify these are genuine class-level declarations (not module-level, which would be out of scope) before transforming.
- **Current status:** not_attempted
- **Priority:** MEDIUM
- **Lane owner:** product-source-task
- **Acceptance criteria:** 0 bare `spec_qname` remain in ods, xcf; both formats' test suites pass.
- **Allowed paths:** `src/python/ods/{Compat/ods_cell,Compat/ods_document,Compat/ods_sheet,spec/office/document,spec/table/table,spec/table/table_cell,spec/table/table_row}.py`; `src/python/xcf/{Compat/xcf_channel,Compat/xcf_header,Compat/xcf_layer,image_document,spec/layer/channel,spec/layer/header,spec/layer/layer,xcf_parser}.py`
- **Dependencies:** none
- **Closeout rules:** Mark CLOSED only after AST scan + both format test suites pass.

### TC-GF013B-006 — Batch D: ipynb, nrrd, safetensors (14 files)
- **Title:** Compat/spec ClassVar backfill, batch D
- **Source audit finding:** Live AST scan, this session — corrects an earlier, incorrect "already complete" assumption for these formats (see Plan File Hardening Change Log)
- **Current status:** not_attempted
- **Priority:** MEDIUM
- **Lane owner:** product-source-task
- **Acceptance criteria:** 0 bare `spec_qname` remain in ipynb, nrrd, safetensors; all 3 formats' test suites pass.
- **Allowed paths:** `src/python/ipynb/{Compat/ipynb_cell,Compat/ipynb_notebook,Compat/ipynb_output,spec/notebook/cell,spec/notebook/notebook,spec/notebook/output}.py`; `src/python/nrrd/{Compat/nrrd_data,Compat/nrrd_header,spec/header/data,spec/header/header}.py`; `src/python/safetensors/{Compat/safetensors_header,Compat/safetensors_tensor,spec/header/header,spec/header/tensor}.py`
- **Dependencies:** none
- **Closeout rules:** Mark CLOSED only after AST scan + all 3 format test suites pass.

### TC-GF013B-007 — Batch E: xliff, ubl (14 files)
- **Title:** Compat/spec ClassVar backfill, batch E
- **Source audit finding:** Live AST scan, this session — same correction as TC-GF013B-006
- **Current status:** not_attempted
- **Priority:** MEDIUM
- **Lane owner:** product-source-task
- **Acceptance criteria:** 0 bare `spec_qname` remain in xliff, ubl; both formats' test suites pass.
- **Allowed paths:** `src/python/xliff/{Compat/xliff_file,Compat/xliff_segment,Compat/xliff_unit,spec/file/file,spec/file/segment,spec/file/unit}.py`; `src/python/ubl/{Compat/ubl_credit_note,Compat/ubl_invoice,Compat/ubl_line_item,Compat/ubl_order,spec/document/credit_note,spec/document/invoice,spec/document/line_item,spec/document/order}.py`
- **Dependencies:** none
- **Closeout rules:** Mark CLOSED only after AST scan + both format test suites pass.

### TC-GF013B-008 — Batch F: mtlx (12 files)
- **Title:** Compat/spec ClassVar backfill, mtlx (dedicated — largest single-format gap)
- **Source audit finding:** Live AST scan, this session — same correction as TC-GF013B-006; mtlx alone has 6 distinct spec-element classes (look, material, nodedef, nodegraph, propertyset, typedef), only 1 of which had ClassVar
- **Current status:** not_attempted
- **Priority:** MEDIUM
- **Lane owner:** product-source-task
- **Acceptance criteria:** 0/12 bare `spec_qname` remain in mtlx; mtlx test suite passes.
- **Allowed paths:** `src/python/mtlx/Compat/{mtlx_look,mtlx_material,mtlx_nodedef,mtlx_nodegraph,mtlx_propertyset,mtlx_typedef}.py`; `src/python/mtlx/spec/element/{look,material,nodedef,nodegraph,propertyset,typedef}.py`
- **Dependencies:** none
- **Closeout rules:** Mark CLOSED only after AST scan + mtlx test suite passes.

### TC-GF013B-005 — Cross-format verification
- **Title:** Full 18-format AST scan and regression re-run
- **Why it matters:** Confirms no batch left residual bare assignments and no cross-batch regression, across the FULL corrected scope (not just the original 12).
- **Current status:** not_attempted
- **Priority:** HIGH (gate before commit)
- **Lane owner:** product-source-task
- **Required verification:** AST scan across all 18 formats (0 bare remaining) — must scan the same way this plan's own scope was verified (whole-`src/python/`-tree AST walk, not a pre-assumed subset); full pytest run across all 18 formats' test directories.
- **Acceptance criteria:** 0/103 bare declarations remain across all 18 formats; 0 new test failures relative to each format's pre-existing baseline.
- **Dependencies:** TC-GF013B-001, TC-GF013B-002, TC-GF013B-003, TC-GF013B-004, TC-GF013B-006, TC-GF013B-007, TC-GF013B-008
- **Closeout rules:** Mark CLOSED only after a clean full-suite run across all 18 formats.

### TC-GF013B-COMMIT-001 — File-list-precise scoped commit
- **Title:** Commit this plan's work with file-list-precise staging
- **Source audit finding:** GAP-FORENSIC-013 L1-002/L2-001 (lesson carried forward — see Audit Findings Incorporated)
- **Why it matters:** GAP-FORENSIC-013 itself proved the working tree routinely carries unrelated pre-existing uncommitted files in the same package directories; this taskcard exists from the start this time instead of being discovered post-hoc.
- **Current status:** not_attempted
- **Priority:** HIGH (gate — nothing is "done" until committed, per GAP-FORENSIC-013's own closure lesson)
- **Lane owner:** SCM Agent
- **Required implementation:** Before staging, run `git diff --name-only` scoped to each of the 18 target format directories and cross-reference against the intended 103-file list (+ any test/tool/plan files touched) — stage via `git add --pathspec-from-file` with an explicit file list, never a directory or wildcard add.
- **Required verification:** Post-commit `git status --short` shows none of the intended files as modified/untracked; staged-set-vs-intended-set automated comparison shows exact match (0 discrepancy) before committing, mirroring the check used in GAP-FORENSIC-013's own TC-GF013-COMMIT-001.
- **Required evidence:** Commit hash(es), `git show --stat` output.
- **Acceptance criteria:** Commit exists with exactly the intended file list; no unrelated pre-existing dirty file swept in.
- **Dependencies:** TC-GF013B-005
- **Closeout rules:** Mark CLOSED only after commit hash is recorded and post-commit verification passes.

---

## Lane Ownership

| Lane | Owner role | Taskcards |
|---|---|---|
| implementation | product-source-task | TC-GF013B-001, -002, -003, -004, -005, -006, -007, -008 |
| closure | SCM Agent | TC-GF013B-COMMIT-001 |

## Gate Contract

- No taskcard may be marked CLOSED without its stated required verification actually having been run and its output captured as evidence (not asserted from memory).
- TC-GF013B-005 (cross-format verification) is a hard gate before TC-GF013B-COMMIT-001 — no partial commits mid-batch.
- TC-GF013B-COMMIT-001 is a hard gate before this plan may be marked TERMINAL_CLOSED.
- **Scope-completeness gate (new, added after this plan's own draft-1 undercount):** before TC-GF013B-005 is marked CLOSED, the AST scan MUST run over the whole `src/python/` tree (all real format directories, excluding `.egg-info`/`build`/`__pycache__`), not a pre-assumed subset — this is exactly the check that would have caught the draft-1 error immediately instead of requiring a second pass.

## Evidence Contract

- Every taskcard's evidence must include: (a) the AST scan command and its numeric output, (b) the pytest command and its pass/fail/skip counts, (c) for the commit taskcard, the commit hash and `git show --stat` output.
- Evidence lives in `.supervisor/state/convergence-loop-GAP-FORENSIC-013B/` once this plan is migrated in-repo and executed (gitignored, local-only, matching the convention used for GAP-FORENSIC-013's own convergence loop).

## Verification Matrix

| Taskcard | Command | Pass criterion |
|---|---|---|
| TC-GF013B-001 | `.venv/Scripts/pytest tests/python/ndjson/ -x -q` | 0 failures |
| TC-GF013B-002 | `.venv/Scripts/pytest tests/python/{dif,fodg,fodp,pgm,ppm}/ -x -q` | 0 failures |
| TC-GF013B-003 | `.venv/Scripts/pytest tests/python/{odt,pbm,qoi,sylk}/ -x -q` | 0 failures |
| TC-GF013B-004 | `.venv/Scripts/pytest tests/python/{ods,xcf}/ -x -q` | 0 failures |
| TC-GF013B-006 | `.venv/Scripts/pytest tests/python/{ipynb,nrrd,safetensors}/ -x -q` | 0 failures |
| TC-GF013B-007 | `.venv/Scripts/pytest tests/python/{xliff,ubl}/ -x -q` | 0 failures |
| TC-GF013B-008 | `.venv/Scripts/pytest tests/python/mtlx/ -x -q` | 0 failures |
| TC-GF013B-005 | Whole-tree AST scan + full 18-format pytest run | 0/103 bare remain; 0 new failures |
| TC-GF013B-COMMIT-001 | `git status --short` + staged-vs-intended cross-reference | exact match, 0 discrepancy |

## Repair Loop

If any batch taskcard's test suite fails on a genuinely new (not pre-existing) failure: stop, root-cause via `git diff` on the specific file, determine whether the backfill script mis-transformed a companion attribute (e.g. an already-typed `facade_names: list` field — a known pattern from GAP-FORENSIC-013's own verification work, correctly handled by the actual transformation script, but worth re-checking if a NEW anomaly appears), fix the script if it is a script defect, reapply, and rerun verification before proceeding to the next batch.

## Anti-Overclaim Rules

- Do not mark any taskcard `completed_verified` without captured command output, not a memory-based assertion.
- Do not treat "the script ran" as proof; the AST scan and pytest run are the proof.
- Do not stage by directory or wildcard for TC-GF013B-COMMIT-001.
- **Do not assume a format is "already complete" from a partial grep match** — this plan's own draft 1 made exactly this mistake for 6 formats (40 declarations) and was only caught by re-verifying with a whole-tree AST scan before finalizing. Any future claim that a format needs no further work must be backed by a full AST scan of that format's directory, not a sampled grep.

## Closeout Criteria

- All 9 taskcards CLOSED with captured evidence.
- 0/103 bare `spec_qname` declarations remain across the 18 formats (AST-verified, whole-tree scan).
- Full regression suite for all 18 formats green (pre-existing unrelated failures, if any are discovered, must be independently confirmed via git-HEAD comparison before exclusion — same discipline as GAP-FORENSIC-013).
- Work committed with file-list-precise staging; commit hash recorded.
- Plan migrated to `plans/.claude/gap-forensic-013b-classvar-compat-spec-backfill.md`, locked, and terminally closed via `write_plan_lock.py --terminal` (add `--audit-gate` once the plan carries a real `## Taskcard Status Summary` table post-migration, matching GAP-FORENSIC-013's own closure pattern).

## Remaining True Blockers

None within this plan's scope. Two items are explicitly out of scope and not blockers for this plan's closure:
- V51 governance validator still tolerates bare and ClassVar-annotated `spec_qname` equally (a deliberate exclusion carried forward from GAP-FORENSIC-013).
- 3 pre-existing fods/zst test failures from an unrelated session's FACT→SAL rename remain open, owned by that other session — fods and zst are not in this plan's 18-format scope regardless.


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-16T12:42:50.036085+00:00"
  locked_by: "2df87f0641b8"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
