---
version: "1.0"
last-updated: "2026-07-28"
phase-available: "all"
gate-required: null
skill-id: reconcile-stashed-work
generated_by: codex
---

# /reconcile-stashed-work

Inventory and materialize exact paths from an immutable stash commit into an
isolated detached worktree. Preserve a verified recovery archive before use.

## Required inputs

- `stash_commit`: full immutable stash commit ID
- `base_commit`: first parent used to create the stash
- `main_commit`: integration commit used for classification
- `worktree_path`: registered detached worktree, never the root checkout
- `path_manifest`: JSON manifest with exact relative paths
- `archive_dir`: local recovery archive containing the stash patch and tree ZIP

## Execution

```powershell
python tools/recovery/stash_reconciler.py inventory `
  --main-commit <main> `
  --stash <index>:<stash>:<base> `
  --output <ledger.jsonl>

python tools/recovery/stash_reconciler.py materialize `
  --worktree <detached-worktree> `
  --stash-commit <stash> `
  --base-commit <base> `
  --manifest <manifest.json> `
  --archive-dir <archive> `
  --receipt <receipt.json>
```

## Safety contract

- Require a detached registered worktree different from the repository root.
- Require immutable full commit IDs and an exact path manifest.
- Refuse `.git`, `.local`, `.env`, credentials, absolute paths, and traversal.
- In `unique` mode, materialize only when the current HEAD blob equals the base
  blob; accept an already-materialized stash blob as an idempotent no-op.
- In `three_way` mode, apply only the manifest paths and stop on conflicts.
- Never commit, push, create a branch, pop a stash, drop a stash, reset, clean,
  or mutate the root worktree.

## Output

Write a local JSON receipt listing verified inputs, changed paths, no-op paths,
conflicts, before/after blobs, and the final verdict.
