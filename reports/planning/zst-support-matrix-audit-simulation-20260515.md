# ZST Support-Matrix Audit Simulation
Sprint: FORMAT-FACTORY-R13A-R12-CLOSURE-AND-ZST-GATE1-PACKET-SWARM-001
Lane: F (ZST Support-Matrix Audit Simulation)
Date: 2026-05-15

## SIMULATION ONLY — No Internet Access — No Real Audit Conducted

This report simulates the audit workflow that WOULD be followed in a real support-matrix audit
for the ZST (Zstandard, .zst) format. All outputs are simulated. No internet access was
performed. No actual Aspose API or documentation was queried. aspose_supported is NOT claimed.

---

## A. Audit Questions

The following questions must be answered in a real support-matrix audit:

### Q1: Does Aspose support .zst natively?
Expected search target: Aspose.Zip for .NET, Aspose.ZIP cloud API, Aspose product pages.
Current status: NOT_AUDITED. aspose_supported = None.

### Q2: If Aspose supports ZST, what is the feature surface?
Expected: decompress-only? compress+decompress? streaming? archive traversal?
Current status: NOT_AUDITED.

### Q3: Does Aspose support ZST in Python via Aspose.Zip Python?
Expected: Check Aspose.Zip for Python via .NET.
Current status: NOT_AUDITED.

### Q4: Is ZST support licensed under Aspose commercial terms?
Expected: Verify if ZST support requires paid license or is in trial/free tier.
Current status: NOT_AUDITED.

### Q5: Is RFC 8878 (Zstandard Compressed Data Format) public and royalty-free?
Expected: IETF RFC — royalty-free by IETF policy; Zstandard licensed BSD+Patent.
Simulated answer (from known public information): LIKELY YES — IETF RFCs are published as
public standards; Zstandard (Facebook/Meta) is BSD-2-Clause + Patent Grant.
WARNING: This is a simulation. Formal confirmation requires spec retrieval in an authorized sprint.

### Q6: Is there a ZST Python reference library?
Expected: python-zstandard (zstd), zstandard package on PyPI.
Simulated answer: YES (known from R11/R12 research). python-zstandard by Gregory Szorc,
BSD license. Formal confirmation requires an authorized retrieval sprint.

### Q7: Are open-license ZST sample files available?
Expected: Compressed files created from public-domain content (e.g. text corpora).
Simulated answer: LIKELY YES — ZST is a compression format; any file can be wrapped.
Formal confirmation requires sample corpus work in an authorized sprint.

---

## B. Expected Evidence Sources (for a real audit)

| Source | What to Check | Authorization Required |
|--------|-------------|----------------------|
| aspose.com/products/zip | ZST feature in Aspose.ZIP | Internet access sprint |
| RFC 8878 (tools.ietf.org) | Spec text, royalty status | Internet access sprint (R14) |
| PyPI: zstandard | Python binding, license | Internet access sprint |
| GitHub: facebook/zstd | Reference implementation, license | Internet access sprint |
| Aspose licensing page | Commercial terms for ZST | Internet access sprint |
| Sample corpus sites | Open-license .zst files | Sample acquisition sprint |

---

## C. Decision States

| Outcome | Condition | Effect on ZST path |
|---------|-----------|-------------------|
| aspose_supported: true | Aspose.ZIP supports ZST fully | DEC-033 route: commercial = Aspose-backed; OSS = independent impl |
| aspose_supported: false | No Aspose support found | Full independent implementation required |
| aspose_supported: partial | Decompress-only or streaming limitation | Hybrid approach; define feature gap |
| aspose_supported: unknown | Audit not yet performed | CURRENT STATE — blocks Gate 2 |

**Current state: aspose_supported = None (not audited)**

---

## D. Blocker Rules

1. BLOCKER_B1: Do not claim Aspose support status without evidence from an authorized audit.
2. BLOCKER_B2: Do not retrieve RFC 8878 or any Aspose page until internet access is authorized.
3. BLOCKER_B3: Do not begin ZST implementation (any tier) until Gate 1 is approved and Gate 2 evidence is complete.
4. BLOCKER_B4: Do not generate ZST requirements until spec is retrieved, cached, and normalized.
5. BLOCKER_B5: Do not claim legal classification beyond LIKELY_SAFE until formal legal review (Gate 2).

All 5 blockers are ACTIVE for this sprint. None are resolved by simulation.

---

## E. Safe Outputs from This Simulation

The following outputs are SAFE to record without real audit:

| Output | Basis | Source |
|--------|-------|--------|
| ZST candidate score: 8.95 | Computed by acquisition_planning_runtime.py from local data | R11/R12 planning runtime |
| ZST acquisition band: ACCEPT | Score > 8.0 threshold | R11 planning bundle |
| RFC 8878 likely public | IETF policy is public-domain for RFCs | Prior general knowledge |
| Zstandard license likely BSD+patent | Known from R10/R11 research | Not formally verified in this sprint |
| unsupported_by_aspose: needs_audit | No audit performed; honest classification | registry/format-registry.yaml |

**CRITICAL CONSTRAINT:** `unsupported_by_aspose: true` MUST NOT be set until a real audit
confirms Aspose does not support ZST. Current status: `needs_audit`.

---

## F. Stop Conditions

Stop the audit immediately if any of the following occur:
- Aspose documentation claims a patent or license restriction on ZST
- RFC 8878 contains any non-royalty-free terms (unlikely but must be checked)
- ZST implementation requires access to proprietary code without a public spec
- Any source for ZST samples is found to have non-open-source or restrictive licensing

---

## G. Mapping to Gate 1 and Gate 2

### Gate 1 (Candidate Accepted — scoring and legal classification)
The support-matrix audit contributes to Gate 1 decision:
- If aspose_supported: true → DEC-033 path applies; acquisition may be Aspose-backed
- If aspose_supported: false → full independent implementation track
- Legal classification requires: RFC royalty-free confirmation + Zstandard BSD+patent review
- Gate 1 approval: human only (Babar Raza)

### Gate 2 (Evidence Complete — spec and legal)
The support-matrix audit feeds into Gate 2:
- spec_evidence: requires RFC 8878 retrieval and legal review
- legal_notes: requires license compatibility analysis (BSD + patent grant analysis)
- sample_sources: open-license ZST samples needed

Neither Gate 1 nor Gate 2 can be approved without the real audit.

---

## H. Effect of DEC-033 on ZST

DEC-033 resolved Option B: .NET track is commercial-only (no .NET FOSS packaging).
Python remains the FOSS track.

For ZST specifically:
- If aspose_supported: true → .NET product COULD use Aspose.ZIP for ZST; Python OSS would
  use python-zstandard (independent implementation)
- If aspose_supported: false → .NET product requires independent ZST implementation in .NET;
  Python OSS requires python-zstandard
- DEC-033 does NOT affect whether ZST acquisition can begin — that is governed by Gate 1
- DEC-033 does NOT affect Python FOSS path — python-zstandard would be used regardless
- DEC-033 means: .NET FOSS packaging of ZST is deferred until DEC-033 is revisited

**DEC-033 is NOT a blocker for ZST Gate 1 or spec retrieval.** It affects the .NET product
track design, not the acquisition pipeline entry decision.

---

## Audit Simulation Verdict

SIMULATION_COMPLETE: YES
REAL_AUDIT_PERFORMED: NO
aspose_supported: None (not audited)
unsupported_by_aspose: needs_audit (NOT changed)
BLOCKERS_ACTIVE: 5/5
SAFE_OUTPUTS_PRODUCED: YES
NEXT_REAL_AUDIT_SPRINT: R13B (if Babar Raza approves ZST Gate 1)
