# Next SAL Healing Sprint Prompt
**Mission:** spec-auth-inv-20260625-001 — generated 2026-06-25

## Context

SAL investigation is COMPLETE. Critical gaps found:
- 7 formats have 0 SAL facts (RC-001: no parser)
- 6 formats have only 2 generic facts (RC-002: stub-only)
- V13 validator degrades silently on ImportError (RC-003)
- Capability compiler not grounded in spec facts (RC-006)

## Immediate Next Sprint: CSV SAL Chain Repair

Execute TC-FA-009 from eager-launching-phoenix plan:

1. **CSV SAL expansion:** Read RFC 4180 grammar, extract 30+ facts:
   - record := field *( "," field ) CRLF — FACT-CSV-001
   - field := (escaped / non-escaped) — FACT-CSV-002
   - escaped := DQUOTE *(TEXTDATA / COMMA / CR / LF / 2DQUOTE) DQUOTE — FACT-CSV-003
   - header := name *( "," name ) CRLF — FACT-CSV-004
   - [continue for all ABNF productions]

2. **V13 hardening:** In `validate_spec_fact_refs_wired()`, replace WARN-on-ImportError with FAIL + message.

3. **Verify:** `python tools/spec/workbench/refresh_check.py --all` + V47 no regressions.

## Evidence Required
- Updated `.local/spec-cache/sal-facts-csv.json` (30+ facts)
- V13 test passing (FAIL not WARN on ImportError)
- Chain status report showing CSV: PARTIAL → CHAIN_INTACT
