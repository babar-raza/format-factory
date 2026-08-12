# [Draft, not submitted] blendmodes (FHPythonUtils): ADDITIVE blend type uses the wrong alpha-compositing formula

**Project**: blendmodes (PyPI `blendmodes`, `github.com/FHPythonUtils/BlendModes`)
**Version**: `2025` (PyPI, pinned via real `pip install blendmodes`)
**Component**: `blendmodes/blend.py`, `blendLayersArray()`'s own
`alphaFunc` dispatch table
**Severity**: Correctness — `BlendType.ADDITIVE` (the library's own
mapping for OpenRaster's `svg:plus`) produces the wrong alpha channel

## Reproduction

```python
from blendmodes.blend import blendLayersArray, BlendType
# destination (230,60,40) alpha 153/255 at (0,0)-(20,20)
# source (40,120,230) alpha 128/255 at (12,12)-(32,32), 32x32 canvas
result = blendLayersArray(bg_img, fg_img, BlendType.ADDITIVE)
# result[16, 16] == (111, 98, 159, 204) -- wrong
```

## Expected result

Per the Porter-Duff Lighter formula (which the library's own `additive()`
RGB blend function name correctly targets), the combined alpha should be
`min(alpha_s + alpha_b, 1.0)` — clamped additive, not the standard
Source-Over alpha formula. Correct result for this fixture:
`(158,96,139,255)`, independently confirmed by GEGL's own
`operations/generated/plus.c` and Cairo's own `OPERATOR_ADD`.

## Actual result

`(111, 98, 159, 204)`. The alpha channel (204) matches neither the
correct clamped-additive value (255) nor an obvious alternative — it is
consistent with the STANDARD Source-Over alpha formula
(`alpha_s + alpha_b - alpha_s*alpha_b = 0.502 + 0.6 - 0.502*0.6 ≈ 0.801`,
`0.801*255 ≈ 204`), because `BlendType.ADDITIVE` is not present in
`blendLayersArray()`'s own `alphaFunc` dict (which only special-cases
`DESTIN`/`DESTOUT`/`SRCATOP`/`DESTATOP`) and therefore falls through to
the generic `alpha_comp_shell()` path, which always uses the Source-Over
alpha formula regardless of which RGB blend function is selected.

## Root cause

Confirmed by direct source reading of `blendLayersArray()`: the
`alphaFunc` dispatch dict used to select a Porter-Duff-aware alpha
formula omits `BlendType.ADDITIVE`, even though the library's own
`additive()` RGB function (`np.minimum(background + foreground, 1.0)`)
is specifically written for the Lighter operator's own additive
semantics. The alpha channel was evidently never updated to match.

## Proposed issue text

> **Title**: `BlendType.ADDITIVE` produces an incorrect alpha channel
> (uses Source-Over alpha instead of clamped additive alpha)
>
> `additive()`'s own RGB formula (`min(background+foreground, 1.0)`)
> correctly implements the Porter-Duff Lighter/"plus" operator's color
> channel, but `blendLayersArray()`'s own `alphaFunc` dispatch dict
> (which special-cases `DESTIN`/`DESTOUT`/`SRCATOP`/`DESTATOP` to use the
> correct Porter-Duff alpha formula for those operators) does not include
> `ADDITIVE`, so it falls through to the generic Source-Over alpha
> formula (`upper_alpha + lower_alpha - upper_alpha*lower_alpha`) instead
> of the correct `min(upper_alpha + lower_alpha, 1.0)`. Concrete
> counter-example: destination alpha 0.6, source alpha 0.502 → correct
> result alpha is `1.0` (clamped), library currently returns `≈0.801`.
> Cross-checked against GEGL's own `plus.c` and Cairo's own
> `OPERATOR_ADD`, both of which agree with the expected value. Suggested
> fix: add an `additiveAlpha` entry to `alphaFunc` (or equivalent) that
> computes `min(upper_alpha + lower_alpha, 1.0)`.
