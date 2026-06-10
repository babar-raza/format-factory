# Next Pilot Recommendation
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Generated: 2026-06-05

## Verdict

Pilot R1 is complete as a **fixture-based proof of concept**. The SAL pipeline is proven
end-to-end for ZST, Netpbm, and DIF. Pilot R2 should focus on real RFC text fetch and
FODS/FODT context pack completion.

## Pilot R2 Mission

Sprint ID (proposed): `FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R2-001`

**Primary goals:**
1. Fetch real RFC 8878 text from tools.ietf.org (plain text format)
2. Verify SHA-256 stability across fetches (idempotent content)
3. Prove staleness detection triggers when RFC content changes
4. Complete FODS/FODT context pack (stretch goal from R1)
5. Add ODF license confirmation (promote FODS to ACCEPTED_SPEC if confirmed)

**Technical prerequisites:**
- HTML→text stripping in vault ingest (D-PARSER-003)
- Auto-recomputation queue trigger (D-STALE-001)
- Network fetch guard (rate limit, timeout, retry)

**Test additions for R2:**
- test_real_rfc8878_fetch_produces_stable_sha256
- test_staleness_triggered_by_content_change_at_url
- test_html_stripping_preserves_section_structure
- test_fods_context_pack_deterministic
- test_fodt_context_pack_deterministic

## R2 Minimum Pass Criteria

- Real RFC 8878 fetch → SHA-256 computed → vault ingested
- Staleness detection tested with real content mutation
- FODS context pack built with determinism proof
- 45+ tests all passing (no regressions from R1)

## R2 Scope Boundary

- NO product source changes (same prohibition as R1)
- NO poc-targets.yaml mutation
- NO capability claims derived from DIF (EMPIRICAL_ONLY maintained)
- Network access only to tools.ietf.org (read-only fetch)

## Verdict

`NEXT_PILOT_RECOMMENDATION_COMPLETE — R2_SCOPE_DEFINED`
