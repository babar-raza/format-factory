// Tests for NetpbmImage.Rotate90Cw, Rotate270Cw, Rotate180, MergeHorizontal, MergeVertical.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R166

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R166: Tests for NetpbmImage.Rotate90Cw, Rotate270Cw, Rotate180, MergeHorizontal, MergeVertical.
/// Rotate90Cw(): rotates image 90 degrees clockwise; swaps Width/Height.
/// Rotate270Cw(): rotates image 270 degrees clockwise; swaps Width/Height.
/// Rotate180(): rotates image 180 degrees; preserves Width and Height.
/// MergeHorizontal(other): places two images side by side; doubles width.
/// MergeVertical(other): places two images top-bottom; doubles height.
/// Covers: Rotate90Cw swaps Width/Height; Rotate90Cw 4 times returns to original dims;
/// Rotate270Cw swaps Width/Height; Rotate180 preserves Width/Height;
/// Rotate180 twice returns to original; MergeHorizontal doubles width;
/// MergeHorizontal height is same; MergeVertical doubles height;
/// MergeVertical width is same; Rotate90Cw+Rotate270Cw = same dims as original;
/// Rotate180 pixel count; dogfood Create->Rotate90->MergeHorizontal->MergeVertical pipeline.
/// </summary>
public class NetpbmR166RotateAndMergeTests
{
    private static NetpbmImage CreateGray(int w, int h, byte fill) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM_P2, fill);

    // -------------------------------------------------------------------------
    // Rotate90Cw
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate90Cw_SwapsWidthAndHeight()
    {
        var img = CreateGray(6, 4, 128);
        var rotated = img.Rotate90Cw();
        Assert.Equal(4, rotated.Width);
        Assert.Equal(6, rotated.Height);
    }

    [Fact]
    public void Rotate90Cw_FourTimes_SameDimensions()
    {
        var img = CreateGray(5, 3, 100);
        var result = img.Rotate90Cw().Rotate90Cw().Rotate90Cw().Rotate90Cw();
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    [Fact]
    public void Rotate90Cw_PixelCountPreserved()
    {
        var img = CreateGray(5, 3, 100);
        var rotated = img.Rotate90Cw();
        Assert.Equal(img.Width * img.Height, rotated.Width * rotated.Height);
    }

    // -------------------------------------------------------------------------
    // Rotate270Cw
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate270Cw_SwapsWidthAndHeight()
    {
        var img = CreateGray(6, 4, 128);
        var rotated = img.Rotate270Cw();
        Assert.Equal(4, rotated.Width);
        Assert.Equal(6, rotated.Height);
    }

    [Fact]
    public void Rotate90CwAnd270Cw_SameOutputDimensions()
    {
        var img = CreateGray(6, 4, 128);
        var r90 = img.Rotate90Cw();
        var r270 = img.Rotate270Cw();
        Assert.Equal(r90.Width, r270.Width);
        Assert.Equal(r90.Height, r270.Height);
    }

    // -------------------------------------------------------------------------
    // Rotate180
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate180_PreservesWidth()
    {
        var img = CreateGray(5, 4, 100);
        var rotated = img.Rotate180();
        Assert.Equal(5, rotated.Width);
    }

    [Fact]
    public void Rotate180_PreservesHeight()
    {
        var img = CreateGray(5, 4, 100);
        var rotated = img.Rotate180();
        Assert.Equal(4, rotated.Height);
    }

    [Fact]
    public void Rotate180_Twice_SameDimensions()
    {
        var img = CreateGray(5, 4, 100);
        var result = img.Rotate180().Rotate180();
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    [Fact]
    public void Rotate180_PixelCountPreserved()
    {
        var img = CreateGray(5, 4, 100);
        var rotated = img.Rotate180();
        Assert.Equal(img.Width * img.Height, rotated.Width * rotated.Height);
    }

    // -------------------------------------------------------------------------
    // MergeHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeHorizontal_DoublesWidth()
    {
        var img = CreateGray(4, 4, 128);
        var merged = img.MergeHorizontal(img);
        Assert.Equal(8, merged.Width);
    }

    [Fact]
    public void MergeHorizontal_HeightIsUnchanged()
    {
        var img = CreateGray(4, 4, 128);
        var merged = img.MergeHorizontal(img);
        Assert.Equal(4, merged.Height);
    }

    [Fact]
    public void MergeHorizontal_DifferentImages()
    {
        var img1 = CreateGray(3, 4, 100);
        var img2 = CreateGray(5, 4, 200);
        var merged = img1.MergeHorizontal(img2);
        Assert.Equal(8, merged.Width);
        Assert.Equal(4, merged.Height);
    }

    // -------------------------------------------------------------------------
    // MergeVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeVertical_DoublesHeight()
    {
        var img = CreateGray(4, 4, 128);
        var merged = img.MergeVertical(img);
        Assert.Equal(8, merged.Height);
    }

    [Fact]
    public void MergeVertical_WidthIsUnchanged()
    {
        var img = CreateGray(4, 4, 128);
        var merged = img.MergeVertical(img);
        Assert.Equal(4, merged.Width);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Rotate90->MergeHorizontal->MergeVertical pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_RotateMergePipeline()
    {
        var img = CreateGray(4, 6, 150);
        Assert.Equal(4, img.Width);
        Assert.Equal(6, img.Height);

        // Rotate 90
        var rot90 = img.Rotate90Cw();
        Assert.Equal(6, rot90.Width);
        Assert.Equal(4, rot90.Height);

        // Merge with rotated version horizontally
        // Both must have same height for MergeHorizontal
        var mergedH = img.Rotate180().MergeHorizontal(img.Rotate180());
        Assert.Equal(img.Width * 2, mergedH.Width);
        Assert.Equal(img.Height, mergedH.Height);

        // Merge vertically
        var mergedV = img.MergeVertical(img);
        Assert.Equal(img.Width, mergedV.Width);
        Assert.Equal(img.Height * 2, mergedV.Height);

        // Rotate 180 twice = same
        var rt180_twice = img.Rotate180().Rotate180();
        Assert.Equal(img.Width, rt180_twice.Width);
    }
}
