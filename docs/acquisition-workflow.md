# Acquisition Workflow

**Document type:** Process Reference — Phase 0 Foundation
**Last reviewed:** 2026-05-04 (run014: global audit — content verified consistent with current governance)
**Authority:** This document defines the stage-by-stage acquisition workflow, reuse policy, and idempotency rules that govern how a format moves from candidate to product.

---

## Purpose

Every format that enters the format-factory system follows a defined acquisition workflow. This workflow covers: candidate identification, scoring, evidence gathering, sample acquisition, prototype development, neutral model design, oracle comparison, fuzz testing, security review, product mapping, and release preparation. Each stage produces specific artifacts. Each stage transition is gated by one of the 11 gates defined in `docs/gates.md`.

This document also defines the reuse-before-regenerate policy that governs all agent work. Agents must not repeat work that has already been done and remains valid.

---

## Stage Overview

| Stage | Gates | Key Artifacts Produced |
|---|---|---|
| 0: Candidate Identification | Pre-Gate 1 | Candidate list, informal notes |
| 1: Scoring and Acceptance | Gate 1 | Registry entry, scoring sheet |
| 2: Evidence Gathering | Gate 2 | spec-evidence.md, legal-notes.md |
| 3: Sample Acquisition | Gate 3 | Sample files, _provenance.yaml entries |
| 4: Prototype Development | Gate 4 | Prototype parser, prototype README |
| 5: Neutral Model Design | Gate 5 | neutral-model schema |
| 6: Oracle Comparison | Gate 6 | Oracle comparison report |
| 7: Fuzz Testing | Gate 7 | Fuzz report, fuzz seeds |
| 8: Security Review | Gate 8 | Security report, sign-off |
| 9: Product Mapping | Gate 9 | Tier map, delivery plan |
| 10: OSS Implementation and Release Readiness | Gate 10 | Product source, tests, release manifest |
| 11: Commercial Implementation and Release Readiness | Gate 11 | Commercial source, commercial manifest |

---

## Stage 0: Candidate Identification

A format candidate is any file format that may be worth implementing support for. Candidates can come from user research, market analysis, competitive review, or direct requests.

Candidates are NOT entered in the registry at this stage. They are informal notes or a simple list. A candidate becomes a registry entry only after it passes Gate 1 scoring.

**Idempotency rule:** Before recording a new candidate, check `registry/format-registry.yaml` for an existing entry with the same format-id. If found, update the existing entry rather than creating a duplicate.

---

## Stage 1: Scoring and Acceptance (Gate 1)

**Trigger:** A candidate is ready for formal evaluation.

**Steps:**
1. Read the scoring model in `registry/scoring/_scoring-model.md`.
2. Apply the scoring criteria to the candidate format on all seven dimensions.
3. Compute the weighted total score (out of 100).
4. Classify the format into a legal category (see `docs/legal-and-licensing.md`).
5. Create a registry entry in `registry/format-registry.yaml`. Set `gate_1.status: scored_pending_human_approval`. Leave `approved_by: null` and `approved_date: null` — these are human-only fields. If score is in the reject band or legal category is 5 or 6, set `gate_1.status: rejected` instead.
6. Record scoring rationale per dimension and weighted total in the `scoring_notes` field.
7. **Do NOT set `gate_1.status: passed`.** Gate 1 is NOT passed by the agent. The agent produces scoring evidence and requests human review. The human records the approval.
8. After human records `gate_1.status: passed` (with `approved_by` and `approved_date`), update `plans/master-plan.md` to record Gate 1 passage.

**Spec download rule for Stage 1:** Stage 1 may identify the relevant specification URL and confirm the format's legal category (required for scoring). Stage 1 does NOT download the specification. The spec URL is recorded in the registry entry for future use. Actual spec acquisition is Stage 2 work and requires Gate 1 passage plus separate explicit authorization.

**Critical rule:** Scoring is evidence for Gate 1, not approval of Gate 1. The acquisition pack (`acquisition-packs/<format-id>/`) must NOT be created until Gate 1 is human-approved AND a Phase 2 execution prompt is issued. Creating the acquisition pack is the first step of Stage 2, not Stage 1.

**Reuse rule:** If a scoring sheet already exists for this format-id, reuse it unless the format has materially changed since scoring. Check `.local/artifact-index.yaml` for a prior scoring artifact.

**Automatic rejects at Gate 1:**
- Legal Category 5 (reverse-engineered binary with no public permission): automatic reject regardless of total score.
- Legal Category 6 (blocked): automatic reject, recorded in registry with block reason.
- Legal safety score of 0 (any legal category): automatic reject regardless of total score.
- Any evidence of DRM circumvention, access-control bypass, or legally prohibited parser work: automatic reject.

---

## Stage 2: Evidence Gathering (Gate 2)

**Trigger:** Gate 1 passed.

**Spec cache check:** Before beginning evidence drafting, verify that a cached copy of the relevant specification exists at `.local/spec-cache/<format-id>/<version>/`. If the cache is missing, the agent must stop, log the missing-spec condition as a gap, and proceed only if the current execution prompt explicitly authorizes spec acquisition. A missing cache does not automatically authorize download. See `docs/specification-cache.md` for the full authorization model. Gate 2 evidence must either cite a cached spec with its metadata (SHA-256, version, source URL) or include an explicit documented rationale for why no official specification exists.

**Steps:**
1. Check spec cache. If missing and acquisition is authorized by the current prompt, acquire the spec per the authorization model in `docs/specification-cache.md`. If not authorized, log the gap and stop.
2. Create an acquisition pack directory at `acquisition-packs/<format-id>/` from the template in `acquisition-packs/_template/`.
3. Write `spec-evidence.md`: primary source URL, specification version (from cached spec), sections relevant to parsing, key data structures, encoding rules. Must cite the official specification (cached copy), not secondary sources. Record the cached spec's SHA-256 in the front matter.
4. Write `legal-notes.md`: confirm legal category, cite the specific permission grant or standard body publication, document any patent risk assessment. For Category 1 fast-path, follow the fast-path rules in `docs/legal-and-licensing.md`. Note that local caching does not imply redistribution rights.
5. Verify spec evidence: record the canonical URL, version, download date, and SHA-256 in `spec-evidence.md`.
6. Mark Gate 2 passed after human review of legal-notes.md.
7. Update `plans/master-plan.md`.

**Reference tools and cached specs:** Both reference tools (e.g., LibreOffice for ODF) and cached specs are evidence inputs for Stage 2. They are never product implementation artifacts.

**Evidence validity:** spec-evidence.md is valid as long as the spec version has not changed and the source hash matches. If the specification publishes a new version, the artifact is stale and must be refreshed.

**Reuse rule:** If `acquisition-packs/<format-id>/spec-evidence.md` already exists and is current (source hash matches, spec version unchanged), reuse it. Log `ARTIFACT_REUSED: <format-id>-spec-evidence` in the run record.

---

## Stage 3: Sample Acquisition (Gate 3)

**Trigger:** Gate 2 passed.

**Steps:**
1. Identify sample sources for the format. Preference order: (a) samples created specifically for this project (best), (b) CC0 or public domain samples, (c) CC-BY samples (attribution required), (d) CC-BY-SA samples (share-alike required), (e) Apache 2.0 / MIT samples from open-source projects.
2. Acquire a minimum set of samples covering: minimal valid file, empty file, file with all core data structures, file with edge cases relevant to the format.
3. For each sample, create a `_provenance.yaml` entry in `samples/_provenance.yaml` with: source URL, license, date acquired, attribution if required, and `provenance_status: confirmed`.
4. Place samples at `samples/by-format/<format-id>/`.
5. Assign `visibility: public` to open-licensed samples. Assign `visibility: blocked` to any sample whose license cannot be confirmed.
6. Mark Gate 3 passed after human review of all provenance entries.
7. Update `plans/master-plan.md`.

**Reuse rule:** Before acquiring a sample, check `samples/_provenance.yaml` for an existing entry with the same source URL. If found and `provenance_status: confirmed`, skip re-acquisition. Log `ARTIFACT_REUSED: <sample-id>` in the run record.

---

## Stage 4: Prototype Development (Gate 4)

**Trigger:** Gate 3 passed.

**Steps:**
1. Create a prototype directory at `prototypes/by-format/<format-id>/`.
2. Implement a minimal working parser in Python. The prototype does not need to be production-quality, but it must correctly parse the sample corpus from Stage 3.
3. Write a prototype README that documents: the approach taken, key parsing decisions, known limitations, security mitigations applied (per `docs/security.md`), and a self-assessment against the threat model.
4. The prototype must pass a basic correctness test: parse each sample in the corpus and produce a structured output without crashing.
5. Mark Gate 4 passed after human review of the prototype and README.
6. Update `plans/master-plan.md`.

**Important:** Prototype code is internal-only (`visibility: internal`). It is never promoted directly to `src/`. Product code is written from scratch, using the prototype as a design reference.

---

## Stage 5: Neutral Model Design (Gate 5)

**Trigger:** Gate 4 passed.

**Steps:**
1. Design a format-neutral data model that can represent the core data from this format family without being tied to any single format's encoding.
2. Express the neutral model as a YAML or JSON Schema file in `schemas/neutral-model/<format-family>/`.
3. The neutral model must be format-family-specific (e.g., Cells family for spreadsheets) but not format-specific. ODS and XLSX should be representable by the same neutral model.
4. Validate the neutral model against the sample corpus: can all samples be losslessly represented in the neutral model?
5. Mark Gate 5 passed after human review of the neutral model schema.
6. Update `plans/master-plan.md`.

---

## Stage 6: Oracle Comparison (Gate 6)

**Trigger:** Gate 5 passed.

**Steps:**
1. Select an oracle tool for the format. The oracle is the most authoritative reference implementation available (e.g., LibreOffice for ODF formats).
2. Load each sample in the corpus with the oracle tool and capture the oracle's interpretation of the file.
3. Load each sample with the prototype parser and compare the output against the oracle's interpretation.
4. Document discrepancies in an oracle comparison report at `reports/<format-id>-oracle.md`.
5. Classify each discrepancy: (a) prototype bug — fix it, (b) spec ambiguity — document it, (c) oracle deviation from spec — document it.
6. The prototype must correctly handle all core data in the sample corpus. Minor presentation deviations are acceptable; data loss is not.
7. Mark Gate 6 passed after human review of the comparison report.
8. Update `plans/master-plan.md`.

**Reuse rule:** Oracle comparison outputs are regeneratable. If the oracle tool version or sample set has changed, regenerate. If both are unchanged (check `source_hash` and tool version in artifact front matter), reuse.

---

## Stage 7: Fuzz Testing (Gate 7)

**Trigger:** Gate 6 passed.

**Steps:**
1. Create fuzz seeds in `tests/fuzz/<format-id>/` covering: minimal valid file, minimal empty file, truncated file, file with illegal values in key fields, file with oversized length fields.
2. Run the fuzz harness against the prototype parser for the minimum required iterations (10,000 for XML formats; 100,000 for binary formats).
3. Document all crashes in `reports/security/<format-id>.md` with: crash input characterization, stack trace, root cause analysis, proposed mitigation.
4. Fix all crashes that could result in arbitrary code execution, memory exhaustion, or file system writes outside the output directory.
5. Mark Gate 7 passed when no unmitigated critical crashes remain.
6. Update `plans/master-plan.md`.

---

## Stage 8: Security Review (Gate 8)

**Trigger:** Gate 7 passed.

**Steps:**
1. Review the prototype and prototype README against all applicable threat categories in `docs/security.md`.
2. Verify that each threat category is addressed: mitigated, explicitly deferred with rationale, or not applicable with rationale.
3. Complete the security report in `reports/security/<format-id>.md`.
4. A human security reviewer signs off by populating the `sign-off` field in the security report.
5. Mark Gate 8 passed only after human sign-off is recorded.
6. Update `plans/master-plan.md`.

---

## Stage 9: Product Mapping (Gate 9)

**Trigger:** Gate 8 passed.

**Steps:**
1. Map all format features to the tier model (Tiers 0-6) defined in `docs/product-tracks.md`.
2. Assign features to tracks: Tiers 0-4 to open-source; Tiers 5-6 to commercial (if applicable).
3. Create a delivery plan: which features ship in the first OSS release, which are deferred.
4. Record tier assignments and delivery plan in the format's acquisition pack.
5. Update `registry/format-registry.yaml` with the tier map.
6. Mark Gate 9 passed after human review of the tier map and delivery plan.
7. Update `plans/master-plan.md`.

---

## Stage 10: OSS Implementation and Release Readiness (Gate 10)

**Trigger:** Gate 9 human approval recorded in `registry/format-registry.yaml` AND explicit Phase 4 OSS implementation execution prompt issued by a human.

**Steps:**
1. Write production-quality Python source code for Tiers 0-4 in `src/python/{format}/` (e.g. `src/python/fods/`) and/or .NET source code for the implemented tiers in `src/net/{format}/` (e.g. `src/net/fods/`).
2. Write unit tests and integration tests in `tests/`.
3. Generate a release manifest listing all artifacts in the release with visibility, license, and provenance status.
4. Human reviews the release manifest: no `commercial`, `blocked`, or unreviewed `generated` artifacts.
5. Run the boundary check: build the open-source solution in isolation, verify no commercial references.
6. Mark Gate 10 passed after human sign-off on the release manifest.
7. Update `plans/master-plan.md`.

**Authorization model:** OSS source writing (Step 1) is authorized when Gate 9 is human-approved AND the human issues an explicit Phase 4 OSS implementation execution prompt. Gate 10 is not the authorization to begin writing source code — Gate 10 is the release readiness gate that approves the completed OSS implementation as production-ready for public release. The implementation may span multiple Phase 4 execution sessions between Gate 9 and Gate 10. No public visibility may be assigned to source artifacts before Gate 10 is passed.

---

## Stage 11: Commercial Implementation and Release Readiness (Gate 11)

**Trigger:** Gate 10 passed AND Decision DD3 (commercial isolation) resolved AND explicit commercial implementation execution prompt issued by a human.

**Steps:**
1. Write production-quality .NET source code for Tiers 5-6 within `src/net/{format}/` (commercial-tier section).
2. Verify one-way dependency rule: commercial code may reference OSS; OSS must not reference commercial.
3. Generate a commercial release manifest.
4. Human reviews the commercial manifest: correct license headers, no OSS-only code in commercial-tier.
5. Mark Gate 11 passed after human sign-off.
6. Update `plans/master-plan.md`.

**Authorization model:** Commercial source writing (Step 1) is authorized when Gate 10 is passed AND DD3 is resolved AND commercial implementation taskcards exist AND the human issues an explicit commercial implementation execution prompt. Gate 11 is not the authorization to begin writing commercial source — Gate 11 is the release readiness gate that approves the completed commercial implementation for release.

---

## Reuse-Before-Regenerate Policy

This policy governs all agent work at all phases.

### Rule 1: Check Before Create

Before creating any artifact, an agent must check `.local/artifact-index.yaml` for an existing entry with the same `artifact_id` or the same (`format_id`, `artifact_type`) pair.

### Rule 2: Validity Conditions

An artifact is valid for reuse if ALL of the following are true:
1. The file exists at its registered path.
2. `source_hash` in the artifact's front matter matches the current hash of the primary source.
3. The spec version (if applicable) matches the current published version.
4. The tool version (for generated outputs) matches the currently installed version.
5. `stale: false` in the artifact's front matter.

### Rule 3: Reuse Action

If the artifact is valid, the agent reuses it and logs `ARTIFACT_REUSED: <artifact_id>` in the run record. No API call, no file write.

### Rule 4: Refresh Action

If the artifact exists but is stale (any validity condition fails), the agent refreshes only the stale artifact. It does not recreate all artifacts from scratch.

### Rule 5: Generate Action

If the artifact does not exist, the agent generates it from scratch.

### Rule 6: Duplicate Prevention

Before creating a new taskcard, registry entry, sample, or report, the agent checks for an existing item covering the same subject. If found, the agent updates the existing item rather than creating a duplicate.

---

## Monthly Refresh Process

On a periodic basis (suggested: monthly while active, quarterly during maintenance):

1. Re-check all spec source URLs in acquisition pack `spec-evidence.md` files for version changes. If a new spec version is published, mark the artifact stale and create a refresh taskcard.
2. Re-check all sample source URLs in `sample-sources.md` files for continued availability. If a source is unavailable, note it in provenance but the sample file remains valid if already acquired.
3. Re-run oracle comparisons for any format where the oracle tool version has changed.
4. Do NOT automatically regenerate stale artifacts. Create refresh taskcards for human review and approval before regeneration.

---

## Note on Future Playbook Layer (Proposed — Requires S-F2F-01 Human Approval)

A future playbook layer is proposed in the Full2Foss-inspired secondary sprint roadmap
(plans/secondary/full2foss-inspired-system-strengthening-plan-v2.md). If and when
S-F2F-01 is approved and implemented, playbook.yaml files may be added to individual
acquisition packs (e.g., acquisition-packs/fods/playbook.yaml) to record execution steps
for reuse in future format acquisitions. This addition is OPTIONAL and does not change any
existing workflow step described in this document. All current workflow steps remain
mandatory regardless of playbook layer status. Playbook adoption requires explicit human
authorization via S-F2F-01 execution.

---

## Relationship to Other Documents

- `docs/gates.md` — detailed pass criteria for each gate
- `docs/legal-and-licensing.md` — legal category model and fast-path rules
- `docs/security.md` — threat categories and mitigations (Stage 4, 7, 8)
- `docs/product-tracks.md` — tier model and track definitions (Stage 9, 10, 11)
- `docs/release-control.md` — artifact visibility and release manifest rules
- `acquisition-packs/_template/` — templates for all acquisition pack artifacts
- `registry/scoring/_scoring-model.md` — Gate 1 scoring criteria
