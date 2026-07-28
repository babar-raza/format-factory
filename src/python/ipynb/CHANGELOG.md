# Changelog

## 0.2.0.dev0

- Add the collision-free `format_factory.ipynb` production namespace.
- Split model, reader, writer, validation, security, analytics, adapter, and
  command-line responsibilities.
- Preserve alpha symbols as migration aliases in the new namespace while
  excluding the top-level `ipynb` package from the production wheel.
