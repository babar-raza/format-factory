# Draft licensing inquiry to OpenPeppol AISBL / CEN

**Status: DRAFT ONLY — not sent.** No authenticated email-sending tool is
available in this session (Gmail MCP requires an interactive OAuth flow this
non-interactive session cannot perform). This is a ready-to-send draft for
Babar Raza's own review, edits, and sending.

**Recommended send channel:** `info@peppol.eu` (OpenPeppol AISBL's published
general contact address, per peppol.org's own contact page) or the Service
Desk at `https://peppol.org/tools-support/service-desk/`, whichever the
sender judges more likely to reach someone able to answer a redistribution
-permission question rather than a technical support queue.

**Background / why this is being sent:** `ubl-sample-coverage-research-memo.md`
(2026-08-10) confirmed 36 of UBL's 91 root document types have no official
OASIS example instance in any UBL release, ever — a genuine specification
-level gap, not something this project can source from OASIS. Two real,
realistic, hand-authored instances were found via OpenPEPPOL's own public
GitHub repositories, but both carry a restrictive notice ("may not be
modified, re-distributed, sold or repackaged... without the prior consent of
CEN and/or OpenPeppol AISBL") that blocks vendoring without explicit
permission. Filing this inquiry was approved by Babar Raza on 2026-08-10 via
explicit structured approval.

---

## Draft letter

**To:** OpenPeppol AISBL (info@peppol.eu)
**Cc:** (sender to add a CEN contact if one is separately known — this draft
does not have one on file)
**Subject:** Redistribution permission request — 2 UBL example documents for
open-source test fixtures (Format Factory)

Dear OpenPeppol AISBL,

I am writing on behalf of Format Factory, an open-source document-format
interoperability project that includes a UBL (Universal Business Language)
reading and writing library. We are requesting permission to redistribute
two specific example documents that OpenPeppol has published publicly on
GitHub, for use solely as internal automated test fixtures.

**The two documents:**

1. An `ApplicationResponse` example instance, from the (now archived)
   `OpenPEPPOL/peppol-bis` repository.
2. `Catalogue` example instances, from the `OpenPEPPOL/pracc-catalogue`
   repository.

**Why we are asking:** OASIS's own UBL specification releases (2.1 through
the current 2.5 development draft) do not include example instance
documents for either of these root types, nor for 34 other related
document types in the same tendering/procurement and catalogue-management
families. OpenPEPPOL's own repositories are the only realistic, real-world
example documents we have located for these types anywhere. The companion
page at docs.peppol.eu carries a notice stating these Peppol BIS documents
"may not be modified, re-distributed, sold or repackaged in any other way
without the prior consent of CEN and/or OpenPeppol AISBL," which is why we
are asking directly rather than assuming permission.

**Intended use, precisely:**

- The documents would be vendored, byte-for-byte unmodified, into our
  project's own test-fixture directory, clearly labeled as OpenPEPPOL
  -sourced content with full attribution.
- They would be used exclusively as inputs to our own automated test suite
  (round-trip parse/validate/write checks), not repackaged, not
  redistributed as standalone documents, and not included in any marketing,
  training, or commercial-sample material.
- They would not be modified in any way, including to alter, remove, or
  obscure any Peppol branding, identifiers, or business content they
  contain.

We are glad to comply with any specific conditions you set — attribution
wording, a scope-limiting license text you provide, a requirement to remove
the files if asked, or a formal written agreement if that is your
organization's preferred process for this kind of request.

**What we are asking for:** written confirmation (an email reply is
sufficient on our side) that Format Factory may vendor these two specific
documents under the terms above. If a different office, contact, or process
is more appropriate for this request, we would be grateful to be redirected.

Thank you for your time and for OpenPEPPOL's own work publishing these
examples in the first place — they are a genuinely useful, realistic
reference that OASIS's own specification releases do not otherwise provide.

Sincerely,
Babar Raza
Format Factory project
(contact email to be filled in by sender)

---

## Notes for the sender before sending

- Fill in a reply-to contact email — the project's own `pyproject.toml`
  files list `formatfactory@aspose.com`; use whichever address you want
  replies routed to.
- Consider whether a CEN contact should be Cc'd directly; this draft does
  not have one on file (CEN is referenced only via OpenPEPPOL's own notice,
  not independently researched this session — out of scope for the research
  pass that produced the underlying memo).
- If OpenPeppol declines, is unreachable, or does not respond, the 36-type
  UBL-WRITE-001 sample gap remains open; see
  `ubl-sample-coverage-research-memo.md`'s own "Options going forward"
  section for the two other paths considered (treat as permanently
  unfillable from official sources, or generate project-owned synthetic
  instances against the already-vendored XSDs, clearly labeled as such).
- No obligation status changes on the strength of sending this letter alone
  — only a granted permission followed by actual vendoring would move
  UBL-WRITE-001 (SAL-UBL-OBL-F9D5251F2302AE3A).
