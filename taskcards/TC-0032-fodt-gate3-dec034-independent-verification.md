---
artifact_id: TC-0032-fodt-gate3-dec034-independent-verification
artifact_type: taskcard
path: taskcards/TC-0032-fodt-gate3-dec034-independent-verification.md
format_id: fodt
product_family: words
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODT Gate 3 DEC-034 independent verification taskcard. Created run043 (2026-05-08) after Gate 3 sample corpus created. Must run in separate session from run043 (DEC-034 rule). 20-check minimum verification."
---

# TC-0032: FODT Gate 3 — DEC-034 Independent Verification

**Taskcard ID:** TC-0032
**Phase:** 3 (Gate 3 sample corpus verification)
**Gate:** 3 (Sample Corpus — independent verification)
**Status:** COMPLETED — DEC-034 PASS 27/27 (run044, 2026-05-08)
**Created:** 2026-05-08 (run043)
**Created by:** claude-sonnet-4-6 (run043)
**Completed:** 2026-05-08 (run044)
**DEC-034:** Satisfied — run044 separate from run043 ✓

---

## IMPORTANT — Execution Gate

**This taskcard may NOT be executed in the same session as run043 (where Gate 3 samples were created).**

DEC-034 (AGENTS.md Section V) requires independent verification to run in a separate
execution session, without access to the producing session's in-context memory.

The execution prompt must state:
- "Execute TC-0032 FODT Gate 3 DEC-034 independent verification"
- Authorized format: FODT
- Prerequisite: Gate 3 sample corpus created (run043) ✓

---

## Objective

Independently verify that the run043 FODT Gate 3 sample corpus is correct, complete, and consistent
with the spec, registry, provenance record, and governance rules. The verifier must NOT rely on the
run043 session's in-context memory.

---

## Verification Checklist (Minimum 20 checks)

### Sample Files (XML Validation)
- [ ] `minimal-document.fodt` exists at `samples/by-format/fodt/`
- [ ] `headings-and-paragraphs.fodt` exists
- [ ] `list-basic.fodt` exists
- [ ] `table-basic.fodt` exists
- [ ] All 4 files are XML well-formed (no parse errors)
- [ ] All 4 files have root element `office:document` (correct namespace)
- [ ] All 4 files have MIME type `application/vnd.oasis.opendocument.text-flat-xml`
- [ ] All 4 files have `office:version="1.3"`
- [ ] All 4 files have `office:body` → `office:text` structure
- [ ] `python tools/samples/validate_fodt_samples.py` outputs FODT_SAMPLE_VALIDATION: PASS 4/4

### Provenance Record (_provenance.yaml)
- [ ] All 4 FODT samples have entries in `samples/_provenance.yaml`
- [ ] All entries have `provenance_status: confirmed`
- [ ] All entries have `license: Apache-2.0`
- [ ] All entries have `creator: format-factory project`
- [ ] SHA-256 hashes in _provenance.yaml match actual file hashes (verify at least 2)

### Registry (format-registry.yaml)
- [ ] FODT gate_3.status is `sample_corpus_created_pending_independent_verification`
- [ ] gate_3.sample_count: 4
- [ ] gate_3.validation_status shows "4/4 PASS"

### Scope Boundary
- [ ] No FODT parser prototype created (no prototypes/by-format/fodt/)
- [ ] No product source created (no src/python/fodt/ or src/net/fodt/)

---

## Expected Outcome

After this verification PASS:
1. Update registry gate_3.status → `sample_corpus_verified_pending_human_review`
2. Update TC-0032 status → COMPLETED
3. Create Gate 3 human review packet at `acquisition-packs/fodt/gate3-human-review-packet.md`
4. Request Gate 3 human review from Babar Raza via explicit execution prompt

---

## Related Files

| File | Purpose |
|---|---|
| `samples/by-format/fodt/` | 4 synthetic FODT samples (created run043) |
| `samples/_provenance.yaml` | Provenance record for all 4 FODT samples |
| `tools/samples/validate_fodt_samples.py` | Validation tool (created run043) |
| `registry/format-registry.yaml` | FODT gate_3 entry (created run043) |
| `taskcards/TC-0030-fodt-gate2-spec-legal-evidence.md` | TC-0030 (CLOSED — Gate 2 APPROVED run043) |
| `taskcards/TC-0031-fodt-gate2-dec034-independent-verification.md` | TC-0031 (COMPLETED — run043) |
