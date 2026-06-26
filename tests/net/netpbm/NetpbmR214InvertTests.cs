// Tests for NetpbmImage.Invert dedicated coverage.
// Sprint: ff-sprint-s208-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R214

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R214: Dedicated tests for NetpbmImage.Invert().
/// PGM: returns new image (not same reference).
/// PPM: returns new image.
/// Format preserved after invert.
/// MaxValue preserved.
/// Dimensions preserved.
/// Pixel value 0 inverted to MaxValue.
/// Pixel value MaxValue inverted to 0.
/// All pixels in valid range after invert.
/// Dogfood: invert twice restores original pixel value.
/// Dogfood: black-and-white invert pipeline.
/// </summary>
public class NetpbmR214InvertTests
{
    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_PGM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Invert();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Invert_PPM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6);
        var result = img.Invert();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Invert_FormatPreserved_PGM()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = img.Invert();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Invert_FormatPreserved_PPM()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        var result = img.Invert();
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void Invert_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Invert();
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    [Fact]
    public void Invert_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(7, 5, NetpbmFormat.PGM_P5);
        var result = img.Invert();
        Assert.Equal(7, result.Width);
        Assert.Equal(5, result.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel value tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_ZeroPixel_BecomesMaxValue()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 0);
        var result = img.Invert();
        Assert.Equal(255, result.GetPixel(1, 1));
    }

    [Fact]
    public void Invert_MaxValuePixel_BecomesZero()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 255);
        var result = img.Invert();
        Assert.Equal(0, result.GetPixel(0, 0));
    }

    [Fact]
    public void Invert_AllPixelsInValidRange()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 200);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                img.SetPixel(x, y, (x + y * 5) % 201);
        var result = img.Invert();
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
            {
                int pv = result.GetPixel(x, y);
                Assert.InRange(pv, 0, 200);
            }
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_InvertTwice_RestoresOriginal()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 128);
        img.SetPixel(1, 1, 64);
        img.SetPixel(2, 2, 200);
        var once = img.Invert();
        var twice = once.Invert();
        Assert.Equal(img.GetPixel(0, 0), twice.GetPixel(0, 0));
        Assert.Equal(img.GetPixel(1, 1), twice.GetPixel(1, 1));
        Assert.Equal(img.GetPixel(2, 2), twice.GetPixel(2, 2));
    }

    [Fact]
    public void DogfoodPipeline_BlackAndWhiteInvert_ValuesSwap()
    {
        var img = NetpbmImage.Create(2, 1, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 255);
        var result = img.Invert();
        Assert.Equal(255, result.GetPixel(0, 0));
        Assert.Equal(0, result.GetPixel(1, 0));
    }
}
