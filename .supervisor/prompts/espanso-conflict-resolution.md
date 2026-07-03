# Espanso Conflict Resolution — Format Factory

**Generated:** 2026-07-03
**Source:** `C:\Users\prora\AppData\Roaming\espanso\match\format-factory.yml`
**Provenance map:** `.supervisor/prompts/espanso-provenance-map.yaml`

This document records all duplicate blocks, trigger collisions, policy conflicts, and
supersession decisions from the Espanso integration. It is the source of truth for
"which rule wins when Espanso blocks disagree with repository governance."

---

## 1. Duplicate Blocks

Blocks whose replacement bodies are semantically equivalent to another block.
The **canonical** block is the authoritative version; duplicates are deprecated.

| Canonical Block | Duplicate Block(s) | Trigger | Decision |
|---|---|---|---|
| Block 27 `:ffreadme` | Block 34, 35 (format READMEs) | NOT duplicates — different scope | Block 27 = root README; Blocks 34/35 = format READMEs. No conflict. |
| Block 10 (canary control) | Block 11 | `:ff-investigate-canary-control` | Block 10 is canonical. Block 11 is a near-duplicate with minor wording differences. |
| Block 30 (operational control) | Block 31 | `:ff-central-operational-control-layer` | Block 30 is canonical. Block 31 is a variant (operational RECORD vs CONTROL layer). |
| Block 34 (format README, old path) | Block 35 (updated path) | `:ff-format-readme-hardening` | Block 35 supersedes Block 34. Block 34 references outdated file paths. |
| Block 38 (layer plans) | Blocks 39, 40 | `:ff-permanent-layer-plans` | Block 38 is canonical. Blocks 39 and 40 add minimal variation. |
| Block 50 (deepening train) | Block 51 | `:ff-product-deepening-train` | Block 50 is canonical. Block 51 is an abbreviated variant. |
| Block 64 (total system audit) | Block 65 | `:ff-total-system-audit` | Block 64 is canonical. Block 65 is abbreviated. |
| Block 68 (skill governance) | Block 69 | `:ff-skill-governance-sprint` | Block 68 is canonical. Block 69 is abbreviated. |
| Block 88 (zero-stub) | Block 89 | `:ff-zero-stub` | Block 88 is canonical. Block 89 is expanded. Espanso trigger collision — last definition wins in Espanso, but repo uses Block 88. |
| Block 99 (pre-acquisition) | Block 100 | `:ff-pre-acquisition-readiness` | Block 99 is canonical. Block 100 is expanded version. |
| Block 108 (expert review) | Block 109 | `:ff-expert-review-plan` | Block 108 is canonical (prompt asset ESP-PROMPT-3). Block 109 is a variant. |
| Block 44 (review bundle) | Block 45 | `:ff-exhaustive-review-bundle-healing` | Block 44 is canonical. Block 45 is a shorter variant. |
| Block 92 (code governance) | Block 93, 94 | `:ff-code-governance-heal-master` | Block 93 is the full version; Block 92 is summary; Block 94 is brief. Block 93 is the authoritative reference for content. |

---

## 2. Trigger Collisions

Cases where the same Espanso trigger text appears in multiple blocks.

| Trigger | Block(s) | Resolution |
|---|---|---|
| `:ff-format-readme-hardening` | Blocks 34 AND 35 | **Block 35 wins** — updated path variant. Espanso last-definition-wins means Block 35 is active in Espanso. Repository uses `/sync-readmes` for both. |
| `:ff-product-deepening-train` | Blocks 50 AND 51 | **Block 51 wins** in Espanso (last definition). Repository uses `autonomous-loop` for both. |
| `:ff-investigate-canary-control-layer` | Block 11 (primary) AND Block 10 (alias) | **Block 11** has it as primary trigger; Block 10 has it as alias. In Espanso, Block 11's trigger definition takes precedence for `:ff-investigate-canary-control-layer`. For `:ff-investigate-canary-control`, Block 10 is primary. No functional difference — both produce the same output. |
| `:ff-zero-stub` | Blocks 88 AND 89 | **Block 89 wins** in Espanso (last definition, expanded version). Repository maps to `implement-spec-stub`. |
| `:ff-pre-acquisition-readiness` | Blocks 99 AND 100 | **Block 100 wins** in Espanso. Repository maps to `create-acquisition-pack`. |
| `:ff-expert-review-plan` | Blocks 108 AND 109 | **Block 109 wins** in Espanso. Repository canonical is Block 108 → ESP-PROMPT-3. |
| `:fferp` | Blocks 108 AND 109 | Same as above. Block 108 used as canonical for ESP-PROMPT-3. |
| `:ff-source` | Blocks 93 AND 94 | **Block 94 wins** in Espanso (abbreviated). Repository uses Block 93 as content reference. |
| `:ffsa` | Block 106 (spec-authority) AND Block 65 (system-audit with `:ffsa:`) | Different triggers (`:ffsa` vs `:ffsa:`). No collision. |

---

## 3. Policy Conflicts Between Espanso Blocks and Repository Governance

**Resolution rule: Repository truth outranks Espanso prompt text.**

| Conflict ID | Espanso Instruction | Repository Truth | Selected Rule | Rationale |
|---|---|---|---|---|
| CONF-001 | Block 53 (`:ff-nohuman`) says "all human requirements are defects" without qualification | AGENTS.md §AG1-AG2 lists legitimate external gates (Gate 11, credentials, branch protection) | **AGENTS.md wins** | Block 53 is a simplified version. Block 118 (`:ff-humanfree`, ESP-PROMPT-6) correctly preserves the external gate list. Block 53 is superseded by Block 118. |
| CONF-002 | Block 21 (blog announcement) implies agent should write marketing content | No repository policy for blog content | **Block 21 is POLICY_ONLY** | Blog announcements are not a governed repository operation. Not imported as a prompt asset. |
| CONF-003 | Blocks 55-58 (analytics micro-triggers) imply inline-only directives for analytics migration | analytics rotation is SUSPENDED per CLAUDE.md (keen-dancing-hopper plan) | **CLAUDE.md wins** | Analytics rotation is suspended. These micro-triggers are classified POLICY_ONLY and not imported. |
| CONF-004 | Block 34 (format README) references old file paths | Block 35 has updated paths; `/sync-readmes` is the authoritative command | **Block 35 + /sync-readmes win** | Block 34 is superseded. |
| CONF-005 | Block 42 (multi-plan orchestrator) implies running multiple plans simultaneously | CLAUDE.md and plan lock system enforce ONE active plan per session | **CLAUDE.md wins** | Multi-plan execution is not supported by the current plan lock architecture. Block 42 marked PARTIAL_COVERAGE; no prompt asset created. |
| CONF-006 | Some blocks describe "autonomous sprint loops" without plan locks | CLAUDE.md CCI-MVP requires session_id checks and plan locks | **CLAUDE.md wins** | All continuation behavior governed by check_continuation.py + plan lock system. |
| CONF-007 | Block 80 (`:ffmgh:`) implies healing product code in the same sprint as governance | production-library-standard-v2.md Section 8.1 requires governance-first | **Standard wins** | ESP-PROMPT-8 (production-standards-enforcement.md) explicitly preserves governance-first ordering. |

---

## 4. Supersession Map

Espanso blocks superseded by existing repository capabilities or by other blocks.

| Superseded Block | Superseded By | Reason |
|---|---|---|
| Block 34 (format README old path) | Block 35 + `/sync-readmes` | Updated paths; `/sync-readmes` is the canonical skill |
| Block 53 (`:ff-nohuman`, brief) | Block 118 (`:ff-humanfree`, ESP-PROMPT-6) | Block 118 is the complete and correct version with external gate list |
| Block 65 (system audit brief) | Block 64 (full version) | Block 65 is an abbreviated duplicate |
| Block 69 (skill governance brief) | Block 68 (full version) | Block 68 is the authoritative version |
| Block 89 (zero-stub expanded) | Block 88 + `/implement-spec-stub` | `/implement-spec-stub` is the canonical skill; Block 88 is the base version |
| Block 100 (pre-acquisition expanded) | Block 99 + `/create-acquisition-pack` | `/create-acquisition-pack` is the canonical skill |
| Block 109 (expert review variant) | Block 108 → ESP-PROMPT-3 | Block 108 selected as canonical |
| Block 94 (src governance brief) | Block 93 (content reference) | Block 93 is the full content version |
| Block 40 (layer plans duplicate) | Blocks 38-39 + `/create-permanent-layer-plan` | Skill covers both |
| Block 45 (review bundle brief) | Block 44 + `/post-sprint-audit` | Skill covers both |
| Block 51 (deepening train brief) | Block 50 + `/autonomous-loop` | Skill covers both |
| Block 11 (canary brief) | Block 10 | Block 10 is the more complete version |
| Block 31 (operational record) | Block 30 + `/query-control-index` | Block 30 is more complete; query-control-index partially covers |

---

## 5. Espanso Trigger to Repository Command Mapping

For agents wanting to find the repository equivalent of an Espanso trigger:

| Espanso Trigger | Repository Equivalent |
|---|---|
| `:ff-execute-short-context-plan` | ESP-PROMPT-1 (`bounded-executor.md`) + route `bounded_execution` |
| `:ffreadme` | ESP-PROMPT-2 (`readme-governance.md`) + route `root_readme_governance` |
| `:ff-expert-review-plan` | ESP-PROMPT-3 (`expert-review-plan.md`) |
| `:found-it-own-it` | ESP-PROMPT-4 (`found-it-own-it.md`) |
| `:ff-machinery-iteration-forensics` | ESP-PROMPT-5 (`machinery-iteration-forensics.md`) |
| `:ff-humanfree` | ESP-PROMPT-6 (`human-free-rectification.md`) + route `governance_rectification` |
| `:ffl0:` through `:ffl7:` | ESP-PROMPT-7 (`layer-hardening-template.md`, `layer_id=0..7`) |
| `:ffla:` | ESP-PROMPT-7 (`layer-hardening-template.md`, `layer_id=all`) |
| `:ffmgh:` | ESP-PROMPT-8 (`production-standards-enforcement.md`) |
| `:ff-format-readme-hardening` | `/sync-readmes` skill |
| `:ff-import-espanso-capabilities` | This integration (self-referential) |
| `:found-it-own-it` | `found-it-own-it.md` protocol |
| `:ff-enforce-skill-command-runtime` | `/enforce-skill-first-execution` |
| `:ff-harden-oracle-layer` | `/run-oracle` + `/sal-pipeline-heal` |
| `:ff-spec-to-code-forensics` | `/spec-literal-qname-to-code-mapping` |
| `:ff-qname-audit` | `/qname-backfill` |
| `:ff-machinery-readiness` | `/check-gate` + `/generate-root-status` |
| `:ff-permanent-layer-plans` | `/create-permanent-layer-plan` |
| `:ff-unified-multi-plan-execution` | `/autonomous-loop` (partial) |
| `:ff-skill-governance-sprint` | `/check-skill-coverage` + `/enforce-skill-first-execution` |
| `:ff-product-deepening-train` | `/autonomous-loop` |
| `:ff-remove-analytics-safely` | `/extract-analytics-from-monolith` |
| `:heal-product-deepening-ledger` | `/validate-product-code-ledger` |
| `:ff-cap-forensics-plan` | `/build-capability-routes` |
| `:ff-autonomous-proof-sprint` | `/build-evidence-bundle` + `/post-sprint-audit` |
| `:ff-pre-acquisition-readiness` | `/create-acquisition-pack` + `/check-gate` |
| `:deep-recon-evidence` | `/build-evidence-bundle` + `/build-context-pack` |
| `:ff-reconcile-plan` | `/reproduce-master-plan` |
| `:ff-plan-governance-heal` | `/plan-hardening` |
| `:ff-spec` | `/ingest-spec-sal` |
| `:ff-spec-authority` | `/ingest-spec-sal` |
| `:ff-spec-machinery` | `/sal-pipeline-heal` |
| `:ff-fullsuite-layering-healing-sprint:` | `/add-roundtrip-test` |
| `:ff-capability-heal` | `/validate-capability-parity` |
| `:ff-source-realization-forensics` | `/spec-parity-source-regeneration-and-migration` |
| `:ff-healing-investigate` | `/audit-root-tools` |
| `:ff-layer-architecture-forensics` | `/identify-primary-layer` + `/reconcile-layer-index` |
| `:harden-plan-from-audit-writeback` | `/plan-hardening` |
| `:ff-audit-and-govern-root-folders` | `/audit-root-tools` |

---

## 6. How to Update This Document

When new Espanso blocks are added to `format-factory.yml`:
1. Update `espanso-provenance-map.yaml` with the new block entry
2. If a new conflict is detected: add a row to Section 3 with `CONF-N` identifier
3. If a new supersession: add to Section 4
4. If a new trigger collision: add to Section 2
5. If a new repository command covers an Espanso trigger: add to Section 5
