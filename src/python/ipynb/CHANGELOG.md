# Changelog

## 0.2.0.dev0

- Add the collision-free `format_factory.ipynb` production namespace.
- Split model, reader, writer, validation, security, analytics, adapter, and
  command-line responsibilities.
- Preserve alpha symbols as migration aliases in the new namespace while
  excluding the top-level `ipynb` package from the production wheel.
- Add digest-checked official nbformat 4.0-4.5 schema validation with
  semantic checks for cell IDs, attachment references, tags, and
  forward-compatibility diagnostics.
- Add explicit, loss-audited nbformat 4.0-4.5 version conversion
  (`downgrade`, `plan_downgrade`, `upgrade`) with a cell-ID rewrite map and a
  content-bound two-step downgrade plan.
- Add explicit, reportable active-content sanitization for Markdown,
  attachments, and output MIME bundles (`sanitize`, `SanitizationMode`,
  `SanitizationPolicy`).
- Add content-addressed trust tracking independent of schema validity
  (`HmacNotebookNotary`).
- Add stable-cell-ID attachment management with dry-run mutation reports
  (`manage_attachments`).
- Add structure-aware notebook diffing and atomic, precondition-checked
  patches (`diff_notebooks`, `DiffPolicy`).
- Add a stable-ID governed cell-collection editor with insert/move/copy/
  replace/remove/search/bulk operations (`edit_cells`, `CellQuery`).
- Add read-only typed metadata snapshot adapters
  (`cell_metadata`, `notebook_metadata`).
- Add an opt-in, isolated notebook code-execution adapter, never reachable
  from load/validate/diff/save (`execute_notebook`).
