// Tests for NetpbmImage.GetMinPixelValue and GetMaxPixelValue dedicated coverage.
// Sprint: ff-sprint-s222-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R229

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R229: Dedicated tests for NetpbmImage.GetMinPixelValue() and GetMaxPixelValue().
/// GetMinPixelValue returns non-negative value.
/// GetMaxPixelValue returns non-negative value.
/// Format preserved after calls.
/// MaxValue preserved after calls.
/// Dimensions preserved after calls.
/// Uniform zero image: min=max=0.
/// Set one pixel: min=0, max=pixel value.
/// GetMin <= GetMax always.
/// Called twice: same result.
/// Dogfood: set spread of pixels, min=0 max=high.
/// </summary>
public class NetpbmR229GetMinMaxPixelValueTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMinPixelValue_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var min = img.GetMinPixelValue();
        Assert.True(min >= 0);
    }

    [Fact]
    public void GetMaxPixelValue_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var max = img.GetMaxPixelValue();
        Assert.True(max >= 0);
    }

    [Fact]
    public void GetMinMax_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.GetMinPixelValue();
        img.GetMaxPixelValue();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void GetMinMax_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 100);
        img.GetMinPixelValue();
        img.GetMaxPixelValue();
        Assert.Equal(100, img.MaxValue);
    }

    [Fact]
    public void GetMinMax_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(5, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        img.GetMinPixelValue();
        img.GetMaxPixelValue();
        Assert.Equal(5, img.Width);
        Assert.Equal(6, img.Height);
    }

    [Fact]
    public void GetMinMax_UniformZeroImage_BothZero()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.Equal(0, img.GetMinPixelValue());
        Assert.Equal(0, img.GetMaxPixelValue());
    }

    [Fact]
    public void GetMinMax_SetOnePixel_MinZeroMaxPixel()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(2, 2, 150);
        Assert.Equal(0, img.GetMinPixelValue());
        Assert.Equal(150, img.GetMaxPixelValue());
    }

    [Fact]
    public void GetMin_LessThanOrEqualToMax()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 200);
        Assert.True(img.GetMinPixelValue() <= img.GetMaxPixelValue());
    }

    [Fact]
    public void GetMinMax_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 7);
        img.SetPixel(1, 1, 5);
        Assert.Equal(img.GetMinPixelValue(), img.GetMinPixelValue());
        Assert.Equal(img.GetMaxPixelValue(), img.GetMaxPixelValue());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SpreadPixels_MinZeroMaxHigh()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 15);
        img.SetPixel(0, 0, 15);
        // Other pixels are 0 by default
        Assert.Equal(0, img.GetMinPixelValue());
        Assert.Equal(15, img.GetMaxPixelValue());
    }
}
