// Tests for NetpbmImage.Resize dedicated coverage.
// Sprint: ff-sprint-s151-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R147

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R147: Dedicated tests for NetpbmImage.Resize(int newWidth, int newHeight).
/// Resize returns a new image scaled to the specified dimensions using nearest-neighbor.
/// Throws ArgumentOutOfRangeException if newWidth or newHeight is zero or negative.
/// Covers: zero width throws; zero height throws; negative width throws; negative height throws;
/// output dimensions match requested size; format preserved; original unchanged after resize;
/// resize to same size preserves dimensions; dogfood Create->SetPixel->Resize->GetPixel pipeline;
/// dogfood Resize->Resize double-scale returns larger dimensions.
/// </summary>
public class NetpbmR147ResizeTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_ZeroWidth_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Resize(0, 4));
    }

    [Fact]
    public void Resize_ZeroHeight_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Resize(4, 0));
    }

    [Fact]
    public void Resize_NegativeWidth_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Resize(-1, 4));
    }

    [Fact]
    public void Resize_NegativeHeight_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Resize(4, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_OutputDimensionsMatchRequested()
    {
        var img = NetpbmImage.Create(4, 6, NetpbmFormat.PGM_P5);
        var resized = img.Resize(8, 12);
        Assert.Equal(8, resized.Width);
        Assert.Equal(12, resized.Height);
    }

    [Fact]
    public void Resize_PreservesFormat()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var resized = img.Resize(8, 8);
        Assert.Equal(NetpbmFormat.PGM_P5, resized.Format);
    }

    [Fact]
    public void Resize_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 55);
        _ = img.Resize(8, 8);
        Assert.Equal(4, img.Width);
        Assert.Equal(4, img.Height);
        Assert.Equal(55, img.GetPixel(0, 0));
    }

    [Fact]
    public void Resize_SameSize_PreservesDimensions()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var resized = img.Resize(5, 3);
        Assert.Equal(5, resized.Width);
        Assert.Equal(3, resized.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Create_SetPixel_Resize_GetPixel()
    {
        // Fill entire 2x2 image with value 200
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200);
        img.SetPixel(0, 1, 200);
        img.SetPixel(1, 0, 200);
        img.SetPixel(1, 1, 200);

        // Scale up 2x — all pixels should map to 200 via nearest-neighbor
        var resized = img.Resize(4, 4);
        Assert.Equal(200, resized.GetPixel(0, 0));
        Assert.Equal(200, resized.GetPixel(3, 3));
    }

    [Fact]
    public void DogfoodPipeline_Resize_Resize_DoubleScale_LargerDimensions()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var first = img.Resize(4, 4);
        var second = first.Resize(8, 8);
        Assert.Equal(8, second.Width);
        Assert.Equal(8, second.Height);
    }
}
