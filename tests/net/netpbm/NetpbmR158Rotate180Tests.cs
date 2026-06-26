// Tests for NetpbmImage.Rotate180 dedicated coverage.
// Sprint: ff-sprint-s162-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R158

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R158: Dedicated tests for NetpbmImage.Rotate180().
/// Rotate180 returns a NEW image rotated 180°. Dimensions are unchanged.
/// The pixel buffer is reversed: pixel[i] maps to pixel[len-1-i] in the result.
/// Covers: output Width equals source Width; output Height equals source Height;
/// format preserved; original unchanged after rotate;
/// top-left pixel maps to bottom-right; bottom-right maps to top-left;
/// single pixel image returns same pixel; double rotate restores pixels;
/// dogfood Create->SetPixel->Rotate180->GetPixel pipeline;
/// dogfood multiple set pixels reversed correctly.
/// </summary>
public class NetpbmR158Rotate180Tests
{
    // -------------------------------------------------------------------------
    // Dimension tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate180_OutputWidth_EqualsSourceWidth()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = img.Rotate180();
        Assert.Equal(5, result.Width);
    }

    [Fact]
    public void Rotate180_OutputHeight_EqualsSourceHeight()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = img.Rotate180();
        Assert.Equal(3, result.Height);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate180_FormatPreserved()
    {
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        var result = img.Rotate180();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Rotate180_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        _ = img.Rotate180();
        Assert.Equal(4, img.Width);
        Assert.Equal(3, img.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel transform tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate180_TopLeftPixel_MapsToBottomRight()
    {
        // 4x3 image: pixel(0,0) → pixel(2,3)
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5); // 4w 3h
        img.SetPixel(0, 0, 123);
        var result = img.Rotate180();
        Assert.Equal(123, result.GetPixel(2, 3)); // row=H-1-0=2, col=W-1-0=3
    }

    [Fact]
    public void Rotate180_BottomRightPixel_MapsToTopLeft()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(2, 3, 77); // bottom-right
        var result = img.Rotate180();
        Assert.Equal(77, result.GetPixel(0, 0)); // maps to top-left
    }

    [Fact]
    public void Rotate180_SinglePixelImage_ReturnsSamePixel()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200);
        var result = img.Rotate180();
        Assert.Equal(200, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DoubleRotate_RestoresPixels()
    {
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 1, 55);
        var r1 = img.Rotate180();
        var r2 = r1.Rotate180();
        Assert.Equal(55, r2.GetPixel(0, 1));
    }

    [Fact]
    public void DogfoodPipeline_CreateSetPixelRotate180_GetPixel()
    {
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5); // 3w 2h
        img.SetPixel(0, 2, 99); // row=0, col=2 (top-right)
        var result = img.Rotate180();
        // maps to row=H-1-0=1, col=W-1-2=0 (bottom-left)
        Assert.Equal(99, result.GetPixel(1, 0));
    }

    [Fact]
    public void DogfoodPipeline_MultiplePixels_AllReversedCorrectly()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 10); // top-left → bottom-right after 180
        img.SetPixel(0, 1, 20); // top-right → bottom-left after 180
        var result = img.Rotate180();
        Assert.Equal(10, result.GetPixel(1, 1));
        Assert.Equal(20, result.GetPixel(1, 0));
    }
}
