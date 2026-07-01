# eager-launching-phoenix — Revised Plan (2026-06-29, third reassessment)
<!-- TASKCARD STATUS SUMMARY (required by lifecycle_audit.py) -->
| TC | Status |
|---|---|
| TC-TEST-001 | CLOSED |
| TC-SAL-CLOSE-13 | CLOSED |
| TC-G11-PREP | CLOSED |
| TC-PORTFOLIO-METRICS | CLOSED |
<!-- END TASKCARD STATUS SUMMARY -->

## A. Current-State Reassessment

This plan was written twice before. Each time, significant system changes made it stale.
This revision is based on verified repository state at HEAD a3ed0a0c (+179 commits since the
prior reassessment at 555aa4c7).

### What changed since the last revision

| Change | Evidence | Impact on prior plan |
|---|---|---|
| Oracle Wave 6 completed — ALL 20 formats | `oracle/formats/*/oracle-package.yaml` glob returns 20 files (abw, csv, dif, fodg, fodp, fods, fodt, gnumeric, ndjson, ods, odt, pbm, pgm, pgm, ppm, qoi, sylk, toml, tsv, xcf, zst) | TC-REV-003 and TC-REV-006 are DONE |
| SAL gaps: 33 → 13 via SAL-VHIP-001 | `sal-qname-gap-20260626.json` summary: entries_resolved=67, entries_missing=13, overall_coverage_pct=83.8% | TC-REV-001 partially done; narrowed scope |
| CAP-REPAIR-001 was already done before last plan | Layer audit H04: "autonomous_cycle.py Step 3a-pre merges gap_ledger_ref — this handoff is the most mature" | TC-REV-004 was OBSOLETE from the start |
| 29 governed layer plans now exist | `plans/layers/*.md` glob returns 29 files (test-infrastructure-layer.md, specification-authority-layer.md, qname-hierarchy-layer.md, etc.) | Layer governance system is the canonical tracking mechanism; old forensic taskcards are superseded |
| Test Infrastructure Layer plan active with TC-TEST-001 ready | `plans/layers/test-infrastructure-layer.md` status=GOVERNED_OPERATIONAL, health=HEALTHY, ready_taskcards=[TC-TEST-001], next_action="Add missing roundtrip tests and define fast/medium/full validation lanes" | TC-TEST-001 is the immediate next task |
| Net deepening reached S189–S190 | Layer-audit-baseline delta: 70 feat(net-deepening) commits | Autonomous .NET deepening loop is active and continuing independently |

---

## B. Item-by-Item Status of Previous Plan

| TC | Task | Status | Evidence |
|---|---|---|---|
| TC-REV-001 | SAL 33-gap closure | **PARTIALLY SOLVED** | 20 gaps closed by SAL-VHIP-001; 13 remain. Gap list: ABW×3, FODG×3, FODP×3, FODS×1, + 3 unread entries |
| TC-REV-002 | SAL validators confirmed registered | **SOLVED** | governance_validators_sal.py wired per SAL-VHIP-001 sprint. 83 validators total per layer-audit-baseline update |
| TC-REV-003 | Oracle Wave 6 Batch A (cells) | **SOLVED** | gnumeric/ods/dif/sylk all have oracle-package.yaml |
| TC-REV-004 | CAP-REPAIR-001: wire gap_ledger_to_work_items | **OBSOLETE** | Was already done before this plan was written. Layer audit H04 confirms handoff is "the most mature" |
| TC-REV-005 | Gate 11 commercial packet | **UNRESOLVED** | No evidence of docs/publication/gate11-submission-fods.md existing |
| TC-REV-006 | Oracle Wave 6 Batches B/C/D | **SOLVED** | All 20 formats have oracle-package.yaml. Oracle layer complete. |
| TC-REV-007 | Post-repair reaudit + final metrics | **PREMATURE** | Still depends on TC-SAL-CLOSE completing |

### What the prior plan missed entirely

1. **TC-TEST-001** — The test infrastructure layer (L07) has a governed plan at
   `plans/layers/test-infrastructure-layer.md` with TC-TEST-001 **ready to execute** as of
   2026-06-29. This was created after the prior plan was written. It is the active next task
   per the layer governance system.

2. **29 governed layer plans now exist** — The entire system is now tracked through
   `plans/layers/*.md`. The forensic-audit-20260625 taskcards are historical artifacts;
   the layer plans are the canonical governance source.

---

## C. Remaining Problems

### C1. 13 SAL Fact ID Gaps (HIGH — blocks L01 → L02 provenance chain)

**Evidence:** `reports/sal-qname-gap-20260626.json` (83.8% coverage, 13 gaps)

**Exact gap list:**
- **ABW** (3 gaps): `abiword:document`, `abiword:section`, `abiword:p` — all reference
  `FACT-ABW-001` which is not in `sal-facts-latest.json`. The qname-registry has 3 entries
  all pointing to the same single fact ID. ABW has 0% coverage.
- **FODG** (3 gaps): `office:document` / FACT-FODG-001, `draw:page` / FACT-FODG-002,
  `draw:frame` / FACT-FODG-003 — none found in sal-facts-latest.json (0% coverage).
- **FODP** (3 gaps): `office:document` / FACT-FODP-001, `presentation:page` / FACT-FODP-002,
  `draw:frame` / FACT-FODP-003 — none found (0% coverage).
- **FODS** (1 gap): `office:body` / FACT-FODS-002 — only 1 remaining of 12 entries (91.7%).
- **Unknown** (3 gaps): Not yet read from the full report — need to complete reading.

**Root cause:** FACT-ABW-001 exists in `.local/spec-cache/abw/` format-specific files but was
not consolidated into `sal-facts-latest.json` during the SAL-VHIP-001 backfill sprint. FODG/FODP
share the ODF namespace with FODS but their format-specific FACT IDs were not seeded.

**Impact:** L01 → L02 provenance chain shows gaps for ABW, FODG, FODP. QName entries say
"verified" or "implemented" but spec_fact_refs cannot be validated.

### C2. TC-TEST-001 Not Executed (MEDIUM — L07 layer stalled at OPERATIONAL_HARDENING)

**Evidence:** `plans/layers/test-infrastructure-layer.md`:
- `status: GOVERNED_OPERATIONAL`
- `ready_taskcards: [TC-TEST-001]`
- `active_taskcards: []` — nothing is running
- `next_action: "Add missing roundtrip tests and define fast/medium/full validation lanes for autonomous trains"`

The layer plan was created 2026-06-29 (today). TC-TEST-001 is defined as ready but has no
active execution. The gap register says: "Formats with fewer than three meaningful tests need
coverage backfill" and "Tests must prove parse/load, edit object model, same-format save, and
dogfood export where applicable."

**Impact:** L07 maturity stuck at 4/5. No fast/medium/full validation lane separation means
all automated trains run the full test suite, making CI slow and brittle.

### C3. Gate 11 Commercial Packet Not Prepared (MEDIUM — blocks FODS/FODT commercial release)

**Evidence:** No `docs/publication/gate11-submission-*.md` found. Taskcard G11-001 from
`reports/forensic-audit-20260625/taskcards.yaml` is still open. FODS/FODT have cleared all
technical gates. Babar Raza sign-off is the TRUE_EXTERNAL_GATE; the packet preparation is
agent-owned.

**Impact:** Commercial release of FODS and FODT is blocked on missing packet, not on missing
technical evidence. This is fully reversible — preparation takes < 1 sprint.

---

## D. Revised Plan — Current Reality Only

### TC-TEST-001: Test Infrastructure Layer — Roundtrip Tests + Validation Lanes
**Priority:** P0 (READY taskcard in active governed layer plan)
**Layer:** L07 (test-infrastructure-layer.md)
**Skills:** `/add-roundtrip-test`, `/create-consumer-roundtrip`
**Dependencies:** None — L06 (product source) is healthy

**Context:** The test infrastructure layer governance plan (plans/layers/test-infrastructure-layer.md,
revision 2, 2026-06-29) has TC-TEST-001 as its sole ready taskcard. The layer is at OPERATIONAL_HARDENING
stage with maturity 4/5. The gap register identifies two concrete problems:

1. **Formats with < 3 meaningful test files** need roundtrip test coverage
2. **No fast/medium/full validation lane separation** — causes slow CI for autonomous trains

**Steps:**
1. Audit test coverage per format: for each of 20 Python formats, count test files in
   `tests/python/<format>/` and classify as: roundtrip (parses a real file), model (exercises
   domain model), mutation (modifies and re-saves), or fixture-only (tests module internals).
2. Identify which formats have < 3 meaningful (non-fixture-only) tests. Target: zero formats
   below this threshold.
3. For each under-covered format, use `/add-roundtrip-test` skill to add a test that:
   - Loads a real sample file from `samples/by-format/<format>/`
   - Calls `from_file()` on the domain model
   - Checks at least 2 typed properties
   - Confirms `spec_qname` value matches registry
4. Define three validation lanes in `registry/test-layer-manifest.yaml` (or equivalent):
   - **fast** (< 30s): unit tests only, no file I/O
   - **medium** (< 120s): unit + roundtrip tests on minimal samples
   - **full** (unlimited): all tests including oracle, property-based, security
5. Write evidence declaration citing: test count delta, lane manifest path, formats covered.
6. Update `plans/layers/test-infrastructure-layer.md`: move TC-TEST-001 from `ready_taskcards`
   to `active_taskcards`, then to `completed_taskcards` when done.

**Allowed paths:**
- `tests/python/<format>/test_<format>_roundtrip.py` (new roundtrip tests, one per format)
- `registry/test-layer-manifest.yaml` (lane definition additions only)
- `plans/layers/test-infrastructure-layer.md` (taskcard status update only)

**Forbidden paths:**
- `src/python/` — do not modify product source during this taskcard
- `registry/source-structure-baseline.json` — test files don't count toward LOC caps

**Verification:**
- Every Python format has ≥ 3 meaningful test files (not counting fixture-only)
- Three lanes (fast/medium/full) defined in registry/test-layer-manifest.yaml
- pytest runs with lane markers complete in < 30s (fast), < 120s (medium)
- All existing tests still pass

---

### TC-SAL-CLOSE-13: Close the 13 Remaining SAL Fact ID Gaps
**Priority:** P1
**Layer:** L01 (specification-authority-layer.md)
**Skills:** `/sal-pipeline-heal`, `/ingest-spec-sal`
**Dependencies:** None (independent of TC-TEST-001)

**Context:** `reports/sal-qname-gap-20260626.json` shows 83.8% coverage (67/80 entries resolved).
13 entries across ABW, FODG, FODP, FODS are unresolved. The SAL-VHIP-001 sprint already closed
20 gaps (from 33 to 13) by seeding facts into sal-facts-latest.json. The remaining 13 need the
same treatment.

**Why these 13 are harder:** ABW has no ODF source — its spec is the AbiWord XML format documentation
(`.local/spec-cache/abw/awml-1.0/`). FODG and FODP share the ODF namespace with FODS/FODT but their
format-specific FACT-FODG-NNN and FACT-FODP-NNN IDs were never seeded from the ODF shared facts.
FODS has 1 gap (office:body = FACT-FODS-002) — the ODF fact file has this but the ID is mismatched.

**Steps:**
1. Run `/sal-pipeline-heal --format abw` — seed FACT-ABW-001 from the AbiWord XML spec
   (`.local/spec-cache/abw/awml-1.0/`). Minimum: 1 fact covering the document root element.
2. For FODG: confirm whether FODS SAL facts include `draw:page` and `draw:frame` equivalents.
   If FACT-FODS-NNN records cover these as ODF Drawing concepts, update FODG qname-registry
   to reference the correct FACT-FODS-NNN IDs (since FODG reuses the same ODF namespace).
   If not, seed FACT-FODG-001/002/003 with `authority: workbench_verified`.
3. For FODP: same approach as FODG (ODF Presentation reuses draw: namespace).
4. For FODS: find `office:body` in the existing FODS SAL facts — it likely exists as a
   different ID (e.g., FACT-FODS-005). Update `shared/qname-registry/fods.yaml` entry for
   `office:body` to reference the correct existing FACT ID.
5. Read remaining 3 unknown gaps from the full `sal-qname-gap-20260626.json` report, apply
   same pattern.
6. Re-run the SAL/qname cross-reference audit tool:
   ```
   python tools/audit_sal_to_qname.py > reports/sal-qname-gap-reaudit.json
   ```
7. Verify: `entries_missing_in_sal = 0` (100% coverage).

**Verification:**
- `reports/sal-qname-gap-reaudit.json` shows 80/80 resolved (100%)
- No new HIGH-severity gaps introduced
- SAL governance validators (governance_validators_sal.py) pass

---

### TC-G11-PREP: Gate 11 Commercial Sign-Off Packet
**Priority:** P2
**Layer:** L15 (package-release-layer.md)
**Dependencies:** None (fully agent-owned preparation)

**Context:** FODS and FODT cleared all technical criteria. Gate 11 G11-G approved by Babar Raza
(2026-06-05 per MEMORY.md). The actual commercial release sign-off is the TRUE_EXTERNAL_GATE.
The preparation packet is agent-owned and takes < 1 sprint.

**Steps:**
1. Read `registry/gate11-criteria.yaml` — extract C1-C20 (.NET) and P1-P11 (Python) criteria.
2. Compile test evidence: `.venv/Scripts/pytest tests/net/fods/ --co -q | wc -l` for count.
3. Write `docs/publication/gate11-submission-fods.md`:
   - Full C1-C20 scorecard with evidence paths
   - Full P1-P11 scorecard
   - NuGet package SHA-256 (from poc-targets.yaml or local build)
   - Test count summary (Python + .NET)
   - Release notes reference
4. Write `docs/publication/gate11-submission-fodt.md` (same structure).
5. Run V48 validation: verify no architecture_only stubs cited as RELEASE_GATE evidence.

**Verification:**
- Both submission docs exist at `docs/publication/`
- V48 passes
- Packet is ready to present to Babar Raza

---

### TC-PORTFOLIO-METRICS: Final Portfolio Metrics (Post-Repair)
**Priority:** P3
**Dependencies:** TC-TEST-001, TC-SAL-CLOSE-13

**Context:** `reports/forensic-audit-20260625/` lacks `format-pipeline-metrics.csv` and
`portfolio-pipeline-metrics.md` (not produced by prior audit sprint). These are the final
required artifacts from the original forensic audit specification.

**Steps:**
1. Produce `reports/forensic-audit-20260625/format-pipeline-metrics.csv` — one row per format,
   30 metrics columns (spec_docs, sal_facts, qname_coverage_pct, test_count, oracle_pass_pct,
   proof_level, etc.) using current system state.
2. Produce `reports/forensic-audit-20260625/portfolio-pipeline-metrics.md` — aggregate totals
   + 20-dimension process grade matrix.
3. Update `reports/forensic-audit-20260625/pipeline-idempotency-verdict.md` — run metrics
   script twice, confirm identical output.
4. Write final verdict: `FORENSIC_AUDIT_COMPLETE_REPAIR_EXECUTION_IN_PROGRESS` if SAL gaps
   remain, or `SPEC_TO_CODE_PIPELINE_AUDITED_HEALED_AND_PORTFOLIO_RECONCILED` if all gaps closed.

---

## E. Execution Order

```
PARALLEL (COMPLETE — 2026-07-01):
  TC-TEST-001   ✓ CLOSED — 4 roundtrip tests (odt/pgm/qoi/xcf), named_lanes added to registry/test-layer-manifest.yaml, 26/26 pass
  TC-SAL-CLOSE-13 ✓ CLOSED — 9 facts added (FODS-002,FODG-001/002/003,FODP-001/002/003,ODS-002,QOI-003), 100% coverage (80/80)

NEXT (active):
  TC-G11-PREP   (P2 — prepare Gate 11 commercial packet for FODS + FODT)

FINAL:
  TC-PORTFOLIO-METRICS (P3 — SAL now 100%, can proceed)
```

---

## F. Items Explicitly NOT in This Plan

| Dropped Item | Reason |
|---|---|
| Oracle Wave 6 (all batches) | DONE — all 20 formats have oracle-package.yaml |
| CAP-REPAIR-001 (gap_ledger wiring) | Was already done; included erroneously in prior plan |
| Domain model backfill (all 20 formats) | DONE — all 20 have models.py |
| DIF/FODG qname ClassVar injection | DONE — dif_parser.py has ClassVar; fodg/models.py has spec_qname |
| Analytics masquerade remediation | Deferred (GAP-PROD-INV-MASQ-001, V42 active) — do not touch |
| Net deepening S191+ | Governed by autonomous loop via next-sprint.md; not plan work |
| taskcards/ archive (TC-LA-006) | Out of scope for this plan; create separate layer task if needed |
| Feature compilation deduplication (TC-LA-007) | Low priority; in scope for feature-compilation-layer.md, not this plan |

---

## G. Layer Governance Note

As of 2026-06-29, there are **29 governed layer plans** in `plans/layers/`. Each major system
component has its own plan file. Work on any component should be executed by updating the
corresponding layer plan's taskcard register. This plan (eager-launching-phoenix.md) governs
the forensic audit mission only; it delegates to layer plans for implementation.

| This plan's task | Governed by |
|---|---|
| TC-TEST-001 | plans/layers/test-infrastructure-layer.md |
| TC-SAL-CLOSE-13 | plans/layers/specification-authority-layer.md |
| TC-G11-PREP | plans/layers/package-release-layer.md |
| TC-PORTFOLIO-METRICS | reports/forensic-audit-20260625/ (direct) |

---

## H. Hard Stops

- Babar Raza Gate 11 commercial sign-off: TRUE_EXTERNAL_GATE (agent owns preparation only)
- Analytics rotation: V42 active; no new arithmetic-only analytics functions
- LOC caps: source-structure-baseline.json write-once; test files not subject to caps


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-01T15:46:11.807469+00:00"
  locked_by: "22efecc290b9"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
