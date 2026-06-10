# TCA-010: Human Review Workflow — Downgrade Auto-Verified Facts
Sprint: SPEC-AUTHORITY-LAYER-STOP-THE-BLEEDING-001
Run: stop-the-bleeding-20260607-e382e5f
Date: 2026-06-07

## RESULT: PASS

## Actions taken

1. Original `verified-facts.yaml` renamed to `verified-facts-auto-seed.yaml` (preserved as backup)
2. New `verified-facts-review.yaml` created with all 10 facts processed:
   - 9 facts downgraded: `verification_status: needs_review`, `validated_by: independent_agent_verifier_required`
   - 1 fact verified: FACT-FODS-001 confirmed by reading normalized spec text

## FACT-FODS-001 Verification (by independent_agent_verifier)

**Claim:** FODS root element is `<office:document>` with `office:mimetype` attribute

**Evidence from spec text** (`.local/spec-cache/fods/1.3/normalized/text.txt`):

- Line 7218: `3.1.2 <office:document>(Single OpenDocument XML Files)`
- Line 7219-7220: `The <office:document> element is the root element of a document in OpenDocument format which is represented as a single XML document.`
- Line 7228: `The <office:document> element has the following attributes: grddl:transformation 19.320, office:mimetype 19.379 and office:version 19.390.`

**Verdict:** CONFIRMED. The `<office:document>` element is explicitly stated as the root element for single XML document format (which FODS is), and `office:mimetype` is listed as one of its attributes.

- `verification_status: verified`
- `validated_by: independent_agent_verifier`
- `validated_at: 2026-06-07`
- `spec_page_confirmed: true`

## FACT-FODS-002 Review Note

**Claim:** FODS mimetype is `application/vnd.oasis.opendocument.spreadsheet-flat-xml`

**Status:** `needs_review` — The string `spreadsheet-flat-xml` was NOT found in normalized text.txt. The spec Part 3 (Schema) covers element/attribute definitions. The flat-XML MIME type may be registered in a different document (IANA or another ODF spec part). This fact requires a targeted search in a broader spec corpus before confirming.

## Validation

```
python -c "... assert len(bad)==0 ... assert len(good)>=1 ..."
```
Result: Facts without validated_by but verified: 0
        Facts verified by independent_agent_verifier: 1
        PASS

## Root cause addressed

GAP-006: 10 auto-verified facts existed with no validated_by field.
After this taskcard: 0 facts have `verified` status without `validated_by`.
