# UBL Official-Sample Coverage: Research Memo

**Status:** Negative result for official OASIS sources. Two real-world examples found, both under restrictive copyright — not usable without explicit permission.
**Affects:** SAL-UBL-OBL-F9D5251F2302AE3A (UBL-WRITE-001) — 36 of 91 root document types have no official OASIS example vendored (independently re-verified this session: exactly `ApplicationResponse, AttachedDocument, AwardedNotification, BillOfLading, CallForTenders, Catalogue, CatalogueDeletion, CatalogueItemSpecificationUpdate, CataloguePricingUpdate, CatalogueRequest, CertificateOfOrigin, ContractAwardNotice, ContractNotice, DocumentStatus, DocumentStatusRequest, Enquiry, EnquiryResponse, ExpressionOfInterestResponse, GuaranteeCertificate, ItemInformationRequest, PackingList, QualificationApplicationRequest, QualificationApplicationResponse, SelfBilledInvoice, Tender, TenderContract, TenderReceipt, TenderStatus, TenderStatusRequest, TenderWithdrawal, TendererQualification, TendererQualificationResponse, UnawardedNotification, UnsubscribeFromProcedureRequest, UnsubscribeFromProcedureResponse, UtilityStatement`).
**Prepared:** 2026-08-10, via a dedicated research pass.

## Bottom line

This is a genuine gap at the OASIS specification level, not an artifact of which release package this project happens to pin. Every OASIS UBL deliverable that could plausibly carry example instances was checked — 2.1, 2.2, 2.3, the newer 2.4 Committee Specification, the 2.5 development draft, the UBL-IFTM-Mapping deliverable, and the TC's own linked community resources — and **none of them contain an example instance for any of these 36 types, in any UBL version, ever.** OASIS itself has never published sample documents for the pre-award/tendering and catalogue-management document families that dominate this gap.

## What was checked

| Source | Result |
|---|---|
| OASIS UBL TC committee home page | No separate example index; only points to JSON re-encodings of the same set and a defunct community-site pointer |
| `ubl.xml.org` (community site) | Defunct/parked — fetched twice, empty both times |
| UBL 2.1 release package `xml/` | 55 examples enumerated, zero of the 36 gap types present (strict subset of 2.3) |
| UBL 2.2 release package `xml/` | 55 examples enumerated, zero of the 36 gap types present |
| UBL 2.3 release package `xml/` | Cross-checked: 55 root types, matches the repo's own manifest exactly |
| UBL 2.4 Committee Specification `xml/` | 89 examples — checked exhaustively against all 36 gap-type names, zero matches (not yet an OASIS Standard) |
| UBL 2.5 development draft `xml/` | 84 examples — zero matches |
| UBL-IFTM-Mapping deliverable | Mapping specification only, no instance documents |
| Full `docs.oasis-open.org/ubl/` deliverable index | Enumerated every TC deliverable; none suggests a dedicated tendering/procurement example package |
| TED eForms / EU eProcurement (OP-TED) | Uses a different vocabulary (eProcurement Ontology), not OASIS UBL schema — no usable instance |
| Norway EHF / anskaffelser.dev | No concrete downloadable instance located within research scope |
| EN 16931 conformant implementations | Only maps to Invoice/CreditNote (already covered) — not relevant to the gap |

## Real-world examples found, and why they aren't usable

**OpenPEPPOL** (a real UBL implementation community) does publish two directly relevant, realistic, hand-authored instance documents:
- `OpenPEPPOL/peppol-bis` (deprecated repo) — a genuine `ApplicationResponse` instance
- `OpenPEPPOL/pracc-catalogue` — genuine `Catalogue` instances with realistic business data

**Neither clears an open-license bar.** The companion `docs.peppol.eu` page carries an explicit restrictive notice: *"This Peppol BIS document may not be modified, re-distributed, sold or repackaged in any other way without the prior consent of CEN and/or OpenPeppol AISBL."* GitHub's own license metadata for `pracc-catalogue` is `null` (no LICENSE file → default all-rights-reserved). **Do not vendor either without explicit permission from OpenPeppol AISBL / CEN.**

## Options going forward (not attempted this session)

1. **Treat as confirmed-unfillable from official/open real-world sources for now.** This is a well-researched, high-confidence negative result, not an under-searched gap.
2. **Generate project-owned synthetic instances** against the already-vendored UBL 2.3 XSDs for the 36 types, clearly labeled as project-generated, not OASIS-authored — mirroring the existing synthetic-fixture pattern already used elsewhere in this repo's own corpus manifests. **Caveat:** UBL-WRITE-001's own rule_text specifically requires round-tripping *official* samples; synthetic fixtures would need a separate, honestly-scoped obligation or an explicit acknowledgment that they don't satisfy this specific clause. This would also be a substantial undertaking (36 distinct, non-trivial document schemas) — not attempted in this session; disclosed as a real option for a dedicated future effort, not a quick fix.
3. **File an explicit licensing inquiry to OpenPeppol AISBL** for redistribution permission on the two examples identified above — a business/legal decision, not something to assume.

No file was vendored or modified based on this research alone.
