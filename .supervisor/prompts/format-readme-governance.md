---
espanso_provenance:
  source_trigger: ":ff-format-readme-hardening"
  source_block: 34
  source_line_range: [41132, 43577]
  gap_id: GAP-ESP-010
  extraction_date: "2026-07-12"
  capability_id: null
prompt_id: ESP-PROMPT-10
title: "Format README Governance"
version: "1.0"
status: ACTIVE
mutating: true
context_profile: full
---

# Format README Governance

Forensic investigation and preservation-first enhancement of per-format README files.
Synthesized from Espanso entries: `:ff-format-readme-hardening`, `:ffsrn`.

## When to Use

- A format's `src/python/{format}/README.md` is stale, missing, or has incorrect counts
- A product sprint has added new APIs that are not reflected in the format README
- A documentation gap has been identified for a specific format

## When NOT to Use

- Root `README.md` governance (use ESP-PROMPT-2 `readme-governance.md` instead)
- General documentation generation without a specific format target
- When `src/python/{format}/` does not yet exist

## Prerequisites

- `src/python/{format}/` exists and is readable
- The format's oracle entry is VERIFIED or CASES_DEFINED
- `registry/format-registry.yaml` entry exists for the format

## Allowed Paths

- `src/python/{format}/README.md` (create or update in-place)
- `docs/formats/{format}/` (create if needed)

## Forbidden Paths

- `README.md` (root — use ESP-PROMPT-2)
- `src/python/{format}/*.py` (read-only during this sprint)
- `src/net/` (not in scope for format README governance)

## Protocol

1. **Read first**: read `src/python/{format}/README.md` before any mutation
2. **Inventory APIs**: read `src/python/{format}/__init__.py` and count public functions
3. **Check spec parity**: compare published API against SAL fact count for the format
4. **Preserve existing context**: do not replace author-written content without evidence it is false
5. **Update counts**: correct function counts, spec_qname coverage, oracle status
6. **Do not commit** without explicit user approval (CLAUDE.md SCM policy)

## Evidence Filing

- Evidence path: `src/python/{format}/README.md` (before/after diff)
- Test layer: 0 (documentation only)
- Worker verdict: PASS when all counts verified against HEAD source

## Completion Gate

- README updated with correct API count and oracle status
- No false claims about Gate 11 or publication readiness
- `validate_prompt_registry.py` exits 0 (structural check)
