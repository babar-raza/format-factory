---
version: "2.0"
last-updated: "2026-07-15"
phase-available: "3+"
gate-required: null
generated_by: claude
visibility: generated
---

# /package-install-proof

Prove that Format Factory Python packages install from a physical wheel and work:
build wheel → pip install into an **ephemeral venv** → import → primary-API smoke
test on the oracle-verified sample corpus. This is the B9 oracle-to-package proof
(GAP-FORENSIC-001).

## Usage

```
/package-install-proof            # full fleet (every format in package-matrix.yaml)
/package-install-proof <format>   # scoped re-proof of one format (e.g. after source change)
```

## What This Skill Does

Single command — the orchestrator handles the whole pipeline:

```
python tools/run_package_install_proof.py                # full fleet
python tools/run_package_install_proof.py --format fods  # scoped
```

1. **Build**: fresh wheels via `packaging/python/build-local-packages.py`
   (matrix-driven; descriptions/dependencies come from `package-matrix.yaml`)
2. **Isolate**: recreate the ephemeral venv `.local/package-install-proof-venv/`
   with pinned tooling (`packaging/python/proof-requirements.txt`).
   The project `.venv` is NEVER used — its editable `.pth` installs would
   shadow wheels and fake the proof.
3. **Install**: `pip install --no-deps <wheel>` per format
   (csv installs+proves in a second pass — it intentionally shadows stdlib csv)
4. **Prove**: runs `tests/python/packaging/test_package_install_proof_all_formats.py`
   inside the proof venv — wheel-origin import check + API smoke per format
5. **Record**: writes the canonical machine-readable manifest
   (wheel sha256 + **source digest** per format), the human report, per-format
   transcripts, and machine-updates `feature-proof-register.yaml`
6. **Deep-import scan** (diagnostic): inventories wheel submodules that fail
   to import (e.g. cross-format converters assuming repo layout) — recorded
   as findings, does not flip the B9 verdict

## Single Source of Truth

The fleet and each format's smoke spec live ONLY in
`packaging/python/package-matrix.yaml` (`install_proof:` block per entry).
No tool in this chain hardcodes a format list.

## Onboarding the Next Python Product

1. Add the format's entry to `packaging/python/package-matrix.yaml` including an
   `install_proof:` block (`smoke_module`, `smoke_callable`,
   `smoke_sample` | `smoke_inline_bytes`, `expected`)
2. Run `/package-install-proof <format>`
3. Done — governance validator **V226** (`validate_package_install_proof_coverage`)
   enforces the rest mechanically and BLOCKS on:
   - **DRIFT**: a `src/python/<fmt>/` package (with pyproject.toml) missing from
     the matrix or lacking an `install_proof` spec
   - **MISSING**: a matrix format with no PASS entry in the proof manifest
   - **STALE**: source changed since the recorded proof (content digest mismatch)
     → re-prove scoped: `/package-install-proof <format>`

## Outputs (canonical locations)

| Artifact | Path |
|----------|------|
| Machine-readable manifest (validator input) | `reports/package-install-proof/proof-manifest.json` |
| Human report | `reports/package-install-proof/proof-report.md` |
| Per-format transcripts | `reports/package-install-proof/transcripts/package-install-proof-<fmt>.json` |
| junit XML | `.local/package-install-proof-results-*.xml` |

## Constraints

- Must install from a physical wheel (never `pip install -e .`)
- Must verify `import <format>` resolves into the proof venv's site-packages
  (not `src/python/` — editable shadowing fails the proof by design)
- Exit code 0 only when every requested format PASSes
- If a wheel cannot be built, the orchestrator stops with the build error
- **No PyPI interaction ever** — `publication_authorized: false`

## Evidence Required

Per format in the manifest: package name, version, wheel file + sha256,
source digest, install result, import result, smoke result, verdict, proved_at.

## Allowed Paths

- `packaging/` (matrix read; wheels built under `.local/package-builds/`)
- `.local/package-install-proof-*` (ephemeral venv, workdir, junit)
- `reports/package-install-proof/` (proof output)
- `reports/spec-to-code-forensic-audit/feature-proof-register.yaml` (machine update)

## Forbidden Paths

- `src/**` (no source edits — a FAIL here is a product defect; fix via
  `/product-source-task`, then re-prove)
- `registry/format-registry.yaml` (gate authority)
- `plans/master-plan.md` (operational authority)

## Rollback

1. Proof artifacts are regenerated on every run; git-revert `reports/package-install-proof/`
2. Delete `.local/package-install-proof-venv/` (recreated on next run)
3. `pip` state is confined to the ephemeral venv — nothing to undo elsewhere

## Validation

Complete when the orchestrator exits 0 and governance validator V226 reports PASS
(run via `/run-governance-validators`).

## Transcript Requirement

The orchestrator emits per-format transcript JSONs to
`reports/package-install-proof/transcripts/` automatically (schema:
skill_id, format_id, package_name, wheel_path, wheel_sha256, source_digest,
install_result, import_result, smoke_result, verdict, generated_at).

## Related Skills

- **`/sync-installed-packages`** — fleet-level EDITABLE install audit for the
  project `.venv` (developer environment). This skill proves WHEEL installs in
  isolation; the two are complementary, not interchangeable.
- **`/product-source-task`** — the governed path to fix product defects this
  proof surfaces.
- **`/new-format-kickstart`** — when kickstarting a format, finish by adding its
  matrix entry + running this skill (see "Onboarding the Next Python Product").

## Changelog

- 1.0 (2026-06-02): Initial version
- 1.1 (2026-06-03): Frontmatter, allowed/forbidden paths, rollback (Skills R99)
- 1.2 (2026-06-03): Validation, transcript requirement (Skills R101)
- 1.3 (2026-07-04): Related Skills cross-reference to /sync-installed-packages
- 2.0 (2026-07-15): GAP-FORENSIC-001 heal — fleet mode via
  tools/run_package_install_proof.py orchestrator; matrix-driven single source
  of truth; ephemeral-venv isolation; source-digest staleness binding; canonical
  manifest consumed by blocking validator V226; onboarding contract for future
  formats; deep-import diagnostic scan.
