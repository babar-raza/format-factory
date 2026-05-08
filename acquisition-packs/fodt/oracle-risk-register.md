---
artifact_id: fodt-oracle-risk-register
artifact_type: acquisition-pack
path: acquisition-packs/fodt/oracle-risk-register.md
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
notes: "FODT Gate 6 oracle risk register. Created run046 (2026-05-08)."
---

# FODT Gate 6 — Oracle Risk Register

**Format:** FODT
**Gate:** 6
**Created:** run046 (2026-05-08)

---

## Risk Register

| ID | Risk | Likelihood | Severity | Mitigation |
|---|---|---|---|---|
| OR-F-001 | LibreOffice FODT export fails (format not supported) | Low | High | LibreOffice supports FODT natively (ODF text). Verified by FODS oracle harness. |
| OR-F-002 | Plain-text export loses too much structure for comparison | Medium | Medium | Comparison limited to text content only. Structural checks (outline_level, list_style) deferred to parser-only validation. |
| OR-F-003 | Word count mismatch exceeds tolerance | Low | Low | ±20% tolerance acceptable; FODT samples are small (<100 words). |
| OR-F-004 | LibreOffice version changes break oracle | Low | Low | Version pinned to 26.2.3.2. New install required if version changes. |
| OR-F-005 | Oracle harness does not support FODT format flag | Medium | Medium | FODS harness uses `--infilter`. FODT requires separate scripts in tools/oracle/. TC-0042 creates fodt-specific oracle scripts. |

---

## Risk Mitigations Applied from FODS Experience

- FODS oracle run identified need for `soffice.com` (not `soffice.exe`). FODT will use same.
- FODS oracle had CSV multi-sheet WARN. FODT text export does not have this limitation.
- FODS comparison script needed parser CLI fix. FODT comparison will use same fixed pattern.
