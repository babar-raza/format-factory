# R14 Evidence Contradiction Classification
Sprint: FORMAT-FACTORY-R14C-ZST-GATE2-CLOSURE-REPAIR-AND-IV-SWARM-001
Gate: 1 (Lane B)
Date: 2026-05-15

---

## Contradiction Findings

### Finding 1: Does commit 2e24110 exist?
**YES** — Confirmed via `git show --stat --oneline 2e24110`. It is the HEAD commit on main.

### Finding 2: Does commit 2e24110 include all R14 changed files?
**YES** — 28 files changed, 1767 insertions. All R14 required files present:
- All reports (governance, verification, legal, planning, specs, testing)
- registry/format-registry.yaml, plans/master-plan.md, README.md
- acquisition-packs/zst/ (legal-notes.md, pack.yaml, spec-evidence.md)
- taskcards (ZST-R14-SPEC-RETRIEVAL.md, ZST-GATE2-IV.md, ZST-R15-GATE3-SAMPLE-SOURCES.md, ZST-GATE1-DECISION-PACKET.md)
- memory/31-zst-r14-gate2-spec-retrieval-20260515.md
- tests/skills/test_zst_spec_cache_gate2.py
- tools/evidence/contracts/r14-zst-spec-retrieval-and-gate2-swarm.yaml

### Finding 3: Are R14 changes still present in working tree (uncommitted)?
**NO** — All R14 changes are committed. Working tree is clean.

### Finding 4: Was the R14 evidence bundle built before the claimed commit?
**YES** — Classification: BUNDLE_BUILT_BEFORE_COMMIT.
The build order was: (1) write files → (2) build bundle → (3) stage → (4) commit.
This is why `git-log.txt` starts at 9b4e624 and `git-status-final.txt` shows files as unstaged.

### Finding 5: Does final git status in the bundle invalidate the closure claim?
**PARTIALLY** — The bundle's git-status-final.txt reflects pre-commit state. This is not a real blocker (commit exists), but means the bundle cannot serve as clean post-commit closure evidence. Classification: BUNDLE_BUILT_BEFORE_COMMIT / STALE_METADATA.

### Finding 6: Does emergency_blocker_bundle=true mean the bundle should not be treated as clean closure evidence?
**YES** — `emergency_blocker_bundle: true` in the R14 contract was used to allow building the bundle with a dirty git state. Per base-run.yaml policy, this is reserved for blocker/failed bundles. Using it for a normal PASS bundle (even with a known pre-existing untracked issue) means the bundle metadata is pre-commit. Repair: rebuild with `require_clean_git: false` and `emergency_blocker_bundle: false` after confirming post-commit state.

### Finding 7: Does the spec cache exist locally and match recorded hashes?
**YES** — `.local/spec-cache/zst/` fully intact. SHA-256 verified:
- RFC 8878: sha256:8ee6be03534113f5689cda75b9539a02e0704a2506d420814223e506420aeea4 ✓
- RFC 9659: sha256:a43584f250506db54df8bc9ff90652888135369fbc331453f67a71829b0827a2 ✓

---

## Classification Summary

| Item | Classification | Repair Action |
|------|----------------|---------------|
| commit 2e24110 exists | POST_BUNDLE_COMMIT_EXISTS | No repair needed |
| bundle git-log shows 9b4e624 | BUNDLE_BUILT_BEFORE_COMMIT | Rebuild bundle post-commit |
| bundle git-status shows unstaged files | BUNDLE_BUILT_BEFORE_COMMIT | Rebuild bundle post-commit |
| emergency_blocker_bundle=true | STALE_METADATA | Rebuild with clean post-commit state |
| spec cache absent from bundle | N/A (gitignored by policy) | Add spec-cache-manifest-record.md |
| spec cache hashes verified | NO_ISSUE | None |

---

## Conclusion

**No REAL_BLOCKER. No COMMIT_MISSING.** R14 sprint work is correctly committed in 2e24110. The contradiction is entirely a BUILD_ORDER_ARTIFACT: the evidence bundle was built before the commit, not after. R14C repair consists of:
1. Running independent verification (this sprint IS the IV)
2. Adding spec-cache-manifest-record.md as committed evidence proxy for gitignored cache
3. Rebuilding the evidence bundle in post-commit clean state

R14C does NOT need to recommit R14 files. It commits only R14C new files.

---

CONTRADICTION_CLASSIFICATION: BUNDLE_BUILT_BEFORE_COMMIT (NO_BLOCKER)
