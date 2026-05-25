# R66 Work-Ahead Policy

Hard prohibitions remain in effect:
- No push, no PyPI/NuGet publication
- No Gate 8/11 approval
- No commercial_product_ready=true
- No broad git reset/stash/clean

Work-ahead lanes W1-W5 produce concrete artifacts (fixtures, tests, validators, pipeline scripts).
All work-ahead items are guarded — no unguarded failures.
