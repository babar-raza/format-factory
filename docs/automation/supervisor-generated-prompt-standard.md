# Supervisor-Generated Prompt Standard

## Required Sections (8)

Every generated next-worker prompt must contain these sections in order:

### 1. Read Before Execution
Lists authority files the worker must read before starting:
- CLAUDE.md
- AGENTS.md
- plans/master-plan.md
- reports/supervisor/session-resume.md
- .supervisor/policies.yaml
- registry/format-registry.yaml

### 2. Previously Accepted Work
Summary of items graded ACCEPTED or ACCEPTED_WITH_WARNINGS in the current cycle.

### 3. Rework Lane (Priority 1)
Items graded REWORK_REQUIRED, with:
- Item ID and title
- What was wrong (missing evidence, failed tests, etc.)
- What the worker must do to fix it
- Acceptance criteria

### 4. System-Healing Lane (Priority 2)
Infrastructure and tooling repairs:
- Supervisor tool fixes
- Schema updates
- Test framework repairs

### 5. Product-Advancement Lane (Priority 3)
Forward work from the product-factory targets:
- Commercial .NET targets (FODS, FODT, QOI/Netpbm)
- FOSS reduced-scope targets (ZST, PBM/PGM/PPM, SYLK/DIF)
- Dogfood exports (PBM->PGM, SYLK->CSV, DIF->CSV)

### 6. Evidence-Hardening Lane (Priority 4)
Improvements to evidence quality:
- Missing tests
- Schema compliance gaps
- Documentation gaps

### 7. State Sync Lane (Priority 5)
Memory and state synchronization:
- Memory file updates
- Session-resume updates
- Approval gate updates

### 8. Verification Lane (Priority 6)
Final verification tasks:
- Run full test suite
- Validate evidence declaration
- Check for regressions

## Additional Sections

After the 8 required lanes, the prompt includes:

### Blocked Items
Items graded BLOCKED_EXTERNAL_GATE with the gate that blocks them.

### Hard Prohibitions
Actions the worker must never take autonomously.

### Final Evidence Declaration Requirements
Instructions for the worker to create the evidence directory and declaration for their sprint.

## Format

The prompt is written as Markdown. Each section uses `##` headers. Items within sections use bullet lists with item IDs.
