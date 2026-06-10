# EXECUTION MODE — SPECIFICATION AUTHORITY LAYER MWP IMPLEMENTATION
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-MWP-IMPLEMENTATION-001
Role: Single-go execution agent. Read this entire prompt before taking any action.
Mode: MWP IMPLEMENTATION — Build the 13 Specification Authority Layer tools and run pilot lifecycles.

---

## Section 1 — Role and Sprint Identity

This sprint IMPLEMENTS the Specification Authority Layer as designed in the healing sprint
(FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001).

You have a complete design package:
- 11 subsystems defined with full specifications
- 13 lifecycle states (source_candidate through refresh_event)
- 47 regression test cases across 9 categories
- 3 full pilot formats (ZST, Netpbm, DIF) with source registrations and requirement extractions
- 2 extended prep formats (Gnumeric, FODS/FODT) with fetch-plans
- Deterministic context pack contract (SHA-256-based manifest.sha256)
- Usage ledger schema (append-only JSONL)
- Four-stream enforcement model

You do NOT re-design. You implement this sprint as specified.

---

## Section 2 — Hard Prohibitions

- Do NOT edit src/net/**, src/python/**, tests/net/**, tests/python/**
- Do NOT edit product-capability-matrix/poc-targets.yaml
- Do NOT edit registry/format-registry.yaml
- Do NOT git commit, git push, git reset --hard, git clean, git stash
- Do NOT approve Gate 8 or Gate 11
- Do NOT mark commercial_product_ready=true
- Do NOT publish to any package registry
- Do NOT call external LLM APIs or store secrets

---

## Section 3 — Allowed Write Paths

```
Write to:
  tools/specification-authority-layer/**
  tests/specification-authority-layer/**
  .local/spec-source-registry/**
  .local/spec-vault/**
  .local/spec-artifacts/**
  .local/spec-usage-ledger/**
  reports/specification-authority-layer-mwp/**
  .local/evidences/specification-authority-layer-mwp/**
  .local/supervisor/reviews/specification-authority-layer-mwp/**
```

---

## Section 4 — What You Are Building

### 11 Subsystems (implement as 13 tools)

1. **SpecSourceRegistry** — `tools/specification-authority-layer/spec_source_registry.py`
   Manage registry of approved spec sources. Register ZST (RFC 8878), Netpbm, DIF, Gnumeric, FODS/FODT.

2. **SpecVault** — `tools/specification-authority-layer/spec_vault_ingest.py`
   SHA-256 content addressing. Immutable write-once snapshots. Ingest ZST, Netpbm, DIF.

3. **SpecParser** — `tools/specification-authority-layer/spec_parser.py`
   Format-specific parser → structured JSON. Parse RFC (ZST), man_page (Netpbm), project_docs (DIF).

4. **SpecNormalizer** — `tools/specification-authority-layer/spec_normalizer.py`
   Cross-format normalization. Canonical schema: requirement_candidates, data_types, error_codes.

5. **SpecIndexer** — `tools/specification-authority-layer/spec_indexer.py`
   Versioned index with staleness tracking. Re-index on normalized_artifact update.

6. **SpecDigestor** — `tools/specification-authority-layer/spec_digestor.py`
   Compressed digest for LLM context window management. Three modes: full, section_summaries, capsule.
   Preserves all MUST requirements. Produces digest artifacts linked to manifest.sha256.

7. **RequirementExtractor** — `tools/specification-authority-layer/requirement_extractor.py`
   Extracts candidate requirements from normalized artifacts. Each requirement: req_id, text,
   type (MUST/SHOULD/MAY), source_snapshot_id, section_ref, extractor_version.

8. **SpecVerifier** — `tools/specification-authority-layer/spec_verifier.py`
   Verifies candidate requirements. Produces provenance_hash. State gate H→I.

9. **RequirementGraph** — `tools/specification-authority-layer/requirement_graph.py`
   Cross-format dependency DAG. Only verified_requirements as nodes.

10. **ContextPackBuilder** — `tools/specification-authority-layer/context_pack_builder.py`
    Deterministic context pack. Contract: same inputs → same manifest.sha256.
    Excludes timestamps from semantic hash. Produces usage ledger entries.

11. **SpecGovernanceRuntime** — `tools/specification-authority-layer/spec_governance_runtime.py`
    Stream enforcement. Anti-bypass rules. stale check. ai_draft detection. Four-stream gates.

12. **coverage validator** — `tools/specification-authority-layer/coverage_validator.py`
    Evaluates requirement coverage for completed tasks. Writes coverage records to usage ledger.

13. **staleness_checker** — `tools/specification-authority-layer/staleness_checker.py`
    Checks and propagates staleness. Triggers refresh events. Reports stale artifacts.

---

## Section 5 — 13 Lifecycle States (A through M)

The 13-state lifecycle governs all spec artifacts:

```
A. source_candidate    → B. registered_source  (SpecSourceRegistry approval)
B. registered_source   → C. raw_snapshot        (SpecVault ingestion)
C. raw_snapshot        → D. parsed_artifact     (SpecParser)
D. parsed_artifact     → E. normalized_artifact (SpecNormalizer)
E. normalized_artifact → F. indexed_artifact    (SpecIndexer)    [parallel]
E. normalized_artifact → G. digest_artifact     (SpecDigestor)   [parallel]
E. normalized_artifact → H. candidate_requirement (RequirementExtractor) [parallel]
H. candidate_requirement → I. verified_requirement (SpecVerifier gate)
I. verified_requirement → J. context_pack       (ContextPackBuilder)
J. context_pack        → K. usage_record        (usage ledger write)
J. context_pack        → L. coverage_record     (coverage validator)
C. raw_snapshot        → M. refresh_event       (SpecGovernanceRuntime on sha256 change)
```

---

## Section 6 — Deterministic Context Pack Contract

**Contract:** same source_sha256_set + same request_type + same index_version → same manifest.sha256

The SHA-256 is computed over:
```python
canonical = "|".join(sorted(source_sha256_list)) + "|" + request_type + "|" + str(index_version)
manifest_sha256 = sha256(canonical.encode() + b"|" + pack_contents_bytes).hexdigest()
```

Timestamps excluded from the semantic hash. manifest.sha256 is the pack's stable identity.

---

## Section 7 — Usage Ledger (append-only)

**Path:** `.local/spec-usage-ledger/usage-YYYYMMDD.jsonl`

Every ContextPack consumption writes one JSONL record with:
- context_pack_id, manifest_sha256, consumer_stream, requirement_ids, source_sha256s
- correction_of pattern for corrections (no in-place updates)
- coverage records (type=coverage) for coverage_validator results

---

## Section 8 — stale / refresh Model

When source sha256 changes:
- All downstream artifacts (D through J) marked stale=true
- refresh_event (M) created
- New raw_snapshot (C) ingested
- Full pipeline re-run from C
- SpecGovernanceRuntime blocks context pack build from stale artifacts

---

## Section 9 — Four-Stream Enforcement

**Mainstream:** context_pack_id + manifest_sha256 + requirement_ids + source_snapshot_ids required.
**Acceleration:** context_pack_id + requirement_ids + ai_draft label on all AI output required.
**Skills:** context_pack_id + requirement_ids + usage_id from usage ledger required.
**Supervisor:** validates context_pack_id, stale check, ai_draft misuse, unsupported claims.

Anti-bypass rules:
- Ad-hoc URL citations rejected until source registered in SpecSourceRegistry
- Memory-only spec claims rejected (no source_ref = UNSOURCED_CLAIM)
- Raw AI summaries without source_refs must carry ai_draft label
- Unverified requirements cannot be in production context packs
- Context pack without manifest.sha256 rejected

---

## Section 10 — Pilot Execution

### Minimum pilots (run full lifecycle — all 13 deliverables):

**ZST (Zstandard):**
- Source: RFC 8878 — PUBLIC_SPEC — license confirmed
- Register src-zst-001 → ingest → parse → normalize → index → extract → verify → context pack
- Extract at least 5 candidate requirements; verify at least 3
- Build deterministic context pack cp-zst-impl-001

**Netpbm:**
- Source: Netpbm project docs — OPEN_SOURCE — license confirmed
- Register src-netpbm-001 → ingest → parse → normalize → extract → verify → context pack
- Note: SVG must not replace Netpbm

**DIF (Data Interchange Format):**
- Source: VisiCalc DIF spec (archival) — PUBLIC_SPEC — license confirmed
- Register src-dif-001 → ingest → parse → normalize → extract → verify → context pack
- If license unclear: quarantine raw snapshot; document fetch-blocker

### Extended prep (source registration + fetch-plan only):

**Gnumeric:**
- Source: Gnumeric project docs — OPEN_SOURCE
- Register src-gnumeric-001; create fetch-plan document

**FODS/FODT:**
- Source: OASIS ODF 1.3 — PUBLIC_SPEC
- Register src-odf-001; create fetch-plan document

---

## Section 11 — Regression Control Suite (run all 47 tests)

Run tests in tests/specification-authority-layer/ across all 9 categories:

| Category | Test Count | Key Tests |
|----------|-----------|-----------|
| A — Schema validation | 5 | Artifact schema conformance |
| B — Provenance | 5 | Source trace chain |
| C — Parser round-trip | 5 | parse → serialize → parse |
| D — Context pack determinism | 5 | Same inputs → same manifest.sha256 |
| E — Requirement verifier negatives | 5 | Unverified req rejected from pack |
| F — coverage validator | 5 | Coverage ratio computed correctly |
| G — Four-stream integration | 5 | Handoff gate enforcement |
| H — Refresh/staleness | 5 | Stale propagation chain |
| I — Anti-bypass | 7 | URL citation, memory claim, ai_draft |
| **Total** | **47** | |

---

## Section 12 — Validation Checks (LOCAL ONLY)

Explicit exclusions: No GitHub Actions, no CI pipeline, no remote push required.

- V01: Declared-vs-materialized (file-ownership-map.json source of truth)
- V02: All Markdown files have H1 headings
- V03: All JSON files parse without error
- V04: All YAML files parse without error
- V05: No duplicate keys in file-ownership-map.json
- V06: All taskcards in terminal state (CLOSED_VERIFIED or CLOSED_SKIPPED_WITH_REASON)
- V07: Final execution prompt contains all 24 required keywords
- V08: No forbidden paths changed (git diff HEAD -- src/net src/python tests/net tests/python)
- V09: autonomous-cycle was run; exit code captured
- V10: Review package ZIP exists
- V11: SHA-256 recorded in review-package-proof.md
- V12: final-git-status.txt captured
- V-BAN: Banned-string scan (no machine-specific paths, no pre-filled verdicts)

---

## Section 13 — Evidence Closeout

Create:
- `.local/evidences/specification-authority-layer-mwp/evidence-declaration.yaml`
- `.local/evidences/specification-authority-layer-mwp/evidence-manifest.yaml`
- `reports/specification-authority-layer-mwp/review-package-proof.md`

Run:
```bash
$PYTHON tools/supervisor/autonomous_cycle.py \
  --declaration .local/evidences/specification-authority-layer-mwp/evidence-declaration.yaml
```

Then:
```bash
$PYTHON tools/supervisor/build_declaration_review_package.py \
  --declaration .local/evidences/specification-authority-layer-mwp/evidence-declaration.yaml
```

Compute SHA-256:
```bash
$PYTHON -c "
import hashlib, os, zipfile
path = os.environ['ZIP_PATH']
data = open(path,'rb').read()
sha = hashlib.sha256(data).hexdigest()
size = len(data)
count = len(zipfile.ZipFile(path).namelist())
print(sha, size, count)
" ZIP_PATH="$ZIP_PATH"
```

---

## Section 14 — Final Response Contract

Use exactly one macro verdict:
```
SPECIFICATION_AUTHORITY_LAYER_MWP_IMPLEMENTATION_COMPLETE
SPECIFICATION_AUTHORITY_LAYER_MWP_IMPLEMENTATION_PARTIAL
SPECIFICATION_AUTHORITY_LAYER_MWP_IMPLEMENTATION_BLOCKED
```

Selection:
- All 13 tools implemented + 47 tests pass + 3 pilots complete → COMPLETE
- Architecture complete but known limitations (license unconfirmed, test subset) → PARTIAL
- Required tools missing or tests failing → BLOCKED

Required response fields:
1. Exact macro verdict
2. Tools implemented (all 13 or list of completed)
3. Test results (47 tests, pass/fail counts)
4. Pilot results (ZST, Netpbm, DIF context pack IDs and manifest.sha256 hashes)
5. Review package absolute path (REPO_ROOT-derived)
6. Review package SHA-256
7. autonomous-cycle exit code
8. All output files PRESENT/MISSING
9. Explicit: "No product source files modified. No commit. No push."

---

## Required Keywords (24)

EXECUTION MODE | SpecSourceRegistry | SpecVault | SpecParser | SpecNormalizer | SpecIndexer
SpecDigestor | RequirementExtractor | SpecVerifier | RequirementGraph | ContextPackBuilder
SpecGovernanceRuntime | deterministic context pack | usage ledger | stale | refresh
coverage validator | ZST | Netpbm | DIF | Gnumeric | FODS/FODT | ai_draft | SHA-256
