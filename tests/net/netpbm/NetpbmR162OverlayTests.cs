// Tests for NetpbmImage.Overlay dedicated coverage.
// Sprint: ff-sprint-s166-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R162

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R162: Dedicated tests for NetpbmImage.Overlay(NetpbmImage overlay, int topOffset, int leftOffset).
/// Overlay composites the overlay image on top of this image at the given offset.
/// Returns a NEW image (clone of base with overlay pixels written into it).
/// Throws InvalidOperationException if overlay format differs from base format.
/// Throws ArgumentOutOfRangeException if topOffset or leftOffset is negative.
/// No-overlap (offsets completely outside base) returns a clone with no changes.
/// Covers: format mismatch throws InvalidOperationException; negative topOffset throws;
/// negative leftOffset throws; format preserved; original unchanged;
/// no-overlap returns same dims; overlay at (0,0) writes pixel to top-left;
/// offset overlay pixel at correct position; dogfood Create->SetPixel->Overlay->GetPixel;
/// dogfood overlay larger than base is clipped to overlap region.
/// </summary>
public class NetpbmR162OverlayTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Overlay_FormatMismatch_ThrowsInvalidOperationException()
    {
        var base_ = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(2, 2, NetpbmFormat.PBM_P4);
        Assert.Throws<InvalidOperationException>(() => base_.Overlay(over, 0, 0));
    }

    [Fact]
    public void Overlay_NegativeTopOffset_ThrowsArgumentOutOfRangeException()
    {
        var base_ = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<ArgumentOutOfRangeException>(() => base_.Overlay(over, -1, 0));
    }

    [Fact]
    public void Overlay_NegativeLeftOffset_ThrowsArgumentOutOfRangeException()
    {
        var base_ = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<ArgumentOutOfRangeException>(() => base_.Overlay(over, 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Overlay_FormatPreserved()
    {
        var base_ = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var result = base_.Overlay(over, 0, 0);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Overlay_OriginalUnchanged()
    {
        var base_ = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        base_.SetPixel(0, 0, 100);
        _ = base_.Overlay(over, 0, 0);
        Assert.Equal(100, base_.GetPixel(0, 0)); // still unchanged
    }

    [Fact]
    public void Overlay_NoOverlap_ReturnsSameDims()
    {
        var base_ = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        // offset completely outside (100,100 >> 4x4 image)
        var result = base_.Overlay(over, 100, 100);
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void Overlay_AtOrigin_WritesPixelToTopLeft()
    {
        var base_ = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        over.SetPixel(0, 0, 77);
        var result = base_.Overlay(over, 0, 0);
        Assert.Equal(77, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_OffsetOverlay_PixelAtCorrectPosition()
    {
        var base_ = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        over.SetPixel(0, 0, 55);
        // Overlay at topOffset=2, leftOffset=3 → pixel maps to base row=2, col=3
        var result = base_.Overlay(over, 2, 3);
        Assert.Equal(55, result.GetPixel(2, 3));
    }

    [Fact]
    public void DogfoodPipeline_CreateSetPixelOverlay_GetPixel()
    {
        var base_ = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        base_.SetPixel(0, 0, 10); // base has pixel 10 at top-left
        var over = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        over.SetPixel(0, 0, 99); // overlay has pixel 99 at (0,0)
        var result = base_.Overlay(over, 0, 0);
        // Overlay pixel overwrites base pixel at (0,0)
        Assert.Equal(99, result.GetPixel(0, 0));
    }

    [Fact]
    public void DogfoodPipeline_OverlayLargerThanBase_ClippedToBaseBounds()
    {
        var base_ = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5); // 3x3
        var over = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5); // 5x5 — larger
        var result = base_.Overlay(over, 0, 0);
        // Output should still be 3x3 (base dims)
        Assert.Equal(3, result.Width);
        Assert.Equal(3, result.Height);
    }
}
