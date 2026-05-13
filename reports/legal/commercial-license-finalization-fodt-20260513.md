# Commercial License Finalization Packet — FODT

**Format:** FODT (Flat OpenDocument Text)
**Date:** 2026-05-13
**Sprint:** GATE11-APPROVAL-AND-RELEASE-READINESS-SWARM-001 (Lane B)
**Status:** NOT_FINALIZED

---

## 1. Current Licensing State

### Python FOSS Track
- Package: `format-factory-fodt`
- License: **Apache-2.0** (confirmed at Gate 10, approved 2026-05-11)
- Source: `src/python/fodt/` (7 modules, 115/115 tests PASS, 15/15 IR-FODT)
- Status: COMPLETED (TC-0052)
- No commercial license dependency

### .NET Commercial Track
- Package: `FormatFactory.Fodt` (NuGet)
- License: **NOT FINALIZED** — placeholder "Proprietary Commercial License" stated but no actual license text selected
- Source: `src/net/fodt/` (skeleton created 2026-05-12)
- Target: net10.0
- Status: commercial_readiness_in_progress

### Underlying Specification
- Spec: OASIS ODF 1.3 Part 3
- Legal category: 1 — Open Standard (Royalty-Free)
- Patent risk: None (OASIS RF on Limited Terms)
- Implementation permission: Granted without royalty or license fee
- No restriction on commercial use of parser implementations
- Same legal basis as FODS (both are ODF 1.3 sub-formats)

---

## 2. DEC-033 Option B Implications

DEC-033 was resolved as **Option B: .NET Commercial Only** by Babar Raza on 2026-05-12.

Implications for FODT licensing:

| Implication | Detail |
|-------------|--------|
| No .NET FOSS package | The .NET track does NOT produce an Apache-2.0 NuGet package |
| No dual-licensing complexity | Single license per track (Apache-2.0 for Python, proprietary for .NET) |
| Commercial license required | The .NET NuGet package requires a proprietary commercial license before release |
| Python track unaffected | `format-factory-fodt` remains Apache-2.0 regardless of .NET license choice |
| No contamination risk from FOSS | Since .NET is commercial-only, there is no FOSS/commercial separation concern within the .NET codebase |
| License should align with FODS | Both FODS and FODT are ODF 1.3 sub-formats under the same spec body; the commercial license should be consistent across both .NET packages |

---

## 3. What "Commercial License Finalization" Means for FODT

Commercial license finalization is one of the two required flags for Gate 11 approval. The approval recording from 2026-05-13 shows:

```
COMMERCIAL_LICENSE_FINALIZED_FOR_FODT: YES_OR_NO   (placeholder — NOT "YES")
APPROVE_FODT_GATE11:                   YES_OR_NO   (placeholder — NOT "YES")
```

"Finalization" means the project lead has:
1. Selected the exact commercial license type (e.g., per-seat, per-server, perpetual, subscription, EULA)
2. Confirmed the license text or confirmed that license text drafting is delegated to legal counsel
3. Confirmed that the chosen license is compatible with the OASIS ODF 1.3 RF terms (which impose no restrictions on commercial implementation)
4. Authorized that the license header can be applied to all .NET source files in `src/net/fodt/`

Until all four items are confirmed, the `COMMERCIAL_LICENSE_FINALIZED_FOR_FODT` flag remains at `YES_OR_NO` (not finalized).

---

## 4. Status: NOT_FINALIZED

### Evidence That the License Is Not Finalized

| Evidence Source | Finding |
|----------------|---------|
| `acquisition-packs/fodt/gate11-commercial-licensing.md` | STATUS: pending_legal_finalization |
| `reports/gate-review/fodt/gate11-approval-recording-20260513.md` | COMMERCIAL_LICENSE_FINALIZED_FOR_FODT = YES_OR_NO (placeholder) |
| `reports/gate-review/fodt/gate11-commercial-readiness-20260512.md` | Commercial license: PENDING (implied) |
| `registry/format-registry.yaml` (fodt gate_11) | approved_by: null; approved_date: null |
| `docs/product-tracks.md` | .NET commercial product: "Proprietary (decided at Gate 11)" |
| `docs/legal-and-licensing.md` Output License Policy | .NET commercial product: "Proprietary (decided at Gate 11)" |

No license text, license type, or license terms have been selected. The word "Proprietary" appears as a category placeholder, not as a finalized license.

---

## 5. Remaining Actions for Finalization

The following actions must be completed by the project lead (Babar Raza) to finalize the FODT commercial license:

### Action 1: Select Commercial License Type
- **Owner:** Babar Raza (project lead)
- **Options to evaluate:**
  - Standard commercial EULA (per-seat or per-organization)
  - Per-server / per-deployment license
  - Subscription-based license
  - Dual commercial license (perpetual + subscription)
  - Custom proprietary license
- **Recommendation:** Use the same license type selected for FODS to maintain consistency across the ODF flat family
- **Deliverable:** Written statement of chosen license type

### Action 2: Draft or Confirm License Text
- **Owner:** Babar Raza, with optional legal counsel
- **Deliverable:** License text file (e.g., `LICENSE-COMMERCIAL.md` or `LICENSE-COMMERCIAL.txt`) to be placed in the .NET package
- **Note:** This report does NOT draft license terms. License terms require human legal judgment.
- **Recommendation:** A single shared commercial license template for the entire FormatFactory .NET product line would reduce maintenance burden

### Action 3: Confirm ODF 1.3 Compatibility
- **Owner:** Babar Raza
- **Requirement:** Confirm in writing that the chosen commercial license does not conflict with OASIS ODF 1.3 RF on Limited Terms patent policy
- **Expected outcome:** No conflict (OASIS RF imposes no restrictions on commercial implementation)
- **Note:** If FODS compatibility was already confirmed, the same confirmation applies to FODT (same spec, same IPR policy)

### Action 4: Approve License Header for Source Files
- **Owner:** Babar Raza
- **Requirement:** Approve the exact license header text to be placed at the top of every .NET source file in `src/net/fodt/`
- **Deliverable:** Header template text
- **Recommendation:** Use the same header template as FODS

### Action 5: Set Gate 11 Approval Flags to YES
- **Owner:** Babar Raza
- **Requirement:** In a Gate 11 approval execution prompt, set:
  - `APPROVE_FODT_GATE11: YES`
  - `COMMERCIAL_LICENSE_FINALIZED_FOR_FODT: YES`
- **Prerequisite:** Actions 1-4 completed; DEC-034 independent verification passed (already PASSED per 2026-05-13 recording)

---

## 6. Technical Prerequisites Already Met

The following technical prerequisites for Gate 11 are already satisfied:

| Prerequisite | Status | Evidence |
|--------------|--------|----------|
| DEC-033 resolved | PASS | Option B, Babar Raza, 2026-05-12 |
| DEC-034 independent verification | PASS | DEC034-GATE11-TIER0-COMMERCIAL-IV-SWARM-001 |
| .NET skeleton created | PASS | src/net/fodt/ (net10.0) |
| .NET Tier 0 parser implemented | PASS | 13/13 tests PASS |
| .NET 10 SDK installed | PASS | 10.0.204 |
| Security posture | PASS | DtdProcessing.Prohibit, XmlResolver=null, 50 MB guard |
| Python FOSS track | COMPLETED | format-factory-fodt (Apache-2.0) |
| Gates 1-10 | ALL PASSED | Babar Raza, 2026-05-07 through 2026-05-11 |

The ONLY remaining blocker is the commercial license finalization (Actions 1-5 above).

---

## 7. FODT-Specific Implementation Notes

The FODT .NET commercial product includes implementation details that may be relevant to license scope:

- Iterative DFS list traversal algorithm (see `src/python/fodt/list_traversal.py` for reference)
- Iterparse streaming parser
- ODF 1.3 text document model: paragraphs, headings, lists, tables
- 7 neutral model entities: Document, Block, List, ListItem, Table, TableRow, TableCell

These are parser implementation details derived from the open OASIS ODF 1.3 specification. They do not introduce any additional licensing constraints.

---

## 8. Cross-References

| File | Relevance |
|------|-----------|
| `acquisition-packs/fodt/gate11-commercial-licensing.md` | Current licensing stub (pending_legal_finalization) |
| `acquisition-packs/fodt/gate11-packaging-plan.md` | NuGet packaging plan |
| `reports/gate-review/fodt/gate11-approval-recording-20260513.md` | Deferred approval recording (YES_OR_NO flags) |
| `reports/gate-review/fodt/gate11-commercial-readiness-20260512.md` | Readiness checklist |
| `reports/legal/commercial-license-finalization-fods-20260513.md` | Companion FODS packet (same license decision recommended) |
| `docs/legal-and-licensing.md` | Project legal policy |
| `docs/product-tracks.md` | Track definitions and license assignments |
| `registry/format-registry.yaml` | Gate status (gate_11: commercial_readiness_in_progress) |

---

LANE_B_VERDICT: LICENSE_NOT_FINALIZED
GATE11_BLOCKED_BY: COMMERCIAL_LICENSE_DECISION_PENDING_HUMAN_ACTION
