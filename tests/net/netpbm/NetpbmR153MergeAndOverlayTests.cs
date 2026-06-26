// Tests for NetpbmImage.MergeHorizontal, MergeVertical, Overlay.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R153

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R153: Tests for NetpbmImage.MergeHorizontal, MergeVertical, Overlay.
/// MergeHorizontal(other): creates a new image by placing this and other side by side.
///   Width = this.Width + other.Width; Height = max(this.Height, other.Height); same format.
/// MergeVertical(other): stacks images vertically.
///   Width = max(this.Width, other.Width); Height = this.Height + other.Height; same format.
/// Overlay(overlay, topOffset, leftOffset): composites overlay on top of this at given offset.
///   Result has same dimensions as this image; OOB offset clips silently.
/// Covers: MergeHorizontal width is sum; MergeHorizontal height is max; MergeHorizontal format preserved;
/// MergeHorizontal null throws; MergeVertical height is sum; MergeVertical width is max;
/// MergeVertical format preserved; MergeVertical null throws;
/// Overlay same dimensions; Overlay OOB offset does not throw; Overlay null throws;
/// dogfood Create->MergeHorizontal->MergeVertical->Overlay pipeline.
/// </summary>
public class NetpbmR153MergeAndOverlayTests
{
    private static NetpbmImage MakePgm(int w, int h, byte fill = 128) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM_P2, fill);

    // -------------------------------------------------------------------------
    // MergeHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeHorizontal_WidthIsSum()
    {
        var a = MakePgm(3, 2);
        var b = MakePgm(5, 2);
        var merged = a.MergeHorizontal(b);
        Assert.Equal(8, merged.Width);
    }

    [Fact]
    public void MergeHorizontal_HeightIsMax()
    {
        var a = MakePgm(3, 2);
        var b = MakePgm(3, 5);
        var merged = a.MergeHorizontal(b);
        Assert.Equal(5, merged.Height);
    }

    [Fact]
    public void MergeHorizontal_FormatPreserved()
    {
        var a = MakePgm(2, 2);
        var b = MakePgm(2, 2);
        var merged = a.MergeHorizontal(b);
        Assert.Equal(NetpbmFormat.PGM_P2, merged.Format);
    }

    [Fact]
    public void MergeHorizontal_Null_Throws()
    {
        var a = MakePgm(2, 2);
        Assert.ThrowsAny<Exception>(() => a.MergeHorizontal(null!));
    }

    [Fact]
    public void MergeHorizontal_PixelCountMatchesDimensions()
    {
        var a = MakePgm(3, 2);
        var b = MakePgm(2, 2);
        var merged = a.MergeHorizontal(b);
        Assert.Equal(merged.Width * merged.Height, merged.Pixels.Length);
    }

    // -------------------------------------------------------------------------
    // MergeVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeVertical_HeightIsSum()
    {
        var a = MakePgm(4, 3);
        var b = MakePgm(4, 2);
        var merged = a.MergeVertical(b);
        Assert.Equal(5, merged.Height);
    }

    [Fact]
    public void MergeVertical_WidthIsMax()
    {
        var a = MakePgm(4, 3);
        var b = MakePgm(6, 2);
        var merged = a.MergeVertical(b);
        Assert.Equal(6, merged.Width);
    }

    [Fact]
    public void MergeVertical_FormatPreserved()
    {
        var a = MakePgm(2, 2);
        var b = MakePgm(2, 2);
        var merged = a.MergeVertical(b);
        Assert.Equal(NetpbmFormat.PGM_P2, merged.Format);
    }

    [Fact]
    public void MergeVertical_Null_Throws()
    {
        var a = MakePgm(2, 2);
        Assert.ThrowsAny<Exception>(() => a.MergeVertical(null!));
    }

    // -------------------------------------------------------------------------
    // Overlay
    // -------------------------------------------------------------------------

    [Fact]
    public void Overlay_ResultSameDimensionsAsBase()
    {
        var base_ = MakePgm(8, 6);
        var over = MakePgm(3, 3, 200);
        var result = base_.Overlay(over, 1, 1);
        Assert.Equal(8, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Overlay_OobOffset_DoesNotThrow()
    {
        var base_ = MakePgm(4, 4);
        var over = MakePgm(3, 3, 200);
        // Large offset that clips — should not throw
        var result = base_.Overlay(over, 10, 10);
        Assert.Equal(4, result.Width);
    }

    [Fact]
    public void Overlay_Null_Throws()
    {
        var base_ = MakePgm(4, 4);
        Assert.ThrowsAny<Exception>(() => base_.Overlay(null!, 0, 0));
    }

    [Fact]
    public void Overlay_ZeroOffset_PixelsComeFromOverlay()
    {
        var base_ = MakePgm(4, 4, 0);
        var over = MakePgm(2, 2, 255);
        var result = base_.Overlay(over, 0, 0);
        // Top-left 2x2 region should have overlay pixels (255)
        Assert.Equal(255, result.GetPixel(0, 0));
        Assert.Equal(255, result.GetPixel(1, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->MergeHorizontal->MergeVertical->Overlay
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_MergeAndOverlay_Pipeline()
    {
        var left = MakePgm(4, 3, 50);
        var right = MakePgm(4, 3, 150);

        // Merge side by side
        var hMerged = left.MergeHorizontal(right);
        Assert.Equal(8, hMerged.Width);
        Assert.Equal(3, hMerged.Height);

        // Stack on top of itself
        var vMerged = hMerged.MergeVertical(hMerged);
        Assert.Equal(8, vMerged.Width);
        Assert.Equal(6, vMerged.Height);

        // Overlay a small image
        var stamp = MakePgm(2, 2, 200);
        var final_ = vMerged.Overlay(stamp, 1, 1);
        Assert.Equal(8, final_.Width);
        Assert.Equal(6, final_.Height);
        Assert.Equal(200, final_.GetPixel(1, 1));
    }
}
