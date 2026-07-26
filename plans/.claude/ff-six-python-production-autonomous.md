---
artifact_id: FF-SIX-PYTHON-PRODUCTION-AUTONOMOUS
artifact_type: execution_plan
visibility: generated
generated_by: codex
generated_at: 2026-07-23
last_updated_at: 2026-07-26T04:02:09Z
mission_id: FF-SIX-PYTHON-PRODUCTION-AUTONOMOUS
status: IN_PROGRESS
lane_id: python-production
last_verified_commit: c8cb0445bc9d50c35561edfc839d470ecb390190
controller_state: VERIFY
exact_next_task: AUTO-IPYNB-PROOF-REPLAY-001
---

# Autonomous Production Program for Six Python Format Libraries

This file is the durable execution authority for the user-approved mission covering
IPYNB, OpenRaster, NRRD, XLIFF, SafeTensors, and OASIS UBL. It does not inherit
completion claims from earlier plans, reports, registries, or evidence bundles.

## Locked decisions

- Execution is non-interactive and resumes from repository state.
- Product work runs in this isolated worktree and never cleans or overwrites the shared tree.
- Technical readiness is computed from content-addressed evidence.
- Distribution imports use the implicit `format_factory.<format>` namespace.
- Python support is 3.11 through 3.14.
- UBL targets complete typed UBL 2.3 schema coverage.
- OpenRaster targets named 0.0.3 through 0.0.5 interoperability profiles.
- Human-only publication authority is not bypassed.

## Resumable controller checkpoint

This block is the authoritative restart point for this mission. Historical prose
below it provides context but cannot override these machine-oriented fields.

```yaml
checkpoint:
  captured_at: 2026-07-26T04:02:09Z
  checkpoint_reason: USER_REQUESTED
  branch: codex/ff-six-python-production
  worktree: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\worktrees\ff-six-python-production
  verified_commit: c8cb0445bc9d50c35561edfc839d470ecb390190
  mission_state: IMPLEMENT
  active_product: ipynb
  active_product_state: VERIFY
  exact_next_task:
    task_id: AUTO-IPYNB-PROOF-REPLAY-001
    skill_id: materialize-production-proof
    operation: Rebuild canonical IPYNB proof from the committed source, tests,
      immutable corpus, built wheel, dependency lock, and installed environment.
    first_input: plans/.claude/ff-six-python-production-autonomous.md
    required_start_commit: c8cb0445bc9d50c35561edfc839d470ecb390190
    resume_from_obligation: SAL-IPYNB-OBL-010C554B8692D166
    promotion_rule: Compute readiness from the rebuilt proof graph; do not reuse
      the stale legacy oracle status or manually promote the package.
  completed_taskcards:
    - TC-FF6-MACH-001
    - TC-FF6-CHASSIS-001
  in_progress_taskcards:
    - TC-FF6-IPYNB-SAFE-001
  pending_taskcards:
    - TC-FF6-NRRD-ORA-001
    - TC-FF6-XLIFF-001
    - TC-FF6-UBL-001
    - TC-FF6-RELEASE-001
  format_states:
    ipynb:
      state: VERIFY
      source_status: IMPLEMENTATION_VERIFIED
      corpus_status: REMEDIATED_AND_VERIFIED
      canonical_proof_status: REPLAY_IN_PROGRESS
      mandatory_obligation_count: 98
      current_live_proof_count: 1
      remaining_mandatory_proof_gaps: 97
      current_graph_digest: b0fc2b342aa239c3edb6473e1d965c829fc4692eb44ac359ab8ef9ffdb36bdf6
      last_accepted_proof:
        obligation_id: SAL-IPYNB-OBL-1F8C3D9742EBC830
        proof_id: PROOF-9AC3DEB63B0F324FECBFBA63ACC4655BFFE75438532B270C5047512F7D705B81
        test: tests/python/ipynb/test_obligation_corpus_integrity.py
        package_sha256: 0e9635f74b0ba850d2b811e1da062e5db5d15deb402bac9e1f288e7657fbe180
      next_obligation: Replay SAL-IPYNB-OBL-010C554B8692D166, then continue
        deterministically through the remaining compiled mandatory obligations.
    safetensors:
      state: VERIFY
      source_status: IMPLEMENTATION_VERIFIED
      canonical_proof_status: PARTIAL_NOT_CERTIFIED
      next_obligation: Resume remaining certification and release-evidence gaps
        after the IPYNB proof replay.
    nrrd:
      state: CONTRACT
      source_status: LEGACY_INPUT_NOT_PRODUCTION_CERTIFIED
    openraster:
      state: DISCOVER
      source_status: PRODUCTION_IMPLEMENTATION_NOT_STARTED
    xliff:
      state: CONTRACT
      source_status: LEGACY_INPUT_NOT_PRODUCTION_CERTIFIED
    ubl:
      state: CONTRACT
      source_status: LEGACY_INPUT_NOT_PRODUCTION_CERTIFIED
  preserved_unrelated_untracked_paths:
    - plans/strategic/autonomous-six-python-production-execution-plan.md
    - reports/skills-rff6/skill-transcripts/create-taskcard-six-python-production-plan-001.json
```

No executor may skip `AUTO-IPYNB-PROOF-REPLAY-001` in favor of additional
feature work: the last committed source change altered source, tests, fixtures,
corpus manifests, oracle inputs, and evidence receipts, so all descendant proof
must be recomputed first.

## Taskcards

### TC-FF6-MACH-001 — Canonical production control plane

**Status:** COMPLETE

skill_ids: [autonomous-loop, materialize-production-proof]

Implement the resumable mission state machine, complete-input run manifest,
content-addressed proof graph, invalidation, computed promotion, and current-gap
projection by extending the existing format-contract and requirements-authority
machinery.

**Done check**

- Focused machinery tests pass.
- Three same-input projections produce identical canonical digests.
- Mutating each input class invalidates the correct descendants.
- Presence-only evidence and prose deferrals cannot promote mandatory obligations.

**Closure evidence:** commit `dabcc732`; focused machinery verification and three
same-input deterministic controller replays recorded below.

### TC-FF6-CHASSIS-001 — Split-ready Python package chassis

**Status:** COMPLETE

skill_ids: [package-install-proof]

Implement `format-factory-core`, the implicit namespace layout, common lifecycle
contracts, diagnostics, resource policies, package build/install proof, API
compatibility checks, and repository extraction manifests.

**Done check**

- Core and a representative format build and install from wheels in isolation.
- Official `safetensors` and `pynrrd` can coexist without import shadowing.
- Source-tree imports cannot satisfy installed-wheel proof.

**Closure evidence:** commits `8c4083de` and `e4c59c4e`; reproducible core wheel
digest and isolated installed import recorded below.

## Verified checkpoints

### 2026-07-23 — control plane and production architecture

- Commit `dabcc732` introduced the atomic controller, strict ProductContract
  projection, content-addressed proof graph, transitive invalidation, computed
  promotion, and execution-manifest v2 closure.
- Three clean controller replays produced identical state digest
  `009429463058fe8d2ca325a2b79803fb6f5148a6287b6c60942f78ba446afea0`
  and gap digest
  `7d290f01a319c88369240cbc0b7f0850698e57bddaa7a25cd5d00fc5c3e57e9e`.
- Production skill routing and `KC-PYTHON-003` replace POC completion criteria
  for migrated packages. The legacy contract remains an accurate migration
  input, not the target architecture.
- The current projection contains 13 live blockers: 11 format contract/
  authority issues and two broken registered-skill command pointers. These
  remain visible and non-promoting.

### 2026-07-23 — core chassis

- `format_factory.core` uses an implicit PEP 420 parent namespace and contains
  only errors, diagnostics, locations, resource limits, protocols, and probe
  results.
- Focused core and machinery tests pass (`26 passed` at this checkpoint);
  Ruff and strict mypy pass.
- The build backend is exact-version and hash locked.
- Two clean wheel builds with `SOURCE_DATE_EPOCH=315532800` produced identical
  SHA-256
  `8926a2e22f1963a6671a4c97986b99d7b130a0fce627e952e887e019c9eb0525`.
- An isolated virtual environment imported
  `format_factory.core` from `site-packages`, not the source tree.

### TC-FF6-IPYNB-SAFE-001 — IPYNB and SafeTensors production hardening

**Status:** IN_PROGRESS

skill_ids: [format-feature-expansion, materialize-production-proof, package-install-proof]

Migrate the existing implementations into the production chassis, preserve current
working behavior with characterization tests, and close all mandatory contract,
security, differential-oracle, packaging, and documentation obligations.

**Done check**

- Both installed wheels pass their complete mandatory obligation graphs.
- Independent differential suites pass or every disagreement is explicitly resolved.
- No critical/high gap remains open.

### 2026-07-23 — SafeTensors production namespace checkpoint

- The pinned normative authority is upstream v0.8.0 commit
  `a406ca3e7a90598be0cd05a50069cb9bf5ef6ba6`; the acquired archive SHA-256 is
  `3b4bf28d71a2b1323bab6a98adbb7e92443c8ae97fb96fa4c8612b25fab4d1b3`.
- Governed SAL ingestion expanded the canonical store from 2 historical v0.4
  facts to 19 facts. The strict contract now compiles 97 obligations and has
  digest `200dd864d95a5c81d81fe0e08ad9528d3126e9039b9a808e37946d67c624999b`.
- `format_factory.safetensors` provides bounded strict parsing, duplicate-key
  rejection, complete v0.8.0 wire dtype coverage, checked shape/offset
  validation, zero-rank and empty tensors, sub-byte alignment, lazy memory
  mapping, deterministic writing, and optional framework adapters.
- The new focused suite passes 36 tests while the 233 existing alpha
  characterization tests remain green. Ruff and strict mypy pass.
- Two clean wheels are byte-identical. An isolated environment co-installed
  `format-factory-safetensors` and official `safetensors==0.8.0`; three vectors
  passed bidirectionally and F6 passed the official Rust reader.
- This is `IMPLEMENTATION_VERIFIED_NOT_CERTIFIED`: cross-platform matrices,
  sustained fuzzing, mutation, sharded-index support, SBOM, signing, provenance,
  and release certification remain open and non-promoting.

### 2026-07-26 — IPYNB implementation and corpus checkpoint

- Commits `9687fbd1` through `43f7cd46` replaced the alpha data shape with a
  typed production model, bounded lifecycle codecs, official nbformat 4.0-4.5
  schemas, explicit conversion, deterministic serialization, safe structural
  editing, typed metadata, and preservation behavior.
- The final schema-enabled wheel is reproducible with SHA-256
  `0e9635f74b0ba850d2b811e1da062e5db5d15deb402bac9e1f288e7657fbe180`.
- Commit `95855203` quarantined two legacy fixtures whose raw bytes declared
  nbformat 4.5 but lacked mandatory cell IDs. The originals remain available by
  SHA-256 under `samples/by-format/ipynb/quarantine/`; active samples are exact
  files from official `nbformat` v5.10.4 commit
  `60b6151fedcbdc9f137fb2d223eeb10c935a8378`.
- The discovered consistency defect was structural: the official Python
  implementation normalizes missing IDs on a copied object while warning,
  whereas exact schema validation rejects the original bytes. Earlier evidence
  attributed normalized validity to immutable source bytes. Corpus integrity
  tests now validate exact bytes before any loader can repair them.
- Installed-package verification passes 387 IPYNB tests; focused corpus
  verification passes 98 tests; Ruff, YAML parsing, dependency integrity,
  receipt validation, and the exact 24-file commit boundary pass.
- The legacy IPYNB oracle package is deliberately `STALE`. This checkpoint is
  `IMPLEMENTATION_VERIFIED`, not certification: canonical proof replay is the
  next mandatory task and promotion remains computed.

### TC-FF6-NRRD-ORA-001 — NRRD and OpenRaster production implementation

**Status:** PENDING

skill_ids: [format-feature-expansion, materialize-production-proof, package-install-proof]

Harden NRRD0001-0005 and implement OpenRaster 0.0.3-0.0.5 with secure container,
payload, streaming, rendering, preservation, and interoperability behavior.

**Done check**

- NRRD attached/detached and all declared encodings pass independent validation.
- OpenRaster passes secure archive tests and two-implementation interoperability.
- Installed packages satisfy all mandatory obligations.

### TC-FF6-XLIFF-001 — XLIFF 2.0/2.1 production implementation

**Status:** PENDING

skill_ids: [format-feature-expansion, materialize-production-proof, package-install-proof]

Implement typed Core and module models, inline-code/state semantics, extension
preservation, schema/processing validation, and installed-package proof.

**Done check**

- Every mandatory XLIFF 2.0/2.1 obligation has executed positive and required
  negative evidence.
- XLIFF 2.2 remains isolated as preview-only.

### TC-FF6-UBL-001 — Fully typed UBL 2.3

**Status:** PENDING

skill_ids: [spec-parity-source-regeneration-and-migration, format-feature-expansion, materialize-production-proof, package-install-proof]

Implement a deterministic checked-in generator and typed API for all 91 UBL 2.3
document roots and common components, with validation, preservation, code-list
hooks, streaming, signatures, examples, and independent schema verification.

**Done check**

- Regeneration is byte-identical.
- All 91 root types build, import, parse, validate, and serialize from the installed wheel.
- Official examples and generated schema-valid minima pass.

### TC-FF6-RELEASE-001 — Independent repositories and release readiness

**Status:** PENDING

skill_ids: [package-install-proof, materialize-production-proof]

Extract independent repositories, rerun certification, build reproducible artifacts,
generate SBOM/provenance/signatures/docs, and publish only when credentials and
required external authority already exist.

**Done check**

- Extraction preserves canonical source and contract digests.
- Linux, Windows, and macOS Python 3.11-3.14 matrices pass.
- Each package reaches computed `RELEASE_CANDIDATE` or records only a true external
  publication block after all technical work is complete.

**Known skill gap:** no active registered skill currently owns manifest-driven
independent-repository extraction. Before the first extraction mutation, execute
the repository's missing-skill workflow: record the recurring capability, extend
or create the smallest production extraction skill, register it, test it,
prove idempotency, and then use it. `package-install-proof` and
`materialize-production-proof` do not authorize repository creation by
themselves.

## Autonomous failure policy

- Retry transient failures with bounded backoff and official cached fallbacks.
- Repair deterministic regressions and rerun affected descendants.
- Quarantine invalid fixtures without deleting their history.
- Record oracle contradictions and add discriminating tests.
- After three materially different failed repairs for the same root cause, mark that
  obligation technically blocked and continue other taskcards.
- Never convert missing evidence into a waiver.

## Prose Findings Disclosed

- The shared worktree began with 1,782 changes and 23 pre-existing coordination
  conflicts; this mission therefore executes in an isolated worktree.
- Existing product and oracle status labels are historical inputs, not certification.
- OpenRaster source and its canonical format contract were absent at mission start.
- SafeTensors had an untracked contract in the shared worktree but none at the pinned
  clean commit; it must be rebuilt from authority rather than silently copied.
