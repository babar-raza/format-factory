# Downstream Contract Check — SAL Real Pilot R1
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Lane: G

---

## Purpose

Define what the Specification Authority layer outputs to the Requirement/Capability Authority layer.
Verify the contract contains no product capability claims.

---

## What Spec Authority Offers to Requirement/Capability Authority

### Outputs available:

| Output Type | ZST | Netpbm | DIF | FODS (stretch) |
|---|---|---|---|---|
| context_pack_id | CP-ZST-a1269259b41f | CP-NETPBM-d746e21cf23d | CP-DIF-fde58d1d14fc | (deferred) |
| manifest.sha256 | a1269259b41fd61c... | d746e21cf23d4ab7... | fde58d1d14fc2fc9... | — |
| candidate requirements | 17 | 13 | 8 | 8 (not packaged) |
| authority_status | ACCEPTED_SPEC (fixture caveat) | ACCEPTED_WITH_CAVEAT | EMPIRICAL_ONLY | ACCEPTED_WITH_CAVEAT |
| staleness status | FRESH | FRESH | FRESH | FRESH |
| provenance metadata | sha256 + source_type + caveat | same | same | same |
| usage ledger entries | YES | YES | YES | YES |

### Outputs NOT provided by Spec Authority:

- Product implementation status → NOT PROVIDED
- Capability proof → NOT PROVIDED
- Test pass/fail results → NOT PROVIDED
- POC readiness → NOT PROVIDED
- commercial_product_ready → NOT PROVIDED

---

## Contract Compliance Check

| Check | Result |
|---|---|
| Contract contains product capability PASS claim | **NO** |
| Contract contains context_pack_id | YES |
| Contract contains manifest.sha256 | YES |
| Contract contains provenance/source_type | YES |
| Contract contains staleness status | YES |
| Contract contains caveat/empirical flags | YES |
| DIF overclaimed as ACCEPTED_SPEC | **NO — correctly EMPIRICAL_ONLY** |
| Context pack informs but does not prove capability | **CONFIRMED** |

**Contract compliance: PASS — no capability claims.**

---

## Authority Boundary Statement

> The Specification Authority layer produces accepted/caveated/empirical spec requirements
> and deterministic context packs. These outputs *inform* the Requirement/Capability Authority
> about what the spec says — they do not *prove* that the product implements any capability.
>
> Downstream layers must independently verify product implementation via:
> - Product source code inspection
> - Unit/integration tests
> - Dogfood export verification
> - POC proof graphs

---

## Downstream Consumption Note

The Requirement/Capability Authority should:
1. Receive `context_pack_id` + `manifest.sha256` as input
2. Verify context pack via `verify_context_pack()` before use
3. Check staleness before deriving capability requirements
4. Check `authority_status` — reject EMPIRICAL_ONLY as sole basis for accepted spec claims
5. Track usage via the usage ledger

See `sample-requirement-authority-input-packet.json` for a concrete ZST sample.
