# Source Acquisition Report — SAL Real Pilot R1
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Lane: B

---

## Source Registration Summary

4 sources registered in pilot-local registry: `.local/evidences/spec-authority-real-pilot-r1/spec-source-registry/sources.jsonl`

| Source ID | Format | Title | Source Type | Authority Status | Fetch Policy |
|---|---|---|---|---|---|
| src-zst-rfc8878 | zst | Zstandard RFC 8878 (Summary Fixture) | rfc | ACCEPTED_SPEC (with fetch caveat) | deferred_local_fixture |
| src-netpbm-docs | netpbm | Netpbm Format Family Documentation | public_domain_spec | ACCEPTED_WITH_CAVEAT | deferred_local_fixture |
| src-dif-softarts | dif | DIF Specification (Software Arts 1981) | empirical_observation | EMPIRICAL_ONLY | deferred_local_fixture |
| src-fods-oasis | fods | FODS/FODT OASIS ODF 1.3 (Summary) | odf_standard | ACCEPTED_WITH_CAVEAT (partial scope) | deferred_local_fixture |

---

## Vault Ingest Results

All 4 sources ingested as text fixtures (network fetch deferred — local pilot).

| Source ID | SHA-256 | Vault Status | Integrity |
|---|---|---|---|
| src-zst-rfc8878 | `c15ec66abc6489c0feb63cdf43246bca6a98cfdae6d9823d893c25ea3f809819` | INGESTED_FROM_FIXTURE | INTEGRITY_OK |
| src-netpbm-docs | `cec3030092754c3687e44b1707fbf832594e569fb9e39388eac13c6379570299` | INGESTED_FROM_FIXTURE | INTEGRITY_OK |
| src-dif-softarts | `3065d192e05345a524ca08db4285bf17fcde1c2415eed80c5f2630089c541d26` | INGESTED_FROM_FIXTURE | INTEGRITY_OK |
| src-fods-oasis | `24e5975f6e7e2890ee1c8da5bdff757c6899244035cd951dd65371b622042c8d` | INGESTED_FROM_FIXTURE | INTEGRITY_OK |

---

## Provenance Notes by Source

### ZST — Zstandard (src-zst-rfc8878)
- **Real source:** IETF RFC 8878 — "Zstandard Compression and the 'application/zstd' Media Type"
- **URL:** https://www.rfc-editor.org/rfc/rfc8878
- **Fetch status:** DEFERRED — network not used; text fixture captures key normative statements
- **License:** IETF open access
- **Authority rating:** RFC is official standards body — would be ACCEPTED_SPEC after real fetch
- **Caveat:** Current pilot uses summary fixture, not the full RFC text; fetch should be done in Pilot R2

### Netpbm — Netpbm Format Family (src-netpbm-docs)
- **Real source:** Netpbm project documentation at netpbm.sourceforge.net
- **URL:** http://netpbm.sourceforge.net/doc/
- **Fetch status:** DEFERRED — text fixture captures PBM/PGM/PPM normative statements
- **License:** Public domain (original; project itself uses GPL)
- **Authority rating:** De facto standard; no formal ISO/IETF standard → ACCEPTED_WITH_CAVEAT
- **Caveat:** No single authoritative RFC; multiple sub-format pages; fixture represents merged summary

### DIF — Data Interchange Format (src-dif-softarts)
- **Real source:** Historical Software Arts specification (1981); Wikipedia and archive references
- **URL:** https://en.wikipedia.org/wiki/Data_Interchange_Format
- **Fetch status:** DEFERRED — historical document not widely available in machine-readable form
- **License:** Public domain (original document)
- **Authority rating:** No current standards body → EMPIRICAL_ONLY
- **Caveat:** Cannot overclaim official authority; provenance is historical only; requirements are advisory

### FODS/FODT — ODF (src-fods-oasis)
- **Real source:** OASIS ODF 1.3 specification
- **URL:** https://docs.oasis-open.org/office/OpenDocument/v1.3/
- **Fetch status:** DEFERRED — full ODF 1.3 is 1000+ pages; only structural summary extracted
- **License:** OASIS open standard
- **Authority rating:** Formal OASIS standard → ACCEPTED_WITH_CAVEAT (scoped only)
- **Caveat:** Only FODS/FODT structural requirements extracted; not full ODF compliance; stretch pilot

---

## Anti-Duplication Check

No source re-downloaded — all fixtures created fresh using `ingest_text_fixture()`.
For future fetch: checking `verify_snapshot_integrity()` before re-ingest is the correct protocol.

---

## Citation Anti-Bypass Verification

- Citation of `src-zst-rfc8878` (registered): **ALLOWED** ✓
- Citation of `src-fake-unknown` (unregistered): **REJECTED** ✓

Anti-bypass rules working correctly.
