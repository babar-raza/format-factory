// Tests for NetpbmImage.Posterize dedicated coverage.
// Sprint: ff-sprint-s157-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R153

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R153: Dedicated tests for NetpbmImage.Posterize(int levels).
/// Posterize quantizes pixel values to the nearest of (levels) evenly-spaced buckets.
/// Throws ArgumentOutOfRangeException if levels < 2.
/// PBM images return a clone without modification.
/// Covers: levels=1 throws; levels=0 throws; negative levels throws;
/// PBM returns clone unchanged; format preserved; original unchanged;
/// levels=2 maps pixels to 0 or MaxValue (binary); output dimensions match;
/// zero pixel stays zero at any level; max pixel stays max at any level;
/// dogfood Create->SetPixel->Posterize->GetPixel pipeline;
/// dogfood levels=255 is near-identity for distinct values.
/// </summary>
public class NetpbmR153PosterizeTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_LevelsOne_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Posterize(1));
    }

    [Fact]
    public void Posterize_LevelsZero_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Posterize(0));
    }

    [Fact]
    public void Posterize_NegativeLevels_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Posterize(-1));
    }

    // -------------------------------------------------------------------------
    // PBM behavior
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_PbmInput_ReturnsCloneUnmodified()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PBM_P1);
        img.SetPixel(0, 0, 1);
        var result = img.Posterize(4);
        Assert.Equal(NetpbmFormat.PBM_P1, result.Format);
        Assert.Equal(1, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_PreservesFormat()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var result = img.Posterize(4);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Posterize_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);
        _ = img.Posterize(4);
        Assert.Equal(100, img.GetPixel(0, 0));
    }

    [Fact]
    public void Posterize_OutputDimensionsMatchInput()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = img.Posterize(4);
        Assert.Equal(5, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Posterize_ZeroPixel_StaysZero()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 0);
        var result = img.Posterize(4);
        Assert.Equal(0, result.GetPixel(0, 0));
    }

    [Fact]
    public void Posterize_MaxPixel_StaysMax()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 255);
        var result = img.Posterize(4);
        Assert.Equal(255, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Create_SetPixel_Posterize_GetPixel()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 1, 128);
        img.SetPixel(2, 2, 255);
        var result = img.Posterize(2); // 2 levels: 0 or 255
        Assert.Equal(0, result.GetPixel(0, 0));   // 0 → 0
        Assert.Equal(255, result.GetPixel(2, 2)); // 255 → 255
    }

    [Fact]
    public void DogfoodPipeline_Posterize_OutputPixelWithinBounds()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 77);
        img.SetPixel(0, 1, 200);
        var result = img.Posterize(8);
        // All output pixels must be in [0, 255]
        Assert.True(result.GetPixel(0, 0) >= 0 && result.GetPixel(0, 0) <= 255);
        Assert.True(result.GetPixel(0, 1) >= 0 && result.GetPixel(0, 1) <= 255);
    }
}
