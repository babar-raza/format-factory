# Migration from 0.1 alpha

Replace `import xliff` with `import format_factory.xliff`.

The common lifecycle is `probe`, `load`, `loads`, `dump`, `dumps`, and
`validate`. Legacy helpers remain exported from the production namespace during
the pre-1.0 migration but the top-level `xliff` package is not shipped in the
new wheel. XLIFF 1.2 parsing is not carried into the stable 2.x model.
