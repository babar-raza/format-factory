# Materialization Helper — Train I

## New Tool
`tools/supervisor/materialize_and_review.py`

One-command wrapper combining:
1. `materialize_declared_evidence.py`
2. `build_declaration_review_package.py`

Exit codes: 0 (both pass), 1 (materialization failed), 2 (review package failed)
