# Declaration Materialization Helper — Train G

Sprint: FORMAT-FACTORY-ACCELERATION-R99-PRODUCT-FACTORY-ACCELERATION-LAYER-PARALLEL-MEGA-TRAIN-001

## Quick-Path Documentation

The acceleration layer documents the evidence packaging quick-path so agents
can materialize evidence without ad hoc steps.

### Step-by-Step Quick-Path

1. **Write declaration**: Create `.local/evidences/<run_id>/evidence-declaration.yaml`
   - Declare all work items, evidence paths, changed files, test results

2. **Run materializer**:
   ```bash
   .local/venv/Scripts/python tools/supervisor/materialize_declared_evidence.py \
     --declaration .local/evidences/<run_id>/evidence-declaration.yaml
   ```
   Output: `.local/supervisor/materialized/<run_id>/`

3. **Run review package builder**:
   ```bash
   .local/venv/Scripts/python tools/supervisor/build_declaration_review_package.py \
     --declaration .local/evidences/<run_id>/evidence-declaration.yaml
   ```
   Output: `.local/supervisor/reviews/<run_id>/declaration-review-package.zip`

4. **Report SHA-256**: Print the ZIP path and SHA from builder output

### Integration with Acceleration Layer

- Lane execution recorder captures evidence artifact paths
- Sprint learning generator reads work-item grades from materializer
- Gap selector uses POC matrix snapshot from materializer

### Existing Tools

| Tool | Path | Role |
|------|------|------|
| materialize_declared_evidence.py | tools/supervisor/ | Verify paths, compute SHAs, capture diffs |
| build_declaration_review_package.py | tools/supervisor/ | Package into reviewable ZIP |
| grade_declared_work.py | tools/supervisor/ | Grade work items against evidence |
| inspect_declared_evidence.py | tools/supervisor/ | Deep-inspect test file content |

No new tool created for Train G; the existing tools are already operational.
The acceleration layer adds this documentation as the canonical quick-path reference.
