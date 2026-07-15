# Spec Evidence: XLIFF

## Primary Specification
- **Title:** XLIFF (XML Localisation Interchange File Format) Version 2.1
- **Version:** XLIFF 2.1
- **URL:** https://docs.oasis-open.org/xliff/xliff-core/v2.1/xliff-core-v2.1.html
- **Body:** OASIS
- **Accessed:** 2026-07-14
- **License:** RF (OASIS)

## Spec Availability Assessment
- Freely accessible: Yes
- Machine-readable schema: Yes (XSD provided by OASIS)
- Actively maintained: Yes

## Key Structural Facts
- The root element is `<xliff>` with required `version` and `srcLang` attributes, and optional `trgLang`
- Translation units are organized in `<file>` elements, each containing `<unit>` elements with `<segment>` children
- Each `<segment>` contains a `<source>` and optional `<target>` element holding the translatable text
- Inline markup uses elements like `<ph>` (placeholder), `<pc>` (paired code), and `<mrk>` (marker) for preserving formatting within translatable content
