# FF-HEAL-QNAME Idempotent Healing Audit — Revised Plan (2026-06-26)

**Plan ID:** tidy-dreaming-lollipop
**Type:** Delta idempotent healing audit (run #6)
**Run ID:** `FF-HEAL-QNAME-20260626-{HHMMSS}` (generated at execution start)
**Output root:** `.local/evidences/FF-HEAL-QNAME-20260626-{HHMMSS}/`

---

## A. Current-State Reassessment

**HEAD (plan authored):** `24cc7fe0` (not `c6b24706` as planned — 3+ more commits since planning)
**HEAD (2026-07-01 hardening):** `b1d39abc` — 7+ additional commits since plan was written; see Section E for delta
**Session resume:** Generated 2026-06-25T17:41; last sprint `ff-gates-advancement-20260625`; 1,609 tests; 0 contradictions; AUTONOMOUS_CONTINUE: YES

**What changed since the original plan was written:**

| Changed Item | What Changed | Impact on Plan |
|---|---|---|
| Gap severity | ALL 1,246 gaps now have severity field (0 missing) | Plan Phase 7 is OBSOLETE |
| Architecture doc | Phase 4 addendum added 2026-06-24 | Plan Phase 12 is OBSOLETE |
| Gap count | 1,132 → 1,246 (+114 new gaps added) | All gap counts in plan are stale |
| Open gaps | 105 → 43 (62 gaps closed) | Traceability state improved |
| SAL-QName cross-ref | New report `reports/sal-qname-gap-20260626.json` generated | NEW finding not in plan |
| SAL traceability | Updated to `gap-sal-traceability-20260626.json`; 48.2% pct | Was 41.4% in plan |
| schemas/sal-facts/ | New `schemas/sal-facts/sal-facts-schema.json` created | New artifact not in plan |
| .NET deepening | S119, S120, S121 added 10 test files, +1,519 lines | .NET maturity improved |
| Supervisor tests | test_ai_non_authority.py, test_sal_path_resolution.py added | New SAL governance |
| TC-QNAME-AUTH-001 | ndjson:field has python_file set | Prior taskcard IMPLICITLY CLOSED |
| Capability compiler | capability_to_feature_compiler.py modified | Phase 2 state changed |

**Critical new discovery (not in any prior plan):**
SAL facts in `.local/spec-cache/sal-facts-latest.json` have **NO fact_id field**. The facts are keyed by `{qname, claim, section, description, authority, source}` — no stable ID. Yet the gap-ledger references IDs like `FACT-CSV-003`, `FACT-ABW-001`, and the qname registry uses `spec_fact_ref: FACT-NDJSON-001`. These are **invented IDs never assigned to actual SAL facts**. This is why 1,816 "dangling refs" exist — the ID scheme is fictional.

---

## B. Item-by-Item Status of the Previous Plan

| Phase | Status | Evidence | What Remains |
|---|---|---|---|
| **Phase 1: Run setup + preflight** | UNRESOLVED — no FF-HEAL-20260626 run created | No matching dir in .local/evidences/ | Create run dir, preflight docs |
| **Phase 2: Prior run review** | UNRESOLVED — delta since 20260623 not documented | 20260623 run is last; 3 days of new work | Delta review: 5 prior runs + new changes |
| **Phase 3: System chain audit** | PRIOR RUN COVERED (20260623 24/24); DELTA needed | 03-system-chain-audit.md in prior run | Delta only: SAL ID scheme gap, new artifacts |
| **Phase 4: QName audit** | TC-QNAME-AUTH-001 IMPLICITLY CLOSED; 33/79 SAL gaps | ndjson:field has python_file; sal-qname-gap-20260626.json | Verify xcf:layer; document 33-gap finding |
| **Phase 5: Source quality** | PRIOR RUN COVERED — no Python source changes since 20260623 | No Python src in recent git diff | Skip — unchanged |
| **Phase 6: SAL audit** | STALE — new facts, new schema, ID scheme root cause | sal-facts-schema.json new; SAL has no fact_id | Delta audit with root cause doc |
| **Phase 7: Gap severity repair** | OBSOLETE — already done | all 1,246 gaps have severity; distribution: CRITICAL 10, HIGH 1, MEDIUM 1036, LOW 36, INFO 163 | Nothing — skip entirely |
| **Phase 8: Skills audit** | PRIOR RUN COVERED; minor delta (ingest-spec-sal added) | ingest-spec-sal now in skills list | Note new skill only |
| **Phase 9: Supervisor/lanes** | PRIOR RUN COVERED; new tests noted | test_ai_non_authority.py, test_sal_path_resolution.py | Note new tests only |
| **Phase 10: Backfill + maturity** | NEEDS DELTA — 3 .NET sprints advanced maturity | S119-S121: 10 new .NET test files | Update .NET maturity for CSV, FODS, FODT, NDJSON, Netpbm, TSV, ZST |
| **Phase 11: Traceability + gap matrix + taskcards** | MAJOR DELTA — new findings | 1,816 dangling refs; SAL has no IDs; 43 open gaps | New taskcards for ID scheme gap |
| **Phase 12: Architecture doc** | OBSOLETE — done 2026-06-24 | Phase 4 addendum present in docs/code-quality/architecture.md | Nothing — skip entirely |
| **Phase 13: Parity matrix refresh** | STILL NEEDED — 22/24 formats have no spec_parity_status | parity-matrix.yaml: only fodt=VERIFIED, fods=PARTIAL | Execute refresh for all 24 formats |
| **Phase 14: Validation** | STILL NEEDED | 1,609 passing tests; new test files to verify | Run targeted subset |
| **Phase 15: Evidence bundle** | STILL NEEDED | No FF-HEAL-20260626 bundle exists | Create bundle |

---

## C. Remaining Problems

### C1. SAL Fact ID Scheme is Fictional (NEW — CRITICAL)
**Root cause:** SAL facts in `.local/spec-cache/sal-facts-latest.json` have no `fact_id` field. Facts are structured as `{qname, claim, section, description, authority, source}`. Yet the qname registry uses `spec_fact_ref: FACT-NDJSON-001` and the gap-ledger references `FACT-CSV-003`, `FACT-ABW-001`, etc. These IDs were invented manually and never assigned to actual SAL fact records.

**Impact:**
- 1,816 dangling refs in gap-ledger (gap → SAL traceability is fictitious for these)
- 33/79 qname registry entries don't resolve to actual SAL facts (via qname matching)
- `traceability_pct: 48.2%` is based on qname matching, not ID matching — the ID-based tracing is 0%
- No stable ID allows incremental SAL updates without breaking all references

**Required fix:** Add `fact_id` field to every SAL fact record (format: `SAL-{FORMAT}-{QNAME_LOCAL}-{NNN}`). This is machinery work.

### C2. 33 QName Registry Entries Missing SAL Resolution (NEW — HIGH)
**Root cause:** `reports/sal-qname-gap-20260626.json` shows 46/79 qname entries resolved (via qname matching), 33 missing. Affected formats likely include the non-ODF formats where SAL facts were written without matching the exact qname string.

**Impact:** 33 spec elements lack SAL fact backing. Any capability depending on these is unproven.

**Required fix:** For each of 33 gaps, either (a) add matching SAL fact or (b) update registry qname to match existing SAL fact.

### C3. Parity Matrix Stale (22/24 formats) (CARRIED FORWARD — MEDIUM)
**Root cause:** `registry/parity-matrix.yaml` was generated 2026-06-14. Only fodt=VERIFIED, fods=PARTIAL. 22 formats have `spec_parity_status: MISSING`.

**Impact:** Parity tracking is unusable for most formats; can't gate product deepening on parity.

**Required fix:** Regenerate or manually populate spec_parity_status for all 24 formats using qname registry data.

### C4. TC-QNAME-AUTH-002 Status Unverified (xcf:layer python_file)
**Root cause:** Prior run had TC-QNAME-AUTH-002 open (xcf:layer has no python_file). The system has evolved but verification against HEAD not done.

**Impact:** XCF qname compliance may have a gap.

### C5. Open Taskcards Not Reconciled Against 2026-06-26 HEAD
**Root cause:** Prior run produced 21 taskcards, 23 open. Many may be implicitly closed (e.g., TC-QNAME-AUTH-001, TC-CAPABILITY-REPAIR-001). No reconciliation since 20260623.

---

## D. Revised Plan

**Run ID:** `FF-HEAL-QNAME-20260701-{HHMMSS}` (timestamp from execution — date updated to 2026-07-01 in 2026-07-01 hardening)

**Scope:** Delta audit run. Skip work already completed (Phase 5, 7, 12). Focus on new findings and remaining open items.

---

### Phase 1 — Run Setup + Preflight

**Steps:**
1. Generate run ID with current timestamp
2. `mkdir -p .local/evidences/{RUN_ID}/`
3. Capture: `git rev-parse HEAD`, `git status --short | head -30`, `git log --oneline -5`
4. Read `reports/supervisor/session-resume.md` — extract test count, verdict, last sprint
5. Read `reports/supervisor/approval-gates.md` — confirm AUTONOMOUS_CONTINUE
6. Quick gap-ledger stats (Python one-liner): total, open, severity distribution
7. List all prior FF-HEAL runs (5 known + check for any new ones)

**Outputs:** `00-run-index.md`, `01-preflight-state.md`

---

### Phase 2 — Previous Run Review + Delta Identification

**Steps:**
1. Read `.local/evidences/FF-HEAL-QNAME-20260623-131042/22-next-run-prompt.md`
2. Read `.local/evidences/FF-HEAL-QNAME-20260623-131042/17-taskcards.yaml` (grep for open items)
3. For each of 23 prior open taskcards, verify current state at HEAD:
   - TC-QNAME-AUTH-001: `ndjson:field python_file` → CLOSED (verified: field set)
   - TC-QNAME-AUTH-002: Check `xcf.yaml` for `xcf:layer python_file` field
   - TC-CAPABILITY-REPAIR-001: `capability_to_feature_compiler.py` exists → CLOSED
   - TC-PRODUCT-PILOT-NDJSON-001: 24 collection errors — recheck with current test run
   - All others: inspect specific file/code evidence
4. Identify which changes since 20260623 implicitly close or regress taskcards
5. List: CLOSED_SINCE_PRIOR_RUN, STILL_OPEN, REGRESSED, NEW_FINDINGS

**Output:** `02-previous-run-review.md`

---

### Phase 3 — System Chain Delta Audit

**Focus:** Only the chain links affected by new findings. Reference prior run for stable links.

**Steps:**
1. **SAL link (NEW FINDING):** Confirm SAL facts have no `fact_id` field — verify against `.local/spec-cache/sal-facts-latest.json` structure. Document root cause.
2. **QName link (DELTA):** Read `reports/sal-qname-gap-20260626.json` — extract 33 missing entries, document which formats are affected.
3. **Capability link (DELTA):** Read summary of `gap-sal-traceability-20260626.json` — 48.2% qname-based, 0% ID-based. Document.
4. **Feature link (DELTA):** Check `tools/capability_layer/capability_to_feature_compiler.py` — what changed? (`git diff HEAD~5 -- tools/capability_layer/capability_to_feature_compiler.py | head -50`)

**Stable links (reference prior run — no re-audit needed):**
- SPEC: 23 formats parsed, stable
- CLASS/Object Model: no Python src changes
- TEST: 1,609+new passing, no regressions

**Output:** `03-system-chain-audit.md` (delta sections only, with prior run ref for stable sections)

---

### Phase 4 — QName Audit Delta

**Steps:**
1. Check `xcf.yaml` for `xcf:layer`, `xcf:channel`, `xcf:header` — verify python_file populated
2. Read `reports/sal-qname-gap-20260626.json` — list all 33 entries missing SAL resolution:
   ```python
   import json
   data = json.load(open('reports/sal-qname-gap-20260626.json'))
   for fmt, info in data['per_format'].items():
       gaps = info.get('missing_in_sal', [])
       if gaps:
           print(f'{fmt}: {len(gaps)} missing:', gaps)
   ```
3. Cross-check: which formats have 0 SAL facts in `.local/spec-cache/sal-facts-latest.json`?
   (Per MEMORY.md as-of-plan-authored-2026-06-26: CSV TSV NDJSON ABW DIF GNUMERIC SYLK TOML XCF PBM PGM PPM QOI had 0 SAL facts)
   (UPDATED 2026-07-01 hardening — TC-LA-001 merge added facts: CSV 55, TOML 55, ABW 5, DIF 3, GNUMERIC 3, SYLK 3, XCF 2, QOI 2. Zero-fact formats now: TSV NDJSON PBM PGM PPM + ora pam xpm zpaq)

**Output:** `04-qname-audit.md` (delta section + prior run ref for stable areas), `05-src-product-compliance.yaml` (update TC-QNAME-AUTH-001/002 status)

---

### Phase 5 — SAL Audit Delta (Root Cause Documentation)

**CRITICAL NEW FINDING:** SAL facts have no `fact_id` field.

**Steps:**
1. Confirm: `python -c "import json; d=json.load(open('.local/spec-cache/sal-facts-latest.json')); r=d['results'][0]['spec_facts'][0]; print(list(r.keys()))"`
2. Inspect `schemas/sal-facts/sal-facts-schema.json` — does the schema include `fact_id`?
3. Check: does any SAL generation tooling assign IDs?
   ```bash
   grep -r "fact_id\|sal_id\|FACT-" tools/ --include="*.py" | head -20
   ```
4. Read the sal-qname-gap report per_format section to identify which 33 qnames are unresolvable
5. Document root cause and required fix in SAL audit section

**Output:** `07-sal-audit.md`

---

### Phase 6 — Capability + Traceability Delta

**Steps:**
1. Read `reports/capability-layer/gap-sal-traceability-20260626.json` summary:
   - 1,246 total gaps, 43 open, 48.2% traceability
   - 1,816 dangling refs (IDs like FACT-CSV-003 that don't exist)
   - 1,342 high-severity dangling refs
2. Categorize the 43 open gaps by format and severity (from gap-ledger.json)
3. Verify: are the 10 CRITICAL severity gaps among the 43 open?
   ```python
   import json
   gaps = json.load(open('reports/capability-layer/gap-ledger.json'))
   g = gaps.get('gaps', gaps)
   critical_open = [x for x in g if x.get('severity') == 'CRITICAL' and x.get('status') not in ('closed','resolved','done')]
   print(f'Critical+open: {len(critical_open)}')
   for c in critical_open[:5]:
       print(f"  {c.get('gap_id', '?')}: {c.get('description','?')[:60]}")
   ```
4. Note: capability_to_feature_compiler.py was modified — check what Phase 2 now does

**Output:** `08-capability-layer-audit.md`

---

### Phase 7 — Parity Matrix Refresh (22 formats)

**This is the primary executable repair for this run.**

**Steps:**
1. For each of 24 formats in `registry/parity-matrix.yaml`, derive `spec_parity_status` from the qname registry:
   ```python
   import yaml, pathlib
   pm_path = pathlib.Path('registry/parity-matrix.yaml')
   pm = yaml.safe_load(pm_path.read_text())

   registry_dir = pathlib.Path('shared/qname-registry')
   for fmt_name in pm.get('formats', {}):
       reg_file = registry_dir / f'{fmt_name.lower()}.yaml'
       if not reg_file.exists():
           continue
       entries = yaml.safe_load(reg_file.read_text())
       if not isinstance(entries, list):
           continue
       total = len(entries)
       implemented = sum(1 for e in entries if e.get('status') == 'implemented')
       arch_only = sum(1 for e in entries if e.get('status') == 'architecture_only')

       existing = pm['formats'][fmt_name].get('spec_parity_status')
       if existing and existing != 'MISSING':
           continue  # idempotent — don't overwrite existing status

       if total == 0:
           status = 'NO_REGISTRY'
       elif implemented == total:
           status = 'VERIFIED'
       elif implemented >= total * 0.5:
           status = 'PARTIAL'
       elif implemented > 0:
           status = 'MINIMAL'
       else:
           status = 'ARCHITECTURE_ONLY'

       pm['formats'][fmt_name]['spec_parity_status'] = status
       pm['formats'][fmt_name]['qname_implemented'] = implemented
       pm['formats'][fmt_name]['qname_total'] = total
       pm['formats'][fmt_name]['parity_refresh_date'] = '2026-06-26'

   pm_path.write_text(yaml.dump(pm, default_flow_style=False, sort_keys=False))
   print('Parity matrix refreshed')
   ```
2. Record before/after: how many formats changed from MISSING to a real status?
3. Idempotency check: re-run → no changes (all already set)

**Files modified:** `registry/parity-matrix.yaml`

**Output:** `13-backfill-facility-design.md` (updated with parity status), `14-product-maturity-matrix.yaml`

---

### Phase 8 — .NET Product Maturity Update

**Steps:**
1. Note S119 additions: TsvR124 StreamReadRows, ZstR127 InvalidMagicException, NetpbmR137 parser constants
2. Note S120 additions: FodtR141 ParseResult metadata, ZstR127 (already counted), CsvR127 HasColumn/GetColumn
3. Note S121 additions: FodsR140 PNG path export, FodtR142 TXT path export, NdjsonR128 LoadFile
4. Update .NET maturity for: TSV (ReadRows(Stream) → P4+), FODS (PNG export → P6), FODT (TXT export → P6), NDJSON (LoadFile → P3+), ZST (error handling → P2+), CSV (column access → P3), Netpbm (constants → P2)
5. **[ADDED 2026-07-01 hardening — sprint S450]** Note S450 FODT deepening results:
   - WI-S450-001: Stub methods GetCitationCount/GetGlossaryTermCount/GetObjectCount (return 0) — PASS
   - WI-S450-002: Header/footer DOM-backed persistence via office:master-styles EnsureMasterPage() — PASS
   - WI-S450-003: DuplicateParagraph, AddTableColumn, GetParagraphAlignment, GetParagraphStyleName — PASS
   - Test baseline after S450: 6,747 passed / **96 irrecoverable failures** (USER CONFIRMED — not fixable)
   - Irrecoverable conflict categories: GetParagraphText OOB behavior (5 vs 9 tests each side),
     GetPlainTextRange inclusive/exclusive semantics (9 vs 108 tests), GetDocumentStats.ParagraphCount
     (body-only vs. total), InsertHeading count+1 buffer vs. throw, SearchText case sensitivity
   - Net improvement: 123 → 96 failures (−27 fixed this sprint)
   - FODT .NET maturity: Extended APIs partially implemented (stubs + DOM persistence)

**Output:** `14-product-maturity-matrix.yaml` (updated .NET section — must include S450 data)

---

### Phase 9 — Taskcard Reconciliation + New Taskcards

**Steps:**
1. Mark implicitly-closed taskcards from prior run:
   - TC-QNAME-AUTH-001: CLOSED (ndjson:field python_file set)
   - TC-CAPABILITY-REPAIR-001: CLOSED (compiler exists)
   - TC-CAPABILITY-REPAIR-002: CLOSED (gap_ledger_to_work_items.py exists)
   - TC-SUPERVISOR-LANES-001: CLOSED (validate_lane_crossing in governance_validators.py)
2. Write NEW taskcards:
   - **TC-SAL-ID-SCHEME-001** (CRITICAL): SAL facts lack fact_id; assign stable IDs to all 14,441 facts (updated from 14,315 — TC-LA-001 merge added 126 facts per MEMORY.md 2026-07-01)
     - Format: `SAL-{FORMAT}-{QNAME_LOCAL_SNAKE}-{NNN}` (e.g. `SAL-NDJSON-RECORD-001`)
     - Required: update SAL generation tooling to emit fact_id; update gap-ledger spec_refs; update qname registry spec_fact_ref
   - **TC-SAL-QNAME-GAP-001** (HIGH): 33/79 qname registry entries don't resolve to SAL facts via qname matching
     - For each gap format, either add SAL fact with matching qname OR fix registry qname to match existing SAL fact
   - **TC-DANGLE-REPAIR-001** (HIGH): 1,816 dangling fact refs in gap-ledger (depends on TC-SAL-ID-SCHEME-001)
     - After stable IDs assigned, map old FACT-FORMAT-NNN refs to new SAL-FORMAT-... IDs
   - **TC-PARITY-REFRESH-001** (MEDIUM): Refresh parity matrix (this run's Phase 7 repair)
3. Carry forward still-open taskcards from prior run (verified against HEAD):
   - TC-QNAME-AUTH-002 (xcf:layer): verify and close or keep open
   - TC-PRODUCT-PILOT-NDJSON-001: recheck 24 collection errors
   - TC-QNAME-BACKFILL-001/002/003, TC-SAL-REPAIR-001/002, TC-FEATURE-COMPILER-001, TC-SKILL-HARDENING-001/002, TC-SRC-STANDARDIZATION-001/002, TC-TRACEABILITY-001/002 — spot-check each

**Output:** `17-taskcards.yaml`

---

### Phase 10 — Traceability + Gap Matrix

**Steps:**
1. Produce per-format traceability table using `reports/sal-qname-gap-20260626.json` per_format section
2. Build top 20 open gaps table (from gap-ledger.json, filtered to open+critical/high)
3. Update `15-traceability-matrix.yaml`, `16-gap-matrix.yaml`

---

### Phase 11 — Validation

**Steps:**
1. Verify gap-ledger JSON is valid after parity matrix changes (no cross-contamination):
   ```bash
   .venv/Scripts/python -c "import json; json.load(open('reports/capability-layer/gap-ledger.json')); print('gap-ledger: valid JSON')"
   ```
2. Verify parity-matrix.yaml is valid YAML after refresh:
   ```bash
   .venv/Scripts/python -c "import yaml; yaml.safe_load(open('registry/parity-matrix.yaml').read()); print('parity-matrix: valid YAML')"
   ```
3. Verify new test files exist and are syntactically valid Python:
   ```bash
   .venv/Scripts/python -m py_compile tests/supervisor/test_ai_non_authority.py tests/supervisor/test_sal_path_resolution.py && echo "test files: valid"
   ```
4. Run targeted test subset (fast):
   ```bash
   .venv/Scripts/pytest tests/supervisor/test_ai_non_authority.py tests/supervisor/test_sal_path_resolution.py -q --timeout=30
   ```
5. Source structure validator:
   ```bash
   .venv/Scripts/python tools/validators/source_structure_validator.py 2>&1 | tail -5
   ```
   Expected: `worsened=0, blocks_sprint=False`

**Output:** `20-validation-log.md`

---

### Phase 12 — Evidence Bundle + Closeout

**Steps:**
1. Write remaining output files: `09-skill-inventory-and-gaps.md` (delta note only), `10-downstream-layer-audit.md` (delta note), `11-autonomous-supervisor-audit.md` (delta note), `12-lane-separation-risk.md` (prior run ref)
2. Write `06-src-source-quality-review.md` (note: no Python src changes since 20260623; reference prior run)
3. Write `18-repair-plan.md`, `19-execution-log.md`, `21-idempotency-report.md`, `22-next-run-prompt.md`, `23-final-verdict.md`
4. Bundle:
   ```python
   import zipfile, hashlib, pathlib
   run_dir = pathlib.Path('.local/evidences/{RUN_ID}')
   zip_path = run_dir / 'evidence-bundle.zip'
   with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
       for f in sorted(run_dir.rglob('*')):
           if f != zip_path and f.is_file():
               z.write(f, f.relative_to(run_dir))
   sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
   print(f'Bundle: {zip_path.absolute()}')
   print(f'SHA-256: {sha}')
   ```
5. Print absolute path + SHA-256

---

## Files Modified (Repair Only)

| File | Change | Reversible |
|---|---|---|
| `registry/parity-matrix.yaml` | Add spec_parity_status for 22 formats | Yes — regenerable |

**NOT modifying:** gap-ledger.json (SAL ID repair is a taskcard, not this run's safe scope), source files, SAL facts.

---

## Expected Outputs (23 files + bundle)

| File | Content |
|---|---|
| 00-run-index.md | Run ID, 5+1=6 prior runs table, this run scope |
| 01-preflight-state.md | HEAD, dirty files, gaps stats, test baseline |
| 02-previous-run-review.md | 23 prior taskcards reconciled; delta table |
| 03-system-chain-audit.md | Delta audit; SAL ID scheme root cause |
| 04-qname-audit.md | 33 missing SAL entries; xcf:layer verification |
| 05-src-product-compliance.yaml | TC-QNAME-AUTH-001 CLOSED; updated |
| 06-src-source-quality-review.md | "No Python src changes since 20260623" delta note |
| 07-sal-audit.md | Root cause: no fact_id in SAL facts |
| 08-capability-layer-audit.md | 43 open gaps; CRITICAL/HIGH breakdown |
| 09-skill-inventory-and-gaps.md | Delta: ingest-spec-sal added |
| 10-downstream-layer-audit.md | Delta note; new supervisor tests |
| 11-autonomous-supervisor-audit.md | test_ai_non_authority.py noted |
| 12-lane-separation-risk.md | Reference prior run; stable |
| 13-backfill-facility-design.md | SAL ID scheme as blocker for backfill |
| 14-product-maturity-matrix.yaml | .NET S119-S121 maturity updates |
| 15-traceability-matrix.yaml | Per-format traceability from sal-qname-gap report |
| 16-gap-matrix.yaml | Top 20 open gaps by severity |
| 17-taskcards.yaml | 3 closed + 3 new + carry-forward |
| 18-repair-plan.md | Parity matrix refresh documented |
| 19-execution-log.md | Timestamped execution log |
| 20-validation-log.md | All validation commands + results |
| 21-idempotency-report.md | Parity matrix refresh is idempotent |
| 22-next-run-prompt.md | TC-SAL-ID-SCHEME-001 as top priority |
| 23-final-verdict.md | ACCEPTED_WITH_REMAINING_TASKCARDS |
| evidence-bundle.zip | All above zipped |

---

## Execution Order (by dependency)

1. Phase 1 (setup) → no deps
2. Phase 2 (prior run review) → needs Phase 1
3. Phase 3 (chain delta) → needs Phase 2
4. Phase 4 (qname delta) → needs Phase 3
5. Phase 5 (SAL delta) → needs Phase 3
6. Phase 6 (capability delta) → needs Phase 5
7. Phase 7 (parity matrix REPAIR) → independent, but needs Phase 4 data
8. Phase 8 (.NET maturity) → independent
9. Phase 9 (taskcards) → needs Phases 4, 5, 6, 7, 8
10. Phase 10 (traceability matrix) → needs Phase 6
11. Phase 11 (validation) → needs Phase 7 (parity repair)
12. Phase 12 (closeout + bundle) → needs all phases

---

## Verification After Execution

```bash
# 1. 24 output files present (23 + bundle)
ls -la .local/evidences/FF-HEAL-QNAME-20260626-*/  | wc -l
# Expected: >= 24

# 2. Parity matrix has real statuses for 24 formats
python -c "import yaml; d=yaml.safe_load(open('registry/parity-matrix.yaml').read()); fmts=d.get('formats',{}); missing=[k for k,v in fmts.items() if v.get('spec_parity_status','MISSING')=='MISSING']; print(f'Still MISSING: {len(missing)} = {missing}')"
# Expected: 0 or near-0 (only if no registry entry exists for that format)

# 3. Parity matrix is valid YAML
python -c "import yaml; yaml.safe_load(open('registry/parity-matrix.yaml').read()); print('VALID')"

# 4. gap-ledger unchanged
python -c "import json; d=json.load(open('reports/capability-layer/gap-ledger.json')); g=d.get('gaps',d); print(f'Gaps: {len(g)}, open: {sum(1 for x in g if x.get(\"status\") not in (\"closed\",\"resolved\",\"done\"))}'); print('All have severity:', all(x.get(\"severity\") for x in g))"

# 5. New supervisor tests pass
.venv/Scripts/pytest tests/supervisor/test_ai_non_authority.py tests/supervisor/test_sal_path_resolution.py -q
```

---

## Final Verdict (expected)

**Run verdict:** ACCEPTED_WITH_REMAINING_TASKCARDS
**Execution readiness:** READY_AFTER_TARGETED_MACHINERY_REPAIRS

**Remaining blockers before autonomous product deepening can resume at full speed:**
1. **TC-SAL-ID-SCHEME-001** (CRITICAL): SAL facts need stable `fact_id` before traceability is real
2. **TC-SAL-QNAME-GAP-001** (HIGH): 33/79 qname entries unresolvable in SAL
3. **TC-DANGLE-REPAIR-001** (HIGH): 1,816 dangling gap-to-SAL refs (depends on #1)

**Safe for current product deepening continuation:**
- .NET deepening (S451+ FODT — irrecoverable conflicts documented, continue with next format or different API surface)
- Python format deepening — not blocked
- Gate 11 execution — requires Babar Raza (TRUE_EXTERNAL_GATE)

---

## E. Plan File Hardening Change Log (2026-07-01)

**Hardening session:** 2026-07-01T18:00Z
**Hardened by:** convergence session 22efecc290b9
**Source of truth HEAD at hardening:** `b1d39abc`
**Prior HEAD in plan:** `24cc7fe0` (Δ = 7+ commits)

### E1. Sources Reviewed

| Source | Path | Relevance |
|---|---|---|
| Sprint s450 evidence | `.local/evidences/ff-sprint-s450-dotnet-fodt-deepening-20260701/evidence-declaration.yaml` | Phase 8 update |
| Convergence report | `.supervisor/state/closure-record-FF-G4-BACKFILL-001.json` | Gate 4 context |
| Convergence loop state | `.supervisor/state/convergence-loop-state.json` | Mission closure |
| Gate4 regression output | background task bxp01jx32 | 1107/1108 pass |
| MEMORY.md | `C:\Users\prora\.claude\projects\...\memory\MEMORY.md` | SAL fact count, TC-LA-001 delta |
| Parity matrix | `registry/parity-matrix.yaml` | Still 22 MISSING (Phase 7 not run) |
| Plan embedded lock | end of this file | advisory only — superseded by hardening |

### E2. Assistant Summary Claim Audit

| Claim ID | Claim | Type | Disposition | Plan Action |
|---|---|---|---|---|
| C-S450-01 | Sprint s450 WI-001/002/003 all PASS | verification | VERIFIED_AND_PRESERVE | Phase 8 updated |
| C-S450-02 | 6,747 tests passed after s450 | verification | VERIFIED_AND_PRESERVE | Phase 8 updated |
| C-S450-03 | 96 remaining failures irrecoverable (user confirmed) | closure | VERIFIED_AND_PRESERVE | TC-FODT-IRR-001 added |
| C-CONV-01 | FF-G4-BACKFILL-001 TERMINAL_CLOSED, 11 taskcards closed | closure | VERIFIED_AND_PRESERVE | Phase 9 context updated |
| C-CONV-02 | 13/13 closure verification checks PASS | verification | VERIFIED_AND_PRESERVE | Gate 4 context noted |
| C-CONV-03 | Gate4 regression 1107/1108, 1 pre-existing | regression | VERIFIED_AND_PRESERVE | Background task confirmed |
| C-PLAN-01 | "mutation_policy: no further writes" in embedded lock | governance | CONTRADICTED — advisory only; hardening is mandatory | Lock superseded (E6) |
| C-PLAN-02 | Run ID `FF-HEAL-QNAME-20260626-{HHMMSS}` | identification | STALE — date was 2026-06-26 | Run ID updated to 2026-07-01 |
| C-PLAN-03 | SAL total "14,315 facts" in TC-SAL-ID-SCHEME-001 | implementation | STALE — TC-LA-001 added 126 | Updated to 14,441 |
| C-PLAN-04 | Phase 4: "CSV TSV NDJSON ABW DIF GNUMERIC SYLK TOML XCF PBM PGM PPM QOI have 0 SAL facts" | implementation | PARTIAL — 8 of 13 now have facts | Phase 4 note updated |
| C-PLAN-05 | ".NET deepening (S122+) — not blocked" | safety | STALE — S450 completed; next is S451+ | Footer updated |

### E3. Explicit Findings Incorporated

| Finding ID | Severity | Description | Resolution |
|---|---|---|---|
| HEAL-FIND-001 | INFO | Sprint S450 results not in plan (Phase 8) | Phase 8 updated with S450 data |
| HEAL-FIND-002 | MEDIUM | Run ID uses stale 2026-06-26 date | Run ID updated to 2026-07-01 |
| HEAL-FIND-003 | MEDIUM | SAL fact count stale (14,315 → 14,441) | TC-SAL-ID-SCHEME-001 updated |
| HEAL-FIND-004 | MEDIUM | Zero-SAL formats list stale after TC-LA-001 | Phase 4 note updated |
| HEAL-FIND-005 | LOW | HEAD baseline stale (`24cc7fe0` → `b1d39abc`) | Section A updated |
| HEAL-FIND-006 | LOW | Embedded lock mutation_policy advisory contradicts mandatory hardening | Lock noted as superseded (advisory) |
| HEAL-FIND-007 | INFO | FF-G4-BACKFILL-001 closure context not in plan | Phase 9 taskcard reconciliation context added |

### E4. Implied / Hidden Gaps Incorporated

| Gap ID | Severity | Description | Resolution |
|---|---|---|---|
| HEAL-GAP-001 | HIGH | Parity matrix Phase 7 STILL NOT EXECUTED — confirmed 22/24 MISSING at `b1d39abc` | Phase 7 remains primary repair; urgency confirmed |
| HEAL-GAP-002 | HIGH | All 12 plan phases remain unexecuted — no `FF-HEAL-QNAME-20260626-*` evidence directory | Plan still fully pending execution |
| HEAL-GAP-003 | MEDIUM | FODT 96 irrecoverable failures need canonical documentation (not just inline prose) | TC-FODT-IRR-001 added |
| HEAL-GAP-004 | LOW | FF-G4-BACKFILL-001 closed — Phase 9 taskcard reconciliation context stale | Phase 9 updated to note TC-G4-* closed |

### E5. Contradictions Reconciled

| Contradiction | Resolution |
|---|---|
| Embedded lock `mutation_policy: "no further plan/hardening/execution writes"` vs. mandatory plan hardening | Lock is advisory only from prior session `923e237958c1`. Current hardening session `22efecc290b9` supersedes it. Lock not removed (historical record) but overridden. |
| Plan baseline HEAD `24cc7fe0` vs. current `b1d39abc` | Section A updated to note both HEADs |
| SAL total `14,315` vs. `14,441` (after TC-LA-001) | TC-SAL-ID-SCHEME-001 scope updated |
| Zero-SAL format list stale for 8 formats | Phase 4 note updated with current state |

### E6. Taskcard Register

#### TC-FODT-IRR-001 — Document 96 Irrecoverable FODT .NET Failures

```yaml
taskcard:
  id: TC-FODT-IRR-001
  title: "Document 96 irrecoverable FODT .NET test failures as permanent baseline"
  source_finding: HEAL-GAP-003
  source_claim_ids: [C-S450-03]
  why_it_matters: >
    96 test failures remain after S450. User confirmed all are irrecoverable
    due to semantic conflicts between test suites (inclusive vs exclusive range,
    body-only vs. total paragraph counts, case-sensitive search). Without a
    canonical record, future FODT sprints may attempt to fix them and introduce
    regressions elsewhere.
  current_status: not_attempted
  priority: MEDIUM
  lane_owner: commercial_dotnet
  dependencies: []
  required_work:
    - Write `.local/fodt-irrecoverable-failures-baseline.md` listing all 96 failure root causes by category
    - Add `# IRRECOVERABLE` marker comments above the 7 conflicting test methods in the C# test files
    - Update evidence-declaration.yaml for S450 to reference the baseline doc
  allowed_actions:
    - Read test files to enumerate the 96 failures
    - Write baseline document
    - Add inline comments to test files (not source files)
  forbidden_actions:
    - Modify FodtDocument*.cs source to fix irrecoverable tests
    - Delete or skip the 96 tests
  required_verification:
    - Baseline doc lists all 96 failures with category and root cause
    - test run still shows exactly 96 failures (not more, not fewer)
  required_evidence:
    - path: .local/fodt-irrecoverable-failures-baseline.md
      type: documentation
  proof_level_current: 0
  proof_level_target: 2
  acceptance_criteria:
    - Baseline document written and committed
    - All 96 failure categories documented with root cause
    - Future FODT sprints can reference this doc to avoid re-attempting irrecoverable fixes
  rollback: delete baseline doc if categories turn out to be wrong
  stop_conditions:
    - Any previously irrecoverable category becomes fixable — escalate as TC-FODT-FIXABLE-NNN
  closeout_rules:
    - close when baseline doc written and test count still 96
  exact_next_action: >
    Read tests/net/fodt/ directory, enumerate all 96 failure test names, categorize by root cause,
    write .local/fodt-irrecoverable-failures-baseline.md
```

#### TC-SAL-ID-SCHEME-001 (updated scope)

Fact count updated to **14,441** (was 14,315 — TC-LA-001 merge added 126 facts for CSV/TOML/ABW/DIF/GNUMERIC/SYLK/XCF/QOI).
All other fields from the original taskcard definition (Phase 9 D.) remain valid.

#### TC-PARITY-REFRESH-001 (Phase 7 — primary repair, urgency confirmed)

Status: **not_attempted** — parity matrix confirmed still 22 MISSING at current HEAD.
Exact next action: execute Phase 7 script in Section D. Output root updated to `FF-HEAL-QNAME-20260701-{HHMMSS}`.

### E7. Gate and Proof Contract (Phase 7)

Phase 7 (Parity Matrix Refresh) must satisfy:
- **Entry:** Parity matrix currently has 22 MISSING statuses (verified at `b1d39abc`)
- **Required proof level:** 2 (focused validation — idempotent re-run produces no changes)
- **Required evidence:** `14-product-maturity-matrix.yaml` with all 24 formats assigned a real status
- **Failure behavior:** If qname-registry file missing for a format → status = `NO_REGISTRY` (not MISSING)
- **Repair path:** Re-run the Phase 7 script; it is idempotent (won't overwrite non-MISSING statuses)
- **Exit condition:** `python -c "..."` check in "Verification After Execution" shows `Still MISSING: 0`
- **Reopening condition:** If a new format is added with no qname registry entry

### E8. Exact Next Action

```
1. Generate run ID: FF-HEAL-QNAME-20260701-$(date +%H%M%S)
2. mkdir -p .local/evidences/FF-HEAL-QNAME-20260701-{HHMMSS}/
3. Execute Phase 1 (Run Setup)
4. Execute Phase 2 (Previous Run Review — reconcile 23 prior taskcards against b1d39abc)
5. Execute Phase 3 (System Chain Delta — SAL ID scheme root cause)
6. Execute Phase 4 (QName Audit Delta — 33 missing SAL entries; xcf:layer)
7. Execute Phase 5 (SAL Audit — confirm no fact_id in 14,441 facts; schema check)
8. Execute Phase 6 (Capability Delta — 43 open gaps; CRITICAL/HIGH breakdown)
9. Execute Phase 7 (Parity Matrix Refresh — PRIMARY REPAIR — fix 22 MISSING statuses)
10. Execute Phase 8 (NET Maturity Update — include S450 FODT data)
11. Execute Phase 9 (Taskcard Reconciliation — include FF-G4-BACKFILL-001 closure; add TC-FODT-IRR-001)
12. Execute Phase 10-12 (Traceability, Validation, Bundle)
```

### E9. Remaining True Blockers

| Blocker | Type | Notes |
|---|---|---|
| Gate 11 execution | TRUE_EXTERNAL_GATE | Requires Babar Raza commercial sign-off |
| FODT 96 irrecoverable failures | NOT_A_BLOCKER | User confirmed; document only (TC-FODT-IRR-001) |
| SAL ID scheme (TC-SAL-ID-SCHEME-001) | NOT_A_BLOCKER_FOR_HEAL_RUN | Taskcard exists; this run documents it, not fixes it |

### E10. Anti-Overclaim Rules for This Run

- Do NOT claim the parity matrix is refreshed without running Phase 7 and verifying `Still MISSING: 0`
- Do NOT claim taskcards are closed without verifying against HEAD
- Do NOT treat advisory lock in embedded `<!--plan_terminal_lock:` as a functional write-block
- Do NOT mark this run COMPLETE until all 23 expected output files exist and evidence bundle is zipped


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-06-26T16:47:19.445801+00:00"
  locked_by: "923e237958c1"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
  hardening_override:
    hardened_at: "2026-07-01T18:10:00Z"
    hardened_by: "22efecc290b9"
    override_reason: "PLAN FILE HARDENING MODE is mandatory per CLAUDE.md and supersedes advisory mutation_policy"
    status_after_hardening: ITERATION_REQUIRED_HARDENED
    next_action: "Execute all 12 phases beginning with Phase 1 (Run ID FF-HEAL-QNAME-20260701)"
-->
