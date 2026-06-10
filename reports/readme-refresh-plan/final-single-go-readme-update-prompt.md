# TC-README-PLAN-006: Final README Update Execution Prompt
# Sprint: FORMAT-FACTORY-ROOT-README-REFRESH-PLAN-001
# Generated: 2026-06-05
#
# STATUS: EXECUTION-READY — Send this prompt verbatim to execute the README update.

---

```
Sprint ID: FORMAT-FACTORY-ROOT-README-REFRESH-EXECUTION-001
Run ID: readme-refresh-execution
Sprint Goal: Update README.md to accurately reflect the current project state.

This is a DOCUMENTATION-ONLY sprint. No product source changes. No commits. No pushes.

---

MANDATORY PREFLIGHT (do these before writing README.md):

1. Read README.md (required before any Write to README.md)
2. Read reports/readme-refresh-plan/readme-content-plan.md (content spec per section)
3. Read reports/readme-refresh-plan/readme-target-outline.md (14-section structure)
4. Read reports/readme-refresh-plan/repo-state-map.json (confirmed repo facts)
5. Read state/current-state.md (current sprint + stream state)
6. Read reports/supervisor/session-resume.md (latest sprint + supervisor mode)
7. Read reports/supervisor/approval-gates.md (gate status + AUTONOMOUS_CONTINUE)
8. Read product-capability-matrix/poc-targets.yaml (verify POC targets before claiming)

---

ALLOWED WRITE PATHS:
- README.md
- reports/readme-refresh-execution/**
- .local/evidences/readme-refresh-execution/**

READ-ONLY PATHS (must read before claiming, must not edit):
- src/net/**
- src/python/**
- tests/**
- registry/format-registry.yaml
- product-capability-matrix/poc-targets.yaml
- plans/master-plan.md
- docs/governance/**
- .supervisor/**
- reports/readme-refresh-plan/**

FORBIDDEN EDITS (hard prohibition):
- src/net/**, src/python/**, tests/**  — no product source changes
- registry/format-registry.yaml       — no registry edits
- product-capability-matrix/poc-targets.yaml — no POC targets edits
- plans/master-plan.md                — no plan edits
- Any git commit, push, or publish
- Any Gate 8 or Gate 11 approval
- Any Ruflo, Superpowers, or GhidraMCP install

---

STRATEGY: FULL REPLACEMENT of README.md

The current README.md (160 lines) requires full replacement. Structural changes are too large
for targeted edits. Replace all content with the 14-section structure below.

Target README structure (exact headings):

1.  # Format Factory
2.  ## Product-First Mission
3.  ## Current POC Targets
4.  ## Repository Layout
5.  ## Four-Stream Operating Model
    ### Mainstream Product
    ### Acceleration / AI Cognitive Layer
    ### Skills / Governed Execution
    ### Autonomous Supervisor / Continuation
6.  ## External Tools
    ### Ruflo
    ### Superpowers Marketplace
    ### GhidraMCP
7.  ## AI Usage and Authority Boundary
8.  ## Governance and Safety Rules
9.  ## Evidence, Taskcards, and Review Packages
10. ## How to Inspect Current State
11. ## How to Run Safe Local Checks
12. ## How Agents Should Work in This Repo
13. ## Current Status
14. ## What Not To Do
15. ## License

(Section 15 License is a brief carry-forward from current README.)

---

HARD CONTENT CONSTRAINTS (verify each before writing):

DO include:
- "commercial_product_ready: false" — CONFIRMED from approval-gates.md
- "Gate 11 NOT_STARTED" — CONFIRMED from approval-gates.md
- Netpbm .NET as third commercial product — CONFIRMED from src/net/netpbm/
- ZST, Python Netpbm (PBM/PGM/PPM), SYLK as FOSS targets — CONFIRMED from poc-targets.yaml
- "AI thinks and drafts. Evidence decides." — from ai-authority-boundary.md
- "Ruflo: NOT installed; full loop requires Supervisor approval + human auth" — governance intent
- "GhidraMCP: DISABLED_BY_DEFAULT" — from ghidra-mcp-compliance-gate.md
- "SVG is NOT a POC target (Aspose already supports SVG; Netpbm is the imaging target)"
- "For authoritative current state, always read state/current-state.md and session-resume.md — not this README"

DO NOT include:
- "commercial_product_ready: true" — FALSE
- "Gate 11 approved" — FALSE
- "Ruflo installed/active" — FALSE (not installed)
- "Superpowers skills installed" — FALSE (none installed)
- Any format listed as "production ready" — all are POC targets
- SVG as an imaging target — governance prohibits this
- DIF or Gnumeric as active POC targets — both are on-hold or staged

---

EVIDENCE FACTS TO USE (all CONFIRMED from repo files):

Products:
- FODS .NET: src/net/fods/ | tests/net/fods/ (116+) | Gates 1-10 PASSED | Gate 11 NOT_STARTED
- FODT .NET: src/net/fodt/ | tests/net/fodt/ (115+) | Gates 1-10 PASSED | Gate 11 NOT_STARTED
- Netpbm .NET: src/net/netpbm/ | tests/net/netpbm/ (48+) | POC active
- ZST: src/python/zst/ | tests/python/zst/ (20+) | production_track_real
- Python Netpbm: src/python/pbm/, pgm/, ppm/ | tests/python/pbm/, pgm/, ppm/ | production_track_real
- SYLK: src/python/sylk/ | tests/python/sylk/ (16+) | POC active

Writer libraries (built in MWP-DOGFOOD-UNBLOCKING sprint):
- src/net/csv/ (CsvWriter.cs) — unblocks FODS→CSV dogfood
- src/net/html/ (HtmlWriter.cs) — unblocks FODS→HTML dogfood
- src/net/txt/ (TxtWriter.cs) — unblocks FODT→TXT dogfood
- src/net/markdown/ (MarkdownWriter.cs) — unblocks FODT→Markdown dogfood

Governance:
- 13 governance docs in docs/governance/
- 15 prompt templates in docs/prompt-templates/
- 39 supervisor tools in tools/supervisor/
- 25 skills (24 active) in .supervisor/skill-registry.yaml
- 30 skill command files in .claude/commands/

Current state:
- Latest sprint: R118 (2026-06-05)
- Last committed: R93 (2026-06-02)
- AUTONOMOUS_CONTINUE: YES
- MCP: MODE 4 ACTIVE
- Tests last sprint: 1423 passed / 0 failed

---

VALIDATION COMMANDS (run after writing README.md):

```bash
# 1. Confirm only README.md changed under monitored paths
git diff --stat HEAD -- README.md src/ tests/ product-capability-matrix/ registry/

# 2. Check required sections are present
grep -c "^## \|^# " README.md

# 3. Spot-check key content
grep -n "Netpbm\|Four-Stream\|Product-First\|External Tool\|Authority Boundary" README.md

# 4. Verify no overclaiming
grep -in "commercial_product_ready: true\|gate 11.*approved\|production.ready" README.md

# 5. Validate repo-state-map.json still parses
python -c "import json; json.load(open('reports/readme-refresh-plan/repo-state-map.json')); print('JSON valid')"

# 6. Capture final git status
git status --short
```

---

SPRINT CLOSEOUT REQUIREMENTS:

1. Write .local/evidences/readme-refresh-execution/evidence-declaration.yaml

   Required fields:
   - sprint_id: FORMAT-FACTORY-ROOT-README-REFRESH-EXECUTION-001
   - run_id: readme-refresh-execution
   - worker_verdict: (one of: README_REFRESHED_COMPLETE | README_REFRESHED_WITH_LIMITATIONS | README_REFRESH_BLOCKED)
   - readme_not_edited: false (it WAS edited in this execution sprint)
   - no_product_source_edits: true
   - no_commit: true
   - no_push: true
   - no_gate_approval: true
   - no_external_tool_install: true
   - changed_files: [README.md]
   - files_created: [reports/readme-refresh-execution/..., .local/evidences/readme-refresh-execution/...]
   - tests_supporting: [] (no tests for README changes)
   - validation_results: (output of git diff --stat + grep checks above)

2. Run autonomous-cycle:
   python tools/supervisor/supervisor_loop.py autonomous-cycle \
     --declaration .local/evidences/readme-refresh-execution/evidence-declaration.yaml

3. Build review package:
   python tools/supervisor/build_declaration_review_package.py \
     --declaration .local/evidences/readme-refresh-execution/evidence-declaration.yaml

4. Capture ZIP path and SHA-256.

---

FINAL RESPONSE CONTRACT:

Your final response MUST include:
- README.md updated: YES/NO
- Sections added: (count)
- Line count before: 160 / Line count after: (actual)
- Absolute path to review package ZIP (full Windows path starting with C:\...)
- SHA-256 of review package
- Output of: git diff --stat HEAD -- README.md src/ tests/
- Explicit confirmation: no src/, tests/, registry/, poc-targets.yaml edits
- Explicit confirmation: no commit, no push, no Gate 8, no Gate 11, no external tool install
- Explicit confirmation: README.md was READ before being written (Write tool requirement)

ALLOWED VERDICTS (use exactly one):
1. README_REFRESHED_COMPLETE
   - README.md fully replaced with 14-section structure
   - All validation checks pass
   - Evidence package built
   - No prohibited edits

2. README_REFRESHED_WITH_LIMITATIONS
   - README.md replaced
   - Some sections have conditional/unverified claims (explicitly flagged in doc)
   - Evidence package built
   - No prohibited edits

3. README_REFRESH_BLOCKED
   - README.md NOT updated
   - Reason: (specific blocker)
   - Evidence package still required
```

---

## Prompt Verification Checklist

Before sending the above prompt, verify:

- [x] Allowed paths listed (README.md + reports/readme-refresh-execution/)
- [x] Forbidden paths listed (src/, tests/, registry/, poc-targets.yaml, plans/)
- [x] No overclaiming constraints included (commercial_product_ready, Gate 11, SVG)
- [x] No commit/push/publication prohibition included
- [x] Evidence bundle requirement included (declaration.yaml + autonomous-cycle + review package)
- [x] Final response must include absolute evidence bundle path (SHA-256)
- [x] Three allowed verdicts defined
- [x] Validation commands included
- [x] Evidence facts are evidence-backed (not from memory)
- [x] Prompt is self-contained (does not require prior context to execute)
