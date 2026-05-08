---
artifact_id: TC-0031-fodt-gate2-dec034-independent-verification
artifact_type: taskcard
path: taskcards/TC-0031-fodt-gate2-dec034-independent-verification.md
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
notes: "FODT Gate 2 DEC-034 independent verification taskcard. Created run042 (2026-05-08) after TC-0030 evidence execution. Execution blocked until explicit verification prompt is issued in a separate session. Must PASS before Gate 2 human review."
---

# TC-0031: FODT Gate 2 — DEC-034 Independent Verification

**Taskcard ID:** TC-0031
**Phase:** 3 (parallel execution alongside FODS Gate 6)
**Gate:** 2 (Spec/Legal Evidence — independent verification)
**Status:** not_started — awaiting explicit verification prompt in a separate session
**Created:** 2026-05-08 (run042)
**Created by:** claude-sonnet-4-6 (run042)
**Prerequisite:** TC-0030 evidence execution COMPLETE (run042) ✓
**DEC-034 rule:** Must run in a separate execution session from TC-0030

---

## IMPORTANT — Execution Gate

**This taskcard may NOT be executed in the same session as TC-0030.**

DEC-034 (AGENTS.md Section V) requires independent verification to run in a separate
execution session, without access to the producing session's in-context memory.

The execution prompt must state:
- "Execute TC-0031 FODT Gate 2 DEC-034 independent verification"
- Authorized format: FODT
- Prerequisite: TC-0030 COMPLETE (run042)

---

## Objective

Independently verify that run042 FODT Gate 2 evidence is correct, complete, and consistent
with the spec cache, registry, and governance rules. The verifier must NOT rely on the
run042 session's in-context memory.

---

## Verification Checklist (Minimum 20 checks)

### Spec Evidence (spec-evidence.md)
- [ ] Status is `SUPPORTED_BY_CACHED_SOURCE`
- [ ] SHA-256 hash matches `.local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf`
- [ ] Spec verification count shows 3 verifications
- [ ] FODT MIME type is correct (`application/vnd.oasis.opendocument.text-flat-xml`)
- [ ] FODT-specific sections (§2, §3, §5, §14, §15, §17, §18, §19) referenced

### Legal Notes (legal-notes.md)
- [ ] Status is `FAST_PATH_DECLARED`
- [ ] 8/8 fast-path items present and confirmed
- [ ] Patent search waiver documented with correct basis (FODS Gate 2, Babar Raza, 2026-05-05)
- [ ] Legal category confirmed as 1 (OASIS RF on Limited Terms)
- [ ] Next steps section present

### Pack YAML (pack.yaml)
- [ ] gate_2.status is `evidence_cached_pending_independent_verification`
- [ ] gate_2.fast_path: true
- [ ] gate_2.fast_path_items_met: 8
- [ ] gate_2.patent_search_waived: true
- [ ] gate_2.evidence_executed_run: run042

### Registry (format-registry.yaml)
- [ ] FODT gate_2.status is `evidence_cached_pending_independent_verification`
- [ ] FODT gate_2.evidence_executed_run: run042
- [ ] FODT gate_1 remains passed (not changed)

### Scope Boundary
- [ ] No FODT samples created
- [ ] No FODT parser or prototype created
- [ ] No FODT neutral model or schema created
- [ ] No product source created

---

## Expected Outcome

After this verification PASS:
1. Update `pack.yaml` gate_2.status → `evidence_cached_pending_human_review`
2. Update registry gate_2.status → `evidence_cached_pending_human_review`
3. Update TC-0030 status → `verification_passed_pending_human_review`
4. Prepare Gate 2 approval packet (already at `acquisition-packs/fodt/gate2-human-review-packet.md`)
5. Request Gate 2 human review from Babar Raza via explicit execution prompt

---

## WIP Limit Check

- FODS: Gate 6 blocked (1/2 Gates 4-6 slots)
- FODT: Gate 2 (1/3 Gates 1-3 slots)
- Total: 2 active format pipelines — within WIP limits

---

## Related Files

| File | Purpose |
|---|---|
| `acquisition-packs/fodt/spec-evidence.md` | Spec evidence (SUPPORTED_BY_CACHED_SOURCE — run042) |
| `acquisition-packs/fodt/legal-notes.md` | Legal notes (FAST_PATH_DECLARED — run042) |
| `acquisition-packs/fodt/pack.yaml` | Acquisition pack (gate_2 updated run042) |
| `acquisition-packs/fodt/gate2-human-review-packet.md` | Gate 2 review packet (created run042) |
| `registry/format-registry.yaml` | FODT entry (gate_2 updated run042) |
| `taskcards/TC-0030-fodt-gate2-spec-legal-evidence.md` | TC-0030 (evidence execution — DONE run042) |
