"""ORA-COMPOSITE-001 / ORA-EDIT-001 -- the two items each obligation's own
narrowed missing_behavior named after FF6-ORA-RENDER-ENGINE-001 built the
core rendering/compositing engine.

ORA-COMPOSITE-001 MUST clause: "pixel semantics through a replaceable
rendering adapter." Before this file, render.py provided one concrete,
non-pluggable compositor -- correct pixel semantics, but nothing a caller
could substitute a different rendering backend into. `Renderer` (a
`Protocol`) is that adapter boundary; `render_document`/
`generate_baseline_assets` both accept one, defaulting to
`DEFAULT_RENDERER` (`W3CCompositingRenderer`, this module's own W3C
compositor unchanged).

ORA-EDIT-001 required_tests: "stale-view invalidation." Before this file,
`generate_baseline_assets` provided a real regeneration path, but
`apply_transaction` never called it -- a caller had to remember to
regenerate baseline assets themselves after every committed edit.
`apply_transaction_and_refresh_baseline_assets` closes that: a successful
commit now regenerates and replaces the thumbnail/merged-image members
automatically. Plain `apply_transaction` is unchanged (still does not
refresh anything) -- proven directly, not merely asserted, by a dedicated
test.
"""

from __future__ import annotations

import dataclasses

from format_factory.ora import (
    DecodedRaster,
    DEFAULT_RENDERER,
    OraLayer,
    OraStack,
    Renderer,
    W3CCompositingRenderer,
    apply_transaction,
    apply_transaction_and_refresh_baseline_assets,
    decode_png,
    load,
)


# ── Renderer adapter (ORA-COMPOSITE-001) ─────────────────────────────────


class _SolidColorRenderer:
    """A trivial Renderer implementation that ignores the document
    entirely and always returns one solid color -- deliberately NOT the
    default compositor's own logic, so using it proves substitution
    genuinely happened rather than coincidentally matching."""

    def __init__(self, rgba: tuple[int, int, int, int]) -> None:
        self._rgba = rgba

    def render(self, root, members, *, width, height, limits=None):  # noqa: ANN001, ANN201
        return DecodedRaster(width=width, height=height, pixels=bytes(self._rgba) * (width * height))


def test_default_renderer_is_the_w3c_compositor() -> None:
    assert isinstance(DEFAULT_RENDERER, W3CCompositingRenderer)


def test_w3c_compositing_renderer_satisfies_the_renderer_protocol() -> None:
    renderer: Renderer = W3CCompositingRenderer()
    assert hasattr(renderer, "render")


def test_render_document_uses_the_default_renderer_when_none_is_supplied() -> None:
    from format_factory.ora import render_document

    image = load("samples/by-format/ora/valid/with-groups.ora")

    result = render_document(image.document, image.members)

    embedded = decode_png(image.members["mergedimage.png"])
    assert result.pixels == embedded.pixels


def test_render_document_accepts_a_substituted_renderer() -> None:
    from format_factory.ora import render_document

    image = load("samples/by-format/ora/valid/with-groups.ora")
    custom = _SolidColorRenderer((10, 20, 30, 255))

    result = render_document(image.document, image.members, renderer=custom)

    assert result.pixels == bytes((10, 20, 30, 255)) * (
        image.document.width * image.document.height
    )


def test_generate_baseline_assets_accepts_a_substituted_renderer() -> None:
    from format_factory.ora import generate_baseline_assets

    image = load("samples/by-format/ora/valid/with-groups.ora")
    custom = _SolidColorRenderer((1, 2, 3, 255))

    _, merged_image_bytes = generate_baseline_assets(
        image.document, image.members, renderer=custom
    )

    decoded = decode_png(merged_image_bytes)
    assert decoded.pixels == bytes((1, 2, 3, 255)) * (
        image.document.width * image.document.height
    )


def test_a_minimal_custom_renderer_class_is_usable_without_inheriting_anything() -> None:
    """Renderer is a structural Protocol -- a plain class with a matching
    `render` method satisfies it, no base class or registration needed."""
    from format_factory.ora import render_document

    image = load("samples/by-format/ora/valid/minimal.ora")

    class MinimalRenderer:
        def render(self, root, members, *, width, height, limits=None):  # noqa: ANN001, ANN201
            return DecodedRaster(width=width, height=height, pixels=bytes(4 * width * height))

    result = render_document(image.document, image.members, renderer=MinimalRenderer())

    assert result.pixels == bytes(4 * image.document.width * image.document.height)


# ── Automatic stale-view invalidation (ORA-EDIT-001) ─────────────────────


def _hide_group_a_step(document_root_children):
    group_a, base = document_root_children
    hidden = dataclasses.replace(group_a, visibility="hidden")

    def step(image):  # noqa: ANN001, ANN201
        new_root = dataclasses.replace(image.document.root, children=(hidden, base))
        new_document = dataclasses.replace(image.document, root=new_root)
        return dataclasses.replace(image, document=new_document)

    return step


def test_committed_transaction_automatically_refreshes_baseline_assets() -> None:
    image = load("samples/by-format/ora/valid/with-groups.ora")
    _, base = image.document.root.children
    original_merged = decode_png(image.members["mergedimage.png"])
    base_raster = decode_png(image.members[base.src])

    result = apply_transaction_and_refresh_baseline_assets(
        image, [_hide_group_a_step(image.document.root.children)]
    )

    assert result.committed is True
    regenerated = decode_png(result.image.members["mergedimage.png"])
    assert regenerated.pixels != original_merged.pixels
    assert regenerated.pixels == base_raster.pixels


def test_rolled_back_transaction_does_not_refresh_anything() -> None:
    image = load("samples/by-format/ora/valid/with-groups.ora")

    def failing_step(current_image):  # noqa: ANN001, ANN201
        raise ValueError("deliberate failure")

    result = apply_transaction_and_refresh_baseline_assets(image, [failing_step])

    assert result.committed is False
    assert result.image is image
    assert result.image.members["mergedimage.png"] == image.members["mergedimage.png"]


def test_plain_apply_transaction_still_does_not_refresh_baseline_assets() -> None:
    """The two functions are genuinely separate, not one with a hidden
    flag: apply_transaction's own committed result must NOT reflect the
    edit in its baseline assets, proving no refresh silently happened."""
    image = load("samples/by-format/ora/valid/with-groups.ora")
    original_merged = decode_png(image.members["mergedimage.png"])

    result = apply_transaction(image, [_hide_group_a_step(image.document.root.children)])

    assert result.committed is True
    unrefreshed = decode_png(result.image.members["mergedimage.png"])
    assert unrefreshed.pixels == original_merged.pixels


def test_refreshed_baseline_assets_pass_validation() -> None:
    from format_factory.ora import dumps, validate

    image = load("samples/by-format/ora/valid/with-groups.ora")

    result = apply_transaction_and_refresh_baseline_assets(
        image, [_hide_group_a_step(image.document.root.children)]
    )

    report = validate(dumps(result.image))
    assert not any(
        "BASELINE" in d.code or "MERGED_IMAGE" in d.code or "THUMBNAIL" in d.code
        for d in report.diagnostics
    )
