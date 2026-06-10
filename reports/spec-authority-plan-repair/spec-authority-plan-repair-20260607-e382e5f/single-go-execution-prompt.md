# Single-Go Execution Prompt
# FORMAT-FACTORY-SPEC-AUTHORITY-LAYER-STOP-THE-BLEEDING-001
# Produced by: FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-REPAIR-FOR-SINGLE-GO-EXECUTION-001
# Run: spec-authority-plan-repair-20260607-e382e5f
# Validator: PASS (exit 0, 832 checks, 0 failures)
# Adversarial: 0 CRITICAL issues
# Date: 2026-06-07

---

## Sprint Identity

Sprint ID: `SPEC-AUTHORITY-LAYER-STOP-THE-BLEEDING-001`

This sprint is Phase 1 of the specification authority layer healing. It stops the bleeding
by enforcing the spec authority gate in the evidence schema, creating the spec source registry,
quarantining synthetic fixtures, and documenting the bypass pilot for formats without specs.

This is NOT a product implementation sprint. No changes to `src/`.

---

## Preflight (Mandatory — compute dynamically, never hardcode)

```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
HEAD_SHA=$(git rev-parse HEAD)
SHORT_SHA=$(git rev-parse --short HEAD)
BRANCH=$(git branch --show-current)
TODAY=$(date +%Y%m%d)
RUN_ID="stop-the-bleeding-${TODAY}-${SHORT_SHA}"

echo "REPO_ROOT=$REPO_ROOT"
echo "RUN_ID=$RUN_ID"

mkdir -p "${REPO_ROOT}/reports/spec-authority-stop-the-bleeding/${RUN_ID}/raw-logs"
mkdir -p "${REPO_ROOT}/.local/spec-authority-stop-the-bleeding/${RUN_ID}"
```

---

## Context from Plan-Repair Sprint

Investigation evidence is at: `${REPO_ROOT}/reports/spec-authority/spec-authority-investigation-001/`
Plan-repair artifacts: `${REPO_ROOT}/reports/spec-authority-plan-repair/spec-authority-plan-repair-20260607-e382e5f/`

Key live repo facts (confirmed at HEAD e382e5f, verify at execution time):
- FODS PDF: `${REPO_ROOT}/.local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf` (exists)
- Normalized text: `${REPO_ROOT}/.local/spec-cache/fods/1.3/normalized/text.txt` (exists, 2.2MB)
- FODS SHA-256: read from `.local/spec-cache/fods/1.3/spec-index.yaml` at runtime — do NOT hardcode
- Synthetic requirements: `.local/spec-artifacts/FODS-SPEC-001-requirements.json` (synthetic, 6 entries)
- Spec source registry: `.local/spec-source-registry/` (exists but empty)

---

## Taskcards to Execute (This Sprint)

### TCA-002: spec_fact_refs BLOCKING Enforcement — Schema Design and Stub Implementation

**Lane:** L-SCHEMA
**Root cause:** GAP-004
**Prerequisite:** none

**Scope:** Produce the formal JSON schema fragment for spec_fact_refs. Write it to
`schemas/evidence-declaration-spec-fact-refs.schema.json`. Add a stub validation check in
`docs/automation/supervisor-worker-contract.md` that marks spec_fact_refs as BLOCKING for
PRODUCT_SOURCE/TEST/REQUIREMENT/READINESS/RELEASE_GATE work items.

**Exception classifications (must be explicitly set, no silent bypass):**
- `investigation_only` — pure investigation/audit work
- `sample_only_non_product` — sample files with no production code
- `legacy_backfill` — pre-existing code being documented retroactively
- `fallback_authority_approved` — explicitly approved fallback by governance
- `no_public_spec_available` — no publicly accessible spec document exists

**Success criteria:**
- `schemas/evidence-declaration-spec-fact-refs.schema.json` exists and JSON-valid
- Schema contains `spec_fact_refs` field definition
- `docs/automation/supervisor-worker-contract.md` updated with BLOCKING enforcement note

**Evidence required:**
- `${REPO_ROOT}/reports/spec-authority-stop-the-bleeding/${RUN_ID}/tca002-schema-design.md`
- `${REPO_ROOT}/schemas/evidence-declaration-spec-fact-refs.schema.json`

**Validation:**
```bash
python -m json.tool "${REPO_ROOT}/schemas/evidence-declaration-spec-fact-refs.schema.json"
grep -q "spec_fact_refs" "${REPO_ROOT}/docs/automation/supervisor-worker-contract.md" && echo PASS || echo FAIL
```

**Negative test:**
- A PRODUCT_SOURCE declaration with empty spec_fact_refs and no exception_classification must fail validation

---

### TCA-003: Spec Source Registry — Initialize sources.jsonl

**Lane:** L-SCHEMA
**Root cause:** GAP-003
**Prerequisite:** none

**Scope:** Initialize `.local/spec-source-registry/sources.jsonl` with entries for each format
that has a spec entry in `.local/spec-cache/`. Write one JSONL line per format per spec version.
Read existing spec-index.yaml files to populate — do NOT hardcode values.

**Success criteria:**
- `.local/spec-source-registry/sources.jsonl` exists and is valid JSONL
- Contains at least one entry for FODS (format_id: fods, version: 1.3)
- Each entry has: format_id, spec_id, version, source_sha256, cached_at, local_path

**Evidence required:**
- `${REPO_ROOT}/.local/spec-source-registry/sources.jsonl`
- `${REPO_ROOT}/reports/spec-authority-stop-the-bleeding/${RUN_ID}/tca003-registry-init.txt`

**Validation:**
```bash
python -c "import json; [json.loads(l) for l in open('.local/spec-source-registry/sources.jsonl') if l.strip()]; print('PASS')"
grep -q "fods" "${REPO_ROOT}/.local/spec-source-registry/sources.jsonl" && echo FODS_PRESENT || echo FAIL
```

---

### TCA-009: Quarantine Synthetic Fixture Data

**Lane:** L-SCHEMA
**Root cause:** GAP-002
**Prerequisite:** none

**Scope:** Rename `.local/spec-artifacts/FODS-SPEC-001-requirements.json` to
`.local/spec-artifacts/FODS-SPEC-001-requirements-synthetic-DO-NOT-USE.json`. Create a
marker file `.local/spec-artifacts/FODS-SPEC-001-requirements-QUARANTINE.md` explaining the
quarantine. Do NOT delete synthetic files — rename them so they cannot be accidentally used.

**Success criteria:**
- `FODS-SPEC-001-requirements-synthetic-DO-NOT-USE.json` exists
- `FODS-SPEC-001-requirements.json` no longer exists (renamed, not deleted)
- Quarantine marker file explains why it's quarantined

**Evidence required:**
- `${REPO_ROOT}/reports/spec-authority-stop-the-bleeding/${RUN_ID}/tca009-quarantine.txt`

**Validation:**
```bash
test ! -f "${REPO_ROOT}/.local/spec-artifacts/FODS-SPEC-001-requirements.json" && echo QUARANTINED || echo NOT_QUARANTINED
test -f "${REPO_ROOT}/.local/spec-artifacts/FODS-SPEC-001-requirements-synthetic-DO-NOT-USE.json" && echo RENAMED_OK || echo FAIL
```

---

### TCA-012: Bypass Pilot — Gnumeric/ABW Metadata-Only Exception Classification

**Lane:** L-SCHEMA
**Root cause:** BYP-005, BYP-006
**Prerequisite:** TCA-002

**Scope:** Create bypass ledger entry documents for Gnumeric and ABW in
`reports/spec-authority-stop-the-bleeding/${RUN_ID}/bypass-ledger/`. Each document declares
`exception_classification: no_public_spec_available` and explains the bypass rationale.

**NON-GOALS (explicit):**
- new_product_implementation
- new_test_files
- src_changes
- modifying gnumeric_codec.py or abw_codec.py

**Success criteria:**
- `bypass-ledger/gnumeric-bypass.yaml` exists with exception_classification=no_public_spec_available
- `bypass-ledger/abw-bypass.yaml` exists with exception_classification=no_public_spec_available
- Neither file creates or references any src/ changes

**Evidence required:**
- `${REPO_ROOT}/reports/spec-authority-stop-the-bleeding/${RUN_ID}/bypass-ledger/gnumeric-bypass.yaml`
- `${REPO_ROOT}/reports/spec-authority-stop-the-bleeding/${RUN_ID}/bypass-ledger/abw-bypass.yaml`

**Validation:**
```bash
grep -q "no_public_spec_available" "${REPO_ROOT}/reports/spec-authority-stop-the-bleeding/${RUN_ID}/bypass-ledger/gnumeric-bypass.yaml" && echo PASS || echo FAIL
grep -q "no_public_spec_available" "${REPO_ROOT}/reports/spec-authority-stop-the-bleeding/${RUN_ID}/bypass-ledger/abw-bypass.yaml" && echo PASS || echo FAIL
```

---

### TCA-010: Human Review Workflow — Downgrade Auto-Verified Facts

**Lane:** L-SCHEMA
**Root cause:** GAP-006
**Prerequisite:** none

**Scope:** The current `${REPO_ROOT}/.local/spec-cache/fods/1.3/workbench/verified-facts.yaml`
has 10 facts set to `verification_status: verified` by `build_spec_workbench.py` with NO
`validated_by` field. These must be downgraded to `verification_status: needs_review`.

Create a copy at `${REPO_ROOT}/.local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml`
with all facts downgraded to `needs_review` and `validated_by: independent_agent_verifier_required`.
Keep the original `verified-facts.yaml` as backup (rename to `verified-facts-auto-seed.yaml`).

The `independent_agent_verifier` role reads the actual spec text in
`.local/spec-cache/fods/1.3/normalized/text.txt` and confirms each claim against the real spec.
For each fact confirmed:
- Set `verification_status: verified`
- Set `validated_by: independent_agent_verifier`
- Set `validated_at: <today ISO date>`
- Add `spec_page_confirmed: true` if the page_start in provenance contains the claim

**Success criteria:**
- `verified-facts-review.yaml` exists
- Original `verified-facts.yaml` renamed to `verified-facts-auto-seed.yaml`
- At least 1 fact has `verification_status: verified` and `validated_by: independent_agent_verifier`
- NO fact has `verified` status without a `validated_by` field

**Evidence required:**
- `${REPO_ROOT}/.local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml`
- `${REPO_ROOT}/reports/spec-authority-stop-the-bleeding/${RUN_ID}/tca010-fact-review.md`

**Validation:**
```bash
python -c "
import yaml
facts = yaml.safe_load(open('.local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml'))
bad = [f for f in facts.get('facts',[]) if f.get('provenance',{}).get('verification_status')=='verified' and not f.get('provenance',{}).get('validated_by')]
print(f'Facts without validated_by but verified: {len(bad)}')
assert len(bad)==0, 'FAIL'
print('PASS')
"
```

---

## Required Negative Tests

Run these checks — they must produce the stated results to confirm the problems are fixed:

```bash
# 1. spec_fact_refs empty for PRODUCT_SOURCE item must block (not warn)
# Create a minimal test declaration and verify validation blocks it:
python -c "
from tools.supervisor.authority_integration_fabric import AuthorityIntegrationFabric
# Or read supervisor-worker-contract.md to find enforcement point
print('Checking spec_fact_refs enforcement exists in validation pipeline')
"

# 2. No synthetic requirements in active use:
test ! -f "${REPO_ROOT}/.local/spec-artifacts/FODS-SPEC-001-requirements.json" && echo "QUARANTINE_CONFIRMED" || echo "FAIL: synthetic still present"

# 3. No facts verified without validated_by:
python -c "
import yaml
facts = yaml.safe_load(open('${REPO_ROOT}/.local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml'))
bad = [f['claim_id'] for f in facts['facts'] if f.get('provenance',{}).get('verification_status')=='verified' and not f.get('provenance',{}).get('validated_by')]
assert not bad, f'FAIL: {bad}'
print('PASS: all verified facts have validated_by')
"
```

---

## spec_fact_refs Enforcement (Standing Constraint — BLOCKING)

spec_fact_refs is a MANDATORY HARD GATE for all new product work in this sprint and all future sprints.

Any work item of type PRODUCT_SOURCE, TEST, REQUIREMENT, READINESS, or RELEASE_GATE that does not
have `spec_fact_refs` populated must provide an explicit `exception_classification` from:
- `investigation_only`
- `sample_only_non_product`
- `legacy_backfill`
- `fallback_authority_approved`
- `no_public_spec_available`

No silent bypass. No default exception. If the work touches product code, it needs spec authority.

---

## validated_by Rules

- `validated_by: independent_agent_verifier` — for spec facts verified by reading the spec
- `validated_by: human` — NEVER used as a default; only when a human actually reviewed
- Do NOT write `validated_by: Babar Raza` unless Babar actually reviewed the specific item

---

## Stop Gates

STOP and report SPEC_AUTHORITY_STOP_BLEEDING_BLOCKED if:
- spec-index.yaml missing for FODS (prevents registry initialization)
- normalized text.txt missing for FODS (prevents fact verification)
- schemas/ directory not writable

STOP and report SPEC_AUTHORITY_STOP_BLEEDING_PARTIAL if:
- TCA-002 completes but TCA-010 fact verification returns 0 confirmed facts
- TCA-003 registry initialized but FODS entry cannot be confirmed

---

## Evidence Declaration

At sprint end, write evidence declaration at:
`${REPO_ROOT}/.local/evidences/stop-the-bleeding-${TODAY}-${SHORT_SHA}/evidence-declaration.yaml`

Required fields (all mandatory):
- run_id: stop-the-bleeding-${TODAY}-${SHORT_SHA}
- sprint_id: SPEC-AUTHORITY-LAYER-STOP-THE-BLEEDING-001
- For each work item:
  - spec_fact_refs: [FACT-xxx, ...] OR exception_classification: <type>
  - No empty spec_fact_refs without exception_classification

---

## Forbidden Paths

- NO src/ changes of any kind
- NO tests/ new files
- NO commits, pushes, gate approvals
- NO overwriting `.local/spec-cache/` — it contains the real spec PDF
- NO setting verification_status: verified via automated tool alone
- NO importing or activating AI/embeddings

---

## Final Verdict Options

- `STOP_BLEEDING_COMPLETE_SPEC_AUTHORITY_GATE_ACTIVE` — all 4 taskcards complete; spec_fact_refs BLOCKING; facts downgraded; registry initialized; synthetic quarantined
- `STOP_BLEEDING_PARTIAL_SCHEMA_ONLY` — TCA-002 complete (schema); TCA-003/009/010 incomplete; document root cause
- `STOP_BLEEDING_BLOCKED_MISSING_NORMALIZED_TEXT` — normalized text.txt absent; FODS fact verification impossible
- `STOP_BLEEDING_BLOCKED_SPEC_PDF_MISSING` — FODS PDF absent; stop; do not proceed with fact verification

---

## Note on BYP-007..010

The bypass inventory from the investigation sprint (BYP-007, BYP-008, BYP-009, BYP-010) are not
individually covered by taskcards in this sprint. They require additional taskcards to be created
in a follow-up sprint. Document them in the evidence declaration as `investigation_only` items and
create a gap report for the next sprint.
