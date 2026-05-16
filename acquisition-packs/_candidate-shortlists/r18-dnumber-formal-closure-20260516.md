# R18 Gate 9: dnumber/.numbers Formal Closure
Sprint: FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001
Date: 2026-05-16

## Formal Closure Record

Candidate identifier: dnumber (also listed as .numbers in sprint prompt variants)
Formal status: AUTOMATIC_REJECT — Category 5 (Proprietary Binary, No Public Spec)

## Identity Resolution (established in R17)

The "dnumber" candidate was researched independently in R17 via WebSearch.

| Search evidence | Result |
|-----------------|--------|
| ".dnumber file format extension" search | Returns only Apple Numbers (.numbers) results |
| File format databases (fileformats.com, fileinfo.com, PRONOM) | No ".dnumber" extension listed |
| IANA media type registry | No ".dnumber" media type |
| Sprint prompt pairing | "dnumber / .numbers" indicates same candidate |
| GNOME LOC Digital Formats | No ".dnumber" entry |

**Resolved identity: Apple Numbers (.numbers) — high confidence**

Evidence chain:
1. No file format databases contain ".dnumber" as a format identifier
2. Sprint prompt explicitly pairs "dnumber / .numbers"
3. All web searches for "dnumber" resolve to Apple Numbers context
4. "dnumber" is likely shorthand: "d(ocument)-number(s)" or acquisition catalog code

## Legal Category Assessment

| Property | Value |
|----------|-------|
| Format owner | Apple Inc. |
| Structure | ZIP container + IWA (iWork Archive) files using Protocol Buffers |
| Public specification | NONE — Apple has never published an official spec |
| Implementation method | Reverse engineering only |
| Legal category | 5 — Reverse-engineered binary; no public spec; no permission |

Per AGENTS.md and _scoring-model.md:
> "Legal Category 5 (reverse-engineered binary): automatic reject regardless of other scores."
> "Score 0 on the legal safety dimension: automatic reject."

Apple has explicitly not published the .numbers format specification. The only available
documentation is from reverse-engineering (e.g., librevenge, numbers-parser community projects).
Implementing .numbers requires reverse-engineering IWA/Protocol Buffers structure without
explicit permission from Apple Inc.

## Formal Rejection Record

| Field | Value |
|-------|-------|
| Candidate ID | dnumber / .numbers |
| Resolved identity | Apple Numbers (.numbers) |
| Rejection basis | Legal Category 5 (automatic reject) |
| Rejection date | 2026-05-16 |
| Rejecting sprint | FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001 |
| Gate 1 status | REJECTED |
| Human review required | NO — automatic reject; no human approval needed for rejection |
| Re-evaluation possible | YES — if Apple publishes official spec and grants implementation rights |

## Condition for Re-Evaluation

If the following conditions are met, the candidate may be reconsidered:
1. Apple Inc. publishes an official .numbers format specification with explicit implementation rights
2. No patent restrictions on implementation
3. Format is reclassified as Category 1-3

As of 2026-05-16, none of these conditions are met.

## If "dnumber" is NOT Apple Numbers

If the human confirms that "dnumber" refers to a different format (not Apple Numbers),
this closure record is superseded. The human must provide:
1. The correct format identity (full name, extension, MIME type)
2. The correct spec body and location
3. Authorization to re-open evaluation

## Reference

R17 identity research: acquisition-packs/_candidate-shortlists/r17-gate1-candidate-packets-20260516.md
R17 scoring intake: reports/planning/r17-multi-format-gate1-intake-and-scoring-20260516.md

DNUMBER_CLOSURE: FORMAL_REJECT_CATEGORY5
