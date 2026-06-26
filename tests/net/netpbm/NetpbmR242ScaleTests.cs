// Tests for NetpbmImage.Scale dedicated coverage.
// Sprint: ff-sprint-s235-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R242

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R242: Dedicated tests for NetpbmImage.Scale(factor).
/// Valid call returns non-null.
/// Returns different object (not same reference).
/// Format preserved after scale.
/// MaxValue preserved after scale.
/// Scale 2x doubles dimensions.
/// Scale 0.5x halves dimensions.
/// Original image dimensions unchanged after scale.
/// Pixel count changes proportionally with scale.
/// Scale with factor 1.0 returns same dimensions.
/// Dogfood: scale up and verify dimensions.
/// </summary>
public class NetpbmR242ScaleTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Scale_ValidCall_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Scale(2.0f);
        Assert.NotNull(result);
    }

    [Fact]
    public void Scale_ReturnsDifferentObject()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Scale(2.0f);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Scale_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Scale(2.0f);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Scale_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var result = img.Scale(2.0f);
        Assert.Equal(200, result.MaxValue);
    }

    [Fact]
    public void Scale_DoubleSize_DimensionsDoubled()
    {
        var img = NetpbmImage.Create(4, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Scale(2.0f);
        Assert.Equal(8, result.Width);
        Assert.Equal(12, result.Height);
    }

    [Fact]
    public void Scale_HalfSize_DimensionsHalved()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Scale(0.5f);
        Assert.Equal(4, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Scale_OriginalDimensionsUnchanged()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        _ = img.Scale(2.0f);
        Assert.Equal(6, img.Width);
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void Scale_Factor1_SameDimensions()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Scale(1.0f);
        Assert.Equal(5, result.Width);
        Assert.Equal(5, result.Height);
    }

    [Fact]
    public void Scale_PixelCountChangesProportionally()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Scale(2.0f);
        Assert.Equal(8 * 8, result.GetPixelCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ScaleUp_VerifyDimensions()
    {
        var img = NetpbmImage.Create(3, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 128);
        var scaled = img.Scale(2.0f);
        Assert.Equal(6, scaled.Width);
        Assert.Equal(10, scaled.Height);
        Assert.Equal(NetpbmFormat.PGM_P5, scaled.Format);
        Assert.Equal(255, scaled.MaxValue);
    }
}
