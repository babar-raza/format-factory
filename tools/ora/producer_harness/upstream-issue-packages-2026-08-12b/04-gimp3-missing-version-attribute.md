# [Draft, not submitted] GIMP 3.0.4: exported `<image>` element omits the required `version` attribute

**Project**: GIMP
**Version**: 3.0.4 (Alpine Linux 3.23.5 `apk` package)
**Component**: `file-openraster-export`
**Severity**: Spec non-conformance — exported `.ora` files fail strict
readers

## Reproduction

Export any document via GIMP 3.0.4's own `file-openraster-export`
(reproduced in
`tools/ora/producer_harness/gimp3/PROVENANCE-gimp3-svg-plus-spike-2026-08-12.md`,
Path A) and inspect the resulting `stack.xml`'s own root `<image>`
element.

## Expected result

Per the OpenRaster specification, the root `<image>` element is
required to declare a `version` attribute (e.g. `version="0.0.4"`).

## Actual result

`<image w="32" h="32">` — no `version` attribute present at all,
confirmed via direct `stack.xml` inspection of the real exported
archive (`gimp3-native-svg-plus.ora`, preserved unmodified in this
project's own evidence).

format-factory's own `ReadMode.STRICT` correctly refuses this
(`OraValidationError: <image> is missing the required 'version'
attribute`); `ReadMode.TOLERANT` accepts it with a named recovery
action.

## Root cause

Confirmed directly by inspecting the real exported `stack.xml` — the
root element writer omits the attribute unconditionally in this
version's own export path.

## Proposed issue text

> **Title**: OpenRaster export omits the required `version` attribute
> on the root `<image>` element
>
> Files exported via `file-openraster-export` in GIMP 3.0.4 have a root
> `<image>` element with no `version` attribute (e.g. `<image w="32"
> h="32">` instead of `<image w="32" h="32" version="0.0.4">`). The
> OpenRaster spec requires this attribute; strict readers correctly
> reject files missing it. Suggested fix: add the `version` attribute
> to the exporter's own root-element construction.
