# SAL Pilot Rerun Plan
**Mission:** spec-auth-inv-20260625-001
**Date:** 2026-06-25

## Pilot A: CSV SAL Chain Repair (Highest ROI)
**Target format:** CSV (RFC 4180)
**Current state:** 2 facts (magic number + header)
**Target state:** 30+ facts covering all RFC 4180 ABNF productions
**Steps:**
1. Read RFC 4180 ABNF grammar sections 2.1-2.7
2. Extract fact per production: record, field, TEXTDATA, CRLF, DQUOTE, etc.
3. Write to `.local/spec-cache/sal-facts-csv.json`
4. Regenerate `sal-facts-latest.json`
5. Verify V47 PASS for new fact refs

**Expected output:** GAP-SAL-RC002-001 closed, CSV SAL chain: PARTIAL → CHAIN_INTACT

## Pilot B: V13 Hardening (Safety)
**Target:** governance_validators.py `validate_spec_fact_refs_wired()`
**Steps:**
1. Find the `except ImportError` block in V13
2. Change WARN return to FAIL with message: "SAL toolchain not installed — cannot verify spec_fact_refs"
3. Add test to `test_governance_validators.py`

**Expected output:** GAP-SAL-RC003-001 closed

## Pilot C: Gnumeric SAL Parser (Highest Gap Impact)
**Target format:** Gnumeric XML
**Steps:**
1. Locate GNOME Gnumeric XML format documentation
2. Extract element/attribute definitions (Sheet, Cell, Style, etc.)
3. Write parser or manual facts to `.local/spec-cache/sal-facts-gnumeric.json`
4. Regenerate merged facts

**Expected output:** GAP-SAL-RC001-001 closed, Gnumeric: CHAIN_BROKEN → PARTIAL

## Timeline
- Pilot A: Next sprint (CSV SAL — can be done without external toolchain)
- Pilot B: Next sprint (V13 hardening — 5 LOC)
- Pilot C: Sprint 2 (Gnumeric — requires spec document access)
