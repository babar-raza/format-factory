// Tests for NetpbmImage.CopyRegion, Resize, Crop deep.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R162

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R162: Tests for NetpbmImage.CopyRegion, Resize, Crop.
/// CopyRegion(source, srcTop, srcLeft, dstTop, dstLeft, h, w): copies region from source.
/// Resize(newWidth, newHeight): scales image to new dimensions.
/// Crop(top, left, h, w): extracts sub-region.
/// Covers: CopyRegion pixels from source; CopyRegion does not affect outside region;
/// CopyRegion preserves dimensions; Resize produces new dimensions;
/// Resize preserves format; Resize to smaller; Resize to larger;
/// Crop produces correct dimensions; Crop top-left preserves corner pixels;
/// Crop produces independent image; Crop/Resize combined pipeline;
/// dogfood Create->FillRegion->CopyRegion->Resize->Crop pipeline.
/// </summary>
public class NetpbmR162CopyRegionAndResizeTests
{
    private static NetpbmImage MakePgm(int w, int h, byte fill = 0) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM_P2, fill);

    // -------------------------------------------------------------------------
    // CopyRegion
    // -------------------------------------------------------------------------

    [Fact]
    public void CopyRegion_CopiesPixelsFromSource()
    {
        var source = MakePgm(6, 6, 200);
        var dest = MakePgm(6, 6, 0);
        dest.CopyRegion(source, srcTop: 0, srcLeft: 0, dstTop: 1, dstLeft: 1, regionHeight: 2, regionWidth: 2);
        Assert.Equal(200, dest.GetPixel(1, 1));
        Assert.Equal(200, dest.GetPixel(2, 2));
    }

    [Fact]
    public void CopyRegion_DoesNotAffectOutsideRegion()
    {
        var source = MakePgm(6, 6, 200);
        var dest = MakePgm(6, 6, 50);
        dest.CopyRegion(source, 0, 0, 1, 1, 2, 2);
        // Outside the copy target: should be 50
        Assert.Equal(50, dest.GetPixel(0, 0));
        Assert.Equal(50, dest.GetPixel(5, 5));
    }

    [Fact]
    public void CopyRegion_PreservesDimensions()
    {
        var source = MakePgm(4, 4, 100);
        var dest = MakePgm(8, 8, 0);
        dest.CopyRegion(source, 0, 0, 0, 0, 4, 4);
        Assert.Equal(8, dest.Width);
        Assert.Equal(8, dest.Height);
    }

    [Fact]
    public void CopyRegion_FullCopy_AllPixelsMatch()
    {
        var source = MakePgm(4, 4, 150);
        var dest = MakePgm(4, 4, 0);
        dest.CopyRegion(source, 0, 0, 0, 0, 4, 4);
        Assert.All(dest.Pixels, p => Assert.Equal(150, p));
    }

    // -------------------------------------------------------------------------
    // Resize
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_ProducesNewDimensions()
    {
        var img = MakePgm(4, 4, 128);
        var resized = img.Resize(8, 8);
        Assert.Equal(8, resized.Width);
        Assert.Equal(8, resized.Height);
    }

    [Fact]
    public void Resize_ToSmaller_CorrectDimensions()
    {
        var img = MakePgm(8, 8, 100);
        var resized = img.Resize(4, 4);
        Assert.Equal(4, resized.Width);
        Assert.Equal(4, resized.Height);
    }

    [Fact]
    public void Resize_PreservesFormat()
    {
        var img = MakePgm(4, 4, 100);
        var resized = img.Resize(6, 6);
        Assert.Equal(NetpbmFormat.PGM_P2, resized.Format);
    }

    [Fact]
    public void Resize_PixelCountMatchesDimensions()
    {
        var img = MakePgm(4, 4, 100);
        var resized = img.Resize(5, 3);
        Assert.Equal(5 * 3, resized.Pixels.Length);
    }

    // -------------------------------------------------------------------------
    // Crop
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_ProducesCorrectDimensions()
    {
        var img = MakePgm(8, 8, 100);
        var cropped = img.Crop(0, 0, 4, 4);
        Assert.Equal(4, cropped.Width);
        Assert.Equal(4, cropped.Height);
    }

    [Fact]
    public void Crop_PreservesTopLeftPixel()
    {
        var img = MakePgm(8, 8, 0);
        img.SetPixel(2, 2, 200);
        var cropped = img.Crop(2, 2, 4, 4);
        Assert.Equal(200, cropped.GetPixel(0, 0));
    }

    [Fact]
    public void Crop_IsIndependentFromOriginal()
    {
        var img = MakePgm(8, 8, 100);
        var cropped = img.Crop(0, 0, 4, 4);
        cropped.SetPixel(0, 0, 255);
        Assert.Equal(100, img.GetPixel(0, 0));
    }

    [Fact]
    public void Crop_PreservesFormat()
    {
        var img = MakePgm(6, 6, 50);
        var cropped = img.Crop(1, 1, 3, 3);
        Assert.Equal(NetpbmFormat.PGM_P2, cropped.Format);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->FillRegion->CopyRegion->Resize->Crop
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FillCopyResizeCrop_Pipeline()
    {
        var base_ = MakePgm(10, 10, 0);
        base_.FillRegion(2, 2, 4, 4, 200);

        // CopyRegion to a new canvas
        var dest = MakePgm(10, 10, 50);
        dest.CopyRegion(base_, srcTop: 2, srcLeft: 2, dstTop: 0, dstLeft: 0, regionHeight: 4, regionWidth: 4);
        Assert.Equal(200, dest.GetPixel(0, 0));

        // Resize up
        var resized = dest.Resize(20, 20);
        Assert.Equal(20, resized.Width);
        Assert.Equal(20, resized.Height);
        Assert.Equal(NetpbmFormat.PGM_P2, resized.Format);

        // Crop from resized
        var cropped = resized.Crop(0, 0, 10, 10);
        Assert.Equal(10, cropped.Width);
        Assert.Equal(10, cropped.Height);
        Assert.Equal(100, cropped.Pixels.Length);
    }
}
