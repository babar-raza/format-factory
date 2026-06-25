# Plan Mode Limitations
# Constraints that apply to this expert review sprint

## Hard Constraints (Non-Negotiable)

These constraints apply throughout the entire expert review sprint:

### Source Modifications PROHIBITED
- src/net/** — NO edits
- src/python/** — NO edits
- tests/** — NO edits
- product-capability-matrix/poc-targets.yaml — NO edits
- registry/format-registry.yaml — NO edits
- .supervisor/policies.yaml — NO edits

### Version Control PROHIBITED
- No git commit
- No git push
- No git stash
- No git reset
- No git clean

### Approvals PROHIBITED
- No Gate 8 approval
- No Gate 11 approval
- No commercial_product_ready=true changes
- No publication authorization

### Execution PROHIBITED
- No new MCP daemon activation
- No GhidraMCP activation
- No Superpowers activation
- No new package installations

## Permitted Actions

### Read-Only
- Read any file in the repository
- Run git status, git diff --name-only, git log (read-only)
- Run Python with .venv for read-only inspection
- Run pytest with --collect-only (no test execution)
- Run wc, ls, find (read-only shell commands)

### Write (Report Files Only)
- Create/write files under `reports/expert-manual-system-review/**`
- Create/write files under `.local/evidences/expert-manual-system-review/**`

## Why These Constraints Exist

1. **Trust verification**: The review must not alter the system being reviewed
2. **Audit integrity**: Report findings must reflect actual state, not post-fix state
3. **Governance compliance**: Repairs must go through the governed system (Skills, Validators, GAP ledger)
4. **Commercial safety**: No product claims can be made or changed during an audit sprint

## Limitations of This Review

1. **LLM evidence quality**: Evidence bundles may have been graded DEFERRED_WITH_REASON if the LLM grader API was unavailable. Some product quality claims in evidence bundles may be ungraded.

2. **Gap ledger taxonomy**: 1131/1132 gaps have "unknown" category. Gap-driven investigation is limited because gaps cannot be filtered by meaningful category.

3. **SAL coverage**: 10 of 20 Python formats have no spec facts in the SAL cache. Spec-parity assessment for these formats must rely on QName registry alone.

4. **Test execution**: Tests are not executed during this review — only test file structure and test names are inspected. Actual test pass/fail state is taken from the last sprint evidence.

5. **Installed packages**: Installed package behavior (from wheels) is not re-tested during this review. Install proof is accepted from prior sprints.

6. **Commercial output quality**: Physical output files (PDFs, PNGs, ZIPs) from exporters are not regenerated and inspected during this review. Their quality is assessed from test coverage and source analysis.
