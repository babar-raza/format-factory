---
artifact_id: FF6-ACTIVE-WORK-CHECKPOINT-001
artifact_type: provider_neutral_work_checkpoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
canonical_event: FF6-EVENT-000014
---

# Active Work Checkpoint: Authority Closure

This file is the exact provider-shift boundary inside
`TC-FF6-AUTHORITY-CLOSURE-001`. It separates tested work from pending work so
the next executor continues the same change set instead of restarting,
parallelizing a competing design, or inferring completion from file presence.

The canonical state is still the GitLab commit containing controller event 14,
the controller projection, event journal, and taskcard. This file is a derived
explanation.

## Checkpoint identity

| Field | Value |
|---|---|
| Mission | `FF6-PRODUCTION-LIBRARIES-001` |
| Program state | `CONTRACT` |
| Parent task | `TC-FF6-PROGRAM-CAPABILITIES-001` — `NEEDS_REPAIR` |
| Active task | `TC-FF6-AUTHORITY-CLOSURE-001` — `WORK_IN_PROGRESS` |
| Controller event | `FF6-EVENT-000014` |
| Event hash | `399a5069b3c843d1b4f668a8f7abeb0deffe40a234a584f6c9f7b5b3a3e70fc8` |
| Product source mutation | Prohibited |
| Promotion/certification effect | None |
| Canonical forge | GitLab `origin/main` |
| GitHub use for mission | Prohibited |

## The production problem being repaired

### Symptoms

- Six contracts contain `acquisition_status: ACQUIRED`.
- A clean checkout has none of the 11 declared external authority artifacts.
- Four `PRODUCT_REQUIREMENT` sources previously had no path or digest.
- Capability compilation could be made to continue with an authority override.
- Mutable prose URLs can change while old evidence remains apparently valid.

### Root causes

1. Acquisition labels were stored as state instead of recomputed from bytes.
2. Fetch locators, versions, expected digests, legal classification, cache
   policy, and materialized paths were not one atomic contract.
3. Ignored `.local` bytes were dependencies but were absent from the tracked
   dependency closure.
4. Internal product requirements masqueraded as acquired sources without a
   canonical tracked document.
5. Contract compilation and capability compilation did not consume the same
   live materialization verdict.
6. Existing acquisition implementations overlap: the spec cache, source
   researcher, and specification authority layer each own only part of the
   lifecycle.

### Structural decision

Extend `research-format-contract-sources` as the single acquisition owner. Do
not add a third authority subsystem.

The durable chain is:

```text
tracked authority-lock.yaml
  -> schema and semantic validation
  -> legal decision and immutable locator
  -> content-addressed local cache
  -> digest-verified materialized path
  -> live MATCH/MISSING/MISMATCH/UNDECLARED/LEGAL_BLOCKED result
  -> strict ProductContract compilation
  -> capability-manifest dependency closure
```

Contract `acquisition_status` remains a declaration for compatibility. It
never proves readiness.

## Completed implementation

### `tools/format_contract/authority_lock.py`

Implemented:

- LF-stable SHA-256 helpers.
- repository-relative path containment with traversal rejection;
- JSON Schema validation and semantic validation;
- duplicate source/path rejection;
- URL, ZIP-member, and local-file consistency rules;
- deterministic lock-to-research source projection;
- deterministic merge that preserves reviewed research metadata;
- deterministic generation/checking of tracked `PRODUCT_REQUIREMENT`
  documents;
- atomic replacement of generated internal documents.

Verified LF-normalized digest:
`b81473e6902523115188bfa8a40e16042a441a0d99ad1e0193acc1b8701ad6a1`.

### `tools/format_contract/authority_runtime.py`

Implemented:

- local content-addressed cache at
  `.local/format-contracts/authority-cas/sha256/<prefix>/<digest>`;
- streamed SHA-256 and `max_bytes` enforcement;
- per-source timeout;
- fallback across declared HTTPS locators;
- digest-before-placement;
- preservation of an existing target after download mismatch;
- offline replay from verified CAS bytes;
- ZIP-member extraction with member-size and compression-ratio limits;
- live materialized-byte audit;
- lock-versus-contract declaration audit;
- the five required result states.

Verified LF-normalized digest:
`d65976979d52282e3204402d1f2b818620834c1cf10a6ca0180ea390d3d1cfd3`.

Known incomplete security properties:

- redirect count is not yet explicitly capped; `urllib` default behavior is
  insufficient for the taskcard acceptance rule;
- atomic temp names for direct copies use the process ID and need a
  same-process concurrent-writer test or unique-file repair;
- ZIP handling needs explicit archive-entry count and aggregate expansion
  limits if later used for more than a named member;
- HTTP status/content-type are not yet recorded in materialization evidence;
- URL allowlisting is schema-shaped (`https://`) but has no host policy.

Do not claim the materializer production-complete until those are resolved or
explicitly scoped with proof.

### `tools/format_contract/authority_materializer.py`

Implemented deterministic CLI subcommands:

```powershell
python -m tools.format_contract.authority_materializer `
  --repo-root . sync-product-requirements `
  --format ipynb --format nrrd --format xliff --format ubl

python -m tools.format_contract.authority_materializer `
  --repo-root . materialize --online

python -m tools.format_contract.authority_materializer `
  --repo-root . materialize

python -m tools.format_contract.authority_materializer `
  --repo-root . audit --contracts
```

The command emits canonical JSON without timestamps and returns nonzero when
the closure is not ready.

### Shared schema

`schemas/format-contracts/authority-lock.schema.json` defines:

- stable source identity and format identity;
- authority class;
- expected SHA-256 and media type;
- legal license/redistribution/use/evidence fields;
- byte and timeout limits;
- HTTPS URL, ZIP member, and local-file acquisition records.

Verified LF-normalized digest:
`334738cbba75243514b95f3e0091e0ce8fe7611f61b7524cf3e8748eea73cdfc`.

### Internal product requirements

The following generated artifacts are tracked, deterministic, and explicitly
non-spec:

| Path | Source ID | LF SHA-256 |
|---|---|---|
| `shared/format-contracts/product-requirements/ipynb.yaml` | `SRC-NB-003` | `903b5e9c4d3f371105d209794221a342ee676f4bd5f36dc15c3ddacb7ceadccd` |
| `shared/format-contracts/product-requirements/nrrd.yaml` | `SRC-NRRD-003` | `4731be2f44166596980728c57750b9bcfea6c8f0d0e9603b406374112cc202d3` |
| `shared/format-contracts/product-requirements/xliff.yaml` | `SRC-XLF-003` | `fde62d8a1310e9cac9608e44530d2cd4b23cd67386f0a9fe64a9ff79eb54b893` |
| `shared/format-contracts/product-requirements/ubl.yaml` | `SRC-UBL-003` | `07d380f7d0b3bb973f4ca223946a4fff5f1e116f98548d036a2322483dc1fa4c` |

SafeTensors and OpenRaster have no `PRODUCT_REQUIREMENT` source in the current
15-source contract inventory; do not synthesize one to make counts uniform.

### Tests and static gates

Executed at this checkpoint:

```text
python -m pytest tests/format_contract/test_authority_materializer.py -q
6 passed

python -m ruff check <three authority modules> <focused test>
All checks passed

python -m mypy <three authority modules> --ignore-missing-imports
Success: no issues found in 3 source files

python -m pyright <three authority modules>
NOT RUN: pyright is not installed in the current interpreter
```

The six tests prove:

1. online acquisition followed by offline CAS replay;
2. failed digest never overwrites existing materialized bytes;
3. path traversal and unknown ZIP container fail closed;
4. internal requirement generation is deterministic and checkable;
5. lock merge preserves reviewed metadata;
6. undeclared contract sources are reported.

They do not prove real-network acquisition, redirect limits, concurrent
writers, all 15 lock records, or compiler integration.

## Primary-source investigation already completed

These are research findings, not yet the canonical lock. The next agent must
reverify before writing and record legal evidence in the lock.

### IPYNB

- Contract source: `SRC-NB-002`.
- Pinned Jupyter nbformat commit archive:
  `https://github.com/jupyter/nbformat/archive/60b6151fedcbdc9f137fb2d223eeb10c935a8378.tar.gz`.
- Observed archive SHA-256 matches the contract:
  `4d3750b55006e92d8063a6ac427a84eb1f91c44e376d90de53d03893674991d9`.
- Upstream license observed at the same commit: BSD-3-Clause.
- `SRC-NB-003` now resolves to the tracked internal artifact above.
- `SRC-IPYNB-004` exists in research as a URL-only secondary record but is not
  one of the 15 canonical contract dependencies. Do not silently add it to the
  promoting denominator.

### OpenRaster

The current wiki URLs and contract hashes are mutable-page identities. A
pinned official KDE OpenRaster documentation repository was found:

- repository: `https://invent.kde.org/documentation/openraster-org.git`;
- pinned 0.0.5 commit:
  `f050b99fa8af44cb4cc3c9d842d25097458765f6`;
- raw base:
  `https://invent.kde.org/documentation/openraster-org/-/raw/f050b99fa8af44cb4cc3c9d842d25097458765f6/`.

Candidate pinned members:

| Source | Member | SHA-256 |
|---|---|---|
| `SRC-ORA-001` | `baseline/baseline.rst` | `bd584b4b998df16c735bc3ce575e382569a101427fd4c4be14b677d30d210613` |
| `SRC-ORA-002` | `baseline/file-layout-spec.rst` | `a9f2cb90009e3cc76883ab9db2f43607a9518e723b9d03f1aa1b150f2c2e546a` |
| `SRC-ORA-003` | `baseline/layer-stack-spec.rst` | `29c77a95396c8c245d259b349fa438e3b40019d7fe6f7e06b8520c2fc9f63a49` |

The repository did not expose an obvious authority-document license during the
completed investigation. Until primary legal evidence is found, use
`LOCAL_CACHE_ONLY`/approved local reference and do not commit the external
bytes. Do not carry the mutable wiki digests into the lock merely to avoid a
contract update.

### NRRD

- `SRC-NRRD-001` and `SRC-NRRD-002` currently point to HTTPS and HTTP forms of
  the same mutable Teem NRRD0005 page.
- Both currently resolve to bytes with SHA-256
  `43ca6102cc998e0191e225d7954278547d491e29b74a132b3118571d85a8b0d5`.
- HTTP redirects to HTTPS; it is not an independent authority.
- The Teem download page states NRRD0005 was added in Teem 1.9.0 and exposes
  source releases.

This is the exact unfinished research point. Next:

1. Locate an official immutable Teem release archive or pinned source revision
   containing the format specification.
2. Inspect the archive without extracting arbitrary paths.
3. Hash the complete archive and the exact normative member.
4. Confirm its license/terms from the same release.
5. Decide whether the two contract IDs intentionally represent distinct
   artifacts. If they are aliases of one byte sequence, model the alias
   explicitly or repair the duplicate contract record; do not pretend HTTP and
   HTTPS are independent evidence.
6. If no immutable official member exists, declare the mutable endpoint
   honestly (`immutable: false`), lock its current digest in the CAS, add an
   official alternate locator if available, and leave an explicit residual
   risk. Do not claim certainty.

`SRC-NRRD-003` now resolves to its tracked internal requirement document.

### XLIFF

- Release bundle `SRC-XLF-002` matched:
  `73efc952aed29a31e8a6af1f985224d49c7bb67e6691fec8c2c994aa3d3d1751`.
- The mutable prose URL for `SRC-XLIFF-001` drifted from its declared digest.
- Use release-bundle member `xliff-core-v2.1-os.html` as the immutable prose
  artifact.
- Member SHA-256:
  `fdd293f4344920dfde643c578caca94da80261dc74f75baba7215da6e6d10bc1`.
- Model `SRC-XLIFF-001` as a ZIP member of `SRC-XLF-002`.
- OASIS notice permits copying/furnishing with the required notice, but the
  exact evidence locator and redistribution decision must be recorded.
- `SRC-XLF-003` now resolves to its tracked internal requirement document.

### SafeTensors

- Contract source: `SRC-SAFETENSORS-002`.
- Pinned official commit archive:
  `https://github.com/safetensors/safetensors/archive/a406ca3e7a90598be0cd05a50069cb9bf5ef6ba6.tar.gz`.
- Observed SHA-256 matches:
  `3b4bf28d71a2b1323bab6a98adbb7e92443c8ae97fb96fa4c8612b25fab4d1b3`.
- Upstream license at the same revision: Apache-2.0.

### UBL

- Release bundle `SRC-UBL-002` matched:
  `623bef8310db4d979ff28000a96bcc56dbcdda4f6206cf094c0aa79b75817970`.
- The mutable `UBL-2.3.html` URL for `SRC-UBL-001` drifted from its declared
  digest.
- Use member `UBL-2.3.html` from the official UBL 2.3 release ZIP.
- Member SHA-256:
  `ccda3f1a2b64e6bdebfe33b2c9645423ef2f6206ac676f0937a304098d43358d`.
- Model `SRC-UBL-001` as a ZIP member of `SRC-UBL-002`.
- Record the OASIS notice/terms evidence and redistribution decision.
- `SRC-UBL-003` now resolves to its tracked internal requirement document.

## Exact pending steps

Continue in this order. Do not skip ahead to product implementation.

### A. Reconstruct and claim

1. Fetch `origin main`; verify the commit containing event 14 is the remote
   head or an ancestor.
2. Require a clean checkout of that commit.
3. Validate the event chain through event 14.
4. Register a new coordination agent for
   `TC-FF6-AUTHORITY-CLOSURE-001`.
5. Verify the previous agent is completed. If it is stale and still owns live
   leases, use governed `takeover --reason`; never release its leases directly.
6. Claim each exact path before writing.
7. Read the Codex or Claude provider adapter and execute through registered
   skills.

### B. Finish the source/legal matrix

1. Complete NRRD immutable-source investigation above.
2. Reverify every candidate byte and digest from the primary endpoint.
3. Record license identifier, terms URL, evidence URL/member, redistribution
   class, and use status for every source.
4. Keep external bytes under ignored `.local` CAS unless affirmative
   redistribution evidence justifies a tracked copy.
5. Record uncertainty; do not upgrade `LOCAL_CACHE_ONLY` based on inference.

### C. Create the canonical lock

Create `shared/format-contracts/authority-lock.yaml` with exactly the 15
canonical contract source IDs unless a separately evidenced contract repair
changes the denominator. Required IDs:

```text
SRC-NB-002
SRC-NB-003
SRC-ORA-001
SRC-ORA-002
SRC-ORA-003
SRC-NRRD-001
SRC-NRRD-002
SRC-NRRD-003
SRC-XLF-002
SRC-XLF-003
SRC-XLIFF-001
SRC-SAFETENSORS-002
SRC-UBL-001
SRC-UBL-002
SRC-UBL-003
```

For archive members, the container must itself be one of the locked URL
sources. Keep materialized paths consistent with the contracts or perform an
evidence-backed contract update in the same bounded task.

### D. Harden the materializer

1. Add a redirect handler with a configurable maximum and HTTPS-only
   post-redirect validation.
2. Replace PID-only copy temp naming with a collision-safe file.
3. Add same-process and multi-process concurrency tests.
4. Add response status/final URL/content length to local evidence without
   introducing nondeterministic canonical outputs.
5. Add negative tests for redirect excess, oversized stream, missing archive
   member, high compression ratio, duplicate materialized paths, legal block,
   mismatch preservation, and concurrent writers.
6. Keep the current passing behavior intact.

### E. Integrate one acquisition owner

Extend, do not duplicate:

- `tools/format_contract/source_researcher.py`;
- `.claude/commands/research-format-contract-sources.md`;
- `.supervisor/skill-registry.yaml` entry
  `research-format-contract-sources`.

The source researcher must load/merge locked source records without discarding
review metadata. The registered skill must own the schema, lock, runtime,
materializer, internal requirement artifacts, focused tests, and ignored CAS
outputs. Run command-registry and skill-contract synchronization only through
their registered generators and stage their exact manifests.

### F. Bind strict contract and capability compilation

1. Update `tools/format_contract/product_contract.py` so every authority class,
   including `PRODUCT_REQUIREMENT`, is verified from the lock/live bytes.
2. Make missing lock records, contract/lock differences, legal blocks,
   missing bytes, and digest mismatches fail strict compilation.
3. Remove promoting reliance on `allow_blocked_authority`; a diagnostic mode
   may remain only if explicitly non-promoting.
4. Update `tools/format_contract/stores.py` so the lock, schema, internal
   requirements, materializer code, and materialized authority digests are in
   `input_digests`.
5. Update `tools/format_contract/capability_universe.py` to consume live audit
   results rather than copying contract declarations.
6. Add invalidation tests for each new dependency category.

### G. Materialize and replay

1. Generate/check all four internal artifacts.
2. Run real online materialization for all legally usable external sources.
3. Audit all 15 sources and all six contracts; require `MATCH` only.
4. Prove offline replay without any network call.
5. Prove a fresh materialization root can be reconstructed from the tracked
   lock and official endpoints.
6. Keep cached external bytes untracked where required.

### H. Recompile and verify

1. Regenerate/reconcile six research drafts and contracts through registered
   skills.
2. Compile all six ProductContracts without an authority override.
3. Compile the capability universe three times in isolated clean roots.
4. Require byte-identical outputs and all 15 authority results `MATCH`.
5. Run focused, format-contract, production-program, SAL, event-chain,
   concurrency, static, security, and affected regression suites.
6. Preserve the known unrelated CSV idempotency baseline failure and verify it
   at the pre-change commit if it appears.

### I. Close atomically

1. Only after all acceptance criteria pass, write close intent.
2. Compute all digests and independently replay verification.
3. Append the verified close event.
4. Update taskcard/index/controller/gaps and regenerate the handover.
5. Leave the parent `NEEDS_REPAIR` for `FF6-GAP-013`.
6. Register/select the OpenRaster profile/surface repair as the next task.
7. Stage explicit owned files, precommit-check, commit, push only to GitLab
   `main`, verify the remote, then complete coordination.

## Forbidden interpretations

- Event 14 is not authority closure.
- Six focused tests are not a production materializer certification.
- Four internal documents do not make external sources available.
- Candidate source digests are not canonical until recorded in the lock and
  independently replayed.
- No product format capability was implemented in this checkpoint.
- No product moved from `UNASSESSED`.
- No release gate was approved.

## Rollback and repair

If a tracked WIP file fails:

1. Do not delete or restore it blindly.
2. Minimize the failure and identify the exact changed proof input.
3. Repair within this taskcard and rerun focused plus affected regressions.
4. If the design must change, record a new event explaining why; do not create
   a competing authority system.
5. After three materially different unsuccessful repairs for one external
   source, mark only that source technically or legally blocked and continue
   safe work on the other sources/formats.
