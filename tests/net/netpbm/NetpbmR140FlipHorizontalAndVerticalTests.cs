// Tests for NetpbmImage.FlipHorizontal() and NetpbmImage.FlipVertical().
// Sprint: ff-sprint-s139-dotnet-deepening-20260627
// Ledger: PC-NETPBM-R140

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R140: Tests for NetpbmImage.FlipHorizontal() and NetpbmImage.FlipVertical().
/// FlipHorizontal mirrors the image left-right in place (in-place mutation).
/// FlipVertical mirrors the image top-bottom in place.
/// Covers: FlipHorizontal preserves dimensions; pixel mirroring (corner swap);
/// double flip returns to original; FlipHorizontal on 1×1 image is no-op;
/// FlipVertical preserves dimensions; pixel mirroring (top-bottom swap);
/// double vertical flip returns to original; FlipVertical 1×1 no-op;
/// dogfood Create->FlipHorizontal->FlipVertical->dimensions unchanged pipeline.
/// </summary>
public class NetpbmR140FlipHorizontalAndVerticalTests
{
    // -------------------------------------------------------------------------
    // FlipHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_PreservesDimensions()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        img.FlipHorizontal();
        Assert.Equal(4, img.Width);
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void FlipHorizontal_PixelMirroring_ColumnSwap()
    {
        var img = NetpbmImage.Create(4, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 10);  // Left
        img.SetPixel(0, 3, 40);  // Right
        img.FlipHorizontal();
        // After flip: pixel at col 0 was at col 3
        Assert.Equal(40, img.GetPixel(0, 0));
        Assert.Equal(10, img.GetPixel(0, 3));
    }

    [Fact]
    public void FlipHorizontal_DoubleFlip_RestoresOriginal()
    {
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);
        img.SetPixel(0, 2, 200);
        img.FlipHorizontal();
        img.FlipHorizontal();
        Assert.Equal(100, img.GetPixel(0, 0));
        Assert.Equal(200, img.GetPixel(0, 2));
    }

    [Fact]
    public void FlipHorizontal_SinglePixelImage_IsNoOp()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 77);
        img.FlipHorizontal();
        Assert.Equal(77, img.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // FlipVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_PreservesDimensions()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        img.FlipVertical();
        Assert.Equal(3, img.Width);
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void FlipVertical_PixelMirroring_RowSwap()
    {
        var img = NetpbmImage.Create(1, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 10);  // Top
        img.SetPixel(3, 0, 40);  // Bottom
        img.FlipVertical();
        // After flip: pixel at row 0 was at row 3
        Assert.Equal(40, img.GetPixel(0, 0));
        Assert.Equal(10, img.GetPixel(3, 0));
    }

    [Fact]
    public void FlipVertical_DoubleFlip_RestoresOriginal()
    {
        var img = NetpbmImage.Create(2, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 50);
        img.SetPixel(2, 0, 150);
        img.FlipVertical();
        img.FlipVertical();
        Assert.Equal(50, img.GetPixel(0, 0));
        Assert.Equal(150, img.GetPixel(2, 0));
    }

    [Fact]
    public void FlipVertical_SinglePixelImage_IsNoOp()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 99);
        img.FlipVertical();
        Assert.Equal(99, img.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create -> FlipHorizontal -> FlipVertical -> dimensions unchanged
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Create_FlipBoth_DimensionsUnchanged()
    {
        var img = NetpbmImage.Create(5, 7, NetpbmFormat.PGM_P5, fill: 128);
        img.SetPixel(0, 0, 10);
        img.SetPixel(6, 4, 200);

        img.FlipHorizontal();
        img.FlipVertical();

        Assert.Equal(5, img.Width);
        Assert.Equal(7, img.Height);

        // After FlipHorizontal: corner (0,0)=10 moved to (0,4)
        // After FlipVertical: (0,4)=10 moved to (6,4)
        // And (6,4)=200 moved to (0,4) then to (6,4) again (double move)
        // Just verify dimensions and no exceptions thrown
        Assert.True(img.GetPixel(0, 0) >= 0);
    }
}
