# Plan: Format Factory Agentic System Completion and Parity
**Plan ID:** glimmering-hopping-kazoo
**Type:** machinery_hardening
**Mission ID:** FF-AGENTS-PARITY-001
**Date:** 2026-07-10
**Status:** IN_PROGRESS
**Authoritative plan path:** plans/.claude/glimmering-hopping-kazoo.md *(after Step 0 migration)*

---

## PREFLIGHT RECORD

```
Repository:     c:\Users\prora\OneDrive\Documents\GitHub\format-factory
Branch:         main
Active plan:    C:\Users\prora\.claude\plans\glimmering-hopping-kazoo.md (seed)
                → plans/.claude/glimmering-hopping-kazoo.md (in-repo after Step 0)
Plan format:    Markdown with embedded YAML blocks
Plan size:      600 lines (pre-enhancement) → ~4000 lines (post-enhancement)
Major sections: 16 parent taskcards
Existing taskcard format: prose descriptions only (pre-enhancement)
Existing lanes: none defined
Existing waves: none
Existing gates: completion criteria per TC
Existing state vocab: OPEN only (pre-enhancement)
Existing validation: single verification list at end
Existing evidence: none
Existing handoff: none
Duplicate plan risk: LOW — no competing execution files found
```

---

## Context: Root Causes, Not Symptoms

### What the Previous Analysis Got Wrong

The first-pass analysis listed visible gaps (Kilo has no config, codex-adapter.md has known gaps). That is the **symptom layer**. The root causes are structural and require redesign, not patching.

### Root Cause 1 — `codex: true` is an opt-out default, not evidence

`tools/capability_sync/inventory_capabilities.py` line 99:
```python
"codex": not skill.get("codex_excluded", False)
```
Since zero skills in `.supervisor/skill-registry.yaml` carry `codex_excluded: true`, every capability gets `codex: true` by default. The `FULL_PARITY` claim in `.governance/capabilities/registry.yaml` means "not excluded" — not "verified capable." This is a false assurance at the registry level.

### Root Cause 2 — No delivery mechanism to non-Claude agents

`AGENTS.md` capability table is generated Markdown, not a machine-readable data feed. Codex and Kilo have no documented runtime path to load, parse, or validate capability metadata. There is no API, bundle, or injection mechanism. Declaring parity in a Markdown file does not confer it.

### Root Cause 3 — Governance is prompt-only, not tool-enforced

`tools/governance/pre_mutation_guard.py` contains its own docstring:
> "KNOWN GAP (EP-002-GAP): This guard must be called EXPLICITLY by the agent. There is no automatic interception from the Claude Code or Codex tool layer. Agents can bypass this script by simply not calling it."

EP-007 (pre-commit hook) is `NOT_IMPLEMENTED`. EP-001, EP-004 are `PROMPT_ONLY`. The governance contract exists as text. The enforcement layer is missing.

### Root Cause 4 — Skill registry has no codex or kilo field

`.supervisor/skill-registry.yaml` has no `codex:` or `kilo:` fields at all. The inventory script derives surfaces from a default constant. Skill authors have no mechanism to declare "this skill is safe for Codex" because the field doesn't exist to set.

### Root Cause 5 — Kilo is a placeholder with zero functional integration

`.kilo/kilo.jsonc` is 2 lines. `.kilo/package.json` imports only `@kilocode/plugin`. No file access, no shell access, no tool APIs, no instruction file loading. The system recon marks it `ISSUE-DISC-001: effectively unused`. There is no adapter, no delivery path, no governance binding.

### What This Means for the Plan

The previous plan proposed patching adapters and adding validators. That is wrong because:
- You cannot complete adapters for platforms that have no delivery mechanism
- Adding validators that check file existence does not fix opt-out default logic
- Ordering adapters before pilots means building without a definition of "done"

**The correct order is:**
1. Fix the opt-out default at the source (skill-registry.yaml schema → inventory_capabilities.py)
2. Define what "done" looks like (canonical contract + pilot specifications)
3. Build a machine-readable delivery format all agents can consume
4. Implement enforcement at the tool layer, not just prompt layer
5. Build adapters against the contract and pilots
6. Run pilots to verify
7. Add drift prevention that catches future regressions

---

## Tradeoffs and Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Kilo AI platform capabilities are unknown from repo alone | HIGH | TC-ACP-001 includes explicit platform capability research before any adapter work |
| `codex: true` → `codex: false` for most skills will break parity-report.yaml | MEDIUM | TC-ACP-002 resets parity claims to CLAIMED_UNVERIFIED; this is a correctness improvement, not a regression |
| EP-007 (pre-commit hook) implementation may conflict with existing hooks | MEDIUM | TC-ACP-006-01 inspects existing hooks before writing new one; chain rather than replace |
| Pilot execution requires live API access to 3 platforms simultaneously | HIGH | Pilots defined as specifications (TC-ACP-004) before adapters; execution scoped to what is verifiable; unrunnable pilots documented as PENDING_RUNTIME |
| Adding 4 validators raises expected_count; future additions cause count conflicts | LOW | TC-ACP-015 switches runner to dynamic count derived from len(ALL_VALIDATORS) |
| Canonical contract creates new authority that may conflict with skill-only-policy.yaml | MEDIUM | Contract explicitly scopes to lifecycle semantics; skill-only-policy.yaml retains authority over skill execution mechanics |
| Codex has never been instantiated — parity claims are unverifiable at runtime | HIGH | All Codex entries marked COMPLETE_UNVERIFIED (not COMPLETE_VERIFIED) until live run confirms |

---

## REQUIREMENTS INVENTORY

| REQ-ID | Description | Source | Primary TC |
|--------|-------------|--------|------------|
| REQ-ACP-001 | Kilo platform capabilities must be researched before any adapter work | Root Cause 5 | TC-ACP-001 |
| REQ-ACP-002 | 22 RC capability areas must be derived and documented as machine-readable YAML | §"What This Means" | TC-ACP-001 |
| REQ-ACP-003 | `codex: true` opt-out default must be replaced with explicit opt-in field in skill-registry.yaml | Root Cause 4 | TC-ACP-002 |
| REQ-ACP-004 | `inventory_capabilities.py` compute_agent_surfaces must use opt-in logic for codex and kilo | Root Cause 1 | TC-ACP-002 |
| REQ-ACP-005 | Registry schemas must include kilo field | Root Cause 4 | TC-ACP-002 |
| REQ-ACP-006 | A single canonical machine-readable agent contract must exist covering all 22 RC areas | Root Cause 2 | TC-ACP-003 |
| REQ-ACP-007 | Pilot test specifications must be defined BEFORE adapters are built | §"Correct Order" | TC-ACP-004 |
| REQ-ACP-008 | A machine-readable agent bundle must replace AGENTS.md Markdown as delivery vehicle | Root Cause 2 | TC-ACP-005 |
| REQ-ACP-009 | pre_mutation_guard.py must be auto-invoked, not just available | Root Cause 3 | TC-ACP-006 |
| REQ-ACP-010 | DEC-014 must be re-classified based on actual Codex activation state | TC-ACP-006 description | TC-ACP-006 |
| REQ-ACP-011 | Claude adapter must be verified against canonical contract | §TC-ACP-007 | TC-ACP-007 |
| REQ-ACP-012 | Codex must have a full instruction file and lifecycle contract | §TC-ACP-008 | TC-ACP-008 |
| REQ-ACP-013 | All 120 skills must have explicit agent_surfaces.codex: true|false | §TC-ACP-008 | TC-ACP-008 |
| REQ-ACP-014 | Kilo must have KILO.md, kilo-adapter.md, and per-skill kilo surfaces | §TC-ACP-009 | TC-ACP-009 |
| REQ-ACP-015 | Model profiles must be defined and routing rules enforced | §TC-ACP-010 | TC-ACP-010 |
| REQ-ACP-016 | Inventory must reflect verified (not claimed) state of all 3 agents × 22 RC | §TC-ACP-011 | TC-ACP-011 |

---

## EXECUTION CONTROL LAYER

### Dependency Ordering (Critical Path)

```
TC-ACP-001 → TC-ACP-002 → TC-ACP-003 ─┬─→ TC-ACP-004 ─┐
                                        └─→ TC-ACP-005 ──┼─→ TC-ACP-006
                                                          │
TC-ACP-006 → TC-ACP-007 ─┐                               │
            TC-ACP-010 ──┼─→ TC-ACP-011 → TC-ACP-012 ───┘
TC-ACP-006 → TC-ACP-008 ─┤                ↓
TC-ACP-006 → TC-ACP-009 ─┘           TC-ACP-013 → TC-ACP-014 → TC-ACP-015 → TC-ACP-016

Parallel-safe pairs:
- TC-ACP-004 ∥ TC-ACP-005 (after TC-ACP-003)
- TC-ACP-007 ∥ TC-ACP-008 ∥ TC-ACP-009 ∥ TC-ACP-010 (after TC-ACP-006)
- TC-ACP-014 ∥ TC-ACP-015 (after TC-ACP-013)
```

---

### TC-ACP-001 — Platform Research and Capability Derivation

```
Parent Taskcard ID: TC-ACP-001
Title: Platform Research and Capability Derivation
Type: PARENT
Status: PROPOSED
Owner: agent/research-lane
Supervisor: governance-lane

Source:
  Plan requirement IDs: REQ-ACP-001, REQ-ACP-002
  Plan section: §TC-ACP-001 (original)
  Root cause: RC5 (Kilo is a placeholder), RC2 (no delivery mechanism)
  Selected solution: Research Kilo platform natively + derive RC model from system contracts

Objective:
  - Establish verified Kilo platform capabilities before any adapter work
  - Produce machine-readable required capability model (22 RC entries)

Outcome:
  - docs/agents/kilo-platform-capabilities.md exists with verified findings
  - docs/agents/required-capability-model.yaml exists with all 22 RC entries

Scope:
  Allowed files: .kilo/*, docs/agents/*, AGENTS.md, CLAUDE.md,
                 docs/automation/supervisor-worker-contract.md,
                 docs/governance/skill-only-policy.yaml,
                 plans/master-plan.md
  Forbidden files: src/*, tools/supervisor/*.py, .supervisor/skill-registry.yaml

Preserved behavior:
  - .kilo/kilo.jsonc and .kilo/package.json unchanged (read-only in this TC)
  - No product source mutations

Dependencies: NONE (first taskcard in DAG)

Child taskcards:
  - TC-ACP-001-01: Kilo Platform Capability Research
  - TC-ACP-001-02: Required Capability Model Derivation

Parent acceptance criteria:
  - docs/agents/kilo-platform-capabilities.md exists, non-empty, covers all 5 questions:
      native file I/O, shell access, tool calling, instruction file loading, system prompt injection
  - docs/agents/required-capability-model.yaml exists with exactly 22 RC entries
  - Every RC entry has: capability_id, name, purpose, required_inputs, required_outputs,
      achievable_on_kilo (true/false/unknown), blocking_reason (if false)
  - REQUIRED_AGENTIC_CAPABILITIES_NOT_DEFINED = 0

Evidence required:
  - docs/agents/kilo-platform-capabilities.md (committed)
  - docs/agents/required-capability-model.yaml (committed)

Rollback strategy:
  - If Kilo platform research yields no useful findings: mark all kilo achievability as "unknown"
    and proceed; do not block TC-ACP-002 on this

Stop conditions:
  - TRUE_EXTERNAL_GATE only (Kilo platform is inaccessible and no documentation exists)

Reroute rule:
  - If kilo-platform-capabilities.md is empty/stub: mark TC-ACP-001-01 REROUTED,
    research web documentation as alternative source
```

#### TC-ACP-001-01 — Kilo Platform Capability Research

```
Child Taskcard ID: TC-ACP-001-01
Parent: TC-ACP-001
Title: Kilo Platform Capability Research
Type: CHILD
Status: TODO

Purpose: Determine what Kilo AI can actually do as a platform before writing any adapter

Scope:
  Allowed files: .kilo/package.json, .kilo/kilo.jsonc,
                 docs/system-recon/FF-DEEP-RECON-20260705-052931/*.md
  Forbidden files: any src/ or tools/ files

Inputs:
  - .kilo/package.json (read)
  - .kilo/kilo.jsonc (read)
  - docs/system-recon/FF-DEEP-RECON-20260705-052931/01-SYSTEM-OVERVIEW.md (read)
  - docs/system-recon/FF-DEEP-RECON-20260705-052931/05-GAPS-CONTRADICTIONS-AND-OPEN-QUESTIONS.md (read)
  - Web search results for kilo.ai platform documentation

Expected output:
  - docs/agents/kilo-platform-capabilities.md with sections:
      1. Platform Summary
      2. Native Capabilities (file I/O, shell, tool calling, prompt injection, instruction files)
      3. Confirmed Limitations
      4. RC Achievability Map (RC-001 through RC-022: achievable/blocked/unknown)
      5. Peer Parity Assessment

Preconditions: None

Micro-steps:
  MS-001-01-01:
    action: Read .kilo/package.json in full; record all declared dependencies, scripts, and APIs
    target: .kilo/package.json
    operation: inspect
    expected: Package name, version, @kilocode/plugin dependency, any script entries
    check: File read succeeds; content captured in working notes
    failure: If file missing → record MISSING in output; proceed to MS-001-01-02
    next: MS-001-01-02

  MS-001-01-02:
    action: Read .kilo/kilo.jsonc in full; record all configuration fields
    target: .kilo/kilo.jsonc
    operation: inspect
    expected: Schema URL (https://app.kilo.ai/config.json), snapshot: false, any other fields
    check: File read succeeds; all fields recorded
    failure: If file missing → record MISSING; proceed
    next: MS-001-01-03

  MS-001-01-03:
    action: Read docs/system-recon/FF-DEEP-RECON-20260705-052931/01-SYSTEM-OVERVIEW.md;
            find and record the Kilo-related paragraph(s)
    target: docs/system-recon/FF-DEEP-RECON-20260705-052931/01-SYSTEM-OVERVIEW.md
    operation: inspect
    expected: Kilo AI platform description, current integration status
    check: Kilo section found; ISSUE-DISC-001 text captured
    failure: If file missing → skip; record "recon not available"
    next: MS-001-01-04

  MS-001-01-04:
    action: Web search "kilo.ai agent platform file access shell execution tool calling API 2024 2025"
    operation: web-search
    expected: Official documentation or credible sources describing Kilo's native capabilities
    check: At least 2 sources found describing platform capabilities
    failure: If no results → record "web search inconclusive"; use .kilo/ config as sole source
    next: MS-001-01-05

  MS-001-01-05:
    action: Create docs/agents/kilo-platform-capabilities.md with all findings organized into
            the 5 required sections; classify each of 22 RC capability areas as
            achievable/blocked/unknown for Kilo based on research
    target: docs/agents/kilo-platform-capabilities.md (CREATE)
    operation: create
    expected: Non-empty markdown file with all 5 sections; RC achievability table present
    check: File exists; has 22 RC rows in achievability table; all marked achievable/blocked/unknown
    failure: If classification is uncertain → mark unknown; do not invent
    next: TC-ACP-001-01 IMPLEMENTED

Acceptance checks:
  - docs/agents/kilo-platform-capabilities.md exists with >= 200 words of real content
  - RC achievability table present with all 22 rows
  - No row is blank — each has one of: achievable, blocked, unknown

Evidence: docs/agents/kilo-platform-capabilities.md (file path + SHA-256)
```

#### TC-ACP-001-02 — Required Capability Model Derivation

```
Child Taskcard ID: TC-ACP-001-02
Parent: TC-ACP-001
Title: Required Capability Model Derivation
Type: CHILD
Status: TODO

Purpose: Produce machine-readable YAML of 22 required agentic capabilities
         derived from system contracts, not from any single agent's config

Scope:
  Allowed files: AGENTS.md, CLAUDE.md,
                 docs/automation/supervisor-worker-contract.md,
                 docs/governance/skill-only-policy.yaml,
                 plans/master-plan.md (read-only),
                 docs/agents/kilo-platform-capabilities.md (read, from TC-ACP-001-01),
                 docs/agents/required-capability-model.yaml (CREATE)
  Forbidden: any src/ writes, any .supervisor/ writes

Inputs:
  - docs/agents/kilo-platform-capabilities.md (TC-ACP-001-01 output)
  - AGENTS.md §A through §AC
  - CLAUDE.md §Session Start through §Sprint Closeout
  - docs/automation/supervisor-worker-contract.md

Expected output:
  - docs/agents/required-capability-model.yaml with 22 RC entries

Preconditions:
  - TC-ACP-001-01 IMPLEMENTED

Micro-steps:
  MS-001-02-01:
    action: Read AGENTS.md lines 1-200; identify and list all agent lifecycle phases
            (reconnaissance, planning, execution, evidence, continuation, closure)
    target: AGENTS.md
    operation: inspect
    expected: Named lifecycle phases; note which sections (A, B, C...) cover each phase
    check: At least 6 phases identified; section references recorded
    failure: If AGENTS.md unreadable → use CLAUDE.md as alternate source
    next: MS-001-02-02

  MS-001-02-02:
    action: Read docs/automation/supervisor-worker-contract.md in full;
            list all capability areas mentioned (evidence capture, grading, etc.)
    target: docs/automation/supervisor-worker-contract.md
    operation: inspect
    expected: Worker obligations, supervisor obligations, proof levels, declaration fields
    check: Obligations section found; proof levels (none/synthetic/real-test/verified) recorded
    failure: If file missing → derive from CLAUDE.md sprint closeout section only
    next: MS-001-02-03

  MS-001-02-03:
    action: Read docs/governance/skill-only-policy.yaml in full;
            note all governed operations (15 categories) and enforcement points
    target: docs/governance/skill-only-policy.yaml
    operation: inspect
    expected: 15 governed operation types; 8 enforcement points (EP-001 through EP-008)
    check: EP list found; governed_operations list found
    failure: If file missing → derive from codex-adapter.md
    next: MS-001-02-04

  MS-001-02-04:
    action: Synthesize findings from MS-001-02-01 through MS-001-02-03 into 22 capability names;
            record as working notes mapping each RC ID to source section
    operation: record
    expected: List of 22 RC names, each traceable to a source document section
    check: Exactly 22 items; each has a source reference; no duplicates
    failure: If fewer than 22 → add remaining from CLAUDE.md §Human-Free Autonomy Doctrine
    next: MS-001-02-05

  MS-001-02-05:
    action: Create docs/agents/required-capability-model.yaml;
            write header + first 11 RC entries (RC-001 through RC-011)
            using schema: capability_id, name, purpose, required_inputs, required_outputs,
            allowed_actions, forbidden_actions, state_read, state_written, minimum_tooling,
            minimum_model_traits, fallback_behavior, achievable_on_kilo, blocking_reason
    target: docs/agents/required-capability-model.yaml (CREATE)
    operation: create
    expected: Valid YAML with 11 RC entries; all required fields present
    check: File exists; python -c "import yaml; yaml.safe_load(open('...').read())" passes
    failure: On YAML parse error → fix the offending block; do not proceed until valid
    next: MS-001-02-06

  MS-001-02-06:
    action: Append RC-012 through RC-022 to docs/agents/required-capability-model.yaml;
            for each, add achievable_on_kilo from kilo-platform-capabilities.md RC table
    target: docs/agents/required-capability-model.yaml (EDIT)
    operation: edit
    expected: File now has 22 RC entries; kilo achievability populated from TC-ACP-001-01 findings
    check: Count RC entries: grep -c "capability_id: RC-" → 22
    failure: If kilo achievability unknown for some RCs → mark unknown; do not leave blank
    next: MS-001-02-07

  MS-001-02-07:
    action: Validate docs/agents/required-capability-model.yaml:
            (1) parse YAML, (2) count entries = 22, (3) verify each has all required fields,
            (4) verify no achievable_on_kilo field is empty
    operation: validate
    expected: 22 entries, all fields present, no empty achievable_on_kilo values
    check: All 4 validation checks pass
    failure: Fix missing fields; re-validate
    next: TC-ACP-001-02 IMPLEMENTED

Acceptance checks:
  - docs/agents/required-capability-model.yaml parses as valid YAML
  - exactly 22 entries (count: grep -c "capability_id: RC-")
  - every entry has achievable_on_kilo value

Evidence: docs/agents/required-capability-model.yaml (file path + line count)
```

---

### TC-ACP-002 — Fix Opt-Out Default at the Source

```
Parent Taskcard ID: TC-ACP-002
Title: Fix Opt-Out Default at the Source
Type: PARENT
Status: PROPOSED
Owner: agent/infrastructure-lane
Supervisor: governance-lane

Source:
  Plan requirement IDs: REQ-ACP-003, REQ-ACP-004, REQ-ACP-005
  Root cause: RC1 (codex: true is opt-out default), RC4 (no codex/kilo field in registry)
  Selected solution: Add agent_surfaces schema to skill-registry; fix inventory_capabilities.py
                     to use opt-in; add kilo column to all schemas

Objective:
  - Replace false-assurance opt-out default with honest opt-in per-skill declaration
  - Add kilo column to all capability schemas

Outcome:
  - inventory_capabilities.py uses skill.get("agent_surfaces", {}).get("codex", False)
  - All capability schemas include kilo field
  - Running run_sync.py produces codex: false, kilo: false for unannotated skills

Scope:
  Allowed files: tools/capability_sync/inventory_capabilities.py,
                 tools/capability_sync/run_sync.py (read-only for understanding),
                 .supervisor/skill-registry.yaml (schema section only),
                 .governance/capabilities/schemas/capability.schema.json,
                 .governance/capabilities/schemas/parity-report.schema.json,
                 .governance/capabilities/registry.yaml (via run_sync.py only),
                 .governance/capabilities/parity-report.yaml
  Forbidden: src/*, any skill entry data in skill-registry.yaml (only schema metadata),
             any AGENTS.md writes

Preserved behavior:
  - claude_code surface derivation unchanged (still uses command file existence check)
  - ci surface derivation unchanged (still uses routing registry)
  - All existing 165 governance validators unchanged

Dependencies: TC-ACP-001 CLOSED (needs RC model to understand what "kilo" means)

Child taskcards:
  - TC-ACP-002-01: Read and map existing sync pipeline
  - TC-ACP-002-02: Add agent_surfaces schema block to skill-registry.yaml
  - TC-ACP-002-03: Fix compute_agent_surfaces in inventory_capabilities.py
  - TC-ACP-002-04: Add kilo field to governance schemas
  - TC-ACP-002-05: Regenerate registry and correct parity_status

Parent acceptance criteria:
  - inventory_capabilities.py: "codex_excluded" pattern absent; opt-in pattern present
  - .governance/capabilities/schemas/capability.schema.json includes "kilo" in agent_surfaces
  - Running run_sync.py regenerates registry with kilo column; no skills show codex: true by default
  - DUPLICATED_AGENT_GOVERNANCE_IMPLEMENTATIONS_WITHOUT_JUSTIFICATION = 0

Evidence required:
  - git diff of inventory_capabilities.py showing opt-in change
  - git diff of capability.schema.json showing kilo field addition
  - Output of run_sync.py (success log)

Rollback strategy:
  - If run_sync.py breaks after inventory_capabilities.py change: revert compute_agent_surfaces
    only; leave schema changes in place; investigate pipeline before re-applying

Stop conditions:
  - If run_sync.py has critical dependency on codex_excluded pattern: file investigation taskcard
    to understand full impact before proceeding

Reroute rule:
  - If pipeline has a downstream consumer that breaks on kilo: false addition: add compatibility
    shim; mark TC-ACP-002-04 REROUTED; investigate consumer first
```

#### TC-ACP-002-01 — Read and Map Existing Sync Pipeline

```
Child Taskcard ID: TC-ACP-002-01
Parent: TC-ACP-002
Type: CHILD / INVESTIGATION
Status: TODO

Purpose: Understand full pipeline before any changes; identify all downstream consumers of
         codex/kilo fields; prevent regressions in later steps

Scope:
  Allowed: tools/capability_sync/*.py, .governance/capabilities/ (read-only)
  Forbidden: any writes

Inputs: tools/capability_sync/inventory_capabilities.py, run_sync.py, any other *.py in capability_sync/

Expected output: Working notes mapping:
  - compute_agent_surfaces function: exact line numbers, logic, all callers
  - All files that read .governance/capabilities/registry.yaml
  - All downstream consumers of codex/kilo fields in registry.yaml

Micro-steps:
  MS-002-01-01:
    action: Read tools/capability_sync/inventory_capabilities.py in full;
            locate compute_agent_surfaces function; record exact line numbers and logic
    target: tools/capability_sync/inventory_capabilities.py
    operation: inspect
    expected: Line number of compute_agent_surfaces; current codex logic ("not skill.get('codex_excluded', False)")
    check: Line number recorded; exact logic copied to notes
    failure: If function not found → search for "codex" in file; record what you find
    next: MS-002-01-02

  MS-002-01-02:
    action: Read tools/capability_sync/run_sync.py in full;
            record all steps it executes in order; note if it validates output
    target: tools/capability_sync/run_sync.py
    operation: inspect
    expected: Ordered list of sync steps; whether it runs tests after generation
    check: Step list recorded; any post-sync validation noted
    failure: If file is an entry point only → look for called modules; record them
    next: MS-002-01-03

  MS-002-01-03:
    action: Search for all files that read .governance/capabilities/registry.yaml;
            record each consumer and what fields it reads from registry
    target: .governance/capabilities/registry.yaml consumers (grep search)
    operation: inspect
    expected: List of consumers (AGENTS.md generator, parity-report generator, CLAUDE.md updater, etc.)
    check: At least 3 consumers identified; codex/kilo field usage noted per consumer
    failure: If grep finds nothing → search for "registry.yaml" string in all .py files
    next: TC-ACP-002-01 IMPLEMENTED

Acceptance checks:
  - compute_agent_surfaces line number documented
  - All consumers of codex field in registry.yaml listed
  - Sync pipeline step order documented

Evidence: Working notes recorded in plan or evidence file
```

#### TC-ACP-002-02 — Add agent_surfaces Schema Block to skill-registry.yaml

```
Child Taskcard ID: TC-ACP-002-02
Parent: TC-ACP-002
Type: CHILD
Status: TODO

Purpose: Create the schema-level declaration that allows skill authors to explicitly set
         codex: true or kilo: true per skill; without this field, no skill can opt in

Scope:
  Allowed: .supervisor/skill-registry.yaml (schema/comment section ONLY)
  Forbidden: Any skill entry data changes; any src/ files

Inputs: .supervisor/skill-registry.yaml (lines 1-80 for schema format)

Expected output: .supervisor/skill-registry.yaml schema section updated to include
  agent_surfaces block with codex and kilo boolean fields

Preconditions: TC-ACP-002-01 IMPLEMENTED

Micro-steps:
  MS-002-02-01:
    action: Read .supervisor/skill-registry.yaml lines 1-80;
            identify where schema documentation or comments appear;
            record the existing schema structure
    target: .supervisor/skill-registry.yaml
    operation: inspect
    expected: Schema section found; existing fields documented; location for insertion identified
    check: Schema location recorded; existing field names copied to notes
    failure: If no schema section → find first skill entry structure; use as template
    next: MS-002-02-02

  MS-002-02-02:
    action: Edit .supervisor/skill-registry.yaml to add agent_surfaces schema block
            in the schema comment section (NOT in individual skill entries):
            ```
            # agent_surfaces: (optional block per skill)
            #   codex: false       # must be explicitly set true; not the default
            #   kilo: false        # must be explicitly set true; not the default
            #   codex_justification: <required when codex: true>
            #   kilo_justification:  <required when kilo: true>
            ```
    target: .supervisor/skill-registry.yaml (schema/comment section)
    operation: edit
    expected: Schema comment added without touching any skill entry data
    check: git diff shows only additions in comment/schema section;
           no existing skill entry data changed
    failure: If diff shows skill entry changes → revert; apply only to comment section
    next: MS-002-02-03

  MS-002-02-03:
    action: Validate .supervisor/skill-registry.yaml still parses as valid YAML after edit
    operation: validate
    expected: python -c "import yaml; yaml.safe_load(open('.supervisor/skill-registry.yaml').read())" exits 0
    check: No YAML parse error
    failure: Fix YAML syntax error; re-validate before proceeding
    next: TC-ACP-002-02 IMPLEMENTED

Acceptance checks:
  - .supervisor/skill-registry.yaml parses as valid YAML
  - agent_surfaces schema comment present in schema section
  - No individual skill entries changed
```

#### TC-ACP-002-03 — Fix compute_agent_surfaces in inventory_capabilities.py

```
Child Taskcard ID: TC-ACP-002-03
Parent: TC-ACP-002
Type: CHILD
Status: TODO

Purpose: Replace the opt-out default with opt-in logic for codex and kilo;
         add kilo to the generated agent_surfaces output

Scope:
  Allowed: tools/capability_sync/inventory_capabilities.py
  Forbidden: any other file in capability_sync/; no src/ changes

Inputs: tools/capability_sync/inventory_capabilities.py (current state from TC-ACP-002-01)

Expected output: compute_agent_surfaces returns codex: false and kilo: false by default;
                 returns true only when skill has explicit agent_surfaces.codex: true
                 or agent_surfaces.kilo: true

Preconditions: TC-ACP-002-01 IMPLEMENTED, TC-ACP-002-02 IMPLEMENTED

Micro-steps:
  MS-002-03-01:
    action: Open tools/capability_sync/inventory_capabilities.py;
            locate the exact line containing:
            "codex": not skill.get("codex_excluded", False)
            Record line number
    target: tools/capability_sync/inventory_capabilities.py
    operation: inspect
    expected: Exact line number of the offending pattern
    check: Line found; "codex_excluded" pattern confirmed
    failure: If pattern differs slightly → find closest match; adapt the replacement
    next: MS-002-03-02

  MS-002-03-02:
    action: Edit tools/capability_sync/inventory_capabilities.py:
            Replace:
              "codex": not skill.get("codex_excluded", False),
            With:
              "codex": bool(skill.get("agent_surfaces", {}).get("codex", False)),
              "kilo":  bool(skill.get("agent_surfaces", {}).get("kilo",  False)),
    target: tools/capability_sync/inventory_capabilities.py (single function)
    operation: edit
    expected: Replacement made; kilo line added immediately after codex line
    check: git diff shows exactly these 2 lines changed (1 replaced, 1 added)
    failure: If other lines changed → revert; apply only this targeted change
    next: MS-002-03-03

  MS-002-03-03:
    action: Search inventory_capabilities.py for any remaining references to "codex_excluded";
            record if any found
    target: tools/capability_sync/inventory_capabilities.py
    operation: inspect
    expected: Zero remaining "codex_excluded" references
    check: grep result is empty
    failure: If references found elsewhere → evaluate each; remove/replace if they propagate
             the same opt-out pattern; otherwise document and leave
    next: MS-002-03-04

  MS-002-03-04:
    action: Run a focused unit test of compute_agent_surfaces:
            python -c "
            import sys; sys.path.insert(0, 'tools/capability_sync')
            from inventory_capabilities import compute_agent_surfaces
            skill_no_surfaces = {'skill_id': 'test', 'command_file': ''}
            skill_with_codex = {'skill_id': 'test', 'command_file': '',
                                 'agent_surfaces': {'codex': True, 'kilo': False}}
            r1 = compute_agent_surfaces(skill_no_surfaces, set(), {})
            r2 = compute_agent_surfaces(skill_with_codex, set(), {})
            assert r1.get('codex') == False, f'opt-out default broken: {r1}'
            assert r1.get('kilo') == False, f'kilo default broken: {r1}'
            assert r2.get('codex') == True, f'opt-in not working: {r2}'
            print('PASS')
            "
    operation: run
    expected: Output: PASS
    check: Exit code 0, output contains "PASS"
    failure: If AssertionError → fix the logic change; re-run until PASS
    next: TC-ACP-002-03 IMPLEMENTED

Acceptance checks:
  - compute_agent_surfaces returns codex: False when skill has no agent_surfaces
  - compute_agent_surfaces returns codex: True when skill has agent_surfaces.codex: True
  - kilo field present in output; same opt-in behavior
  - No "codex_excluded" pattern remaining (unless used for backward compat documentation)
```

#### TC-ACP-002-04 — Add kilo Field to Governance Schemas

```
Child Taskcard ID: TC-ACP-002-04
Parent: TC-ACP-002
Type: CHILD
Status: TODO

Purpose: Add kilo to the JSON Schema definitions so downstream consumers treat it as a
         required/known field; prevents silent failures when kilo is generated but schema rejects it

Scope:
  Allowed: .governance/capabilities/schemas/capability.schema.json,
            .governance/capabilities/schemas/parity-report.schema.json
  Forbidden: any other files

Preconditions: TC-ACP-002-01 IMPLEMENTED (need to understand schema consumers)

Micro-steps:
  MS-002-04-01:
    action: Read .governance/capabilities/schemas/capability.schema.json in full;
            locate agent_surfaces object definition; record its current fields
    target: .governance/capabilities/schemas/capability.schema.json
    operation: inspect
    expected: JSON Schema object for agent_surfaces; fields: claude_code, codex, ci (booleans)
    check: agent_surfaces object found; existing field names recorded
    failure: If schema uses different structure → adapt insertion to match actual structure
    next: MS-002-04-02

  MS-002-04-02:
    action: Edit .governance/capabilities/schemas/capability.schema.json:
            In the agent_surfaces object, add after the "ci" field:
            "kilo": { "type": "boolean", "description": "Kilo AI agent surface" }
    target: .governance/capabilities/schemas/capability.schema.json
    operation: edit
    expected: kilo field added to agent_surfaces; JSON remains valid
    check: python -c "import json; json.load(open('.governance/capabilities/schemas/capability.schema.json'))"
    failure: JSON parse error → fix syntax; re-validate
    next: MS-002-04-03

  MS-002-04-03:
    action: Read .governance/capabilities/schemas/parity-report.schema.json in full;
            locate where codex parity fields are defined; add equivalent kilo fields
    target: .governance/capabilities/schemas/parity-report.schema.json
    operation: inspect then edit
    expected: parity-report schema now includes kilo section parallel to codex section
    check: python -c "import json; json.load(open('.governance/capabilities/schemas/parity-report.schema.json'))"
    failure: JSON parse error → fix; re-validate
    next: TC-ACP-002-04 IMPLEMENTED

Acceptance checks:
  - Both schema files parse as valid JSON
  - capability.schema.json includes kilo in agent_surfaces
  - parity-report.schema.json includes kilo section
```

#### TC-ACP-002-05 — Regenerate Registry and Correct parity_status

```
Child Taskcard ID: TC-ACP-002-05
Parent: TC-ACP-002
Type: CHILD
Status: TODO

Purpose: Apply the opt-in changes by running the sync pipeline; correct any entries
         that falsely claimed FULL_PARITY without runtime evidence

Scope:
  Allowed: tools/capability_sync/run_sync.py (execute),
            .governance/capabilities/registry.yaml (via run_sync.py output),
            .governance/capabilities/parity-report.yaml
  Forbidden: manual edits to registry.yaml; any src/ changes

Preconditions: TC-ACP-002-02, TC-ACP-002-03, TC-ACP-002-04 all IMPLEMENTED

Micro-steps:
  MS-002-05-01:
    action: Run python tools/capability_sync/run_sync.py
    operation: run
    expected: Exit code 0; .governance/capabilities/registry.yaml updated;
              kilo: false present for all skills that have no agent_surfaces.kilo: true
    check: Exit code 0; grep "kilo:" .governance/capabilities/registry.yaml | wc -l > 0
    failure: If exit non-zero → read error output; investigate broken step; fix before retrying
    next: MS-002-05-02

  MS-002-05-02:
    action: Verify .governance/capabilities/registry.yaml now has kilo column:
            grep -c "kilo: false" .governance/capabilities/registry.yaml
            Expected: > 100 (all skills default to false)
    operation: validate
    expected: count > 100
    check: Command returns number > 100
    failure: If count = 0 → run_sync.py did not use updated inventory_capabilities.py;
             investigate; may need to re-run after ensuring module reload
    next: MS-002-05-03

  MS-002-05-03:
    action: Verify codex: true no longer appears for any skills that have no agent_surfaces:
            grep "codex: true" .governance/capabilities/registry.yaml | wc -l → 0
            (All should now be false since no skills have explicit agent_surfaces.codex: true yet)
    operation: validate
    expected: count = 0
    check: count = 0
    failure: If count > 0 → some skills still have the old opt-out value cached;
             investigate if run_sync.py reads from a cache; clear and re-run
    next: MS-002-05-04

  MS-002-05-04:
    action: Update .governance/capabilities/parity-report.yaml to add Kilo section;
            change any entry with parity_status: FULL_PARITY and codex: false to
            parity_status: CLAIMED_UNVERIFIED
    target: .governance/capabilities/parity-report.yaml
    operation: edit
    expected: Kilo section present; no FULL_PARITY entries for capabilities with codex: false
    check: File parses as valid YAML; Kilo section present; parity_status corrections applied
    failure: If file is auto-generated → run_sync.py should update it; if not, edit manually
    next: TC-ACP-002-05 IMPLEMENTED

Acceptance checks:
  - registry.yaml: kilo: false for all 120+ active skills (no explicit opt-in yet)
  - registry.yaml: codex: false for all skills (no remaining opt-out defaults)
  - parity-report.yaml: Kilo section present
  - parity-report.yaml: no FULL_PARITY entries where codex: false
```

---

### TC-ACP-003 — Canonical Agent Contract

```
Parent Taskcard ID: TC-ACP-003
Title: Canonical Agent Contract
Type: PARENT
Status: PROPOSED
Owner: agent/architecture-lane
Supervisor: governance-lane

Source:
  Plan requirement IDs: REQ-ACP-006
  Root cause: RC2 (no delivery mechanism), RC3 (governance prompt-only)
  Selected solution: Create docs/agents/canonical-agent-contract.yaml as the single
                     authoritative lifecycle contract for all 3 agents

Objective:
  - Produce one machine-readable contract that defines lifecycle semantics
    for all 22 RC capabilities across Claude, Codex, and Kilo

Outcome:
  - docs/agents/canonical-agent-contract.yaml exists with all required sections
  - Contract is referenced by all adapter files as authority for lifecycle semantics

Scope:
  Allowed: docs/agents/canonical-agent-contract.yaml (CREATE),
            docs/agents/required-capability-model.yaml (read, from TC-ACP-001)
  Forbidden: docs/governance/skill-only-policy.yaml (do not modify; it has separate authority),
             AGENTS.md (do not modify), CLAUDE.md (do not modify)

Preserved behavior:
  - skill-only-policy.yaml retains authority over skill execution mechanics
  - AGENTS.md table generation unchanged
  - CLAUDE.md unchanged

Dependencies: TC-ACP-001 CLOSED (needs RC entries from required-capability-model.yaml)

Child taskcards:
  - TC-ACP-003-01: Write contract header, authority order, and RC entry schema
  - TC-ACP-003-02: Write all 22 RC capability entries
  - TC-ACP-003-03: Write delivery mechanisms and conflict resolution sections

Parent acceptance criteria:
  - docs/agents/canonical-agent-contract.yaml parses as valid YAML
  - Contains all required sections: contract_id, version, authority_order,
    capability_semantics (22 entries), delivery_mechanisms, conflict_resolution
  - AGENT_SPECIFIC_CAPABILITIES_WITHOUT_SHARED_CONTRACT = 0
```

#### TC-ACP-003-01 — Contract Header and RC Schema

```
Child TC: TC-ACP-003-01 | Parent: TC-ACP-003 | Status: TODO

Micro-steps:
  MS-003-01-01:
    action: Create docs/agents/canonical-agent-contract.yaml with header section:
            contract_id, version, scope_note (lifecycle semantics only),
            authority_order (6-level hierarchy), not_governed_by_this_contract list
    target: docs/agents/canonical-agent-contract.yaml (CREATE)
    operation: create
    expected: Valid YAML header; authority_order has 6 entries starting with plans/master-plan.md
    check: File exists; python -c "import yaml; d=yaml.safe_load(open('docs/agents/canonical-agent-contract.yaml').read()); assert 'authority_order' in d"
    failure: YAML parse error → fix; re-validate
    next: MS-003-01-02

  MS-003-01-02:
    action: Add capability_semantics list to the YAML with the RC entry schema definition
            (as a comment block) and begin writing RC-001:
            capability_id, name, purpose, required_inputs, required_outputs,
            proof_level, evidence_requirements, failure_behavior, continuation_rule,
            review_requirement, promotion_criteria, closure_criteria, conflict_resolution,
            model_suitability (minimum_tier, reasoning_required, context_required)
    target: docs/agents/canonical-agent-contract.yaml
    operation: edit
    expected: capability_semantics list started; RC-001 entry complete
    check: yaml.safe_load succeeds; RC-001 entry has all 14 fields
    failure: Missing field → add it; do not leave fields blank or null without reason
    next: TC-ACP-003-01 IMPLEMENTED
```

#### TC-ACP-003-02 — Write All 22 RC Entries

```
Child TC: TC-ACP-003-02 | Parent: TC-ACP-003 | Status: TODO
Preconditions: TC-ACP-003-01 IMPLEMENTED

Micro-steps:
  MS-003-02-01:
    action: Write RC-001 through RC-006:
            RC-001 (repository-reconnaissance), RC-002 (authority-discovery),
            RC-003 (plan-ingestion), RC-004 (plan-hardening),
            RC-005 (plan-binding), RC-006 (requirement-reconciliation)
            Each must have all 14 fields; derive content from required-capability-model.yaml
    target: docs/agents/canonical-agent-contract.yaml
    operation: edit
    expected: 6 complete RC entries; all fields populated
    check: Count capability entries: grep -c "capability_id:" → increases by 6
    failure: If content is unclear for a field → use required_inputs: [TBD] and note it
    next: MS-003-02-02

  MS-003-02-02:
    action: Write RC-007 through RC-012:
            RC-007 (taskcard-generation), RC-008 (dependency-queue-lane-management),
            RC-009 (file-mutation-ownership), RC-010 (safe-source-writing),
            RC-011 (complete-file-diff-review), RC-012 (architecture-aware-work)
            For RC-010, RC-011: set model_suitability.minimum_tier: high
    target: docs/agents/canonical-agent-contract.yaml
    operation: edit
    expected: 6 more RC entries; RC-010/011/012 have minimum_tier: high
    check: count increases by 6; RC-010 has minimum_tier: high
    next: MS-003-02-03

  MS-003-02-03:
    action: Write RC-013 through RC-022:
            RC-013 (qname-aspose-governance), RC-014 (test-validation-execution),
            RC-015 (evidence-capture-provenance), RC-016 (root-cause-analysis),
            RC-017 (failure-healing), RC-018 (replanning-autonomous-continuation),
            RC-019 (e2e-pilot-proof), RC-020 (independent-review),
            RC-021 (promotion-release-governance), RC-022 (closure-external-blocker-decisions)
            RC-016, RC-020: minimum_tier: high
    target: docs/agents/canonical-agent-contract.yaml
    operation: edit
    expected: 10 more RC entries; total = 22
    check: grep -c "capability_id:" → 22
    failure: Count not 22 → add missing entries; do not proceed until 22
    next: MS-003-02-04

  MS-003-02-04:
    action: Validate full YAML: python -c "
            import yaml
            d = yaml.safe_load(open('docs/agents/canonical-agent-contract.yaml').read())
            entries = d['capability_semantics']
            assert len(entries) == 22, f'Expected 22, got {len(entries)}'
            required = ['capability_id','name','purpose','proof_level','failure_behavior',
                        'model_suitability']
            for e in entries:
                for f in required:
                    assert f in e, f'Missing {f} in {e.get(\"capability_id\")}'
            print('PASS: 22 entries, all required fields present')
            "
    operation: validate
    expected: PASS message printed
    check: Exit code 0; PASS in output
    failure: Fix missing entry or field; re-validate
    next: TC-ACP-003-02 IMPLEMENTED
```

#### TC-ACP-003-03 — Delivery Mechanisms and Conflict Resolution

```
Child TC: TC-ACP-003-03 | Parent: TC-ACP-003 | Status: TODO
Preconditions: TC-ACP-003-02 IMPLEMENTED

Micro-steps:
  MS-003-03-01:
    action: Add delivery_mechanisms section to canonical-agent-contract.yaml with
            3 subsections (claude, codex, kilo), each specifying:
            instruction_file, context_loading, enforcement, entry_point
    target: docs/agents/canonical-agent-contract.yaml
    operation: edit
    expected: delivery_mechanisms section with 3 agent entries
    check: grep "delivery_mechanisms:" docs/agents/canonical-agent-contract.yaml → found
    next: MS-003-03-02

  MS-003-03-02:
    action: Add conflict_resolution section:
            - When agents produce different results for same task: Claude verdict is authority
            - Codex/Kilo must escalate disagreements to supervisor loop
            - Proof levels: verified > real-test > synthetic > none (higher supersedes lower)
            - Cross-agent consistency is semantic, not textual
    target: docs/agents/canonical-agent-contract.yaml
    operation: edit
    expected: conflict_resolution section present with 4 rules
    check: grep "conflict_resolution:" → found
    next: MS-003-03-03

  MS-003-03-03:
    action: Final validation: python -c "
            import yaml
            d = yaml.safe_load(open('docs/agents/canonical-agent-contract.yaml').read())
            assert 'capability_semantics' in d
            assert 'delivery_mechanisms' in d
            assert 'conflict_resolution' in d
            assert 'authority_order' in d
            print('PASS')
            "
    operation: validate
    expected: PASS
    failure: Fix missing section; re-validate
    next: TC-ACP-003-03 IMPLEMENTED
```

---

### TC-ACP-004 — Pilot Specifications (Before Adapters)

```
Parent Taskcard ID: TC-ACP-004
Title: Pilot Specifications — Define Before Building Adapters
Type: PARENT
Status: PROPOSED
Owner: agent/qa-lane
Supervisor: governance-lane

Source:
  Plan requirement ID: REQ-ACP-007
  Root cause: (ordering mistake) adapters built before acceptance tests defined
  Selected solution: Define 12 pilot specs as YAML; adapters built to pass these specs

Objective: Produce docs/agents/pilots/pilot-specs.yaml with 12 complete pilot specifications
           before any adapter (TC-ACP-007, TC-ACP-008, TC-ACP-009) begins

Scope:
  Allowed: docs/agents/pilots/pilot-specs.yaml (CREATE)
  Forbidden: any implementation files; do not execute pilots here (that is TC-ACP-013)

Dependencies: TC-ACP-003 CLOSED (needs RC IDs from canonical contract)

Child taskcards:
  - TC-ACP-004-01: Write pilot schema and pilots PILOT-001 through PILOT-006
  - TC-ACP-004-02: Write pilots PILOT-007 through PILOT-012 and validate all 12
```

#### TC-ACP-004-01 — Pilots 1–6

```
Child TC: TC-ACP-004-01 | Parent: TC-ACP-004 | Status: TODO

Micro-steps:
  MS-004-01-01:
    action: Create docs/agents/pilots/ directory (if not exists);
            create docs/agents/pilots/pilot-specs.yaml with file header and pilot schema
            (id, name, maps_to, task, success_criteria, failure_criteria,
            per_agent_mechanism, verification, run_status)
    target: docs/agents/pilots/pilot-specs.yaml (CREATE)
    operation: create
    expected: Directory exists; file exists with schema comment
    check: File exists; valid YAML
    next: MS-004-01-02

  MS-004-01-02:
    action: Write PILOT-001 (repository-reconnaissance) and PILOT-002 (plan-import-binding)
            Each: task description, ≥3 success criteria, ≥2 failure criteria,
            per_agent_mechanism for claude/codex/kilo, verification method, run_status: PENDING_EXECUTION
    target: docs/agents/pilots/pilot-specs.yaml
    operation: edit
    expected: 2 pilot entries present; all required fields populated
    check: grep -c "id: PILOT-" → 2
    next: MS-004-01-03

  MS-004-01-03:
    action: Write PILOT-003 (taskcard-generation), PILOT-004 (bounded-code-change),
            PILOT-005 (complete-file-diff-review), PILOT-006 (test-evidence-generation)
    target: docs/agents/pilots/pilot-specs.yaml
    operation: edit
    expected: 4 more pilot entries; total = 6
    check: grep -c "id: PILOT-" → 6
    failure: If any field is unclear → use placeholder with NEEDS_CLARIFICATION marker
    next: TC-ACP-004-01 IMPLEMENTED
```

#### TC-ACP-004-02 — Pilots 7–12 and Validation

```
Child TC: TC-ACP-004-02 | Parent: TC-ACP-004 | Status: TODO

Micro-steps:
  MS-004-02-01:
    action: Write PILOT-007 (failure-diagnosis-repair), PILOT-008 (autonomous-resume),
            PILOT-009 (independent-review), PILOT-010 (rejection-of-insufficient-proof)
    target: docs/agents/pilots/pilot-specs.yaml
    operation: edit
    expected: 4 more entries; total = 10
    check: grep -c "id: PILOT-" → 10
    next: MS-004-02-02

  MS-004-02-02:
    action: Write PILOT-011 (promotion-or-reopening-decision), PILOT-012 (idempotent-rerun)
    target: docs/agents/pilots/pilot-specs.yaml
    operation: edit
    expected: 2 more entries; total = 12
    check: grep -c "id: PILOT-" → 12
    next: MS-004-02-03

  MS-004-02-03:
    action: Validate pilot-specs.yaml: parse YAML; count = 12;
            verify each entry has id, name, maps_to, task, success_criteria,
            failure_criteria, per_agent_mechanism, run_status
    operation: validate
    expected: python -c "
    import yaml; d = yaml.safe_load(open('docs/agents/pilots/pilot-specs.yaml').read())
    p = d['pilots']; assert len(p)==12; req=['id','name','maps_to','success_criteria']
    [assert f in e for e in p for f in req]; print('PASS')
    " → PASS
    failure: Fix missing entries/fields; re-validate
    next: TC-ACP-004-02 IMPLEMENTED
```

---

### TC-ACP-005 — Machine-Readable Agent Bundle Format

```
Parent Taskcard ID: TC-ACP-005
Title: Machine-Readable Agent Bundle Format
Type: PARENT
Status: PROPOSED
Owner: agent/infrastructure-lane
Supervisor: governance-lane

Source:
  Plan requirement ID: REQ-ACP-008
  Root cause: RC2 (no delivery mechanism to non-Claude agents)
  Selected solution: Bundle YAML file per agent generated from registry.yaml (not AGENTS.md)

Objective:
  - Create build_agent_bundle.py generator
  - Produce codex-bundle.yaml and kilo-bundle.yaml
  - Wire generator into run_sync.py as final step

Dependencies: TC-ACP-002 CLOSED (registry.yaml must have kilo column before bundles generated)
              TC-ACP-003 CLOSED (bundles reference canonical-agent-contract.yaml)

Child taskcards:
  - TC-ACP-005-01: Design and write agent-bundle-schema.yaml
  - TC-ACP-005-02: Create tools/agents/build_agent_bundle.py
  - TC-ACP-005-03: Generate and validate codex-bundle.yaml
  - TC-ACP-005-04: Generate kilo-bundle.yaml and wire into run_sync.py
```

#### TC-ACP-005-01 — Bundle Schema

```
Child TC: TC-ACP-005-01 | Parent: TC-ACP-005 | Status: TODO

Micro-steps:
  MS-005-01-01:
    action: Create docs/agents/bundles/ directory (if not exists);
            create docs/agents/bundles/agent-bundle-schema.yaml defining the structure
            with required fields: bundle.generated, bundle.agent, bundle.source,
            bundle.instruction_file, bundle.contract_file, bundle.session_state,
            bundle.capabilities (list), bundle.governance, bundle.blocked_capabilities,
            bundle.model_requirements
    target: docs/agents/bundles/agent-bundle-schema.yaml (CREATE)
    operation: create
    expected: Valid YAML schema file; all required fields documented with types
    check: File exists; python yaml parse succeeds
    next: MS-005-01-02

  MS-005-01-02:
    action: Add design-note to schema: "Bundles include paths to read, not inline content.
            Agent fetches the referenced files at runtime. Bundle is committed to git.
            Bundle is regenerated on every run_sync.py run."
    target: docs/agents/bundles/agent-bundle-schema.yaml
    operation: edit
    expected: Design note present as comment or description field
    next: TC-ACP-005-01 IMPLEMENTED
```

#### TC-ACP-005-02 — Create build_agent_bundle.py

```
Child TC: TC-ACP-005-02 | Parent: TC-ACP-005 | Status: TODO

Micro-steps:
  MS-005-02-01:
    action: Create tools/agents/ directory (if not exists);
            inspect .governance/capabilities/registry.yaml to understand its exact structure
            (what fields are available; how capabilities are listed)
    target: .governance/capabilities/registry.yaml
    operation: inspect
    expected: List of capability entries with agent_surfaces.codex, agent_surfaces.kilo fields
    check: Structure confirmed; field names recorded for script
    next: MS-005-02-02

  MS-005-02-02:
    action: Create tools/agents/build_agent_bundle.py with:
            - argparse: --agent {codex,kilo} --output <path>
            - Reads .governance/capabilities/registry.yaml
            - Filters capabilities for the requested agent (codex: true or kilo: true)
            - Writes agent-specific bundle YAML per schema in TC-ACP-005-01
            - Sets bundle.generated to current UTC ISO timestamp
            - Writes to --output path
    target: tools/agents/build_agent_bundle.py (CREATE)
    operation: create
    expected: Script parses, takes --agent and --output args, reads registry, writes bundle
    check: python tools/agents/build_agent_bundle.py --help → exits 0; shows usage
    failure: SyntaxError → fix before proceeding
    next: MS-005-02-03

  MS-005-02-03:
    action: Test build_agent_bundle.py with --agent codex:
            python tools/agents/build_agent_bundle.py --agent codex
                   --output /tmp/test-codex-bundle.yaml
            Verify output file exists and parses
    operation: run
    expected: /tmp/test-codex-bundle.yaml exists; valid YAML; bundle.agent == "codex"
    check: python -c "import yaml; d=yaml.safe_load(open('/tmp/test-codex-bundle.yaml').read()); assert d['bundle']['agent']=='codex'; print('PASS')"
    failure: Script error → debug; fix; retest
    next: TC-ACP-005-02 IMPLEMENTED
```

#### TC-ACP-005-03 — Generate codex-bundle.yaml

```
Child TC: TC-ACP-005-03 | Parent: TC-ACP-005 | Status: TODO
Preconditions: TC-ACP-005-02 IMPLEMENTED

Micro-steps:
  MS-005-03-01:
    action: Run: python tools/agents/build_agent_bundle.py --agent codex
                 --output docs/agents/bundles/codex-bundle.yaml
    target: docs/agents/bundles/codex-bundle.yaml (CREATE/OVERWRITE)
    operation: run
    expected: File created; valid YAML; bundle.agent: codex
    check: File exists; yaml parse succeeds
    next: MS-005-03-02

  MS-005-03-02:
    action: Verify codex-bundle.yaml contains required sections:
            bundle.session_state, bundle.capabilities, bundle.governance, bundle.blocked_capabilities
    operation: validate
    expected: All 4 sections present
    check: python -c "import yaml; d=yaml.safe_load(open('docs/agents/bundles/codex-bundle.yaml').read())['bundle']; [assert k in d for k in ['session_state','capabilities','governance','blocked_capabilities']]; print('PASS')"
    failure: Missing section → update build_agent_bundle.py to include it; regenerate
    next: TC-ACP-005-03 IMPLEMENTED
```

#### TC-ACP-005-04 — Generate kilo-bundle.yaml and Wire into run_sync.py

```
Child TC: TC-ACP-005-04 | Parent: TC-ACP-005 | Status: TODO
Preconditions: TC-ACP-005-02 IMPLEMENTED

Micro-steps:
  MS-005-04-01:
    action: Run: python tools/agents/build_agent_bundle.py --agent kilo
                 --output docs/agents/bundles/kilo-bundle.yaml
    target: docs/agents/bundles/kilo-bundle.yaml
    operation: run
    expected: File created; bundle.agent: kilo; all blocked_capabilities present
    check: File exists; yaml parse succeeds; bundle.agent == "kilo"
    next: MS-005-04-02

  MS-005-04-02:
    action: Read tools/capability_sync/run_sync.py; identify the last step;
            add bundle generation as a new final step calling build_agent_bundle.py
            for both codex and kilo
    target: tools/capability_sync/run_sync.py
    operation: edit
    expected: run_sync.py calls build_agent_bundle.py for codex and kilo at end
    check: git diff shows addition of 2 bundle generation calls after last existing step
    next: MS-005-04-03

  MS-005-04-03:
    action: Run python tools/capability_sync/run_sync.py end-to-end;
            verify both bundle files are regenerated with updated timestamps
    operation: run
    expected: Both bundle files have new generated timestamp; no errors
    check: grep "generated:" docs/agents/bundles/codex-bundle.yaml → recent timestamp
    failure: Error in run_sync.py → revert run_sync.py changes; investigate pipeline first
    next: TC-ACP-005-04 IMPLEMENTED
```

---

### TC-ACP-006 — Enforce Pre-Mutation Guard

```
Parent Taskcard ID: TC-ACP-006
Title: Enforce Pre-Mutation Guard (EP-002-GAP / EP-007)
Type: PARENT
Status: PROPOSED
Owner: agent/governance-lane
Supervisor: governance-lane

Source:
  Plan requirement IDs: REQ-ACP-009, REQ-ACP-010
  Root cause: RC3 (governance prompt-only, guard must be called explicitly)
  Selected solution: Hybrid — pre-commit hook (EP-007) + declaration validator gate

Objective:
  - Close EP-002-GAP: auto-invoke pre_mutation_guard.py, not just make it available
  - Close DEC-014: reclassify based on actual Codex activation state

Scope:
  Allowed: .git/hooks/pre-commit (CREATE/EDIT),
            tools/supervisor/sprint_executor_validate.py (EDIT),
            docs/governance/skill-only-policy.yaml (UPDATE gap status only),
            docs/governance/codex-adapter.md (UPDATE DEC-014 status only)
  Forbidden: tools/governance/pre_mutation_guard.py (read-only; do not change its interface),
             src/*, AGENTS.md

Preserved behavior:
  - pre_mutation_guard.py interface unchanged (--agent-type, --task-id, --skill-id, --paths)
  - Existing sprint_executor_validate.py validations unchanged; only ADD new check

Dependencies:
  TC-ACP-001 CLOSED (need Kilo platform info to understand if hook covers Kilo)
  TC-ACP-003 CLOSED (canonical contract defines what "authorized mutation" means)

Child taskcards:
  - TC-ACP-006-01: Investigate existing git hooks and CI checks
  - TC-ACP-006-02: Implement pre-commit hook (EP-007)
  - TC-ACP-006-03: Add authorization_id check to sprint_executor_validate.py
  - TC-ACP-006-04: Update DEC-014 and EP-002-GAP status records
```

#### TC-ACP-006-01 — Investigate Existing Git Hooks and CI

```
Child TC: TC-ACP-006-01 | Parent: TC-ACP-006 | Type: CHILD/INVESTIGATION | Status: TODO

Micro-steps:
  MS-006-01-01:
    action: List .git/hooks/ directory; record all existing hook files and their current content
    target: .git/hooks/
    operation: inspect
    expected: List of hook files (pre-commit, commit-msg, etc.); content of each
    check: Directory listed; contents captured
    failure: If .git/hooks/ missing → record as "no hooks directory"; proceed
    next: MS-006-01-02

  MS-006-01-02:
    action: Read tools/governance/pre_mutation_guard.py in full; record:
            (1) exact CLI interface (--agent-type values, --paths format),
            (2) exit codes (0=AUTHORIZED, 1=BLOCKED, 2=CONFIG_ERROR),
            (3) what happens with AUTO agent-type
    target: tools/governance/pre_mutation_guard.py
    operation: inspect
    expected: CLI interface documented; exit codes confirmed; AUTO handling noted
    check: Interface documented; all 3 items recorded
    failure: If script has no --agent-type AUTO → record "AUTO not supported"; use UNKNOWN
    next: MS-006-01-03

  MS-006-01-03:
    action: Search .github/workflows/ for any CI step that calls pre_mutation_guard.py;
            record if found (workflow file + step name) or "not found"
    target: .github/workflows/
    operation: inspect
    expected: Either "found in workflow X at step Y" or "not found"
    check: Search complete; result recorded
    next: TC-ACP-006-01 IMPLEMENTED

Acceptance checks:
  - .git/hooks/ contents documented (or absence noted)
  - pre_mutation_guard.py CLI interface fully documented
  - CI usage of guard documented (or absence noted)
```

#### TC-ACP-006-02 — Implement Pre-Commit Hook (EP-007)

```
Child TC: TC-ACP-006-02 | Parent: TC-ACP-006 | Status: TODO
Preconditions: TC-ACP-006-01 IMPLEMENTED (must know existing hooks)

Micro-steps:
  MS-006-02-01:
    action: Determine whether .git/hooks/pre-commit already exists:
            If YES → read it; plan to APPEND (chain), not replace
            If NO → plan to CREATE new hook
    target: .git/hooks/pre-commit
    operation: inspect
    expected: Decision: CHAIN or CREATE
    check: Decision recorded; existing content (if any) captured
    next: MS-006-02-02

  MS-006-02-02:
    action: Create or update .git/hooks/pre-commit to add guard invocation:
            #!/bin/bash
            # EP-007: Pre-mutation governance guard
            CHANGED=$(git diff --cached --name-only 2>/dev/null)
            if [ -n "$CHANGED" ]; then
              python tools/governance/pre_mutation_guard.py \
                --agent-type AUTO \
                --paths "$CHANGED"
              EXIT_CODE=$?
              if [ $EXIT_CODE -eq 1 ]; then
                echo "BLOCKED by pre_mutation_guard.py (EP-007). See output above."
                exit 1
              fi
            fi
            # [existing hook content below if chaining]
    target: .git/hooks/pre-commit
    operation: create or edit
    expected: Hook file exists; is executable; calls pre_mutation_guard.py
    check: ls -la .git/hooks/pre-commit shows executable bit (x)
    failure: If hook breaks existing pre-commit logic → append AFTER existing content; test
    next: MS-006-02-03

  MS-006-02-03:
    action: Verify hook is executable: chmod +x .git/hooks/pre-commit (if needed);
            test that it runs without error on a dry run:
            bash -n .git/hooks/pre-commit (syntax check)
    operation: validate
    expected: Exit code 0 from bash -n; hook file is executable
    check: Both checks pass
    failure: Syntax error → fix; re-test
    next: TC-ACP-006-02 IMPLEMENTED
```

#### TC-ACP-006-03 — Add Authorization ID Check to sprint_executor_validate.py

```
Child TC: TC-ACP-006-03 | Parent: TC-ACP-006 | Status: TODO

Micro-steps:
  MS-006-03-01:
    action: Read tools/supervisor/sprint_executor_validate.py in full;
            locate where PRODUCT_SOURCE work items are validated;
            record the function name and line number
    target: tools/supervisor/sprint_executor_validate.py
    operation: inspect
    expected: Function name for PRODUCT_SOURCE validation; line number
    check: Function found and recorded
    next: MS-006-03-02

  MS-006-03-02:
    action: Add new validation check in sprint_executor_validate.py:
            For PRODUCT_SOURCE work items, check if pre_mutation_guard_authorization_id is present.
            If absent: emit WARNING (not FAIL) with message:
            "WARN: PRODUCT_SOURCE item '{item_id}' missing pre_mutation_guard_authorization_id.
             EP-002-GAP mitigation requires explicit guard invocation."
            Do NOT make this a hard FAIL yet (too strict for initial rollout)
    target: tools/supervisor/sprint_executor_validate.py
    operation: edit
    expected: Warning emitted for PRODUCT_SOURCE items without authorization_id
    check: git diff shows addition of warning check; no existing validations changed
    failure: If edit breaks other validations → revert; apply more surgically
    next: MS-006-03-03

  MS-006-03-03:
    action: Test the new check:
            python -c "
            # Create minimal test declaration with PRODUCT_SOURCE item lacking auth_id
            import yaml, subprocess
            test_decl = {'run_id': 'test', 'sprint_id': 'test',
                         'planned_work_items': [{'item_id': 'X', 'item_type': 'PRODUCT_SOURCE',
                                                  'status': 'completed'}]}
            with open('/tmp/test-decl.yaml','w') as f: yaml.dump(test_decl, f)
            result = subprocess.run(['python','tools/supervisor/sprint_executor_validate.py',
                                     '/tmp/test-decl.yaml'], capture_output=True, text=True)
            assert 'pre_mutation_guard_authorization_id' in result.stdout + result.stderr
            print('PASS: warning emitted')
            "
    operation: validate
    expected: PASS
    failure: If warning not emitted → debug the check; fix and retest
    next: TC-ACP-006-03 IMPLEMENTED
```

#### TC-ACP-006-04 — Update DEC-014 and EP-002-GAP Status

```
Child TC: TC-ACP-006-04 | Parent: TC-ACP-006 | Status: TODO

Micro-steps:
  MS-006-04-01:
    action: Read docs/governance/codex-adapter.md in full;
            locate DEC-014 status record; record current status string
    target: docs/governance/codex-adapter.md
    operation: inspect
    expected: DEC-014 entry found; current status recorded
    check: DEC-014 found with status string
    next: MS-006-04-02

  MS-006-04-02:
    action: Update docs/governance/codex-adapter.md DEC-014 status:
            From: "backlog" or "deferred"
            To: "CLOSED_BY_PLAN_FF-AGENTS-PARITY-001" (if adapter is completed in this plan)
                OR "BLOCKED_PENDING_RUNTIME_VALIDATION" (if Codex not yet instantiated)
            Use value determined by TC-ACP-001-01 findings about Codex activation state
    target: docs/governance/codex-adapter.md
    operation: edit
    expected: DEC-014 status updated; rationale added
    check: grep "DEC-014" → updated status visible
    next: MS-006-04-03

  MS-006-04-03:
    action: Update docs/governance/skill-only-policy.yaml EP-002-GAP status:
            From: "partial" → "MITIGATED_BY_PLAN_FF-AGENTS-PARITY-001"
            Add note: "Pre-commit hook (EP-007) added. Declaration validator warning added.
                       Not fully RESOLVED: hook covers Claude Code commits;
                       Codex/Kilo commit paths may still bypass guard."
    target: docs/governance/skill-only-policy.yaml
    operation: edit
    expected: EP-002-GAP status updated with MITIGATED status and scope note
    check: grep "EP-002-GAP" → updated; grep "MITIGATED" → found
    next: TC-ACP-006-04 IMPLEMENTED
```

---

### TC-ACP-007 — Complete Claude Adapter Verification

```
Parent Taskcard ID: TC-ACP-007
Title: Complete Claude Adapter Verification
Type: PARENT
Status: PROPOSED
Owner: agent/verification-lane

Source:
  Plan requirement ID: REQ-ACP-011
  Selected solution: Map each RC capability to its governing CLAUDE.md section +
                     command file; document honest status

Dependencies: TC-ACP-003 CLOSED (canonical contract), TC-ACP-004 CLOSED (pilot specs)

Child taskcards:
  - TC-ACP-007-01: Map CLAUDE.md sections to RC entries
  - TC-ACP-007-02: Map command files to RC entries; set claude_code surfaces
  - TC-ACP-007-03: Write Claude entries to agent-inventory.yaml
```

#### TC-ACP-007-01 — Map CLAUDE.md to RC Entries

```
Child TC: TC-ACP-007-01 | Parent: TC-ACP-007 | Status: TODO

Micro-steps:
  MS-007-01-01:
    action: Read CLAUDE.md fully; for each of 22 RC capabilities, identify which
            CLAUDE.md section governs it; record mapping:
            RC-001 (recon) → §"Read session-resume.md"
            RC-003 (plan-ingestion) → §"Step 0 Plan Lock" + §"Mandatory Plan Files"
            RC-009 (mutation-ownership) → §"settings.json write permissions"
            etc. for all 22
    target: CLAUDE.md
    operation: inspect
    expected: 22-row mapping table: RC-ID → CLAUDE.md section reference
    check: All 22 RCs have a section reference; no blanks
    failure: If RC has no CLAUDE.md section → mark as GAP; this becomes an update needed in TC-ACP-007-02
    next: MS-007-01-02

  MS-007-01-02:
    action: For each RC where CLAUDE.md coverage was marked as GAP:
            Search .claude/commands/ for a relevant command file that covers it;
            if found: note "covered by command file, not CLAUDE.md directly"
            if not found: mark as REQUIRES_CLAUDE_MD_UPDATE
    operation: inspect
    expected: All 22 RCs classified as: covered-claude-md, covered-command-file, or REQUIRES_UPDATE
    check: No RC remains blank
    next: TC-ACP-007-01 IMPLEMENTED
```

#### TC-ACP-007-02 — Map Command Files to RC; Set claude_code Surfaces

```
Child TC: TC-ACP-007-02 | Parent: TC-ACP-007 | Status: TODO
Preconditions: TC-ACP-007-01 IMPLEMENTED

Micro-steps:
  MS-007-02-01:
    action: For each of the 120 active skills in .supervisor/skill-registry.yaml:
            Read the command file in .claude/commands/<skill>.md;
            determine which RC capability area it serves;
            add agent_surfaces.codex: false, agent_surfaces.kilo: false to skill entry
            (leave codex/kilo decisions for TC-ACP-008/TC-ACP-009;
             just ensure agent_surfaces block exists for each skill)
    target: .supervisor/skill-registry.yaml (batch edit)
    operation: edit
    expected: All 120 active skills have agent_surfaces block
    check: grep -c "agent_surfaces:" .supervisor/skill-registry.yaml → 120+
    failure: If bulk edit risks corruption → process 20 skills at a time; validate YAML after each batch
    next: MS-007-02-02

  MS-007-02-02:
    action: Validate .supervisor/skill-registry.yaml still parses:
            python -c "import yaml; yaml.safe_load(open('.supervisor/skill-registry.yaml').read()); print('PASS')"
    operation: validate
    expected: PASS
    failure: Fix YAML error; identify which batch introduced it; fix only that batch
    next: TC-ACP-007-02 IMPLEMENTED
```

#### TC-ACP-007-03 — Write Claude Entries to agent-inventory.yaml

```
Child TC: TC-ACP-007-03 | Parent: TC-ACP-007 | Status: TODO
Preconditions: TC-ACP-007-01, TC-ACP-007-02 IMPLEMENTED

Micro-steps:
  MS-007-03-01:
    action: Create docs/agents/agent-inventory.yaml with file header;
            write 22 Claude entries using the schema:
            agent_implementation: {agent: claude, capability_id: RC-NNN,
            implementation_path: ..., mechanism: ..., current_status: COMPLETE_VERIFIED,
            runtime_verified: true, limitations: [], gaps: []}
            Use findings from TC-ACP-007-01 for implementation_path and mechanism
    target: docs/agents/agent-inventory.yaml (CREATE)
    operation: create
    expected: File with 22 Claude entries; all current_status: COMPLETE_VERIFIED
              except those marked REQUIRES_UPDATE (those get PARTIAL)
    check: grep -c "agent: claude" → 22
    next: MS-007-03-02

  MS-007-03-02:
    action: Validate docs/agents/agent-inventory.yaml:
            python -c "import yaml; d=yaml.safe_load(open('docs/agents/agent-inventory.yaml').read());
            claude_entries=[e for e in d['implementations'] if e['agent']=='claude'];
            assert len(claude_entries)==22; print('PASS')"
    operation: validate
    expected: PASS
    next: TC-ACP-007-03 IMPLEMENTED
```

---

### TC-ACP-008 — Complete Codex Adapter

```
Parent Taskcard ID: TC-ACP-008
Title: Complete Codex Adapter
Type: PARENT
Status: PROPOSED
Owner: agent/adapter-lane

Source:
  Plan requirement IDs: REQ-ACP-012, REQ-ACP-013
  Root cause: RC2 (no delivery mechanism), RC3 (governance prompt-only), RC4 (no codex field)
  Selected solution: Create codex-instructions.md; update codex-adapter.md; opt-in skills

Dependencies:
  TC-ACP-002 CLOSED, TC-ACP-003 CLOSED, TC-ACP-004 CLOSED, TC-ACP-005 CLOSED
  TC-ACP-007-02 CLOSED (agent_surfaces blocks must exist in skill-registry.yaml before opt-in)

Child taskcards:
  - TC-ACP-008-01: Create docs/governance/codex-instructions.md
  - TC-ACP-008-02: Update docs/governance/codex-adapter.md
  - TC-ACP-008-03: Opt-in skills for Codex (set agent_surfaces.codex: true per skill)
  - TC-ACP-008-04: Regenerate codex-bundle.yaml; write Codex inventory entries

Preserved behavior:
  - Existing codex-adapter.md 7-step contract preserved; extended not replaced
  - skill-only-policy.yaml unchanged
```

#### TC-ACP-008-01 — Create codex-instructions.md

```
Child TC: TC-ACP-008-01 | Parent: TC-ACP-008 | Status: TODO

Micro-steps:
  MS-008-01-01:
    action: Create docs/governance/codex-instructions.md with the following sections:
            1. Session Start (read codex-bundle.yaml to discover all state paths)
            2. Plan Binding (locate .local/supervisor/active-plan-lock.json;
               lock plan without VSCode plan-mode)
            3. Skill-First Execution (reference codex-adapter.md 7-step contract)
            4. Evidence Declaration (call sprint_executor_validate.py --repair before submitting)
            5. Pre-Mutation Guard (call pre_mutation_guard.py --agent-type CODEX)
            6. Continuation (read continuation-signal.json; verify session_id)
            7. Hard Stops (same conditions as CLAUDE.md POST_PLAN_TERMINAL etc.)
            8. Blocked Capabilities (list from codex-bundle.yaml blocked_capabilities)
    target: docs/governance/codex-instructions.md (CREATE)
    operation: create
    expected: Markdown file with all 8 sections; non-empty; references codex-bundle.yaml
    check: File exists; wc -l > 100 (substantial content)
    next: MS-008-01-02

  MS-008-01-02:
    action: Cross-check codex-instructions.md against pilot-specs.yaml:
            For each of 12 pilots, verify codex-instructions.md addresses
            the per_agent_mechanism.codex field defined in the pilot spec
    target: docs/agents/pilots/pilot-specs.yaml (read),
            docs/governance/codex-instructions.md (read/edit if gaps found)
    operation: inspect + edit if needed
    expected: Each pilot's codex mechanism is addressed in codex-instructions.md
    check: 12 pilots checked; any gaps noted and filled
    next: TC-ACP-008-01 IMPLEMENTED
```

#### TC-ACP-008-02 — Update codex-adapter.md

```
Child TC: TC-ACP-008-02 | Parent: TC-ACP-008 | Status: TODO

Micro-steps:
  MS-008-02-01:
    action: Read docs/governance/codex-adapter.md in full; identify the 7-step contract section
            and all known-gaps entries; record what is missing relative to the 22 RC areas
    target: docs/governance/codex-adapter.md
    operation: inspect
    expected: 7-step contract located; missing RC areas identified
    next: MS-008-02-02

  MS-008-02-02:
    action: Extend docs/governance/codex-adapter.md:
            - After 7-step contract: add link to codex-instructions.md for full lifecycle
            - Add section "Full Lifecycle Reference (22 RC Areas)" with table mapping
              RC-NNN → codex-instructions.md section
            - Update DEC-014 status (per TC-ACP-006-04 finding)
    target: docs/governance/codex-adapter.md
    operation: edit
    expected: codex-adapter.md now references codex-instructions.md; RC area table present;
              DEC-014 status updated
    check: wc -l codex-adapter.md increases; grep "codex-instructions.md" → found
    next: TC-ACP-008-02 IMPLEMENTED
```

#### TC-ACP-008-03 — Opt-In Skills for Codex

```
Child TC: TC-ACP-008-03 | Parent: TC-ACP-008 | Status: TODO
Preconditions: TC-ACP-007-02 IMPLEMENTED (agent_surfaces blocks exist in skill-registry.yaml)

Micro-steps:
  MS-008-03-01:
    action: Define the classification rule for codex: true:
            A skill gets codex: true if ALL are true:
            (1) command file does not reference VSCode plan-mode mechanics,
            (2) command file does not reference Claude-native UI tools (like EnterPlanMode),
            (3) skill is not in the BLOCKED capabilities list from codex-bundle.yaml,
            (4) skill's operations can be performed via file-read + script-execution only
            Record this rule as a comment in skill-registry.yaml schema section
    target: .supervisor/skill-registry.yaml schema comment
    operation: edit
    expected: Classification rule documented; not applied yet
    next: MS-008-03-02

  MS-008-03-02:
    action: Process skills batch 1 (first 40 active skills):
            For each: read command file in .claude/commands/; apply classification rule;
            set agent_surfaces.codex: true or false;
            add codex_justification if false (e.g., "requires_claude_native_tool: EnterPlanMode")
    target: .supervisor/skill-registry.yaml (batch of 40 skills)
    operation: edit
    expected: 40 skills have codex: true or false set
    check: yaml.safe_load passes; no blank codex fields in first 40 entries
    next: MS-008-03-03

  MS-008-03-03:
    action: Process skills batch 2 (next 40 active skills); same process
    target: .supervisor/skill-registry.yaml (next 40)
    operation: edit
    expected: 40 more skills classified; YAML still valid
    check: yaml.safe_load passes; count of classified skills = 80
    next: MS-008-03-04

  MS-008-03-04:
    action: Process skills batch 3 (remaining ~40 active skills); same process;
            validate full skill-registry.yaml after
    target: .supervisor/skill-registry.yaml (remaining ~40)
    operation: edit
    expected: All 120 active skills classified for codex; YAML valid
    check: python -c "import yaml; d=yaml.safe_load(open('.supervisor/skill-registry.yaml').read())
    print('PASS: parsed')"
    failure: YAML error → identify offending batch; fix before proceeding
    next: TC-ACP-008-03 IMPLEMENTED
```

#### TC-ACP-008-04 — Regenerate codex-bundle.yaml; Write Codex Inventory

```
Child TC: TC-ACP-008-04 | Parent: TC-ACP-008 | Status: TODO
Preconditions: TC-ACP-008-03 IMPLEMENTED

Micro-steps:
  MS-008-04-01:
    action: Run python tools/capability_sync/run_sync.py to regenerate registry.yaml with
            updated codex opt-in values from skill-registry.yaml;
            verify codex-bundle.yaml regenerated with correct true/false values
    operation: run
    expected: registry.yaml updated; codex-bundle.yaml regenerated
    check: Run succeeds; codex-bundle.yaml has updated generated timestamp
    next: MS-008-04-02

  MS-008-04-02:
    action: Write 22 Codex entries to docs/agents/agent-inventory.yaml (append to Claude entries):
            For each RC: agent: codex, current_status: COMPLETE_UNVERIFIED,
            runtime_verified: false, limitations: ["live_execution_not_tested"],
            mechanism: "codex-instructions.md + codex-bundle.yaml"
    target: docs/agents/agent-inventory.yaml
    operation: edit
    expected: agent-inventory.yaml now has 44 entries (22 Claude + 22 Codex)
    check: grep -c "agent:" docs/agents/agent-inventory.yaml → 44
    next: TC-ACP-008-04 IMPLEMENTED
```

---

### TC-ACP-009 — Create Kilo Adapter

```
Parent Taskcard ID: TC-ACP-009
Title: Create Kilo Adapter (Full Peer Parity)
Type: PARENT
Status: PROPOSED
Owner: agent/adapter-lane

Source:
  Plan requirement ID: REQ-ACP-014
  Root cause: RC5 (Kilo placeholder)

CRITICAL GATE: TC-ACP-001-01 (Kilo platform research) MUST be IMPLEMENTED before
               any Kilo adapter work begins. Do not write KILO.md without knowing
               what Kilo can do.

Dependencies:
  TC-ACP-001 CLOSED, TC-ACP-002 CLOSED, TC-ACP-003 CLOSED, TC-ACP-005 CLOSED
  TC-ACP-007-02 CLOSED

Child taskcards:
  - TC-ACP-009-01: Create .kilo/KILO.md
  - TC-ACP-009-02: Create docs/governance/kilo-adapter.md
  - TC-ACP-009-03: Update .kilo/kilo.jsonc
  - TC-ACP-009-04: Opt-in skills for Kilo
  - TC-ACP-009-05: Regenerate kilo-bundle.yaml; write Kilo inventory entries
```

#### TC-ACP-009-01 — Create .kilo/KILO.md

```
Child TC: TC-ACP-009-01 | Parent: TC-ACP-009 | Status: TODO

Micro-steps:
  MS-009-01-01:
    action: Read docs/agents/kilo-platform-capabilities.md (TC-ACP-001-01 output) in full;
            extract confirmed native capabilities and blocked ones; record for use below
    target: docs/agents/kilo-platform-capabilities.md
    operation: inspect
    expected: List of confirmed Kilo native capabilities; list of blocked capabilities
    check: Both lists non-empty OR "unknown" rationale documented if all are unknown
    next: MS-009-01-02

  MS-009-01-02:
    action: Create .kilo/KILO.md with sections parallel to CLAUDE.md:
            1. Session Start — read kilo-bundle.yaml to discover state paths
            2. Plan Binding — Kilo-native mechanism (per platform research findings)
            3. Skill-First Execution — reference kilo-adapter.md
            4. Pre-Mutation Guard — if Kilo can exec scripts:
               call pre_mutation_guard.py --agent-type KILO;
               else: document as BLOCKED_ON_KILO
            5. Evidence Declaration — if Kilo has file write: sprint_executor_validate.py;
               else: BLOCKED_ON_KILO
            6. Blocked Capabilities — explicit list from kilo-bundle.yaml blocked_capabilities
               with routing: "ROUTE_TO: Claude Code for this capability"
    target: .kilo/KILO.md (CREATE)
    operation: create
    expected: Markdown file; all 6 sections; BLOCKED_ON_KILO clearly marked for inaccessible items
    check: File exists; wc -l > 80
    next: MS-009-01-03

  MS-009-01-03:
    action: Cross-check .kilo/KILO.md against pilot-specs.yaml per_agent_mechanism.kilo entries;
            ensure every pilot mechanism is addressed in KILO.md
    operation: inspect + edit if needed
    expected: All 12 pilot kilo mechanisms addressed
    next: TC-ACP-009-01 IMPLEMENTED
```

#### TC-ACP-009-02 — Create kilo-adapter.md

```
Child TC: TC-ACP-009-02 | Parent: TC-ACP-009 | Status: TODO
Preconditions: TC-ACP-009-01 IMPLEMENTED

Micro-steps:
  MS-009-02-01:
    action: Create docs/governance/kilo-adapter.md with the following sections:
            1. Entry Point (kilo-bundle.yaml)
            2. Execution Contract (parallel to codex-adapter.md 7 steps, Kilo-native)
            3. State File Paths
            4. Evidence Generation Flow
            5. Pre-Mutation Guard Invocation
            6. Missing Skill Workflow
            7. Known Limitations
            8. Blocked Capabilities with Routing
    target: docs/governance/kilo-adapter.md (CREATE)
    operation: create
    expected: Markdown file with all 8 sections; wc -l > 100
    check: File exists; all 8 sections present (grep section headings)
    next: MS-009-02-02

  MS-009-02-02:
    action: For each blocked capability (from kilo-platform-capabilities.md RC table):
            add a row in section 8 "Blocked Capabilities":
            | RC-NNN | capability name | blocking_reason | ROUTE_TO: agent |
            Ensure all BLOCKED_ON_KILO entries from RC table are in this table
    target: docs/governance/kilo-adapter.md
    operation: edit
    expected: Blocked capabilities table complete; no RC marked blocked without routing
    check: All BLOCKED entries have ROUTE_TO value
    next: TC-ACP-009-02 IMPLEMENTED
```

#### TC-ACP-009-03 — Update kilo.jsonc

```
Child TC: TC-ACP-009-03 | Parent: TC-ACP-009 | Status: TODO

Micro-steps:
  MS-009-03-01:
    action: Read .kilo/kilo.jsonc current content; identify what fields schema allows
            (check $schema URL: https://app.kilo.ai/config.json — if schema is accessible via web,
             search for its documented fields)
    target: .kilo/kilo.jsonc
    operation: inspect
    expected: Current fields listed; schema fields researched
    next: MS-009-03-02

  MS-009-03-02:
    action: Update .kilo/kilo.jsonc to add meaningful fields within the schema's allowed scope:
            Candidate fields (add only those supported by the schema):
              "instructions": ".kilo/KILO.md",
              "governance": "docs/governance/kilo-adapter.md",
              "context_bundle": "docs/agents/bundles/kilo-bundle.yaml"
            If schema disallows these fields: add them as comments explaining intent
    target: .kilo/kilo.jsonc
    operation: edit
    expected: .kilo/kilo.jsonc updated; still valid JSONC
    check: node -e "require('./.kilo/kilo.jsonc')" OR verify JSONC is valid manually
    failure: If schema validation fails → revert; document desired fields in KILO.md instead
    next: TC-ACP-009-03 IMPLEMENTED
```

#### TC-ACP-009-04 — Opt-In Skills for Kilo

```
Child TC: TC-ACP-009-04 | Parent: TC-ACP-009 | Status: TODO
Preconditions: TC-ACP-007-02, TC-ACP-009-01 IMPLEMENTED

Micro-steps:
  MS-009-04-01:
    action: Define classification rule for kilo: true:
            A skill gets kilo: true if ALL: (1) Kilo has confirmed file read capability,
            (2) command file does not require script execution (or Kilo has confirmed shell access),
            (3) skill is not in blocked_capabilities list,
            (4) skill does not require VSCode-native operations
            If Kilo capabilities are "unknown" from TC-ACP-001-01 → mark ALL skills kilo: false
            with kilo_justification: "platform_capabilities_unknown"
    operation: record
    expected: Classification rule recorded; decision on "unknown" case made
    next: MS-009-04-02

  MS-009-04-02:
    action: Apply classification rule to all 120 active skills in .supervisor/skill-registry.yaml:
            Set agent_surfaces.kilo: true or false; add kilo_justification if false
            Process in 3 batches of 40 (same pattern as TC-ACP-008-03)
    target: .supervisor/skill-registry.yaml
    operation: edit
    expected: All 120 skills have kilo: true or false; all false entries have kilo_justification
    check: python yaml parse passes;
           grep -c "kilo: false" .supervisor/skill-registry.yaml → expected count
    failure: YAML error → identify offending batch; fix; re-validate
    next: TC-ACP-009-04 IMPLEMENTED
```

#### TC-ACP-009-05 — Regenerate kilo-bundle.yaml; Write Kilo Inventory

```
Child TC: TC-ACP-009-05 | Parent: TC-ACP-009 | Status: TODO
Preconditions: TC-ACP-009-04 IMPLEMENTED

Micro-steps:
  MS-009-05-01:
    action: Run python tools/capability_sync/run_sync.py; verify kilo-bundle.yaml updated
    operation: run
    expected: Exit 0; kilo-bundle.yaml has new generated timestamp
    next: MS-009-05-02

  MS-009-05-02:
    action: Write 22 Kilo entries to docs/agents/agent-inventory.yaml (append to Claude+Codex entries):
            For each RC: agent: kilo, current_status based on achievable_on_kilo field
            (achievable → COMPLETE_UNVERIFIED; blocked → DISCONNECTED; unknown → MISSING)
            For DISCONNECTED: add limitations and routing to alternative agent
    target: docs/agents/agent-inventory.yaml
    operation: edit
    expected: agent-inventory.yaml now has 66 entries (22 × 3 agents)
    check: grep -c "agent:" → 66
    next: TC-ACP-009-05 IMPLEMENTED
```

---

### TC-ACP-010 — Model Profiles and Routing Rules

```
Parent Taskcard ID: TC-ACP-010
Title: Model Profiles and Task-Routing Rules
Type: PARENT
Status: PROPOSED
Owner: agent/architecture-lane

Dependencies: TC-ACP-001 CLOSED (Kilo model info from platform research),
              TC-ACP-003 CLOSED (routing rules go into canonical contract)
Can run in parallel with: TC-ACP-007, TC-ACP-008, TC-ACP-009

Child taskcards:
  - TC-ACP-010-01: Research and collect model info per platform
  - TC-ACP-010-02: Write docs/agents/model-profiles.yaml
  - TC-ACP-010-03: Add routing rules to canonical-agent-contract.yaml
```

#### TC-ACP-010-01 — Research Models Per Platform

```
Child TC: TC-ACP-010-01 | Status: TODO

Micro-steps:
  MS-010-01-01:
    action: Read .claude/settings.json; record active Claude model ID;
            list all Claude model IDs known (opus-4-6, sonnet-4-6, haiku-4-5)
    target: .claude/settings.json
    operation: inspect
    expected: Active model: claude-opus-4-6; other IDs documented
    next: MS-010-01-02

  MS-010-01-02:
    action: Read docs/ai/llm-endpoint-strategy.md; identify which Codex/OpenAI models
            are permitted for use; record model IDs and their constraints
    target: docs/ai/llm-endpoint-strategy.md
    operation: inspect
    expected: List of permitted Codex models; any API key or endpoint constraints
    failure: If file missing → document as "Codex model policy: undocumented; research needed"
    next: MS-010-01-03

  MS-010-01-03:
    action: From docs/agents/kilo-platform-capabilities.md (TC-ACP-001-01 output):
            extract what models Kilo exposes; record model IDs
    target: docs/agents/kilo-platform-capabilities.md
    operation: inspect
    expected: Kilo model IDs or "unknown if research inconclusive"
    next: TC-ACP-010-01 IMPLEMENTED
```

#### TC-ACP-010-02 — Write model-profiles.yaml

```
Child TC: TC-ACP-010-02 | Status: TODO
Preconditions: TC-ACP-010-01 IMPLEMENTED

Micro-steps:
  MS-010-02-01:
    action: Create docs/agents/model-profiles.yaml with Claude profiles:
            claude-opus-4-6: reasoning_capacity: high, context_capacity: 200K,
            tool_support: full, code_generation: high, review_strength: high,
            allowed_capabilities: [all 22 RC], restricted_capabilities: [],
            status: active
            claude-sonnet-4-6: same but review_strength: medium, status: active
            claude-haiku-4-5: reasoning_capacity: medium, allowed: [RC-001,RC-002,RC-014],
            restricted: [RC-016,RC-020,RC-011], required_supervision: high
    target: docs/agents/model-profiles.yaml (CREATE)
    operation: create
    expected: Valid YAML; 3 Claude model profiles
    check: yaml.safe_load passes; 3 entries
    next: MS-010-02-02

  MS-010-02-02:
    action: Add Codex model profiles from TC-ACP-010-01 findings;
            add Kilo model profiles from TC-ACP-010-01 findings;
            if models unknown → add placeholder with status: UNDOCUMENTED
    target: docs/agents/model-profiles.yaml
    operation: edit
    expected: All 3 platforms documented; total entries ≥ 5
    check: yaml.safe_load passes; all 3 platforms have at least 1 entry
    next: TC-ACP-010-02 IMPLEMENTED
```

#### TC-ACP-010-03 — Add Routing Rules to Canonical Contract

```
Child TC: TC-ACP-010-03 | Status: TODO
Preconditions: TC-ACP-003 CLOSED, TC-ACP-010-02 IMPLEMENTED

Micro-steps:
  MS-010-03-01:
    action: Edit docs/agents/canonical-agent-contract.yaml; add model_routing section:
            - RC-011, RC-016, RC-020 require minimum_tier: high (strong reasoning)
            - RC-007, RC-012 require context_capacity: >= 100K
            - claude-haiku-4-5 may only handle RC-001, RC-002, RC-014
              and requires supervisor validation of output
    target: docs/agents/canonical-agent-contract.yaml
    operation: edit
    expected: model_routing section added; references model-profiles.yaml
    check: yaml.safe_load passes; grep "model_routing:" → found
    next: TC-ACP-010-03 IMPLEMENTED
```

---

### TC-ACP-011 — Complete Agent Inventory

```
Parent Taskcard ID: TC-ACP-011
Title: Complete Agent Inventory (Post-Adapter)
Type: PARENT
Status: PROPOSED

Note: TC-ACP-007-03, TC-ACP-008-04, TC-ACP-009-05 each write entries to agent-inventory.yaml.
      This parent TC validates and finalizes the combined inventory.

Dependencies: TC-ACP-007 CLOSED, TC-ACP-008 CLOSED, TC-ACP-009 CLOSED

Child taskcards:
  - TC-ACP-011-01: Finalize and validate agent-inventory.yaml
```

#### TC-ACP-011-01 — Finalize agent-inventory.yaml

```
Child TC: TC-ACP-011-01 | Parent: TC-ACP-011 | Status: TODO

Micro-steps:
  MS-011-01-01:
    action: Read docs/agents/agent-inventory.yaml; count total entries;
            verify 66 entries (22 × 3 agents) with no duplicates
    target: docs/agents/agent-inventory.yaml
    operation: inspect
    expected: 66 entries; count = 22 Claude + 22 Codex + 22 Kilo
    check: grep -c "agent:" → 66
    failure: If count wrong → identify missing agent/RC combos; add them
    next: MS-011-01-02

  MS-011-01-02:
    action: Verify no entry has current_status: blank or null;
            verify every DISCONNECTED entry has limitations and routing documented
    operation: validate
    expected: All 66 entries have non-blank current_status;
              all DISCONNECTED have routing
    check: python -c "import yaml; d=yaml.safe_load(open('docs/agents/agent-inventory.yaml').read());
    [assert e.get('current_status') for e in d['implementations']]; print('PASS')"
    failure: Fix blank entries; re-validate
    next: MS-011-01-03

  MS-011-01-03:
    action: Verify no entry claims current_status: COMPLETE_VERIFIED
            for Codex or Kilo entries (they should be COMPLETE_UNVERIFIED at most,
            since no live Codex/Kilo pilots have run yet)
    operation: validate
    expected: All Codex/Kilo entries ≤ COMPLETE_UNVERIFIED
    check: grep -A2 "agent: codex" docs/agents/agent-inventory.yaml |
           grep "COMPLETE_VERIFIED" → empty
    failure: Downgrade any COMPLETE_VERIFIED Codex/Kilo entry to COMPLETE_UNVERIFIED
    next: TC-ACP-011-01 IMPLEMENTED

Acceptance checks:
  - 66 entries; no blanks; Codex/Kilo ≤ COMPLETE_UNVERIFIED
  - AGENT_CAPABILITIES_NOT_INVENTORIED = 0
```

---

### TC-ACP-012 — Agent Parity Matrix

```
Parent Taskcard ID: TC-ACP-012
Title: Agent Parity Matrix
Type: PARENT
Status: PROPOSED
Dependencies: TC-ACP-011 CLOSED

Child taskcards:
  - TC-ACP-012-01: Compile agent-parity-matrix.yaml from agent-inventory.yaml
```

#### TC-ACP-012-01 — Compile agent-parity-matrix.yaml

```
Child TC: TC-ACP-012-01 | Parent: TC-ACP-012 | Status: TODO

Micro-steps:
  MS-012-01-01:
    action: Create docs/agents/agent-parity-matrix.yaml;
            For each of 22 RCs: read all 3 agent entries from agent-inventory.yaml;
            write one parity entry per RC:
            capability_id, required, claude {status, mechanism, verified},
            codex {status, mechanism, verified}, kilo {status, mechanism, verified},
            semantic_parity (true only when all 3 are COMPLETE_VERIFIED or formally BLOCKED),
            remaining_gaps, blocking
    target: docs/agents/agent-parity-matrix.yaml (CREATE)
    operation: create
    expected: Valid YAML; 22 entries; all 3 agent sections per entry
    check: yaml.safe_load passes; grep -c "capability_id:" → 22
    next: MS-012-01-02

  MS-012-01-02:
    action: Calculate completion counters:
            REQUIRED_CAPABILITIES_WITHOUT_PARITY_DISPOSITION = count of RCs with
            any agent status blank; Expected: 0
    operation: validate
    expected: All 22 RCs have all 3 agent dispositions → counter = 0
    failure: Fix blank dispositions
    next: TC-ACP-012-01 IMPLEMENTED
```

---

### TC-ACP-013 — Run Cross-Agent Pilots

```
Parent Taskcard ID: TC-ACP-013
Title: Run Cross-Agent Pilots
Type: PARENT
Status: PROPOSED
Dependencies: TC-ACP-004 CLOSED, TC-ACP-007 CLOSED, TC-ACP-008 CLOSED, TC-ACP-009 CLOSED

Child taskcards:
  - TC-ACP-013-01: Execute Claude pilots (all 12 — Claude IS the executing agent)
  - TC-ACP-013-02: Record Codex pilot status (PENDING_RUNTIME; live execution not available)
  - TC-ACP-013-03: Record Kilo pilot status (PENDING_RUNTIME; live execution not available)
```

#### TC-ACP-013-01 — Execute Claude Pilots

```
Child TC: TC-ACP-013-01 | Parent: TC-ACP-013 | Status: TODO

Note: These pilots are executed by Claude itself during plan execution.
      Each pilot is a bounded task with defined inputs and success criteria.

Micro-steps:
  MS-013-01-01:
    action: Create docs/agents/pilots/pilot-results.yaml with file header and result schema
    target: docs/agents/pilots/pilot-results.yaml (CREATE)
    operation: create
    expected: File exists with schema comment and empty results list
    next: MS-013-01-02

  MS-013-01-02:
    action: Execute PILOT-001 (repository-reconnaissance):
            Read reports/supervisor/session-resume.md; extract sprint ID and 3 work items;
            compare against next-sprint.md; record result
    target: reports/supervisor/session-resume.md, reports/supervisor/next-sprint.md
    operation: inspect + record
    expected: Sprint ID extracted; 3 work items identified by ID
    check: Write PILOT-001 result to pilot-results.yaml with outcome: PASS or FAIL
    next: MS-013-01-03

  MS-013-01-03:
    action: Execute PILOT-002 through PILOT-006 sequentially;
            for each: follow the pilot spec task, evaluate against success/failure criteria,
            record result in pilot-results.yaml
            Note: PILOT-004 (bounded code change) must NOT change production source;
            use a test fixture or dry-run only
    operation: run (bounded; no production source changes)
    expected: 5 pilot results written; each has outcome: PASS, FAIL, or SKIPPED_SCOPE_UNSAFE
    check: grep -c "outcome:" pilot-results.yaml → 6 (001-006)
    next: MS-013-01-04

  MS-013-01-04:
    action: Execute PILOT-007 through PILOT-012 sequentially;
            record results in pilot-results.yaml
            Note: PILOT-012 (idempotent rerun) should rerun pilot-001 and verify same outcome
    expected: 6 more results written
    check: grep -c "outcome:" → 12
    next: TC-ACP-013-01 IMPLEMENTED

Acceptance checks:
  - 12 Claude pilot results in pilot-results.yaml
  - No PILOT result is blank
  - FAILED pilots have diagnosis recorded; FAILED_REQUIRED_PILOTS = count of FAIL outcomes
```

#### TC-ACP-013-02 — Record Codex Pilot Status

```
Child TC: TC-ACP-013-02 | Parent: TC-ACP-013 | Status: TODO

Micro-steps:
  MS-013-02-01:
    action: For each of 12 pilots: add Codex result block to pilot-results.yaml:
            agent: codex, outcome: PENDING_RUNTIME,
            rationale: "Live Codex API access not available in this session.
                        Codex instruction file and bundle created. Runtime verification
                        deferred to TC-CODEX-RUNTIME-001 (future session)."
    target: docs/agents/pilots/pilot-results.yaml
    operation: edit
    expected: 12 Codex result blocks present; all outcome: PENDING_RUNTIME with rationale
    check: grep -c "agent: codex" pilot-results.yaml → 12
    next: TC-ACP-013-02 IMPLEMENTED
```

#### TC-ACP-013-03 — Record Kilo Pilot Status

```
Child TC: TC-ACP-013-03 | Parent: TC-ACP-013 | Status: TODO

Micro-steps:
  MS-013-03-01:
    action: For each of 12 pilots: add Kilo result block to pilot-results.yaml:
            agent: kilo, outcome: PENDING_RUNTIME,
            rationale: "Kilo AI platform activation not available in this session.
                        Kilo adapter and bundle created. Runtime verification
                        deferred to TC-KILO-RUNTIME-001 (future session)."
    target: docs/agents/pilots/pilot-results.yaml
    operation: edit
    expected: 12 Kilo result blocks; total results = 36 (12 pilots × 3 agents)
    check: grep -c "agent:" pilot-results.yaml → 36
    next: TC-ACP-013-03 IMPLEMENTED
```

---

### TC-ACP-014 — Tests for Cross-Agent Governance

```
Parent Taskcard ID: TC-ACP-014
Title: Cross-Agent Governance Test Suite
Type: PARENT
Status: PROPOSED
Dependencies: TC-ACP-002 CLOSED, TC-ACP-009 CLOSED, TC-ACP-011 CLOSED

Child taskcards:
  - TC-ACP-014-01: test_capability_opt_in.py
  - TC-ACP-014-02: test_bundle_completeness.py
  - TC-ACP-014-03: test_parity_matrix_coverage.py
  - TC-ACP-014-04: test_blocked_assignments.py
```

#### TC-ACP-014-01 — test_capability_opt_in.py

```
Child TC: TC-ACP-014-01 | Parent: TC-ACP-014 | Status: TODO

Micro-steps:
  MS-014-01-01:
    action: Create tests/agents/ directory (if not exists);
            create tests/agents/__init__.py (empty)
    target: tests/agents/
    operation: create
    expected: Directory exists; __init__.py exists
    next: MS-014-01-02

  MS-014-01-02:
    action: Create tests/agents/test_capability_opt_in.py with test:
            def test_no_skill_uses_opt_out_default():
                "Verify inventory_capabilities.py does not contain the banned opt-out pattern"
                import ast, pathlib
                source = pathlib.Path("tools/capability_sync/inventory_capabilities.py").read_text()
                assert "codex_excluded" not in source, \
                    "FAIL: opt-out pattern 'codex_excluded' still present in inventory_capabilities.py"

            def test_all_active_skills_have_agent_surfaces():
                "Verify all active skills in skill-registry.yaml have agent_surfaces block"
                import yaml
                registry = yaml.safe_load(open(".supervisor/skill-registry.yaml").read())
                skills = [s for s in registry.get("skills", []) if s.get("status") == "active"]
                missing = [s["skill_id"] for s in skills if "agent_surfaces" not in s]
                assert not missing, f"Missing agent_surfaces in {len(missing)} skills: {missing[:5]}"
    target: tests/agents/test_capability_opt_in.py (CREATE)
    operation: create
    expected: File exists; 2 test functions
    next: MS-014-01-03

  MS-014-01-03:
    action: Run: .venv/Scripts/pytest tests/agents/test_capability_opt_in.py -v
    operation: run
    expected: 2 PASSED, 0 FAILED
    check: Exit code 0
    failure: Diagnose failure; fix the underlying issue (not the test);
             re-run until 2 PASSED
    next: TC-ACP-014-01 IMPLEMENTED
```

#### TC-ACP-014-02 — test_bundle_completeness.py

```
Child TC: TC-ACP-014-02 | Parent: TC-ACP-014 | Status: TODO
Preconditions: TC-ACP-005 CLOSED (bundles exist)

Micro-steps:
  MS-014-02-01:
    action: Create tests/agents/test_bundle_completeness.py with tests:
            def test_codex_bundle_exists_and_valid():
                import yaml, pathlib
                f = pathlib.Path("docs/agents/bundles/codex-bundle.yaml")
                assert f.exists(), "codex-bundle.yaml missing"
                d = yaml.safe_load(f.read_text())
                assert d["bundle"]["agent"] == "codex"
                assert "capabilities" in d["bundle"]
                assert "governance" in d["bundle"]
                assert "blocked_capabilities" in d["bundle"]

            def test_kilo_bundle_exists_and_valid():
                "Same structure check for kilo-bundle.yaml"

            def test_bundle_references_registry_source():
                "Verify bundles reference .governance/capabilities/registry.yaml as source"
    target: tests/agents/test_bundle_completeness.py (CREATE)
    operation: create; then run
    expected: 3 PASSED
    failure: Fix bundle generation (TC-ACP-005); re-run
    next: TC-ACP-014-02 IMPLEMENTED
```

#### TC-ACP-014-03 — test_parity_matrix_coverage.py

```
Child TC: TC-ACP-014-03 | Parent: TC-ACP-014 | Status: TODO
Preconditions: TC-ACP-012 CLOSED

Micro-steps:
  MS-014-03-01:
    action: Create tests/agents/test_parity_matrix_coverage.py with tests:
            def test_parity_matrix_has_22_entries():
                import yaml
                d = yaml.safe_load(open("docs/agents/agent-parity-matrix.yaml").read())
                assert len(d["parity"]) == 22

            def test_every_entry_has_all_3_agents():
                "Verify claude, codex, kilo sections present in every entry"

            def test_no_blocking_without_routing():
                "Verify every BLOCKED capability has a routing field to alternative agent"
    target: tests/agents/test_parity_matrix_coverage.py (CREATE)
    operation: create; then run
    expected: 3 PASSED
    failure: Fix parity matrix; re-run
    next: TC-ACP-014-03 IMPLEMENTED
```

#### TC-ACP-014-04 — test_blocked_assignments.py

```
Child TC: TC-ACP-014-04 | Parent: TC-ACP-014 | Status: TODO

Micro-steps:
  MS-014-04-01:
    action: Create tests/agents/test_blocked_assignments.py with tests:
            def test_blocked_kilo_capabilities_have_routing():
                "Every kilo-blocked capability in agent-inventory.yaml has routing defined"
                import yaml
                inv = yaml.safe_load(open("docs/agents/agent-inventory.yaml").read())
                kilo_blocked = [e for e in inv["implementations"]
                                if e["agent"]=="kilo" and e["current_status"]=="DISCONNECTED"]
                for entry in kilo_blocked:
                    assert entry.get("routing"), f"Missing routing for {entry['capability_id']}"

            def test_codex_blocked_capabilities_documented():
                "Every codex-blocked capability has a justification"
                import yaml
                inv = yaml.safe_load(open("docs/agents/agent-inventory.yaml").read())
                codex_blocked = [e for e in inv["implementations"]
                                 if e["agent"]=="codex" and e["current_status"]=="DISCONNECTED"]
                for entry in codex_blocked:
                    assert entry.get("limitations"), f"Missing limitations for {entry['capability_id']}"
    target: tests/agents/test_blocked_assignments.py (CREATE)
    operation: create; then run
    expected: 2 PASSED
    failure: Fix agent-inventory.yaml entries; re-run
    next: TC-ACP-014-04 IMPLEMENTED
```

---

### TC-ACP-015 — Drift Prevention Validators

```
Parent Taskcard ID: TC-ACP-015
Title: Drift Prevention Governance Validators
Type: PARENT
Status: PROPOSED
Dependencies: TC-ACP-002 CLOSED, TC-ACP-012 CLOSED, TC-ACP-014 CLOSED

Note on expected_count: Current expected_count in governance_validator_runner.py = 165.
Adding 4 validators makes 169. However, runner.py may be modified to use dynamic count
(len(ALL_VALIDATORS)) to prevent future count conflicts. TC-ACP-015-02 makes this change.

Child taskcards:
  - TC-ACP-015-01: Create governance_validators_agent_parity.py (V166-V169)
  - TC-ACP-015-02: Update governance_validator_runner.py
  - TC-ACP-015-03: Update CI workflow for agent parity drift detection
```

#### TC-ACP-015-01 — Create governance_validators_agent_parity.py

```
Child TC: TC-ACP-015-01 | Parent: TC-ACP-015 | Status: TODO

Micro-steps:
  MS-015-01-01:
    action: Read tools/supervisor/governance_validators.py lines 1-50;
            record the validator function signature pattern and how validators are registered
    target: tools/supervisor/governance_validators.py
    operation: inspect
    expected: Validator signature pattern; registration mechanism
    next: MS-015-01-02

  MS-015-01-02:
    action: Create tools/supervisor/governance_validators_agent_parity.py with 4 validators:

            def validate_agent_opt_in_not_default(repo_root=None):
                "V166: Verify inventory_capabilities.py uses opt-in logic"
                # Check that "codex_excluded" pattern is absent from inventory_capabilities.py
                # Return PASS/FAIL result in governance validator format

            def validate_kilo_column_in_registry(repo_root=None):
                "V167: Verify kilo field present for all active capabilities"
                # Load registry.yaml; check all active entries have agent_surfaces.kilo field

            def validate_canonical_contract_integrity(repo_root=None):
                "V168: Verify canonical-agent-contract.yaml covers all 22 RC entries"
                # Load file; count capability_semantics entries; assert == 22

            def validate_agent_bundles_current(repo_root=None):
                "V169: Verify bundles are not stale relative to registry.yaml"
                # Compare mtime of bundles vs registry.yaml; warn if bundle older
    target: tools/supervisor/governance_validators_agent_parity.py (CREATE)
    operation: create
    expected: File with 4 validator functions; follows existing validator signature pattern
    check: python -c "from tools.supervisor.governance_validators_agent_parity import
                      validate_agent_opt_in_not_default; print('PASS')"
    failure: ImportError → fix module structure; retest
    next: MS-015-01-03

  MS-015-01-03:
    action: Test each validator function individually:
            For each validator: call it; verify it returns a result dict (not None, not exception)
    operation: validate
    expected: All 4 validators return result dicts when called
    check: All 4 calls succeed without exception
    failure: Debug failing validator; fix; retest
    next: TC-ACP-015-01 IMPLEMENTED
```

#### TC-ACP-015-02 — Update governance_validator_runner.py

```
Child TC: TC-ACP-015-02 | Parent: TC-ACP-015 | Status: TODO
Preconditions: TC-ACP-015-01 IMPLEMENTED

Micro-steps:
  MS-015-02-01:
    action: Read tools/supervisor/governance_validator_runner.py in full;
            locate where validators are imported and ALL_VALIDATORS list is built;
            locate the expected_count assertion
    target: tools/supervisor/governance_validator_runner.py
    operation: inspect
    expected: Import location; ALL_VALIDATORS assembly; expected_count = 165 (current)
    next: MS-015-02-02

  MS-015-02-02:
    action: Add import for governance_validators_agent_parity in runner;
            add V166-V169 to ALL_VALIDATORS list
    target: tools/supervisor/governance_validator_runner.py
    operation: edit
    expected: 4 new validators imported and added to ALL_VALIDATORS
    check: git diff shows imports and list additions
    next: MS-015-02-03

  MS-015-02-03:
    action: Change expected_count assertion from hardcoded 165 to dynamic:
            expected_count = len(ALL_VALIDATORS)
            (Remove or comment out the hardcoded 165 assertion)
    target: tools/supervisor/governance_validator_runner.py
    operation: edit
    expected: Assertion is now dynamic; future validator additions will not break this check
    check: git diff shows expected_count change; new count = len(ALL_VALIDATORS) = 169+
    next: MS-015-02-04

  MS-015-02-04:
    action: Run python tools/supervisor/governance_validator_runner.py;
            verify all validators pass including V166-V169
    operation: run
    expected: Exit code 0; all validators pass; 169+ validators reported
    check: Exit 0; output contains "169 validators" or similar
    failure: If V166-V169 fail → fix the underlying issue they detect;
             do not weaken the validators
    next: TC-ACP-015-02 IMPLEMENTED
```

#### TC-ACP-015-03 — Update CI Workflow

```
Child TC: TC-ACP-015-03 | Parent: TC-ACP-015 | Status: TODO

Micro-steps:
  MS-015-03-01:
    action: Read .github/workflows/ directory; identify the workflow that runs governance validators
    target: .github/workflows/
    operation: inspect
    expected: Workflow file name; step that calls governance_validator_runner.py
    next: MS-015-03-02

  MS-015-03-02:
    action: Update or add a step in the identified workflow to run governance_validator_runner.py
            on PRs that touch: agent configs (.kilo/, docs/governance/),
            skill-registry.yaml, registry.yaml, inventory_capabilities.py
            Add trigger condition: on: pull_request: paths: ['.kilo/**', 'docs/governance/**',
            '.supervisor/skill-registry.yaml', 'tools/capability_sync/inventory_capabilities.py']
    target: .github/workflows/<identified workflow file>
    operation: edit
    expected: Workflow triggers governance validator run on relevant PR changes
    check: git diff shows path trigger addition; step references governance_validator_runner.py
    failure: If workflow structure differs → adapt paths trigger to match existing YAML structure
    next: TC-ACP-015-03 IMPLEMENTED
```

---

### TC-ACP-016 — Idempotency Proof

```
Parent Taskcard ID: TC-ACP-016
Title: Idempotency Proof — Second Run Produces No Material Changes
Type: PARENT
Status: PROPOSED
Dependencies: ALL prior TCs CLOSED

Child taskcards:
  - TC-ACP-016-01: Capture baseline file hashes of all outputs
  - TC-ACP-016-02: Rerun all generators; compare hashes
```

#### TC-ACP-016-01 — Capture Baseline Hashes

```
Child TC: TC-ACP-016-01 | Parent: TC-ACP-016 | Status: TODO

Micro-steps:
  MS-016-01-01:
    action: Create docs/agents/idempotency-proof.yaml with baseline section;
            record SHA-256 of each output file created by this plan:
            docs/agents/required-capability-model.yaml,
            docs/agents/canonical-agent-contract.yaml,
            docs/agents/pilots/pilot-specs.yaml,
            docs/agents/bundles/codex-bundle.yaml,
            docs/agents/bundles/kilo-bundle.yaml,
            .governance/capabilities/registry.yaml
            Command: python -c "import hashlib, pathlib
            files = [<list>]
            for f in files:
              h = hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
              print(f'{f}: {h}')
            "
    target: docs/agents/idempotency-proof.yaml (CREATE)
    operation: create
    expected: YAML with baseline_hashes section containing all 6 file hashes
    check: File exists; 6 hash entries present
    next: TC-ACP-016-01 IMPLEMENTED
```

#### TC-ACP-016-02 — Rerun and Compare

```
Child TC: TC-ACP-016-02 | Parent: TC-ACP-016 | Status: TODO
Preconditions: TC-ACP-016-01 IMPLEMENTED

Micro-steps:
  MS-016-02-01:
    action: Rerun python tools/capability_sync/run_sync.py;
            rerun python tools/agents/build_agent_bundle.py --agent codex
                        --output docs/agents/bundles/codex-bundle.yaml;
            rerun python tools/agents/build_agent_bundle.py --agent kilo
                        --output docs/agents/bundles/kilo-bundle.yaml
    operation: run
    expected: All 3 commands exit 0
    next: MS-016-02-02

  MS-016-02-02:
    action: Recompute SHA-256 of the same 6 files; compare with baseline hashes;
            record result in docs/agents/idempotency-proof.yaml second_run section
    operation: validate
    expected: All 6 hashes match baseline
    check: No hash mismatch; idempotency-proof.yaml second_run section shows "MATCH" for all
    failure: Hash mismatch → investigate which file changed and why;
             if timestamp-only change (e.g., bundle.generated field): acceptable;
             document as "EXPECTED_TEMPORAL_CHANGE";
             if content changed beyond timestamp → MATERIAL_SECOND_RUN_CHANGE → investigate
    next: MS-016-02-03

  MS-016-02-03:
    action: Run python tools/supervisor/governance_validator_runner.py second time;
            verify exit 0 and same validator count
    operation: run
    expected: Exit 0; same validator count (169+)
    check: Same count; exit 0
    next: TC-ACP-016-02 IMPLEMENTED

Parent acceptance criteria:
  - idempotency-proof.yaml shows MATCH or EXPECTED_TEMPORAL_CHANGE for all files
  - MATERIAL_SECOND_RUN_CHANGES = 0
  - DUPLICATE_AGENT_INSTRUCTIONS = 0
  - DUPLICATE_ADAPTERS = 0
```

---

## DEPENDENCY DAG (Machine-Readable)

```yaml
execution_dag:
  TC-ACP-001:
    prerequisites: []
    parallel_safe_with: []
    blocks: [TC-ACP-002, TC-ACP-006, TC-ACP-009, TC-ACP-010]

  TC-ACP-002:
    prerequisites: [TC-ACP-001]
    parallel_safe_with: []
    blocks: [TC-ACP-003, TC-ACP-007-02, TC-ACP-008, TC-ACP-009]

  TC-ACP-003:
    prerequisites: [TC-ACP-001]
    parallel_safe_with: []
    blocks: [TC-ACP-004, TC-ACP-005, TC-ACP-006, TC-ACP-008, TC-ACP-009, TC-ACP-010-03]

  TC-ACP-004:
    prerequisites: [TC-ACP-003]
    parallel_safe_with: [TC-ACP-005]
    blocks: [TC-ACP-007, TC-ACP-008, TC-ACP-009, TC-ACP-013]

  TC-ACP-005:
    prerequisites: [TC-ACP-002, TC-ACP-003]
    parallel_safe_with: [TC-ACP-004]
    blocks: [TC-ACP-008-04, TC-ACP-009-05, TC-ACP-014-02]

  TC-ACP-006:
    prerequisites: [TC-ACP-001, TC-ACP-003]
    parallel_safe_with: [TC-ACP-004, TC-ACP-005]
    blocks: [TC-ACP-007, TC-ACP-008, TC-ACP-009]

  TC-ACP-007:
    prerequisites: [TC-ACP-003, TC-ACP-004, TC-ACP-006]
    parallel_safe_with: [TC-ACP-008, TC-ACP-009, TC-ACP-010]
    blocks: [TC-ACP-011]
    file_locks: [.supervisor/skill-registry.yaml (agent_surfaces blocks)]

  TC-ACP-008:
    prerequisites: [TC-ACP-002, TC-ACP-003, TC-ACP-004, TC-ACP-005, TC-ACP-006, TC-ACP-007-02]
    parallel_safe_with: [TC-ACP-009, TC-ACP-010]
    blocks: [TC-ACP-011]
    file_locks: [.supervisor/skill-registry.yaml (codex opt-in), docs/governance/codex-adapter.md]
    NOTE: TC-ACP-007-02 and TC-ACP-008-03 both write to skill-registry.yaml.
          Execute 007-02 (add agent_surfaces blocks) BEFORE 008-03 (set codex values).
          Do NOT run in parallel with 007-02 step.

  TC-ACP-009:
    prerequisites: [TC-ACP-001, TC-ACP-002, TC-ACP-003, TC-ACP-005, TC-ACP-006, TC-ACP-007-02]
    parallel_safe_with: [TC-ACP-008, TC-ACP-010]
    blocks: [TC-ACP-011]
    file_locks: [.supervisor/skill-registry.yaml (kilo opt-in), .kilo/KILO.md]
    NOTE: TC-ACP-008-03 and TC-ACP-009-04 both write to skill-registry.yaml.
          Execute in sequence, not parallel. Run 008-03 completely before 009-04.

  TC-ACP-010:
    prerequisites: [TC-ACP-001, TC-ACP-003]
    parallel_safe_with: [TC-ACP-007, TC-ACP-008, TC-ACP-009]
    blocks: []

  TC-ACP-011:
    prerequisites: [TC-ACP-007, TC-ACP-008, TC-ACP-009]
    parallel_safe_with: []
    blocks: [TC-ACP-012]

  TC-ACP-012:
    prerequisites: [TC-ACP-011]
    parallel_safe_with: []
    blocks: [TC-ACP-013, TC-ACP-014-03, TC-ACP-014-04]

  TC-ACP-013:
    prerequisites: [TC-ACP-004, TC-ACP-012]
    parallel_safe_with: []
    blocks: [TC-ACP-014, TC-ACP-015]

  TC-ACP-014:
    prerequisites: [TC-ACP-002, TC-ACP-009, TC-ACP-011, TC-ACP-012]
    parallel_safe_with: [TC-ACP-015]
    blocks: [TC-ACP-016]

  TC-ACP-015:
    prerequisites: [TC-ACP-002, TC-ACP-012, TC-ACP-014]
    parallel_safe_with: [TC-ACP-014]
    blocks: [TC-ACP-016]

  TC-ACP-016:
    prerequisites: [all prior TCs CLOSED]
    parallel_safe_with: []
    blocks: []
```

---

## STATE MACHINE

```yaml
parent_transitions:
  valid:
    - [PROPOSED, READY]
    - [READY, IN_PROGRESS]
    - [IN_PROGRESS, CHILDREN_IN_PROGRESS]
    - [CHILDREN_IN_PROGRESS, INTEGRATION_PENDING]
    - [INTEGRATION_PENDING, VERIFIED]
    - [VERIFIED, SCORED]
    - [SCORED, CLOSED]
    - [SCORED, REROUTED]
    - [REROUTED, IN_PROGRESS]
    - [any_non_closed, BLOCKED]
    - [BLOCKED, READY]
    - [any_non_closed, BLOCKED_EXTERNAL]
    - [any_non_closed, DEFERRED_WITH_REASON]
  invalid_and_blocked:
    - [PROPOSED, CLOSED]   # must traverse all intermediate states
    - [READY, CLOSED]
    - [SCORED, IN_PROGRESS]  # must go through REROUTED first
    - [BLOCKED_EXTERNAL, CLOSED]  # must have unblock evidence first

child_transitions:
  valid:
    - [TODO, READY]
    - [READY, IN_PROGRESS]
    - [IN_PROGRESS, IMPLEMENTED]
    - [IMPLEMENTED, VERIFIED]
    - [VERIFIED, SCORED]
    - [SCORED, CLOSED]
    - [SCORED, REROUTED]
    - [REROUTED, IN_PROGRESS]
    - [any_non_closed, BLOCKED]
    - [BLOCKED, READY]
    - [any_non_closed, BLOCKED_EXTERNAL]
  invalid_and_blocked:
    - [TODO, CLOSED]       # must be implemented and verified first
    - [IMPLEMENTED, CLOSED]  # must be verified and scored
    - [REROUTED, CLOSED]  # must re-enter IN_PROGRESS and re-verify

micro_step_transitions:
  valid:
    - [PENDING, READY]
    - [READY, ACTIVE]
    - [ACTIVE, COMPLETE]
    - [ACTIVE, FAILED]
    - [ACTIVE, BLOCKED]
    - [FAILED, READY]
    - [BLOCKED, READY]
    - [PENDING, SKIPPED_NOT_APPLICABLE]
  rule: SKIPPED_NOT_APPLICABLE requires written rationale;
        micro-step may not be silently omitted

quality_scoring:
  threshold: 4/5 on all mandatory dimensions
  below_threshold_action: mark taskcard REROUTED; create repair child; re-score before CLOSED
  parent_dims: [root_cause_coverage, child_completeness, integration_completeness,
                dependency_correctness, preserved_behavior, evidence_completeness,
                rerun_consistency, production_readiness]
  child_dims: [requirement_correctness, implementation_correctness, scope_discipline,
               validation_strength, evidence_completeness, regression_safety,
               maintainability, production_readiness]
```

---

## VALIDATION MATRIX

| TC / Child | Validation Type | Command / Method | Expected | Mandatory |
|------------|-----------------|------------------|----------|-----------|
| TC-ACP-001-02 | Schema validation | `python -c "import yaml; yaml.safe_load(open('docs/agents/required-capability-model.yaml').read())"` | No exception | YES |
| TC-ACP-001-02 | Count check | `grep -c "capability_id: RC-" docs/agents/required-capability-model.yaml` | 22 | YES |
| TC-ACP-002-03 | Unit test | Inline test from MS-002-03-04 | PASS printed | YES |
| TC-ACP-002-04 | Schema parse | `python -c "import json; json.load(open('.governance/capabilities/schemas/capability.schema.json'))"` | No exception | YES |
| TC-ACP-002-05 | Registry kilo count | `grep -c "kilo: false" .governance/capabilities/registry.yaml` | >100 | YES |
| TC-ACP-002-05 | No opt-out default | `grep "codex: true" .governance/capabilities/registry.yaml` | Count = 0 (pre-opt-in) | YES |
| TC-ACP-003-02 | Schema + count | Inline from MS-003-02-04 | PASS printed | YES |
| TC-ACP-003-03 | Section presence | grep "delivery_mechanisms:", "conflict_resolution:" | Both found | YES |
| TC-ACP-004-02 | Pilot count | `grep -c "id: PILOT-"` | 12 | YES |
| TC-ACP-005-02 | Script help | `python tools/agents/build_agent_bundle.py --help` | Exit 0 | YES |
| TC-ACP-005-03 | Bundle structure | Inline from MS-005-03-02 | PASS | YES |
| TC-ACP-005-04 | run_sync.py end-to-end | `python tools/capability_sync/run_sync.py` | Exit 0 | YES |
| TC-ACP-006-02 | Hook syntax | `bash -n .git/hooks/pre-commit` | Exit 0 | YES |
| TC-ACP-006-03 | Warning emitted | Inline test from MS-006-03-03 | PASS | YES |
| TC-ACP-007-02 | Registry parse | `python -c "import yaml; yaml.safe_load(open('.supervisor/skill-registry.yaml').read())"` | No exception | YES |
| TC-ACP-007-03 | Claude entries | `grep -c "agent: claude" docs/agents/agent-inventory.yaml` | 22 | YES |
| TC-ACP-008-03 | Registry parse | Same as TC-ACP-007-02 | No exception | YES |
| TC-ACP-008-04 | run_sync.py | `python tools/capability_sync/run_sync.py` | Exit 0 | YES |
| TC-ACP-009-05 | Total inventory | `grep -c "agent:" docs/agents/agent-inventory.yaml` | 66 | YES |
| TC-ACP-011-01 | No COMPLETE_VERIFIED for Codex/Kilo | Inline from MS-011-01-03 | Count = 0 | YES |
| TC-ACP-012-01 | Parity entries | `grep -c "capability_id:" docs/agents/agent-parity-matrix.yaml` | 22 | YES |
| TC-ACP-013-01 | Pilot results | `grep -c "outcome:" docs/agents/pilots/pilot-results.yaml` | 36 | YES |
| TC-ACP-014-01 | Test run | `.venv/Scripts/pytest tests/agents/test_capability_opt_in.py -v` | 2 PASSED | YES |
| TC-ACP-014-02 | Test run | `.venv/Scripts/pytest tests/agents/test_bundle_completeness.py -v` | 3 PASSED | YES |
| TC-ACP-014-03 | Test run | `.venv/Scripts/pytest tests/agents/test_parity_matrix_coverage.py -v` | 3 PASSED | YES |
| TC-ACP-014-04 | Test run | `.venv/Scripts/pytest tests/agents/test_blocked_assignments.py -v` | 2 PASSED | YES |
| TC-ACP-014 (INT) | All tests | `.venv/Scripts/pytest tests/agents/ -v` | 10 PASSED, 0 FAILED | YES |
| TC-ACP-015-01 | Validator import | `python -c "from tools.supervisor.governance_validators_agent_parity import validate_agent_opt_in_not_default; print('OK')"` | OK | YES |
| TC-ACP-015-02 | Runner pass | `python tools/supervisor/governance_validator_runner.py` | Exit 0, 169+ validators | YES |
| TC-ACP-016-02 | Idempotency | Hash comparison from MS-016-02-02 | All MATCH or EXPECTED_TEMPORAL_CHANGE | YES |

---

## FILES CREATED (NEW)

| Path | Taskcard | Affected by DAG conflicts |
|------|----------|--------------------------|
| `docs/agents/kilo-platform-capabilities.md` | TC-ACP-001-01 | None |
| `docs/agents/required-capability-model.yaml` | TC-ACP-001-02 | None |
| `docs/agents/canonical-agent-contract.yaml` | TC-ACP-003 | None |
| `docs/agents/pilots/pilot-specs.yaml` | TC-ACP-004 | None |
| `docs/agents/pilots/pilot-results.yaml` | TC-ACP-013 | None |
| `docs/agents/bundles/agent-bundle-schema.yaml` | TC-ACP-005-01 | None |
| `docs/agents/bundles/codex-bundle.yaml` | TC-ACP-005-03; regenerated by 008-04 | Regenerated twice — idempotent |
| `docs/agents/bundles/kilo-bundle.yaml` | TC-ACP-005-04; regenerated by 009-05 | Regenerated twice — idempotent |
| `tools/agents/build_agent_bundle.py` | TC-ACP-005-02 | None |
| `docs/governance/codex-instructions.md` | TC-ACP-008-01 | None |
| `docs/governance/kilo-adapter.md` | TC-ACP-009-02 | None |
| `.kilo/KILO.md` | TC-ACP-009-01 | None |
| `docs/agents/model-profiles.yaml` | TC-ACP-010-02 | None |
| `docs/agents/agent-inventory.yaml` | TC-ACP-007-03 + 008-04 + 009-05 (sequential appends) | Write order matters: Claude first, then Codex, then Kilo |
| `docs/agents/agent-parity-matrix.yaml` | TC-ACP-012-01 | None |
| `tests/agents/__init__.py` | TC-ACP-014-01 | None |
| `tests/agents/test_capability_opt_in.py` | TC-ACP-014-01 | None |
| `tests/agents/test_bundle_completeness.py` | TC-ACP-014-02 | None |
| `tests/agents/test_parity_matrix_coverage.py` | TC-ACP-014-03 | None |
| `tests/agents/test_blocked_assignments.py` | TC-ACP-014-04 | None |
| `tools/supervisor/governance_validators_agent_parity.py` | TC-ACP-015-01 | None |
| `docs/agents/idempotency-proof.yaml` | TC-ACP-016 | None |

## FILES MODIFIED

| Path | Taskcard | Change | Conflict Risk |
|------|----------|--------|---------------|
| `tools/capability_sync/inventory_capabilities.py` | TC-ACP-002-03 | opt-in logic + kilo column | LOW: single function change |
| `.supervisor/skill-registry.yaml` | TC-ACP-002-02 (schema); TC-ACP-007-02 (agent_surfaces blocks); TC-ACP-008-03 (codex opt-in); TC-ACP-009-04 (kilo opt-in) | Sequential writes — must not overlap | HIGH: execute in order 002-02 → 007-02 → 008-03 → 009-04 |
| `.governance/capabilities/schemas/capability.schema.json` | TC-ACP-002-04 | kilo field | LOW |
| `.governance/capabilities/schemas/parity-report.schema.json` | TC-ACP-002-04 | kilo section | LOW |
| `.governance/capabilities/registry.yaml` | TC-ACP-002-05 (via run_sync.py) + TC-ACP-008-04 + TC-ACP-009-05 (re-runs of run_sync.py) | Generated file; idempotent reruns OK | MEDIUM: each run_sync.py regenerates it cleanly |
| `.governance/capabilities/parity-report.yaml` | TC-ACP-002-05 | Kilo section + parity_status corrections | LOW |
| `tools/capability_sync/run_sync.py` | TC-ACP-005-04 | bundle generation step added | LOW: append step only |
| `tools/supervisor/sprint_executor_validate.py` | TC-ACP-006-03 | authorization_id warning check | LOW: addition only |
| `docs/governance/codex-adapter.md` | TC-ACP-006-04 (DEC-014); TC-ACP-008-02 (lifecycle extension) | Two sequential edits | LOW: different sections |
| `docs/governance/skill-only-policy.yaml` | TC-ACP-006-04 | EP-002-GAP status update only | LOW |
| `.kilo/kilo.jsonc` | TC-ACP-009-03 | governance references | LOW |
| `tools/supervisor/governance_validator_runner.py` | TC-ACP-015-02 | V166-V169 + dynamic count | MEDIUM: count change |
| `.github/workflows/<workflow>` | TC-ACP-015-03 | path trigger for agent parity | LOW |

## PRESERVED (DO NOT CHANGE)

| Item | Reason |
|------|--------|
| `docs/governance/skill-only-policy.yaml` contents (except EP-002-GAP status) | Authority for skill execution mechanics |
| `AGENTS.md` Markdown table | Human-readable documentation; bundles replace as machine-readable feed |
| `CLAUDE.md` | Claude session contract; only update if TC-ACP-007-01 finds missing RC coverage |
| Existing 165 governance validators (V1-V165) | Extended not replaced; V166-V169 added |
| `.supervisor/skill-registry.yaml` skill entry DATA | Only agent_surfaces schema block and per-skill opt-in fields added |
| `tools/governance/pre_mutation_guard.py` interface | CLI signature unchanged; hook invokes existing script |

---

## SUPPORTING ARTIFACTS LEDGER

```yaml
authoritative_plan: plans/.claude/glimmering-hopping-kazoo.md
artifact_role: analysis_or_evidence_only
execution_authority: false

# All supporting artifacts referenced here are produced DURING execution of this plan.
# They are evidence artifacts, not competing plans.

artifacts:
  - id: ART-001
    name: taskcardization-preflight.md
    produced_at: plan analysis time (pre-execution)
    content: EMBEDDED in this plan (PREFLIGHT RECORD section)
    execution_authority: false

  - id: ART-002
    name: section-processing-ledger.yaml
    produced_at: plan analysis time
    evidence: All 16 TC-ACP sections were read in full; all actionable items extracted and
              decomposed. No prose sections were skipped. All completion criteria and
              verification steps were extracted and placed in child taskcards.
    execution_authority: false

  - id: ART-003
    name: execution-dag.yaml
    produced_at: plan enhancement time
    content: EMBEDDED in this plan (DEPENDENCY DAG section)
    execution_authority: false

  - id: ART-004
    name: taskcard-state-machine.yaml
    produced_at: plan enhancement time
    content: EMBEDDED in this plan (STATE MACHINE section)
    execution_authority: false

  - id: ART-005
    name: verification-matrix.md
    produced_at: plan enhancement time
    content: EMBEDDED in this plan (VALIDATION MATRIX section)
    execution_authority: false

  - id: ART-006
    name: evidence-obligation-matrix
    produced_at: per-taskcard
    content: Each child taskcard specifies "Evidence required" and "Acceptance checks"
    execution_authority: false

  - id: ART-007
    name: solution-options-analysis
    note: "For TC-ACP-002 (opt-out default fix): Option A (suppress warning) rejected —
           does not fix root cause. Option B (opt-in field) selected — fixes root cause
           in inventory_capabilities.py. Option C (governance validator only) rejected —
           too late in the pipeline. Option D (hybrid: schema + inventory + validator) selected."
    execution_authority: false
```

---

## EXECUTION HANDOFF

The execution agent receiving this plan MUST follow these steps exactly:

### Before Starting Any Taskcard
1. Read this entire plan (all sections, not just the first TC)
2. Verify current repository state matches plan prerequisites:
   - Branch: main
   - No uncommitted changes to files in the Files Modified list
3. Run `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/glimmering-hopping-kazoo.md`
   (AFTER migrating from external path per CLAUDE.md Step 0)
4. Read the DEPENDENCY DAG to understand execution order

### For Each Taskcard
5. Read the parent taskcard schema: Objective, Scope, Dependencies, Child taskcards
6. Verify all listed Dependencies are CLOSED before beginning
7. Select the first child taskcard (TODO status)
8. Read the child taskcard in full: Purpose, Scope, Inputs, Micro-steps
9. Verify Preconditions for the child are met
10. Execute micro-steps ONE AT A TIME:
    - Read the micro-step: action, target, operation, expected, check, failure handling
    - Execute exactly the specified action on exactly the specified target
    - Do NOT broaden scope to neighboring files
    - Capture the evidence specified
    - Verify the completion check passes
    - If check fails → follow failure handling; do NOT proceed to next step
    - Update micro-step status to COMPLETE
    - Move to next micro-step
11. After all micro-steps complete → run Acceptance checks for the child
12. All acceptance checks pass → mark child IMPLEMENTED
13. Run focused test/validation from the Validation Matrix for this child
14. Pass → mark child VERIFIED
15. Score child against quality dimensions (must be ≥ 4/5 on all)
16. Pass → mark child CLOSED
17. Below threshold on any dim → mark REROUTED; create repair micro-step; re-score
18. After all children CLOSED → run Parent acceptance criteria checks
19. Run integration tests listed under parent Integration checks
20. All pass → mark parent VERIFIED → SCORED → CLOSED
21. Consult DEPENDENCY DAG for next valid parent taskcard
22. Repeat from step 5

### Forbidden During Execution
- Do NOT close a parent while any mandatory child is not CLOSED
- Do NOT treat code existence as verification (must run the check command)
- Do NOT mark a child CLOSED without evidence recorded
- Do NOT modify files not listed in the child's Allowed files scope
- Do NOT run TC-ACP-008-03 and TC-ACP-009-04 in parallel (both write skill-registry.yaml)
- Do NOT invent work not described in the taskcards
- Do NOT escalate to product deepening while this plan is active

### On Completion of All 16 Parent Taskcards
- Run: `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/glimmering-hopping-kazoo.md --terminal`
- Report: "Plan glimmering-hopping-kazoo complete. All 16 taskcards closed. Awaiting your next instruction."
- Do NOT call check_continuation.py
- Do NOT start product deepening sprints

---

## Taskcard Status Summary Table

| TC-ID | Parent Status | Children | Notes |
|-------|--------------|----------|-------|
| TC-ACP-001 | PROPOSED | TC-ACP-001-01, TC-ACP-001-02 | First in DAG; no prerequisites |
| TC-ACP-002 | PROPOSED | 001-02-03-04-05 | Blocked until TC-ACP-001 CLOSED |
| TC-ACP-003 | PROPOSED | 001-02-03 | Blocked until TC-ACP-001 CLOSED |
| TC-ACP-004 | PROPOSED | 001-02 | Blocked until TC-ACP-003 CLOSED |
| TC-ACP-005 | PROPOSED | 001-02-03-04 | Blocked until TC-ACP-002 + TC-ACP-003 CLOSED |
| TC-ACP-006 | PROPOSED | 001-02-03-04 | Blocked until TC-ACP-001 + TC-ACP-003 CLOSED |
| TC-ACP-007 | PROPOSED | 001-02-03 | Blocked until TC-ACP-003+004+006 CLOSED |
| TC-ACP-008 | PROPOSED | 001-02-03-04 | Blocked until TC-ACP-002+003+004+005+006+007-02 CLOSED |
| TC-ACP-009 | PROPOSED | 001-02-03-04-05 | Blocked until TC-ACP-001+002+003+005+006+007-02 CLOSED |
| TC-ACP-010 | PROPOSED | 001-02-03 | Can run parallel with TC-ACP-007+008+009 |
| TC-ACP-011 | PROPOSED | 001 | Blocked until TC-ACP-007+008+009 CLOSED |
| TC-ACP-012 | PROPOSED | 001 | Blocked until TC-ACP-011 CLOSED |
| TC-ACP-013 | PROPOSED | 001-02-03 | Blocked until TC-ACP-004+012 CLOSED |
| TC-ACP-014 | PROPOSED | 001-02-03-04 | Blocked until TC-ACP-002+009+011+012 CLOSED |
| TC-ACP-015 | PROPOSED | 001-02-03 | Blocked until TC-ACP-002+012+014 CLOSED |
| TC-ACP-016 | PROPOSED | 001-02 | Blocked until ALL prior TCs CLOSED |
