<!--
playbook_contract:
  playbook_id: package-release-readiness
  title: "Prepare Format Package for PyPI/NuGet Release"
  version: "1.0"
  status: ACTIVE
  category: sprint_task_template
  owner_layer: packaging
  authority: TASK_TEMPLATE
  purpose: >
    Verify release readiness for a format package and prepare the release packet.
    Does NOT perform the actual release (requires Babar Raza publication sign-off for PyPI/NuGet).
  applicability: >
    Format has reached gate threshold (Gate 10+ PASS). Evidence bundle complete.
    Visibility class verified. No commercial references in FOSS layer.
  triggers:
    - Gate 10 PASS recorded for a format
    - CUSTOMER_READY milestone reached
    - Explicit release readiness check requested
  prerequisites:
    - Gate 10 PASS for the format in registry/format-registry.yaml
    - Evidence bundle exists and is complete
    - Visibility class is public or commercial (not blocked)
    - No outstanding contradictions in approval-gates.md
  required_inputs:
    - format_name
    - gate_status
    - evidence_bundle_path
    - visibility_class
  optional_inputs:
    - target_registry
    - version_override
  required_skills:
    - check-release-boundary
    - check-gate
    - package-install-proof
  required_commands: []
  allowed_paths:
    - "registry/format-registry.yaml"
    - "reports/gate-review/<format>/"
    - "reports/release/<format>/"
    - ".local/evidences/<run-id>/"
  forbidden_paths:
    - "src/net/"
    - "src/python/"
    - "plans/"
    - "AGENTS.md"
    - "GOVERNANCE.md"
  phases:
    - gate_status_verification
    - evidence_completeness_check
    - visibility_class_verification
    - oss_release_manifest_review
    - commercial_reference_boundary_check
    - package_install_proof
    - release_packet_generation
  task_types:
    - RELEASE_READINESS_CHECK
    - PACKAGE_RELEASE_PREP
  validation:
    - gate_10_pass_confirmed: true
    - evidence_bundle_complete: true
    - no_commercial_refs_in_foss_layer: true
    - install_proof_exists: true
    - no_active_contradictions: true
  evidence_requirements:
    - gate_status_snapshot
    - evidence_bundle_path
    - oss_release_manifest
    - package_install_proof
    - release_packet_path
  rollback: >
    Release readiness check is read-only (no source changes). If evidence found
    incomplete: create gap entries for missing evidence. Do NOT proceed with
    publication. Document specific blocking items in reports/release/<format>/blockers.md.
  stop_conditions:
    - gate_10_not_passed
    - evidence_bundle_missing_required_items
    - visibility_class_is_blocked
    - commercial_references_found_in_foss_layer
    - active_contradictions_exist
    - publication_credentials_unavailable
  outputs:
    - release_readiness_verdict
    - release_packet_if_ready
    - blocker_list_if_not_ready
  supersedes: []
  limitations:
    - "No gate approval authority"
    - "No evidence contract replacement"
    - "Does NOT perform actual PyPI/NuGet publication (requires Babar Raza sign-off)"
    - "Does NOT mark gates as passed"
    - "Sprint task template only — preparation only, not release execution"
    - "Publication is EXTERNAL_BLOCKER: publication_credentials_unavailable"
-->

# Sprint Task Template: Package Release Readiness

**Skill ID**: package-release-readiness
**Version**: 1.0
**Authority**: Based on observed gate-10 and publication workflows. Sprint Task Template — NOT an acquisition playbook.
**Category**: Sprint Task Template (see docs/governance/playbook-layer.md for acquisition playbooks)

---

## Purpose

Verify release readiness for a format package and prepare the release packet.
Does NOT perform the actual publication (requires Babar Raza sign-off for PyPI/NuGet).

---

## When to Use

- Format has reached Gate 10 PASS milestone
- CUSTOMER_READY milestone is being claimed
- Release readiness needs to be verified before requesting publication sign-off

---

## Required Inputs

| Input | Description |
|-------|-------------|
| `format_name` | e.g. `fods`, `fodt` |
| `gate_status` | Current gate status from registry/format-registry.yaml |
| `evidence_bundle_path` | Path to evidence bundle |
| `visibility_class` | `public`, `internal`, `commercial`, `blocked` |

---

## Allowed Paths

- `registry/format-registry.yaml` — read-only gate status check
- `reports/gate-review/<format>/` — read gate review artifacts
- `reports/release/<format>/` — write release readiness report
- `.local/evidences/<run-id>/` — write evidence artifacts

## Forbidden Paths

- `src/net/`, `src/python/` — no source changes during release readiness check
- `plans/`, `AGENTS.md`, `GOVERNANCE.md`

---

## Readiness Checklist

1. **Gate Status** — confirm Gate 10 PASS in `registry/format-registry.yaml`
2. **Evidence Bundle** — confirm all required evidence artifacts exist
3. **Visibility Class** — confirm format is `public` or `commercial`, NOT `blocked`
4. **OSS Release Manifest** — review for zero commercial references in FOSS layer
5. **Commercial Boundary** — run /check-release-boundary; confirm no commercial leakage
6. **Package Install Proof** — run /package-install-proof; confirm installable from package
7. **No Active Contradictions** — check `reports/supervisor/approval-gates.md`
8. **Release Packet** — generate `reports/release/<format>/release-packet.md`

---

## Stop Conditions

| Condition | Action |
|-----------|--------|
| Gate 10 NOT passed | STOP — cannot proceed; close gate first |
| Evidence bundle missing items | STOP — create gap entries for missing evidence |
| Visibility class = `blocked` | STOP — classify blocker; do not proceed |
| Commercial refs in FOSS layer | STOP — run analytics separation before release |
| Active contradictions | STOP — resolve contradictions first |
| Publication credentials unavailable | STOP — EXTERNAL_BLOCKER (Babar Raza sign-off required) |

---

## Evidence Required

- Gate status snapshot from registry/format-registry.yaml
- Evidence bundle completeness summary
- OSS release manifest review result
- Package install proof artifact
- Release packet at `reports/release/<format>/release-packet.md`

---

## Rollback

Release readiness check is READ-ONLY — no source changes.
If evidence found incomplete: create gap entries. Do NOT proceed with publication.
Document specific blocking items in `reports/release/<format>/blockers.md`.

---

## Known Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Claiming CUSTOMER_READY without Gate 10 PASS | Always verify gate-registry.yaml first |
| Missing visibility class check | Always verify format is not `blocked` before generating release packet |
| Publication without Babar Raza sign-off | Publication is ALWAYS a TRUE_EXTERNAL_GATE — stop and report |
| Commercial references in FOSS source | Run /check-release-boundary before generating release packet |
