---
version: "1.0"
last-updated: "2026-08-01"
phase-available: "all"
gate-required: null
skill_type: "ATOMIC_SKILL"
idempotency: "The same reviewed proof-text patterns produce the same Git attributes and identical supported-checkout bytes; a second application is a no-op."
loc_budget: "Configuration-only repair plus one focused governance regression module; no product code."
test_path: "tests/governance/test_proof_checkout_identity.py"
risk_level: HIGH
created-by: SKILL-GAP-FF6-PROOF-CHECKOUT-IDENTITY-001
product_track: machinery_repair
generated_by: codex
visibility: generated
---

# /proof-checkout-identity-repair

Repair cross-platform proof identity when Git can materialize the same tracked
text object with different line endings. This skill preserves the repository's
single raw SHA-256 evidence model by making checkout bytes deterministic; it
must never add a validator fallback that accepts both raw and normalized hashes.

## Required Inputs

- `defect_id`
- `failing_commit`
- `proof_bearing_paths`
- `supported_checkout_modes`
- `binary_fixture_paths`

## When to Use

Use this skill only when clean checkouts of the same Git object produce
different proof input bytes because an applicable text/EOL attribute is absent
or contradictory. Compose it with `/test-driven-development` so a clean
checkout regression fails for the observed reason before `.gitattributes`
changes.

Do not use it for semantic serialization differences, generated-output
nondeterminism, corrupt fixtures, authority-content drift, or arbitrary
repository formatting.

## Execution

1. Pin the failing commit and reproduce the digest disagreement in isolated
   checkouts using every supported `core.autocrlf` mode.
2. Inventory the exact proof-bearing text extensions and paths consumed by the
   failing proof closure. Inventory format samples, compressed files, images,
   tensor payloads, archives, and other binary or byte-sensitive fixtures
   separately.
3. Add a RED regression that proves the current attributes leave at least one
   proof-bearing input without a deterministic LF checkout policy. Confirm the
   test reaches that assertion and fails for the observed reason.
4. Add the smallest reviewed `.gitattributes` rules that enforce
   `text eol=lf` for proof-bearing source, schemas, manifests, receipts, plans,
   and metadata. Add later `-text` overrides for byte-sensitive fixture trees
   and binary format extensions.
5. Do not add line-ending normalization, an alternate digest function, or
   "raw-or-canonical" acceptance to any proof producer or consumer.
6. Prove with temporary repositories that the same committed object produces
   identical raw bytes and raw SHA-256 under `core.autocrlf=false`, `input`,
   and `true`.
7. Prove a non-EOL content change changes the raw SHA-256, binary fixture
   attributes remain non-text, and missing inputs still fail closed.
8. Inspect `git diff --check`, `git ls-files --eol`, and `git check-attr`.
   Stage only the reviewed explicit paths; never run repository-wide
   renormalization in a shared worktree.
9. Replay the originally failing suite from a fresh detached Windows checkout.
   The replay, surrounding machinery regressions, and transcript validation
   must all pass before evidence may advance.

## Mandatory Validations

- `clean_windows_failure_reproduced`
- `test_precedes_attribute_change`
- `proof_text_checkout_is_lf`
- `binary_fixture_attributes_unchanged`
- `supported_checkout_raw_hashes_equal`
- `non_eol_tamper_changes_hash`
- `no_dual_digest_acceptance`
- `clean_detached_replay_passes`
- `shared_worktree_not_renormalized`

## Allowed Paths

- `.gitattributes`
- `tests/governance/test_proof_checkout_identity.py`
- `reports/skills-*/skill-transcripts/proof-checkout-identity-repair-*.json`

## Forbidden Paths

- `src/**`
- authority artifacts, samples, corpora, and format fixtures
- proof receipts, proof graphs, promotion records, and controller events
- digest validators or evidence consumers
- `.git/config` and contributor-global Git configuration
- repository-wide `git add --renormalize`, formatters, or generators
- human-only gate and release records

## Stop Conditions

- Stop if the observed failure is not caused by checkout byte conversion.
- Stop if a proposed rule would classify an unreviewed binary or byte-sensitive
  extension as text; add a specific `-text` override or narrow the rule first.
- Stop if GREEN would require accepting more than one digest model.
- Stop if the clean detached replay still differs after attributes are applied;
  retain the raw-hash model and investigate the next nondeterministic input.
- Never edit historical receipts to make them appear current.

## Idempotency Contract

Given the same failing commit, proof-path inventory, binary exclusions, and
supported checkout modes, this skill produces byte-identical attribute rules
and test results. Re-running it after repair makes no repository change and
reproduces the same raw hashes. Any pattern-set change starts a new governed
repair with a new RED checkout counterexample.

## Output

Write a transcript containing the pinned commit, RED and GREEN commands,
attribute inventory, explicit binary exclusions, raw hashes from each checkout
mode, tamper hash, detached replay result, changed paths, and truth boundary.
