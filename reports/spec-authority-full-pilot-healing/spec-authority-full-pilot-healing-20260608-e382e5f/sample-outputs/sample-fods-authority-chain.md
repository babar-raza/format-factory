# FODS Authority Chain — TCA-FULL-010

## Chain Trace

```
spec source:  .local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf
source hash:  sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066
spec name:    ODF 1.3 Part 3 (OASIS RF, legal category 1)
normalized:   .local/spec-cache/fods/1.3/normalized/text.txt
verified fact file: .local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml
  FACT-FODS-001: verified, validated_by=independent_agent_verifier, spec_page_confirmed=True
  FACT-FODS-002 through FACT-FODS-010: needs_review
```

## Fact Verification Evidence

**FACT-FODS-001**: "FODS root element is `<office:document>` with `office:mimetype` attribute"
- Source: normalized/text.txt line 7218-7228
- Spec section: 3.1.2 — `<office:document>` (Single OpenDocument XML Files)
- Confirmation: "The `<office:document>` element is the root element..." + "office:mimetype 19.379"
- Confidence: HIGH
- validation_status: VERIFIED ✓

## Pilot Declaration Test

A declaration with `spec_fact_refs: ["FACT-FODS-001"]` on a PRODUCT_SOURCE item → ACCEPTED ✓
(See pilot-003-result.json — exit 0, compliant=true)

## Proof Level Classification

| Component | Present? |
|-----------|----------|
| Spec source cached | ✓ PDF at .local/spec-cache/fods/1.3/ |
| Source SHA256 verified | ✓ sha256:92cfe64... |
| Normalized text extracted | ✓ text.txt exists |
| Verified fact (≥1) | ✓ FACT-FODS-001 |
| Spec→fact citation confirmed | ✓ line 7218-7228 in normalized |
| Declaration with spec_fact_refs | ✓ pilot-003 accepts FACT-FODS-001 |
| Supervisor enforces gate | ✓ evidence_declaration.py wired |
| Code/test cites fact | ✗ product src/ does not have FACT-FODS-001 citations |
| Test cites fact | ✗ test files do not reference FACT-FODS-001 |

**Proof Level: P4** — source-backed requirements exist; enforcement wired; but code and tests do not yet cite FACT-xxx facts.

P5 would require: tests explicitly referencing spec facts.
P6 would require: code, tests, AND supervisor all citing FACT-FODS-001 in a traceable chain.

## Remaining Gaps

1. FACT-FODS-002 through FACT-FODS-010 need human/agent verification (9 facts)
2. Product source code (`src/python/fods/fods_codec.py`, etc.) does not cite FACT-FODS-001
3. Test files do not reference spec facts
4. Full P6 chain requires annotation pass across code + tests
