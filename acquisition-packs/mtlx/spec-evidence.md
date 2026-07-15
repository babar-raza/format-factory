# Spec Evidence: MaterialX

## Primary Specification
- **Title:** MaterialX Specification
- **Version:** MaterialX v1.39
- **URL:** https://materialx.org/Specification.html
- **Body:** Academy Software Foundation
- **Accessed:** 2026-07-14
- **License:** Apache 2.0/BSD/MIT

## Spec Availability Assessment
- Freely accessible: Yes
- Machine-readable schema: Yes (XSD provided in the MaterialX repository)
- Actively maintained: Yes

## Key Structural Facts
- The root element is `<materialx>` with a required `version` attribute specifying the spec version
- Materials are defined through node graphs (`<nodegraph>`), shader references (`<surfacematerial>`), and typed inputs/outputs
- Data types include scalars, vectors (vector2, vector3, vector4), colors (color3, color4), matrices, strings, filenames, and arrays
- The format supports inheritance via `<nodedef>` (node type definitions) and `<implementation>` (bindings to shader code)
