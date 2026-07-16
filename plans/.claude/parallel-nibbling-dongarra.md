# Plan: Durable Package-Install-Proof System for All 26 Python Formats (GAP-FORENSIC-001)

## Context

Every Python format passes the oracle (73/73), but "oracle PASS" only proves in-repo behavior. No format except partial fods evidence has proof it installs and works from a built wheel. GAP-FORENSIC-001 (CRITICAL/OPEN) is the visible symptom. User directives: heal the **system** that allowed this, make the process **repeatable for the next Python product** (as a skill), run the healed system on the same data set to verify, **no PyPI push**. Decisions confirmed: scope = **all 26 formats** (20 matrix + ipynb, mtlx, nrrd, safetensors, ubl, xliff); staleness policy = **FAIL on stale**.

---

## Diagnosis: Symptoms vs Root Causes vs Structural Weaknesses

**Symptoms (visible):**
- 19/20 formats lack install proof; GAP-FORENSIC-001 OPEN
- `pyrel_g4` (Install Verification) `not_implemented` even for fods ([format-registry.yaml:317](registry/format-registry.yaml#L317))
- `test_package_install_proof_wave1.py` docstring claims "after pip install" but tests `sys.path` imports — fake proof masking the gap

**Root causes (mechanisms):**
- RC-005 (already registered): oracle results and `feature-proof-register.yaml` are audit-only; proof level 4 defined, consumed by nothing — `check_continuation.py` and all 221 validators have zero references
- Closest validator (V138 consumer-proof) is `blocks_sprint: False` — enforcement was designed WARN-only
- Proof was manual, per-format, multi-step → O(N) effort that predictably never happened fleet-wide

**Structural weaknesses (why it will recur without redesign):**
1. **Write-only registers**: the system repeatedly creates data artifacts (proof register, transcripts, gates) with no consumer. Enforcement is presumed, never wired.
2. **No proof↔source binding**: existing proof reports (r132/r133 fods) carry no source hash. Nothing invalidates proof when `src/python/<fmt>/` changes → *this is what breaks consistency across reruns*: a proof looks equally valid forever.
3. **Hardcoded fleet lists everywhere, all drifted**: wave1 test = 20, `package_install_proof.py` helper = 14, `verify_package_install.py` = 4, `build-local-packages.py` duplicates matrix deps in local dicts. Meanwhile `src/python/` has **26** formats — the 6 newest have no matrix entry, no wheel, no proof path. The "next product" failure has already happened 6 times.
4. **Ad-hoc proof locations** (`reports/r<N>/`, `reports/skills-r<N>/`): every run writes somewhere new; no canonical "current proof" a validator could check; no machine-readable manifest.
5. **Nondeterministic replay**: manual sequence (build→venv→install→test→report→register) diverges each replay; tool versions unpinned.

**Preserve (works, don't touch behavior):** `build-local-packages.py` build mechanics + hatchling template + no-publish stance; oracle layer + sample corpus (reused as smoke corpus); `feature-proof-register.yaml` level 0–5 schema; the `@validator` framework (V172–V175 precedent); `/package-install-proof` skill identity + its transcript JSON schema; wave1 test as a fast in-repo import check (relabeled honestly).

**Redesign:** fleet definition (hardcoded → matrix-derived), proof execution (manual → one governed command), proof storage (ad-hoc → canonical + machine-readable + source-bound), enforcement (none → blocking validator with freshness), register updates (hand-edited → machine-written).

---

## The Durable Design

**Single source of truth:** `packaging/python/package-matrix.yaml` becomes the only fleet definition. Each entry gains an additive `install_proof:` block:

```yaml
  install_proof:
    smoke_module: fods.parser          # import path inside installed wheel
    smoke_callable: parse_fods_strict
    smoke_sample: samples/by-format/fods/minimal-spreadsheet.fods   # or smoke_inline_bytes for zst
    expected: dict                      # minimal type/shape assertion
```

Everything downstream — build script, orchestrator, proof test, validator — reads the matrix. Onboarding the next Python product = one matrix entry; the drift validator makes omission a blocking failure, not a silent gap.

**Proof freshness:** each proof records `wheel_sha256` + `source_digest` (deterministic content hash of `src/python/<fmt>/`, sorted walk, excluding `__pycache__`/egg-info; includes `src/python/_shared/` if the format imports it) + python version + timestamp. Validator recomputes digests; mismatch ⇒ STALE ⇒ FAIL for that format. Re-proof is scoped: `--format <id>` (~1–2 min).

**Canonical proof location:** `reports/package-install-proof/proof-manifest.json` (machine-readable, one entry per format) + `proof-report.md` (human) + per-format transcript JSONs (existing schema from `reports/skills-r1080/skill-transcripts/package-install-proof-ndjson.json`). History via git; no more per-run `r<N>` scatter.

---

## Implementation Phases

### Phase 0 — Baseline capture
Run the full governance validator suite and record the green count (expect 221) and current junit state. This is the regression reference.

### Phase 1 — Matrix as single source of truth
1. Add `install_proof:` blocks to all 20 existing matrix entries (APIs/samples verified during exploration — abw:`abw_codec.load`, csv:`csv_parser.parse_csv_strict`, dif:`dif_parser.parse_dif`, fodg/fodp/gnumeric:`*_codec.load`, fods:`parser.parse_fods_strict`, fodt:`parser.parse_fodt_strict`, ndjson:`ndjson_codec.load_ndjson`, ods/odt/pbm/pgm/ppm/qoi/tsv/xcf:`*_parser.parse_*_strict`, sylk:`sylk_parser.parse_sylk`, toml:`toml_codec.load_toml`, zst:`zst_codec.compress_bytes` inline `b"hello"`)
2. Add 6 new matrix entries: **ipynb, mtlx, nrrd, safetensors, ubl, xliff** — copy deps/metadata from their in-tree `src/python/<fmt>/pyproject.toml`; derive smoke spec from each codec's public API + `samples/by-format/<fmt>/valid/`; verify each at execution by reading the codec
3. Refactor `build-local-packages.py` to read `description`/`dependencies` from the matrix instead of its hardcoded `PACKAGE_DESCRIPTIONS`/`PACKAGE_DEPS` dicts (removes a drift source). **Regression control:** rebuild the original 20 and diff wheel content lists + metadata against pre-refactor artifacts before adding the 6.
4. Pin proof-env tooling in `packaging/python/proof-requirements.txt` (pytest, zstandard, any deps of the 6 — pinned versions for rerun determinism)

### Phase 2 — Orchestrator + real proof test
- **`tools/run_package_install_proof.py`** (CREATE): `--all` | `--format <id>`. Pipeline: build wheels (matrix-driven) → recreate ephemeral venv `.local/package-install-proof-venv/` (project `.venv` is disqualified: its editable `.pth` installs would shadow wheels and fake the proof) → install `proof-requirements.txt` then `pip install --no-deps` each wheel → run proof test with proof-venv pytest, `FF_REPO_ROOT` env, junit to `.local/package-install-proof-results.xml` → write manifest/report/transcripts → machine-update `feature-proof-register.yaml` proof levels from actual verdicts. Exit 0 only if all requested formats PASS.
- **`tests/python/packaging/test_package_install_proof_all_formats.py`** (+`__init__.py`) (CREATE): parametrized from the matrix (no hardcoded fleet). Per format: `test_wheel_import` (module imports AND `__file__` resolves into proof-venv site-packages, not `src/python/` — proves wheel origin) and `test_api_smoke` (spec-driven call on the same sample corpus the oracle verified). CSV stdlib shadow is contained to the ephemeral venv; test asserts `csv.csv_parser` exists.

### Phase 3 — Enforcement validator
- New `validate_package_install_proof_coverage` in `tools/supervisor/governance_validators_ext4.py` (`@validator` pattern, model V172 at line 954; pick next free rule ID at execution — V224 is taken). Checks, all blocking:
  - **Drift**: every `src/python/<fmt>/` with a `pyproject.toml` (excluding `_shared`, egg-info, obligation-only formats ora/pam/xpm/zpaq) has a matrix entry with an `install_proof` spec
  - **Coverage**: every matrix format has a manifest entry with `verdict: PASS`
  - **Freshness**: recomputed `source_digest` matches manifest; mismatch ⇒ FAIL naming exactly which formats need re-proof
- Bump `_EXPECTED_VALIDATOR_COUNT` ([governance_validator_runner.py:131](tools/supervisor/governance_validator_runner.py#L131)) 221 → 222
- **`tests/supervisor/test_validate_package_install_proof_coverage.py`** (CREATE): four fixtures — pre-fix replay (19 formats level 3, no manifest) ⇒ FAIL; stale digest ⇒ FAIL; missing matrix spec (drift) ⇒ FAIL; healthy state ⇒ PASS. The pre-fix FAIL proves the healed system would have caught GAP-FORENSIC-001.

### Phase 4 — Skill as the repeatable entry point (EP-3)
- Upgrade **`.claude/commands/package-install-proof.md` to v2.0** (extend, don't duplicate — avoids `/detect-duplicate-skills` violations): fleet mode (`--all`) and per-format mode wrapping the orchestrator; canonical output paths; transcript emission; "onboarding the next Python product" section (add matrix entry → run skill → validator enforces the rest). Update changelog.
- Run `/sync-skill-command-registry` and `/validate-skill-contracts` to keep registries coherent; run `/run-skill-idempotency` against the upgraded skill.
- Fix the lying wave1 docstring (RC honesty): state it checks source-tree importability, point to the real proof test.

### Phase 5 — Run the healed system on the same data set
- `/package-install-proof --all` → build 26 wheels → prove in ephemeral venv against the oracle's sample corpus
- Expected: 26/26 PASS. Any FAIL is a genuine product defect the old system hid (likely candidates: `_shared` imports not packaged in a wheel, undeclared deps in the 6 newer formats). Fix via governed skill path (`/product-source-task`), rebuild, re-prove scoped. **Do not hand-edit the register**; if a format cannot pass, it ships as an honest FAIL in the manifest + a gap entry — no fake progress.

### Phase 6 — Verify with the healed system (regression controls)
1. New validator standalone ⇒ PASS; its unit tests: pre-fix FAIL / stale FAIL / drift FAIL / healthy PASS
2. Full validator suite ⇒ 222/222, no regressions vs Phase 0 baseline
3. **Rerun determinism check**: run the orchestrator twice back-to-back; verdicts and digests identical (only timestamps differ)
4. **Staleness live check**: touch one format's source (whitespace), validator flags exactly that format STALE, scoped re-proof clears it, revert the touch
5. Adjacent suites unregressed: `.venv/Scripts/pytest tests/python/conveyor/ tests/supervisor/acceleration/test_package_install_proof.py`

### Phase 7 — Close the loop (EP-2)
1. `forensic-gap-register.yaml`: GAP-FORENSIC-001 ⇒ CLOSED with evidence chain (wheel SHA-256 → install log → smoke → manifest → validator ID)
2. `root-cause-register.yaml`: add RC entries for the four structural weaknesses (register schema: `rc_id, title, type, status, impact, fix_options, chosen_fix, remediation_tc`); mark RC-005 fix option A partially implemented (proof wiring done; oracle→continuation wiring remains open — named residual)
3. `registry/format-registry.yaml`: fods `pyrel_g3`/`pyrel_g4` ⇒ `passed` with evidence pointer — an evidence-backed status update, NOT a gate approval (Gate 11 untouched, Babar Raza's authority)
4. Memory updates: validator count 210→222 stale fix; naming rule (self-descriptive, no opaque codes); system-healing-first expectation

---

## Files Summary

| File | Action |
|------|--------|
| `packaging/python/package-matrix.yaml` | MODIFY — `install_proof` blocks ×20, new entries ×6 |
| `packaging/python/build-local-packages.py` | MODIFY — read desc/deps from matrix (dedup) |
| `packaging/python/proof-requirements.txt` | CREATE — pinned proof-env deps |
| `tools/run_package_install_proof.py` | CREATE — orchestrator |
| `tests/python/packaging/{__init__.py, test_package_install_proof_all_formats.py}` | CREATE — matrix-driven proof test |
| `tools/supervisor/governance_validators_ext4.py` + `governance_validator_runner.py` | MODIFY — validator + count 222 |
| `tests/supervisor/test_validate_package_install_proof_coverage.py` | CREATE — 4-fixture unit test |
| `.claude/commands/package-install-proof.md` | MODIFY — v2.0 fleet mode + onboarding doc |
| `tests/python/conveyor/test_package_install_proof_wave1.py` | MODIFY — honest docstring |
| `reports/package-install-proof/{proof-manifest.json, proof-report.md, transcripts}` | GENERATED |
| `reports/spec-to-code-forensic-audit/{forensic-gap, root-cause, feature-proof}-register.yaml` | MODIFY/machine-updated |
| `registry/format-registry.yaml` | MODIFY — fods pyrel_g3/g4 evidence-backed |

No `src/` edits except via governed skills if Phase 5 surfaces product defects. No PyPI interaction (`publication_authorized: false` respected throughout).

---

## Tradeoffs, Risks, Honest Limits

- **Freshness FAIL = sprint friction**: every source-touching sprint must re-prove changed formats (~1–2 min each; full 26-fleet rebuild+proof ~15–30 min). Accepted deliberately — WARN-on-stale is the exact failure mode that produced this gap, one level up.
- **The 6 newer formats are unproven territory**: deps and API shapes assumed from in-tree pyprojects; genuine build/install failures may surface. That is the point — they'll be fixed or honestly FAILed, not skipped.
- **`_shared` coupling risk**: wheels package only `src/python/<fmt>/`; any codec importing `_shared` will fail install proof. This is a real latent packaging defect the proof is designed to expose; fix is vendoring or packaging `_shared`, decided per finding.
- **Manifest is not tamper-proof**: a file can be hand-edited to fake PASS. Mitigated (junit XML + SHA-256 chain + machine-written register) but not cryptographically strong. Named residual, not solved here.
- **Network dependency**: proof venv creation pip-installs pinned tools; fully offline reruns fail at venv setup. Optional later: local wheel cache.
- **Windows-first verification**: orchestrator uses platform-aware paths, but CI (ubuntu) behavior is untested in this effort; CI job is a follow-up, not claimed here.
- **RC-005 only partially closed**: proof-register enforcement lands; oracle→check_continuation wiring remains open and is recorded as a named residual, not silently absorbed.

---

## COMPLETION RECORD (2026-07-15)

All phases executed and verified. Status: **COMPLETE**.

| Phase | Outcome |
|-------|---------|
| 0 Baseline | 225 validators, 0 FAIL (`.local/supervisor/phase0-validator-baseline.json`) |
| 1 Matrix SSoT | 26 entries (6 onboarded: ipynb/mtlx/nrrd/safetensors/ubl/xliff), all with empirically-verified `install_proof` specs; build script dedup'd; `proof-requirements.txt` pinned |
| 2 Orchestrator+test | `tools/run_package_install_proof.py` + `tests/python/packaging/test_package_install_proof_all_formats.py` (matrix-driven, zero hardcoded fleet) |
| 3 Enforcement | V226 registered (count 225→226), blocking on DRIFT/MISSING/STALE; 6/6 unit tests incl. pre-fix replay proving GAP-FORENSIC-001 state now FAILs |
| 4 Skill | `/package-install-proof` v2.0 (fleet+scoped), registry sync PASS, wave1 fake-proof docstring corrected |
| 5 Fleet proof | **25/26 PASS.** csv = honest FAIL, a REAL defect the proof discovered (stdlib shadows the wheel module → GAP-FORENSIC-025, register-backed waiver). Converter-module wheel defect inventoried by deep-import scan → GAP-FORENSIC-026. `feature-proof-register` machine-updated: 19 formats at level 4, 6 new at level 2, csv honestly kept at 3 |
| 6 Verification | Two consecutive full runs IDENTICAL (verdicts/digests/wheel hashes); V226 standalone WARN (tracked waiver only); full suite 226 ran / 0 FAIL / 35 WARN (=baseline+waiver); live staleness drill flagged exactly the touched format; adjacent suites 27/27 |
| 7 Closure | GAP-FORENSIC-001 → CLOSED with evidence chain; RC-008..RC-011 added (RESOLVED), RC-005 marked partially resolved (oracle→continuation wiring = named residual); fods pyrel_g3/g4 → passed (evidence-backed) |

Canonical evidence: `C:\Users\prora\OneDrive\Documents\GitHub\format-factory\reports\package-install-proof\proof-manifest.json`

Named residuals (tracked, not silently absorbed):
- GAP-FORENSIC-025: csv import-rename product decision (PYREL-001 amendment)
- GAP-FORENSIC-026: converter modules unimportable from wheels (repo-layout imports)
- RC-005 remainder: oracle→check_continuation wiring
- CI job (ubuntu) for the proof orchestrator — follow-up, Windows-verified only


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-15T17:43:26.471681+00:00"
  locked_by: "3b723cdf94ae"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

---

## CONVERGENCE ADDENDUM (2026-07-16) — Post-Closure Audit, Hardening, Re-Execution, Re-Verification

Amendment appended in place per this repo's "amend, don't overwrite history" convention. The
COMPLETION RECORD above and the terminal-lock marker are preserved unchanged. This addendum
documents a governed post-closure convergence pass (audit -> harden -> execute -> reverify)
run against this plan's own closure evidence, using `.supervisor/prompts/prompt1-3` and the
`tools/supervisor/post_sprint_loop_controller.py` supervisor. Full evidence bundle:
`.local/evidences/gap-forensic-001-convergence/`.

**Audit (Stage 1) found 4 real issues**, none requiring architectural rework:

| Issue | Severity | Blocker | Finding |
|---|---|---|---|
| GAP-CONV-001 | MEDIUM | yes | GAP-FORENSIC-025/026 were registered with `remediation_tc: null` — no taskcard existed, violating this repo's EP-2 lifecycle rule |
| GAP-CONV-002 | LOW | no | `root-cause-register.yaml` summary rollup text was stale (didn't account for RC-008..RC-011) |
| GAP-CONV-003 | HIGH | yes | Live re-invocation of V226 returned **FAIL, blocks_sprint=true**: 6 of the 26 onboarded formats (ipynb, mtlx, nrrd, safetensors, ubl, xliff) were STALE — concurrent agent work had changed their source since the 2026-07-15T17:36:29Z proof run. This is RC-009's freshness design firing correctly under real, non-synthetic drift, not a defect. |
| GAP-CONV-004 | LOW | no | V226 import failure is caught and silently appended to `_skipped_validators` rather than hard-failing the suite — a latent path back toward GAP-FORENSIC-001's original failure mode if it ever regresses |

**Hardening (Stage 2):** created 5 taskcards under
`plans/.claude/parallel-nibbling-dongarra-taskcards/`: `TC-GAP-CONV-002`, `TC-GAP-CONV-003`
(both executed this session), `TC-GAP-FORENSIC-025`, `TC-GAP-FORENSIC-026` (deferred —
genuinely out-of-scope follow-up work: a breaking product naming decision and a 14-format
import-path fix respectively), `TC-GAP-CONV-004` (deferred, non-blocking hardening item).
`forensic-gap-register.yaml`'s `remediation_tc` fields for GAP-FORENSIC-025/026 now point to
real taskcards instead of `null`.

**Execution (Stage 3):**
- Fixed `root-cause-register.yaml`'s stale summary rollup (`agent_owned_remediations: 6` ->
  `10`, added RC-008..011 to `remediation_tc_mapping` and a presence check to `negative_controls`).
- Ran `python tools/run_package_install_proof.py --format ipynb --format mtlx --format nrrd
  --format safetensors --format ubl --format xliff` -> **6/6 PASS**, `proved_at:
  2026-07-16T06:12:37Z`.

**Re-verification:** live re-invocation of `validate_package_install_proof_coverage()`
flipped from `FAIL/blocks_sprint=true` to **`WARN, blocks_sprint=false`**
("25/26 packages have fresh passing install proof; known failures under gap-register waiver:
csv (waived: GAP-FORENSIC-025)"). Confirmed V226's registration in the actual
`governance_validator_runner.py` entry point is intact and unaffected by concurrent-agent
additions of V227-V231 in the same file. Regression check:
`test_validate_package_install_proof_coverage.py` (6/6) +
`test_package_install_proof_wave1.py` (4/4) = 10/10 PASS, no regressions.

**Classification:** `post_sprint_loop_controller.py --classify` returned
`STRUCTURED_ALL_GREEN` / `ACCEPTED_ALL_GREEN` (confidence 1.0) against the Stage 3 output.

**Named residual, explicitly not claimed as resolved:** freshness is a live, time-bound
property (RC-009) — any future sprint touching `src/python/<fmt>/` must re-run the scoped
proof for that format before the fleet can be called green again. This addendum does not
claim the fleet will *stay* green; it claims it *was verified* green at 2026-07-16T06:12:37Z
plus the pre-existing governed csv waiver.

Convergence verdict: **CONVERGENCE_COMPLETE_ALL_GREEN_AND_TASK_CLOSED** (see
`.local/evidences/gap-forensic-001-convergence/` for the full stage1/2/3 evidence bundle).

---

## PLAN FILE HARDENING (2026-07-16)

This section makes the plan file itself the governance artifact — no unresolved item below
is prose-only; every one has a taskcard with full fields, an owner, and a closeout rule.
Everything above this line (COMPLETION RECORD, terminal-lock marker, Convergence Addendum)
is preserved unchanged as history.

### 1. Plan File Hardening Change Log

| Date | Event | Trigger / Source |
|---|---|---|
| 2026-07-15 | Plan executed and closed (COMPLETION RECORD) | User plan approval; Phases 0-7 executed |
| 2026-07-16 (AM) | Convergence Addendum: post-closure audit found 4 issues, 2 executed, 2 taskcarded-deferred | User directive "POST-PLAN AUTONOMOUS CONVERGENCE AND GOVERNED CLOSURE" |
| 2026-07-16 (PM) | This Plan File Hardening block: restructured audit/taskcard content into 13 named sections directly in the plan file | User directive "PLAN FILE HARDENING MODE" |

### 2. Audit Findings Incorporated

Source: `.local/evidences/gap-forensic-001-convergence/stage1-issue-model.json`.

| ID | Severity | Blocker | Finding | Resolution |
|---|---|---|---|---|
| GAP-CONV-001 | MEDIUM | yes | GAP-FORENSIC-025/026 registered with `remediation_tc: null` — no taskcard, violating EP-2 | RESOLVED — taskcards TC-GAP-FORENSIC-025/026 created and linked |
| GAP-CONV-002 | LOW | no | `root-cause-register.yaml` summary rollup stale (omitted RC-008..RC-011) | RESOLVED — see TC-GAP-CONV-002 |
| GAP-CONV-003 | HIGH | yes | Live V226 FAIL: 6 of 26 formats (ipynb, mtlx, nrrd, safetensors, ubl, xliff) STALE from concurrent source edits post-proof | RESOLVED — see TC-GAP-CONV-003 |
| GAP-CONV-004 | LOW | no | V226 import failure silently swallowed into `_skipped_validators` instead of hard-failing | OPEN — see TC-GAP-CONV-004 |
| GAP-FORENSIC-025 | HIGH | n/a (out of scope) | csv wheel unimportable — stdlib `csv` always shadows it | OPEN — see TC-GAP-FORENSIC-025 |
| GAP-FORENSIC-026 | MEDIUM | n/a (out of scope) | 16 submodules / 14 formats use repo-relative imports, break in real wheel installs | OPEN — see TC-GAP-FORENSIC-026 |

### 3. Resolved / Preserved Work

**Preserved untouched:** the original Phase 0-7 COMPLETION RECORD above remains the authoritative
record of GAP-FORENSIC-001's core closure (25/26 formats proven, V226 enforcement wired, RC-008..011
resolved). This hardening pass does not reopen or restate that closure.

**Resolved by this hardening pass:**
- `TC-GAP-CONV-002` — `root-cause-register.yaml` summary rollup fixed (`agent_owned_remediations: 6` -> `10`, RC-008..011 added to `remediation_tc_mapping` and `negative_controls`). Evidence: direct file diff, re-read confirmed consistent.
- `TC-GAP-CONV-003` — 6 stale formats re-proved via `python tools/run_package_install_proof.py --format ipynb --format mtlx --format nrrd --format safetensors --format ubl --format xliff` -> 6/6 PASS at `2026-07-16T06:12:37Z`. Evidence: `reports/package-install-proof/proof-manifest.json`, live V226 re-invocation flipped FAIL->WARN.

### 4. Unresolved Work Register

| Taskcard | Status | Priority | Lane Owner | Why still open |
|---|---|---|---|---|
| `TC-GAP-FORENSIC-025` | `blocker` | HIGH | `agent_owned_after_naming_decision` | Requires a deliberate, breaking product-naming decision — not mechanical, not a TRUE_EXTERNAL_GATE, but deliberately out of this convergence's scope |
| `TC-GAP-FORENSIC-026` | `follow_up` | MEDIUM | `agent_owned` | 14-format import-path fix — real work, genuinely out of GAP-FORENSIC-001's scope (proof-machinery closure, not every defect the proof found) |
| `TC-GAP-CONV-004` | `follow_up` | LOW | `agent_owned` | Forward-looking hardening; V226 currently runs correctly, so this is preventive, not corrective |

### 5. Taskcard Register

**TC-GAP-CONV-002** — Fix stale summary rollup in `root-cause-register.yaml`
- Source audit finding: GAP-CONV-002 / `stage1-issue-model.json#issues[1]`
- Why it matters: a rollup that drifts from its own detail entries is misleading to future readers/auditors
- Status: `completed_verified` | Priority: LOW | Lane owner: `agent_owned` (convergence_controller)
- Required work: update `agent_owned_remediations` count and `remediation_tc_mapping` to include RC-008..RC-011
- Required verification: direct re-read confirms rollup text matches detail entries
- Required evidence: before/after diff of the summary block (applied, see commit `cb52f2c7`)
- Acceptance criteria: summary references RC-008..RC-011 by ID+status; `total_root_causes` matches actual RC-* entry count
- Stop conditions: none triggered
- Allowed paths: `reports/spec-to-code-forensic-audit/root-cause-register.yaml` | Forbidden paths: `src/**`
- Dependencies: none
- Closeout rules: close when diff applied and re-read confirms consistency — **CLOSED**
- Validation command run: `grep -c 'rc_id:' reports/spec-to-code-forensic-audit/root-cause-register.yaml` -> 11, matches `total_root_causes: 11`

**TC-GAP-CONV-003** — Re-prove the 6 formats whose install-proof went STALE
- Source audit finding: GAP-CONV-003 / `stage1-issue-model.json#issues[2]`
- Why it matters: fleet cannot be honestly called green while 6/26 formats' proof is time-decayed
- Status: `completed_verified` | Priority: HIGH | Lane owner: `agent_owned` (convergence_controller)
- Required work: `python tools/run_package_install_proof.py --format <fmt>` for each of the 6 formats
- Required verification: live re-invocation of `validate_package_install_proof_coverage()` shows no STALE for these 6
- Required evidence: `reports/package-install-proof/proof-manifest.json` entries dated `2026-07-16T06:12:37Z`, verdict PASS; live V226 result FAIL->WARN
- Acceptance criteria: all 6 formats PASS with fresh `source_digest`; live V226 no longer lists them under STALE
- Stop conditions: if any format still fails for a non-staleness reason, reroute to `product_source_task` lane (not triggered — all 6 passed cleanly)
- Dependencies: none
- Closeout rules: close when live V226 re-check is clean for these 6 formats — **CLOSED**
- Validation command run: `python tools/run_package_install_proof.py --format ipynb --format mtlx --format nrrd --format safetensors --format ubl --format xliff` -> `RESULT: 6/6 PASS`

**TC-GAP-FORENSIC-025** — Resolve csv wheel/stdlib module-name collision
- Source audit finding: `reports/package-install-proof/proof-manifest.json` csv verdict FAIL
- Why it matters: `format-factory-csv` installs as top-level `csv`, which stdlib `csv` always shadows — the wheel is dead code in any real environment
- Status: `blocker` | Priority: HIGH | Lane owner: `agent_owned_after_naming_decision` (product_source_task)
- Required work: breaking naming change (e.g. rename the installed package/import path) decided via the governed `product-source-task` skill — not mechanical
- Required verification: re-run `tools/run_package_install_proof.py --format csv` after the rename; verdict must flip to PASS
- Required evidence: updated `proof-manifest.json` csv entry with verdict PASS
- Acceptance criteria: naming decision recorded via a governed skill invocation; csv package importable in an ephemeral venv without stdlib collision
- Stop conditions: do not silently rename without recording the decision and its rationale
- Allowed actions: invoke `/product-source-task` to scope and execute the rename | Forbidden actions: ad hoc rename outside the governed skill; waiving the gap without a recorded decision
- Dependencies: none
- Closeout rules: close only after the naming decision ships and re-proof confirms PASS — **OPEN**
- Full taskcard: `plans/.claude/parallel-nibbling-dongarra-taskcards/TC-GAP-FORENSIC-025.yaml`

**TC-GAP-FORENSIC-026** — Fix repo-relative imports in `*_to_csv` converter submodules across 14 formats
- Source audit finding: `reports/package-install-proof/proof-manifest.json` `deep_import.failing_modules`
- Why it matters: 16 submodules across 14 formats use `from src.python...` imports that break under a real wheel install — dead code for any real consumer
- Status: `follow_up` | Priority: MEDIUM | Lane owner: `agent_owned` (product_source_task)
- Required work: convert each affected module's imports to package-relative or installed-package-absolute imports
- Required verification: `tools/run_package_install_proof.py` deep-import scan shows zero `failing_modules` for all 14 formats
- Required evidence: updated `proof-manifest.json` with empty `deep_import.failing_modules` per format
- Acceptance criteria: all 16 submodules importable from a wheel install; no regression in existing in-repo test suites
- Stop conditions: none defined yet — first violation becomes a stop condition at execution time
- Allowed actions: import-path edits inside the 14 formats' converter submodules | Forbidden actions: excluding modules from wheels as a silent workaround without a recorded decision
- Dependencies: `TC-GAP-FORENSIC-025` (shares the csv-import-namespace root cause for csv-adjacent converters — not a hard blocker, but should be sequenced after)
- Closeout rules: close when the deep-import scan is clean fleet-wide — **OPEN**
- Full taskcard: `plans/.claude/parallel-nibbling-dongarra-taskcards/TC-GAP-FORENSIC-026.yaml`

**TC-GAP-CONV-004** — Make V226 import failure a hard suite-level FAIL instead of a silent skip
- Source audit finding: GAP-CONV-004 / `stage1-issue-model.json#issues[3]`
- Why it matters: a broken V226 import would silently disappear the fleet's only install-proof gate, recreating GAP-FORENSIC-001's original failure mode one layer up
- Status: `follow_up` | Priority: LOW | Lane owner: `agent_owned` (governance_hardening)
- Required work: add an explicit assertion/meta-check that V226 (and other must-not-silently-skip validators) appears in the executed results set, failing the suite loudly if not
- Required verification: simulated broken-import test proves the suite now hard-fails instead of silently skipping
- Required evidence: new unit test + suite run showing the hard-fail behavior
- Acceptance criteria: broken V226 import produces a visible suite-level FAIL, not a silent skip; existing `_skipped_validators` behavior for non-critical validators unaffected
- Stop conditions: do not change skip behavior for validators not explicitly designated must-not-skip
- Dependencies: none
- Closeout rules: close when the hard-fail test passes and does not regress other validators — **OPEN**
- Full taskcard: `plans/.claude/parallel-nibbling-dongarra-taskcards/TC-GAP-CONV-004.yaml`

### 6. Lane Ownership

| Lane | Owner Role | Taskcards | Status |
|---|---|---|---|
| `convergence_controller` | agent_owned | TC-GAP-CONV-002, TC-GAP-CONV-003 | CLOSED |
| `product_source_task` | agent_owned / agent_owned_after_naming_decision | TC-GAP-FORENSIC-025, TC-GAP-FORENSIC-026 | OPEN |
| `governance_hardening` | agent_owned | TC-GAP-CONV-004 | OPEN |

### 7. Gate Contract

- **V226** (`tools/supervisor/governance_validators_package_proof.py`, registered in `governance_validator_runner.py`): blocking governance validator. FAILs (blocks_sprint=true) on DRIFT (src package missing from `package-matrix.yaml`), MISSING (no manifest entry), or STALE (source changed since proof). WARNs (blocks_sprint=false) only for a registered, taskcarded, gap-tracked known-failure waiver (currently: csv only, via GAP-FORENSIC-025).
- **`pyrel_g3`/`pyrel_g4`** (`registry/format-registry.yaml`, fods): evidence-backed `passed`, evidence source `reports/package-install-proof/proof-manifest.json`. This is a machinery-status update, not a Gate 11 commercial-release approval (Gate 11 remains Babar Raza's sole authority, untouched by this plan).
- **Freshness gate (rule, not a bug to route around):** any change to `src/python/<fmt>/` invalidates that format's proof. V226 will FAIL for that format until a scoped re-proof (`tools/run_package_install_proof.py --format <fmt>`) is run. There is no override mechanism, and none should be added — this is RC-009's fix operating as designed.

### 8. Evidence Contract

- **Canonical proof:** `reports/package-install-proof/proof-manifest.json` (machine-readable, one entry per format: `wheel_sha256`, `source_digest`, `proved_at`, `verdict`) + `proof-report.md` (human) + `transcripts/package-install-proof-<fmt>.json` (per-format skill-transcript schema).
- **Convergence evidence:** `.local/evidences/gap-forensic-001-convergence/` — `stage1-issue-model.json`, `stage2-taskcard-contract.json`, `stage3-quality-scoring-rubric.json`, `final-all-green-candidate.json`, `close-task-result.json` (not committed, per repo `.local/` convention — regenerable, not authoritative history; the plan file and register commits are the durable record).
- **Closure rule:** no taskcard may be marked `completed_verified` without at least one `validation_commands` entry that was actually executed, with its literal output cited (not paraphrased) in the taskcard's evidence field. This plan file cites literal outputs (e.g. `RESULT: 6/6 PASS`, `grep -c` -> `11`) rather than describing them.

### 9. Verification Matrix

| Check | Command | Last Result | Timestamp |
|---|---|---|---|
| 6-format scoped re-proof | `python tools/run_package_install_proof.py --format ipynb --format mtlx --format nrrd --format safetensors --format ubl --format xliff` | `RESULT: 6/6 PASS` | 2026-07-16T06:12:37Z |
| V226 live invocation | `validate_package_install_proof_coverage({}, repo_root='.')` | `WARN, blocks_sprint=false` (was `FAIL, blocks_sprint=true` before re-proof) | 2026-07-16T06:14Z (post-fix) |
| Coverage unit tests | `.venv/Scripts/python -m pytest tests/supervisor/test_validate_package_install_proof_coverage.py -v` | 6/6 PASS | 2026-07-16 |
| Wave1 regression | `.venv/Scripts/python -m pytest tests/python/conveyor/test_package_install_proof_wave1.py -v` | 4/4 PASS | 2026-07-16 |
| Register consistency | `grep -c 'rc_id:' reports/spec-to-code-forensic-audit/root-cause-register.yaml` | 11, matches `total_root_causes: 11` | 2026-07-16 |
| V226 registration intact under concurrent edits | `grep -n "V226" tools/supervisor/governance_validator_runner.py` | import/registration block present and unaffected by concurrent V227-V231 additions | 2026-07-16 |

### 10. Repair Loop

1. V226 (or the Verification Matrix above) reports STALE or FAIL for format `X`.
2. Run `python tools/run_package_install_proof.py --format X`.
3. Re-invoke `validate_package_install_proof_coverage()` live.
4. If `X` now PASSes: done, no further action.
5. If `X` still fails for a reason **other than staleness** (a real defect, e.g. an import error): do not waive it silently. Open (or reuse) a `GAP-FORENSIC-*` register entry, create a taskcard, reroute to the `product_source_task` lane.
6. A waiver (V226 WARN instead of FAIL) is only valid when it is backed by exactly this chain: gap-register entry -> taskcard -> `known_failure` waiver in `package-matrix.yaml`. No format may be waived by editing the matrix alone.

### 11. Anti-Overclaim Rules

- Do not claim "26/26 formats pass install proof." The true, current, cite-able state is 25/26 PASS + 1 governed waiver (csv, GAP-FORENSIC-025), until `TC-GAP-FORENSIC-025` closes.
- Do not claim the fleet's proof is durably green. Freshness is a live, time-bound property (RC-009) — a claim of "green" is only valid as of the timestamp it was last verified, not as a permanent fact.
- Do not count a taskcarded item as fixed. `TC-GAP-CONV-004`, `TC-GAP-FORENSIC-025`, `TC-GAP-FORENSIC-026` are governed and owned, not resolved — governance coverage is not remediation.
- Do not treat `GAP-FORENSIC-025`/`GAP-FORENSIC-026` as blocking GAP-FORENSIC-001's own closure. They are real defects the proof system was built to discover, correctly split into their own scoped, owned follow-up work — that is the system working as intended, not an incomplete closure.
- Do not re-invoke `close-task.md` or write a new `TERMINAL_CLOSED` marker for GAP-FORENSIC-001's core scope from this hardening pass — that closure already exists and is not reopened by this section.

### 12. Closeout Criteria

- **This hardening pass** closes when: all 5 taskcards carry status + owner + evidence path (true as of this section) and every audit finding (GAP-CONV-001..004) maps to a taskcard, no prose-only recommendation remains (true as of this section). **This hardening pass is CLOSED.**
- **GAP-FORENSIC-001's core closure** (Phases 0-7, COMPLETION RECORD) is explicitly **not reopened** by this pass — it governs only the residual follow-up work surfaced by the convergence audit.
- **The 3 open taskcards** (`TC-GAP-FORENSIC-025`, `TC-GAP-FORENSIC-026`, `TC-GAP-CONV-004`) each close independently, in a future session, strictly via their own `closeout_rules` above — not by being re-described here as done.

### 13. Remaining True Blockers

**None.** No TRUE_EXTERNAL_GATE — per this repo's Supreme Directive definition (git push credentials, Gate 11 execution approval by Babar Raza, package-publication credentials) — blocks any open taskcard in this plan.

- `TC-GAP-FORENSIC-025`'s naming decision is agent-executable via the governed `/product-source-task` skill. It is deliberately scoped out of this session, not blocked by external authority.
- `TC-GAP-FORENSIC-026` and `TC-GAP-CONV-004` are ordinary agent-owned follow-up work with no external dependency.

If a future session picks up any of the 3 open taskcards, this Taskcard Register (section 5) is the complete, self-contained starting context — no other document needs to be consulted to know what to do, why, and how to verify it.
