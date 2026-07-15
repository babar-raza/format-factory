# Gate Model

**Document type:** Process Reference — Phase 0 Foundation
**Last reviewed:** 2026-05-04 (run014: global audit — content verified consistent with current governance)
**Authority:** This document defines all 11 acquisition gates: their pass criteria, required artifacts, authorization rules, and fast-path options. No gate may be bypassed. Gates 1-10 are agent-owned policy gates requiring evidence, validators, and acceptance criteria. Gate 11 G11-G is the sole TRUE_EXTERNAL_GATE requiring Babar Raza's commercial business authority.

---

## Purpose

Gates are mandatory checkpoints that a format must pass before work at the next stage may begin. They enforce quality, legal safety, security, and release readiness at defined points in the acquisition pipeline. Gates cannot be self-approved without evidence. Gates 1-10 require the agent to produce validated evidence, pass governance validators, satisfy acceptance criteria, and record the decision in the registry. Gate 11 G11-G requires Babar Raza's explicit commercial business authority.

---

## Gate Authorization Rules

1. **Evidence-backed agent approval (Gates 1-10).** An agent that completes the work required for a gate must verify all acceptance criteria are met, pass governance validators, and record the decision in `registry/format-registry.yaml` with `gate_N_approved_by: agent_policy_gate` and `gate_N_approved_date`. No gate may be passed without real evidence — skeleton, placeholder, or fabricated artifacts are prohibited. Gate 11 G11-G: agent prepares the evidence packet; Babar Raza executes the final commercial approval.
1a. **Delegated execution path.** When the human project lead explicitly delegates a gate decision to the agent via an execution prompt, the agent may record the decision on the human's behalf. The delegated execution must: (a) cite the execution prompt as authority; (b) be supported by complete evidence; (c) record `approval_method: delegated_agent_decision_under_<human>_instruction` in the registry; (d) produce a delegated-decision report. This is not autonomous self-approval — it is the agent carrying out an explicit human decision. See GOVERNANCE.md §2.1a and AGENTS.md §D1a.
2. **Registry recording required.** Gate passage must be recorded in `registry/format-registry.yaml` by setting `gate_N_status: passed`, `gate_N_approved_by: <agent_policy_gate | babar_raza>`, and `gate_N_approved_date: <ISO-8601 date>`. For Gates 1-10, the agent records approval after evidence validation. For Gate 11 G11-G, the record is written only after Babar Raza's explicit commercial authorization.
3. **Sequential progression.** A format may not begin Stage N+1 work until Gate N has been passed and recorded in the registry.
4. **No retroactive approval.** Artifacts produced before a preceding gate was passed do not count toward the later gate. For example, a prototype started before Gate 3 was passed does not satisfy Gate 4.
5. **Master plan update required.** After any gate passage, `plans/master-plan.md` must be updated with the gate history entry before the format proceeds to the next stage.

---

## Gate 1: Candidate Accepted

**Stage:** Candidate Scoring

**Pass criteria:**
1. The format has been scored using the model in `registry/scoring/_scoring-model.md`.
2. The weighted total score places the format in the "accept" band (see scoring model for thresholds).
3. The format has been assigned a legal category (Categories 1-4 only; Categories 5-6 are automatic rejects).
4. Score is not 0 on any single dimension that triggers automatic rejection (legal safety).
5. A registry entry exists in `registry/format-registry.yaml` with format-id, family, tier target, legal category, and scoring notes.

**Required artifacts:**
- Registry entry in `registry/format-registry.yaml`
- Completed scoring sheet (embedded in registry entry or linked acquisition pack)

**Fast-path:** None. All Gate 1 evaluations require the scoring model to be applied.

**Automatic rejects:**
- Legal Category 5 (reverse-engineered binary): reject regardless of other scores.
- Legal Category 6 (blocked): reject, record reason in registry.
- Score 0 on the legal safety dimension: reject regardless of total score.

---

## Gate 2: Evidence Complete

**Stage:** Evidence Gathering

**Pass criteria:**
1. `spec-evidence.md` exists in `acquisition-packs/<format-id>/` and has been populated with: primary source URL, specification version, date accessed, source hash (SHA-256), key sections and their relevance, and a summary of the parsing approach.
2. The primary source is an official specification from the recognized standard body or rights holder — not a secondary analysis or blog post.
3. `legal-notes.md` exists and has been populated with: legal category confirmation, citation of the specific permission grant or standard body publication, patent risk assessment (for non-Category 1 formats), and project lead sign-off.
4. For Category 1 (open standard RF) formats: fast-path approval is available. See fast-path rules below.
5. For all other categories: full legal review notes must be present with project lead sign-off.

**Required artifacts:**
- `acquisition-packs/<format-id>/spec-evidence.md` (with source hash and spec version)
- `acquisition-packs/<format-id>/legal-notes.md` (with sign-off)

**Fast-path (Category 1 only):**
If the format is on the Pre-Approved Fast-Path List in `docs/governance/legal-and-licensing.md`, the project lead may self-approve Gate 2 with a brief rationale in `legal-notes.md`. No external legal review required. The fast-path requires: (1) documented RF license citation, (2) named standard body, (3) date reviewed, (4) project lead sign-off.

---

## Gate 3: Sample Corpus Ready

**Stage:** Sample Acquisition

**Pass criteria:**
1. A minimum sample corpus exists in `samples/by-format/<format-id>/` covering: minimal valid file, empty/trivial file, file with all core data structures present, at least one edge-case file.
2. Every sample in the corpus has a `_provenance.yaml` entry with `provenance_status: confirmed`.
3. Every sample's license is in the acceptable licenses list in `docs/governance/legal-and-licensing.md`.
4. No sample has `visibility: blocked` (blocked samples may not be used in the corpus).
5. All provenance entries have been human-reviewed.

**Required artifacts:**
- `samples/by-format/<format-id>/` directory with corpus files
- `_provenance.yaml` entries for all samples

**Normalization dependency:** Normalization is not required to pass Gate 3, but absence must be noted. If `sections.jsonl` or `parser-requirements.yaml` have been produced by the normalization layer, sample categories should be validated against spec-defined data structures before Gate 3 is approved. If normalization is not available, document this as a noted absence in the Gate 3 approval record.

**Fast-path:** None. All sample provenance must be confirmed.

---

## Gate 4: Prototype Complete

**Stage:** Prototype Development

**Pass criteria:**
1. A working prototype parser exists in `prototypes/by-format/<format-id>/`.
2. The prototype correctly parses all samples in the corpus from Gate 3 without crashing.
3. The prototype README documents: parsing approach, key decisions, known limitations, and security mitigations applied (per `docs/governance/security.md`).
4. The prototype demonstrates that XXE and entity expansion mitigations are in place (for XML-based formats).
5. The prototype has been human-reviewed for correctness and security baseline.

**Required artifacts:**
- `prototypes/by-format/<format-id>/` with parser source code
- Prototype README with security section
- `parser-requirements.yaml` under `.local/spec-cache/{format-id}/{version}/normalized/` (or an explicit human-approved waiver logged as gap G-NORM-004)

**Normalization dependency (REQUIRED):** Gate 4 may not begin until `parser-requirements.yaml` exists in the normalized artifact directory, OR an explicit human waiver is logged as gap G-NORM-004 in the gap register. If normalization tooling failed (G-NORM-001) or the cached spec is unavailable, the waiver must document this constraint and what alternative was used for parser requirement extraction.

**Fast-path:** None. Human review is required for prototype correctness and security baseline.

---

## Gate 5: Neutral Model Defined

**Stage:** Neutral Model Design

**Pass criteria:**
1. A neutral model schema exists in `schemas/neutral-model/<format-family>/` that can represent all core data from this format without being tied to the format's encoding.
2. The neutral model has been validated: all samples in the corpus can be represented in the neutral model without data loss.
3. The neutral model schema is documented with field descriptions and any constraints.
4. For format families that already have a neutral model (e.g., a second Cells format after ODS/FODS), the new format has been verified to be representable by the existing neutral model (or the model has been extended with a documented rationale).
5. Evidence-backed agent review and approval recorded (or Babar Raza sign-off for Gate 11).

**Required artifacts:**
- `schemas/neutral-model/<format-family>/<schema-file>`
- Neutral model validation notes in the acquisition pack

---

## Gate 6: Oracle Comparison Complete

**Stage:** Oracle Comparison

**Pass criteria:**
1. An oracle tool has been selected and its version recorded.
2. All samples in the corpus have been loaded with the oracle tool and with the prototype parser.
3. An oracle comparison report exists at `reports/<format-id>-oracle.md` documenting all discrepancies.
4. Every discrepancy has been classified: prototype bug (fixed), spec ambiguity (documented), or oracle deviation from spec (documented).
5. No unresolved data-loss discrepancies remain. Minor presentation differences are acceptable.
6. Human review of the comparison report recorded.

**Required artifacts:**
- `reports/<format-id>-oracle.md`

---

## Gate 7: Fuzz Testing Complete

**Stage:** Fuzz Testing

**Pass criteria:**
1. Fuzz seeds exist in `tests/fuzz/<format-id>/` covering the required seed types (minimal valid, empty, truncated, illegal values, oversized fields).
2. The prototype parser has been run against the fuzz corpus for the minimum iteration count: 10,000 for XML formats; 100,000 for binary formats.
3. All crashes have been documented in `reports/security/<format-id>.md` with: input characterization, stack trace, root cause, and mitigation.
4. No unmitigated crashes that could result in arbitrary code execution, uncontrolled memory exhaustion, or file system writes outside the output directory remain.
5. Human review of the fuzz report recorded.

**Required artifacts:**
- `tests/fuzz/<format-id>/` with seed files
- `reports/security/<format-id>.md` with fuzz results section

---

## Gate 8: Security Review Complete

**Stage:** Security Review

**Pass criteria:**
1. The security report in `reports/security/<format-id>.md` covers all applicable threat categories from `docs/governance/security.md`.
2. Each threat category is marked as: mitigated (with implementation notes), explicitly deferred (with rationale), or not applicable (with rationale).
3. A human security reviewer has signed off on the security report by populating the `sign-off` field with their name and the review date.
4. No residual risks are classified as "unacceptable." Accepted residual risks are documented.
5. For prototype-phase reviews: the reviewer may be the project lead. A dedicated security reviewer is recommended at Gate 10.

**Required artifacts:**
- `reports/security/<format-id>.md` with sign-off field populated

**Note:** Gate 8 requires validator-backed security evidence (automated fuzz results, security scan artifacts) before agent approval per AGENTS.md §AG5.

---

## Gate 9: Product Mapping Complete

**Stage:** Product Mapping

**Pass criteria:**
1. All features of the format have been assigned to tiers 0-6 using the model in `docs/product-factory/product-tracks.md`. **The feature list used for this assignment MUST originate from a `reports/spec-coverage/manifests/<format-id>-feature-manifest.json` produced by `tools/specification-authority-layer/enumerate_spec_features.py` (schema: `schemas/spec-coverage/feature-manifest-schema.json`) — a structured enumeration derived from the real specification, not an ad hoc list a human or agent writes down from memory.** This closes a confirmed portfolio-wide gap (2026-07-15 audit): prior to this manifest requirement, no artifact anywhere in the repo represented "the complete feature set a spec defines, with implementation status per item" — Gate 9 was satisfiable by any feature list a human happened to write, regardless of how much of the real specification it actually covered.
2. A delivery plan exists in the acquisition pack specifying which features ship in the first OSS release and which are deferred.
3. Tier assignments are recorded in `registry/format-registry.yaml`.
4. Any features assigned to Tier 5-6 (commercial) are explicitly noted with a deferral condition (Gate 10 + DD3 + explicit commercial implementation prompt).
5. Implementation taskcards for the Phase 4 OSS implementation work have been created based on the delivery plan.
6. Evidence-backed agent review and approval recorded.
7. **A `reports/spec-coverage/<format-id>-coverage-report.json` exists (produced by `tools/specification-authority-layer/compute_feature_coverage.py`, schema: `schemas/spec-coverage/coverage-report-schema.json`) with `gate_9_eligible: true`.** This requires every manifest feature to be either IMPLEMENTED or have an explicit, reviewed `deferred_reason` — silent gaps (a feature the spec requires that nobody noticed was missing) are structurally impossible to satisfy this criterion, only consciously-scoped-out ones are.

**Required artifacts:**
- Updated `registry/format-registry.yaml` with tier map
- Delivery plan in acquisition pack
- Phase 4 OSS implementation taskcards
- `reports/spec-coverage/manifests/<format-id>-feature-manifest.json` and `reports/spec-coverage/<format-id>-coverage-report.json` with `gate_9_eligible: true`

**`implementation_authorized` in `registry/format-registry.yaml` may only be set `true` once criterion 7's coverage report exists and shows `gate_9_eligible: true`.** This is the mechanical enforcement point: Gate 9 approval without a passing coverage report is not a valid gate passage, regardless of other evidence.

**Note on implementation authorization:** Gate 9 approval, combined with an explicit Phase 4 implementation execution prompt issued by a human, authorizes creation of `src/python/{format}/` and `src/net/{format}/`. Gate 9 alone does not create product source — it creates the delivery plan and implementation taskcards that enable Phase 4 execution. No product source may be written before both conditions are met. **Obsolete paths:** `src/python/open-source/` and `src/dotnet/open-source/` are not the target layout and must not be created.

---

## Gate 10: OSS Readiness Complete

**Stage:** Open-Source Release Preparation

**Pass criteria:**
1. Production-quality Python source code exists in `src/python/{format}/` for Tier 0-4 features in the delivery plan, and/or .NET source code exists in `src/net/{format}/` for the implemented tiers.
2. Unit tests and integration tests exist in `tests/` for the implemented features.
3. A release manifest has been generated listing all artifacts with visibility, license, and provenance status.
4. Human review of the release manifest: no `commercial`, `blocked`, or unreviewed `generated` artifacts present.
5. The open-source solution has been built in isolation (boundary check): zero commercial namespace references confirmed.
6. All samples used in tests have `provenance_status: confirmed` with a compatible open-source license.
7. `registry/format-registry.yaml` updated with `gate_10_status: passed`.

**Required artifacts:**
- `src/python/{format}/` (Python FOSS) and/or `src/net/{format}/` (.NET product) with production source
- `tests/` with passing tests
- Release manifest (YAML) with agent policy-gate approval recorded

**Gate 10 is the gate that changes format-registry.yaml visibility from `internal` to `public`.**

**Gate 10 semantics:** Gate 10 is OSS release readiness, not the authorization to start writing product source. OSS source writing begins after Gate 9 human approval and an explicit Phase 4 OSS implementation execution prompt. Gate 10 approves the completed OSS implementation as production-ready. The source code required by criteria 1 above is written during Phase 4 execution sessions (between Gate 9 and Gate 10), not as a consequence of Gate 10 passage.

---

## Gate 11: Commercial Readiness Complete

**Stage:** Commercial Release Preparation

**Precondition:** Gate 10 passed AND Decision DD3 (commercial isolation) formally resolved AND commercial implementation taskcards exist AND explicit commercial implementation execution prompt issued.

**Pass criteria:**
1. Commercial-tier source code exists within `src/net/{format}/` for all Tier 5-6 features in the delivery plan.
2. One-way dependency verified: no open-source project references commercial projects.
3. Commercial release manifest generated: correct proprietary license headers, no open-source-only content in commercial tier.
4. Human review of commercial manifest with commercial product lead sign-off.
5. Legal review of commercial license terms.
6. `registry/format-registry.yaml` updated with `gate_11_status: passed`.

**Required artifacts:**
- Commercial-tier source within `src/net/{format}/` (e.g. `src/net/fods/`)
- Commercial release manifest with sign-off

**Gate 11 semantics:** Gate 11 is commercial release readiness, not the authorization to start writing commercial source. Commercial source writing begins after Gate 10 is passed, DD3 is resolved, commercial implementation taskcards exist, and the human issues an explicit commercial implementation execution prompt. Gate 11 approves the completed commercial implementation for release. The commercial source required by criterion 1 above is written during commercial implementation sessions (after the explicit commercial prompt), not as a consequence of Gate 11 passage.

---

## Gate Status Fields in Registry

Every format entry in `registry/format-registry.yaml` includes gate status fields:

```yaml
gates:
  gate_1:
    status: passed | failed | not_started
    approved_by: <name>
    approved_date: <ISO-8601>
    notes: <optional>
  gate_2:
    status: passed | failed | not_started
    approved_by: <name>
    approved_date: <ISO-8601>
    fast_path: true | false
    notes: <optional>
  # ... gate_3 through gate_11
```

An agent must update `gate_N.status` to `passed` only after human approval has been confirmed and `approved_by` + `approved_date` have been recorded. An agent must never set `status: passed` without human confirmation.

---

## Relationship to Other Documents

- `docs/python-foss/acquisition-workflow.md` — stage-by-stage workflow with reuse rules
- `docs/governance/security.md` — Gate 7 and Gate 8 criteria detail
- `docs/governance/legal-and-licensing.md` — Gate 2 fast-path rules and legal categories
- `docs/product-factory/product-tracks.md` — Gate 9, 10, 11 tier model and boundary check
- `docs/governance/release-control.md` — release manifest requirements for Gate 10 and 11
- `docs/python-foss/specification-normalization.md` — normalization gate dependencies (Gate 3 optional, Gate 4 required)
- `registry/scoring/_scoring-model.md` — Gate 1 scoring criteria
- `plans/master-plan.md` — gate history for all in-flight formats
