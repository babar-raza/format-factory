# Governance Discovery — dual-orchestration-supervisor-e2e-20260530-165603

## Governance Files Found
- AGENTS.md: present (not read in full — governs agent behavior, non-negotiable rules)
- GOVERNANCE.md: present (governs product readiness, gate approval, commercial standards)
- plans/master-plan.md: present (operational authority, Phase 3 current state)
- registry/format-registry.yaml: present (gate status, L1 authority)
- .claude/settings.json: present (78 allow entries, valid JSON)
- .gitignore: present

## Key Governance Rules (from MEMORY.md and prior exploration)
- AGENTS.md §AE: git-safety — no push, no amend published commits
- AGENTS.md §Y: evidence — build via build_evidence_bundle.py, validate before reporting
- AGENTS.md §Z: run-state — .local/ is ephemeral; .supervisor/state/ must be gitignored
- GOVERNANCE.md §26.8: commercial readiness NOT declared by this sprint
- GOVERNANCE.md §26.14: AI platform operating model consulted for AI work
- Gate 11 sub-gate G11-G: NOT_STARTED — human approval required (Babar Raza)
- No push without explicit user authorization
- No commit without explicit user authorization

## Current Product State
- Phase: 3 — FODS/FODT Gates 1-10 PASSED; Gate 11 G11-G NOT_STARTED
- Latest sprint: R78 (FODS product slice complete, ZST local RC ready)
- R78 HEAD: 9b4e9e38a254b24ccb558e2b9dcb21d5f59c3506
- This sprint does NOT advance any product gates

## Evidence Builder Interface
- build_evidence_bundle.py: requires --repo-root, --contract, --output
- validate_evidence_bundle.py: requires --contract, --bundle
- Contract format: YAML with sprint_id, required_repo_files, min_metadata_count, etc.
- This sprint needs its own contract for the evidence bundle

## .claude/settings.json Allow List Status
- Current allow list: 78 entries
- Missing entries needed: tools/supervisor/**, .supervisor/**, tests/taskmaster/**,
  reports/supervisor/**, tools/taskmaster/**, docs/automation/**,
  reports/dual-orchestration-supervisor-e2e/**
- Action: PHASE 5 will append these (read-first, append-only, validate JSON after)

## .gitignore Status
- Current: covers .local/, .env, node_modules/, Python/dotnet artifacts
- Missing: .supervisor/state/, .vscode/mcp.json, .env.taskmaster, .ruflo/**, .swarm/
- Action: PHASE 5 will append (append-only, no existing entries removed)
