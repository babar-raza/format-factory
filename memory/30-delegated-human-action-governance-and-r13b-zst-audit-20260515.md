# Memory Note 30: Delegated Human-Action Governance and R13B ZST Gate 1 Audit
Sprint: FORMAT-FACTORY-R13B-DELEGATED-ZST-GATE1-REAL-SUPPORT-AUDIT-AND-GOVERNANCE-NORMALIZATION-SWARM-001
Date: 2026-05-15

## Governance Model Update

A new concept was added to the governance model:
**Delegated Decision Execution** (GOVERNANCE.md §2.1a, AGENTS.md §D1a, docs/gates.md rule 1a)

### Key Distinction

| Forbidden | Allowed |
|-----------|---------|
| Autonomous self-approval (agent acts without human consent) | Delegated execution (agent carries out explicit human decision) |
| Agent sets gate_1.status: passed without authorization | Agent records decision when human explicitly delegates via execution prompt |
| Bypasses evidence gates | All evidence gates still required |

### Delegated Execution Criteria (GOVERNANCE.md §2.1a)
1. Human explicitly authorized delegation in named execution prompt
2. Complete evidence gates exist in repo
3. No external authority, credential, payment, or legal signature required
4. Decision derivable from project goals and verified evidence
5. Decision transparently recorded in delegated-decision report
6. Registry approval_method identifies as delegated execution

## R13B Sprint State (2026-05-15)

**Sprint:** FORMAT-FACTORY-R13B-DELEGATED-ZST-GATE1-REAL-SUPPORT-AUDIT-AND-GOVERNANCE-NORMALIZATION-SWARM-001
**Status:** COMPLETE (pending bundle)

### Real Audit Results

| Audit | Result | Classification |
|-------|--------|---------------|
| Aspose ZST support | aspose_supported: TRUE | ZstandardArchive + TarArchive.SaveZstandard; full round-trip |
| Legal/spec readiness | public_spec_quality: full_public_verified | RFC 8878 IETF Informational; BSD+patent grant |
| Product strategy | PRODUCT_ALIGNMENT_PASS_WITH_LIMITATIONS | Archive handler; no document DOM |

### ZST Gate 1 Decision

- Decision: APPROVE_ZST_GATE1_REAL_SUPPORT_AUDIT_ONLY (Option 1)
- Approved by: Babar Raza (delegated execution)
- Date: 2026-05-15
- approval_method: delegated_agent_decision_under_babar_instruction

### Artifacts Created

- registry/format-registry.yaml: ZST entry added (gate_1: passed)
- acquisition-packs/zst/pack.yaml
- acquisition-packs/zst/support-matrix.md
- acquisition-packs/zst/legal-notes.md
- acquisition-packs/zst/product-strategy-notes.md
- taskcards/ZST-GATE1-DECISION-PACKET.md: updated to delegated_decision_executed
- taskcards/ZST-R14-SPEC-RETRIEVAL.md: created (pending R14 authorization)

### NOT authorized in R13B — R14 NOW AUTHORIZED (2026-05-15)

R14 (FORMAT-FACTORY-R14-ZST-SPEC-RETRIEVAL-AND-GATE2-SWARM-001) was issued by Babar Raza
on 2026-05-15. Gate 2 spec retrieval is now executing.

- RFC 8878 full retrieval (Gate 2) — AUTHORIZED by R14 execution prompt
- .local/spec-cache/zst/ — AUTHORIZED for creation in R14
- generated-requirements/zst/ — still NOT authorized (requires Gate 5+)
- src/python/zst/ or src/net/zst/ — still NOT authorized (requires Gate 4+)
- Gate 3+ — still requires separate authorization after Gate 2 completes

## Key Legal Facts (ZST)

- RFC 8878: IETF Informational (2021-02-01); royalty-free implementation rights
- Reference impl: BSD/GPLv2 dual (use BSD for commercial); patent grant with defensive termination clause
- python-zstandard: BSD-3-Clause
- legal_category: 2 (Permissive OSS)

## Next Sprint (ACTIVE)

R14: FORMAT-FACTORY-R14-ZST-SPEC-RETRIEVAL-AND-GATE2-SWARM-001
Status: IN PROGRESS (2026-05-15)
Authorization: Babar Raza via R14 execution prompt

## Governance Invariants (unchanged)

- commercial_product_ready: false
- FODS Gate 11: NOT APPROVED
- FODT Gate 11: NOT APPROVED
- ZST Gate 1: APPROVED (delegated 2026-05-15)
- ZST Gate 2+: NOT AUTHORIZED
