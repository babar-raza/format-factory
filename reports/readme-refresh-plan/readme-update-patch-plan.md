# TC-README-PLAN-005: README Update Patch Plan
# Sprint: FORMAT-FACTORY-ROOT-README-REFRESH-PLAN-001
# Generated: 2026-06-05

## Strategy: Full Replacement

**Decision: FULL REPLACEMENT of README.md**

Rationale:
1. Every existing section requires either major rewrite or complete replacement
2. The structural change is too large for targeted section patches:
   - 14 new sections to add (vs 11 current sections)
   - Core architecture (four-stream model, AI boundary, external tools, autonomous supervisor) is ENTIRELY absent
3. Current Status section is ~100 sprints stale (references R18; latest is R118)
4. Six format families framing is misleadingly broad vs. specific POC targets
5. The agent methodology section points to stale doc references
6. A patchwork approach risks missing stale language embedded in kept sections

---

## Execution Order (for the implementing agent)

### Step 1: Read Required Files (mandatory before Write)

The Write tool requires all files to be read before they can be overwritten.

```
Read: README.md                                       (REQUIRED before any Write)
Read: reports/readme-refresh-plan/readme-content-plan.md
Read: reports/readme-refresh-plan/readme-target-outline.md
Read: reports/readme-refresh-plan/repo-state-map.json
Read: state/current-state.md                          (for current status section)
Read: reports/supervisor/approval-gates.md            (for gate status)
Read: product-capability-matrix/poc-targets.yaml      (verify POC targets are current)
```

### Step 2: Verify Key Facts Before Writing

Before writing README.md, verify these claims are still current (they may have changed since this plan):

```python
# Verify poc-targets.yaml still lists FODS, FODT, Netpbm as commercial .NET
# Verify poc-targets.yaml still lists ZST, PBM/PGM/PPM, SYLK as FOSS targets
# Verify approval-gates.md still says AUTONOMOUS_CONTINUE: YES
# Verify Gate 11 still NOT_STARTED
# Verify commercial_product_ready: false
# Verify session-resume.md for latest sprint ID
```

### Step 3: Write README.md (single Write call)

Execute a single Write tool call replacing all 160 current lines with the new ~370-line content.
Structure: exactly 14 sections as defined in readme-target-outline.md.
Content: exactly as specified in readme-content-plan.md.

### Step 4: Verify No Other Files Changed

```bash
git diff --stat HEAD -- README.md      # Should show only README.md changed
git diff HEAD -- src/ tests/           # Should show NO changes
git diff HEAD -- product-capability-matrix/ registry/  # Should show NO changes
```

### Step 5: Run Content Verification

```bash
# Verify required sections exist
grep -c "^## " README.md              # Should be 14 or close

# Verify key claims are present
grep -i "netpbm" README.md            # Should appear in POC targets
grep -i "four-stream" README.md       # Should appear in stream section
grep -i "ai.*draft\|draft.*ai" README.md   # Should appear in AI boundary section
grep -i "ruflo" README.md             # Should appear in external tools
grep -i "autonomous supervisor\|autonomous-cycle" README.md  # Should appear

# Verify prohibited claims are absent
grep -i "commercial_product_ready.*true" README.md   # Should return nothing
grep -i "gate 11.*approved" README.md                # Should return nothing
grep -i "svg.*target\|target.*svg" README.md         # Should return nothing
```

---

## Rollback Plan

If the README.md Write produces incorrect content or the agent wants to revert:

```bash
git checkout -- README.md
```

This restores README.md to the R93 committed version. Since the worktree is dirty (R94–R118 uncommitted),
no other work is affected. The file at R93 is the current "safe" baseline.

---

## Validation Commands (for TC-007)

After README.md is written, the implementing agent must run and capture:

```bash
# 1. Confirm README.md changed, nothing else under monitored paths
git diff --stat HEAD -- README.md src/ tests/ product-capability-matrix/ registry/

# 2. Count sections in new README
grep -c "^## \|^# " README.md

# 3. Spot-check key sections exist
grep -n "Four-Stream\|Product-First\|POC Targets\|External Tools\|AI.*Authority\|What Not To Do" README.md

# 4. Verify no overclaiming
grep -in "commercial_product_ready: true\|gate 11.*approved\|production.ready" README.md

# 5. Python JSON check for repo-state-map.json
python -c "import json; f=open('reports/readme-refresh-plan/repo-state-map.json'); json.load(f); print('JSON valid')"

# 6. Final git status
git status --short
```

---

## Expected Changed Files (Execution Sprint)

| File | Change Type | Justification |
|------|-------------|---------------|
| README.md | FULL REPLACEMENT | Primary deliverable of this sprint |
| reports/readme-refresh-execution/*.md | CREATE | Sprint execution evidence |
| .local/evidences/readme-refresh-execution/evidence-declaration.yaml | CREATE | Sprint evidence declaration |
| .local/evidences/readme-refresh-execution/evidence-manifest.yaml | CREATE | Sprint evidence manifest |

**Files that must NOT change:**
- src/net/**
- src/python/**
- tests/**
- registry/format-registry.yaml
- product-capability-matrix/poc-targets.yaml
- plans/master-plan.md
- docs/governance/**
- .supervisor/**

---

## Hard Prohibitions (carry forward to execution sprint)

- No commit
- No push
- No Gate 8 or Gate 11 approval
- No external tool install
- No product source edits (src/net/, src/python/)
- No test edits
- No registry/poc-targets mutation

---

## Notes for Execution Agent

1. The README should use present tense throughout — these are current facts, not plans.
2. Conditional content (Ruflo, Superpowers, Gnumeric) should be explicitly marked as NOT YET ACTIVE.
3. Do not claim any format is "production ready" — all are POC targets.
4. Preserve the legal/IP disclaimer from Section 1 (it is accurate and important).
5. Section 13 (Current Status) should explicitly note: "For the authoritative current state, always read `state/current-state.md` and `reports/supervisor/session-resume.md` — not this README."
6. The product-code ledger note (R90+) in Section 8 should link to the actual tool: `tools/supervisor/validate_product_code_ledger.py`.
7. Do not add a "Future Plans" section — the roadmap lives in `plans/master-plan.md`, not README.
