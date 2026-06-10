# Package Proof Protocol
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-R3-CLOSURE-REPAIR-AND-R4-ODF-PREPARATION-001
Lane: B — Package Proof Protocol
Generated: 2026-06-05

## Protocol: How to Write a Non-Stale review-package-proof.md

### Invariant

`review-package-proof.md` MUST NOT be listed in `evidence_artifacts` of the
evidence-declaration.yaml. This avoids the self-reference problem where the ZIP
would need to contain a proof that documents the ZIP's own SHA.

`review-package-proof.md` IS listed in `reports_created` for documentation purposes.

### Steps

1. Build ZIP (run `build_declaration_review_package.py`)
2. Read ZIP SHA-256 from `.local/supervisor/reviews/<run_id>/declaration-review-package.sha256.json`
3. Read ZIP size from same file
4. Read missing_artifacts_count from same file
5. Write `review-package-proof.md` with:
   - Evidence directory absolute path
   - ZIP absolute path
   - SHA-256 (64-char hex)
   - Byte size (integer)
   - File count (from sha256.json or ZIP listing)
   - autonomous-cycle exit code
   - Package-builder command
   - Final git status summary
   - Explicit: no [PLACEHOLDER] strings
6. Do NOT change any other file after this step.
7. If SHA256 must be updated, rebuild ZIP and loop once (step 1→6 again).

### Anti-Placeholder Checks

Before declaring sprint complete, verify:
```python
proof_text = open('reports/.../review-package-proof.md').read()
assert '[PLACEHOLDER]' not in proof_text
assert 'will be computed' not in proof_text.lower()
sha = re.search(r'SHA-256[^\n]+', proof_text)
assert sha and len(sha.group(0)) > 70  # must have actual 64-char hex
```

### R3C Application

For this sprint:
- review-package-proof.md is NOT in evidence_artifacts
- review-package-proof.md IS in reports_created
- ZIP will be built, then proof written from sha256.json values
- Result: proof accurately describes the ZIP; ZIP does not contain proof
