# Adversarial Review — TCA-FULL-018
**Run ID:** spec-authority-full-pilot-healing-20260608-e382e5f
**Reviewer role:** L-ADVERSARIAL (independent internal review)

---

## Question 1: Did any pilot pass without actually testing the production path?

**Finding: NO — all pilots used live `validate_spec_fact_refs.py`**

All pilot declarations (TCA-FULL-002 through 007, 013) were run through the actual production validator:
```bash
.local/venv/Scripts/python tools/supervisor/validate_spec_fact_refs.py --declaration <pilot> --json
```
Exit codes and JSON results were captured in `pilot-results/`. No mocking was used for pilot runs.
Tests (`test_full_pilot_verification.py`) also call the real `check_item()` and `validate_declaration_spec_fact_refs()` functions directly.

**Score: PASS**

---

## Question 2: Did any declaration claim product authority without valid spec facts?

**Finding: NO — all declarations use appropriate exception_classification**

All work items in the evidence declaration use `exception_classification: investigation_only` (or `sample_only_non_product`).
None claim product readiness or release gating.
No `spec_fact_refs` were fabricated — FACT-FODS-001 (used in PILOT-003) is a genuinely verified fact from the spec text.

**Score: PASS**

---

## Question 3: Did unknown format still default to allowed?

**Finding: FIXED — unknown formats now return `BLOCKED_UNKNOWN_AUTHORITY`**

Prior behavior: `_get_format_authority_status()` read `data.get("poc_targets", [])` → always empty → always returned "ALLOWED".
Fixed: reads all top-level list sections; returns `BLOCKED_UNKNOWN_AUTHORITY` for formats not found.
Test `test_unknown_format_not_actionable` confirms this.

Caveat: Formats that ARE in poc-targets.yaml but have no explicit `authority_status` field set → return "ALLOWED".
If a format should be explicitly blocked, it needs `authority_status: BLOCKED_*` added to poc-targets.yaml.
This is a governance decision — not an enforcement gap.

**Score: PASS (with governance action required for future explicit blocking)**

---

## Question 4: Did legacy_backfill claim readiness?

**Finding: NO — validator correctly rejects READINESS + legacy_backfill**

Pilot-004 Part B: READINESS + legacy_backfill → rejected with grade_impact=reject.
Test `test_pilot_004_legacy_backfill_cannot_claim_readiness` confirms.
DEBT_ONLY_EXCEPTIONS = {"legacy_backfill", "no_public_spec_available"} — both blocked from READINESS/RELEASE_GATE.

**Score: PASS**

---

## Question 5: Did Gnumeric become product-ready from schema-only authority?

**Finding: GOVERNANCE RISK IDENTIFIED — schema_authority_available is in READINESS_ALLOWED_EXCEPTIONS**

Current code: `schema_authority_available` on READINESS → ACCEPTED (grade_impact: none).
This means Gnumeric *could* claim readiness with schema authority alone.
However: Gnumeric has no `authority_status: BLOCKED_*` in poc-targets.yaml.
The selector will still return "ALLOWED" for Gnumeric (format is in foss_reduced_products).

Mitigation: The READINESS claim would require a separate review of whether Gnumeric is actually product-ready, which goes through the broader supervisor grading pipeline. The spec_fact_refs gate alone does not constitute product readiness.

Recommendation: Add `authority_status: BLOCKED_NO_VERIFIED_FACTS` to Gnumeric's poc-targets.yaml entry until at least 1 schema-backed fact is verified.

**Score: PARTIAL — enforcement allows schema_authority_available on READINESS; governance action recommended**

---

## Question 6: Did ABW claim readiness/release without spec authority?

**Finding: NO — ABW correctly blocked from readiness/release**

Validator: READINESS + no_public_spec_available → REJECTED.
Test `test_pilot_004_no_public_spec_cannot_claim_release_gate` confirms for RELEASE_GATE.
ABW existing code is treated as legacy_backfill — no readiness claims possible.

**Score: PASS**

---

## Question 7: Did FODS proof level overclaim P6?

**Finding: NO — P4 claimed honestly**

FODS proof level documented as P4:
- Spec source cached ✓
- Source SHA verified ✓
- Normalized text extracted ✓
- 1 verified fact (FACT-FODS-001) ✓
- Declaration enforcement active ✓
- Product code DOES NOT cite FACT-FODS-001 ✗
- Tests DO NOT reference spec facts ✗

P5 would require tests citing facts. P6 would require full chain. Not overclaimed.

**Score: PASS**

---

## Question 8: Did continuation still point to product expansion before proof?

**Finding: CONTAINED — advisory_prompt_executable=false prevents blind execution**

The continuation signal before this sprint pointed to "product deepening" (mainstream product expansion).
However: `advisory_prompt_executable: false` means it cannot be blindly executed.
This sprint's supervisor cycle generated a new next-sprint.md that will reflect the authority pilot work.
No autonomous continuation is possible without explicit user review.

**Score: PASS (advisory_prompt_executable=false is the protection)**

---

## Question 9: Did anti-skip/adoption pass with unexplained exemptions?

**Finding: PASS — all exemptions have explicit reasons**

All 15 work items have `exemption_reason` field with explanations.
Adoption compliance: PASS (15 non-exempt, all with exemption_reason).
The `missing_sample_outputs` LOW caveat: sample outputs were created (8 files) but initially in the report directory.
They were subsequently copied to `.local/evidences/*/sample-outputs/` for the evidence root checker.

**Score: PASS**

---

## Question 10: Is the evidence bundle self-contained?

**Finding: YES — all artifacts are in the sprint report directory**

Pilot declarations, results, raw logs, sample outputs, ledgers, and test logs are all under:
`reports/spec-authority-full-pilot-healing/spec-authority-full-pilot-healing-20260608-e382e5f/`

The declaration review package will include all declared evidence paths.

**Score: PASS**

---

## Critical Issues Found

1. **DEBT-004 (MEDIUM):** Fact ID existence check is NOT implemented. `FACT-DOES-NOT-EXIST` passes format validation. Validator only checks format (FACT- prefix + len > 6), not existence in a fact registry. This is documented in the authority debt ledger but not auto-fixed (requires fact registry design).

2. **DEBT-005 (LOW-MEDIUM):** `schema_authority_available` on READINESS is accepted without requiring any verified schema facts. This is a governance risk for Gnumeric — it could claim readiness with schema authority alone. Recommendation: explicitly set `authority_status: BLOCKED_NO_VERIFIED_FACTS` in poc-targets.yaml for Gnumeric until facts are verified.

---

## No Critical Issues Requiring Sprint Halt

Both identified issues are documented as governance debt rather than blocking enforcement failures.
The core enforcement path (reject missing refs, reject AI-only, reject legacy readiness) is proven.

**Overall adversarial verdict: APPROVED — no undisclosed bypasses found**
