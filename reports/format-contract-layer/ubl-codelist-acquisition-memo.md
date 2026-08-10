# UBL Code-List Data Acquisition: Research Memo

**Status:** Negative result for a bulk fix. A few narrow, unverified opportunities remain open.
**Affects:** SAL-UBL-OBL-788B2748204338B8 (UBL-VALIDATE-001) — bundled official code-list data covers 11 of 273 discoverable code-bearing element types; 262 remain uncovered.
**Prepared:** 2026-08-10, via a dedicated research pass (multi-agent workflow, primary-source fetches where accessible).

## Bottom line

No source, or combination of sources checked, provides a clean, primary-sourced, clearly-licensed path to closing anything close to the 262-type gap. The two most-cited "obvious" paths (OASIS's own supplementary code-list package; the OASIS TC's own harvesting repo) are both confirmed dead ends by direct inspection, not assumption.

## What was checked, and what was found

**1. OASIS UBL TC's own "more complete" code-list package does not exist.** Fetched `docs.oasis-open.org/ubl/os-UBL-2.3/cl/gc/default/` directly: contains exactly the same ~11 code-list types already bundled in `src/python/ubl/src/format_factory/ubl/model/codelists/*.gc` — a 1:1 match, confirmed by diff. This IS the currently-bundled set, not a superset.

**2. The OASIS TC's own supplementary harvesting repo (`github.com/oasis-tcs/ubl-codelists`) is explicitly dead.** Its own README states: *"the source content for most of these code lists no longer is useable for the creation of genericode files... development of this repository has ceased until alternative sources of machine-readable code list content can be found."* It reports HTTP 403 errors from data custodians when it tried to scrape them automatically — the identical wall hit independently on unece.org, iso.org, and loc.gov in this session. Its `raw/` directory contains one unprocessed HTML scrape; its `genericode/` directory contains only schema files, no generated code lists. OASIS's own TC hit the same obstacle this research did.

**3. Primary sources for ISO 3166/4217/639 and UN/CEFACT (unece.org) are systematically inaccessible to automated fetch** — every direct URL tried returned HTTP 403. Their actual redistribution terms could not be quoted from the source. What could be verified were third-party characterizations:
- ISO 4217's Maintenance Agency (SIX Group) offers free downloads but its own Terms and Conditions page did not yield explicit redistribution/bundling language — **free-to-download is confirmed; free-to-vendor-into-an-open-source-repo is not.**
- Two third-party UN/CEFACT redistributions declare PDDL (public domain) licensing for their data: `github.com/CIFConsulting/unece-recommendation-20` (Rec 20, units of measure — already bundled, zero new coverage) and `github.com/datasets/un-locode` (UN/LOCODE — genuinely new, 1 type, PDDL-licensed per its own `datapackage.json`).
- A third project, `github.com/edi3/edi3-codelists` (covers Rec 20/21/24), has a **genuine, unreconciled license ambiguity**: its repository-level `LICENSE.txt` is GPL-3.0, but its individual spec pages separately assert PDDL for the underlying data. The project is in "Working Draft" status with no visible releases — stale, unverified.

**4. GS1's own site is not a relevant primary source.** GS1's own documentation states it does not maintain these code lists itself, pointing back to UN/CEFACT/ISO. Its one directly-relevant asset (GPC) is licensed via a member-scoped RAND/royalty-free grant, not general open redistribution.

## What remains open, narrowly

- **UN/LOCODE, ~1 type** — via `github.com/datasets/un-locode`, which declares ODC-PDDL-1.0 and cites UNECE as its source. Not yet vendored: this is a third party's own characterization of UNECE's license, not a direct quote of UNECE's own terms (UNECE's own site returned 403 to every fetch attempt this session).
- **Rec 21/24, up to ~2 types** — via `edi3/edi3-codelists`, but blocked on the unreconciled GPL-3.0-repo-vs-PDDL-data ambiguity described above, and the project's own staleness.

Neither of these is ready to integrate without further primary-source verification, which requires either successfully reaching UNECE's own site (currently bot-blocking automated fetches) or a manual/human verification pass. **This is disclosed as a genuinely open item, not vendored on the strength of a third party's own license claim.**

## Recommended next steps (not attempted this session, require judgment or further access)

1. Treat the 262-type gap as confirmed-unfillable from official/open real-world sources for now.
2. If example coverage matters enough to prioritize, the viable path is likely a **human-driven** direct contact with UNECE (their bot-blocking prevented this session from getting primary terms at all) or manual verification of the `datasets/un-locode` / `edi3-codelists` license claims against UNECE's own published text (retrievable via non-automated means).
3. Do not vendor the UN/LOCODE or Rec 21/24 third-party data on the strength of this research alone — the license characterizations are secondhand.
