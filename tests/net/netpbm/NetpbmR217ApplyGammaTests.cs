// Tests for NetpbmImage.ApplyGamma dedicated coverage.
// Sprint: ff-sprint-s211-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R217

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R217: Dedicated tests for NetpbmImage.ApplyGamma(double gamma).
/// Non-positive gamma → ArgumentOutOfRangeException (or ArgumentException).
/// PGM: returns new image.
/// PPM: returns new image.
/// Format preserved.
/// MaxValue preserved.
/// Dimensions preserved.
/// All output pixels in valid range.
/// Original unchanged after apply gamma.
/// Gamma=1.0: pixels unchanged (identity).
/// Dogfood: gamma chain format/dims preserved.
/// </summary>
public class NetpbmR217ApplyGammaTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_ZeroGamma_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.ApplyGamma(0.0));
    }

    [Fact]
    public void ApplyGamma_NegativeGamma_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.ApplyGamma(-1.0));
    }

    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_PGM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.ApplyGamma(1.5);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void ApplyGamma_PPM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6);
        var result = img.ApplyGamma(1.5);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void ApplyGamma_FormatPreserved()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = img.ApplyGamma(2.0);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void ApplyGamma_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.ApplyGamma(1.5);
        Assert.Equal(255, result.MaxValue);
    }

    [Fact]
    public void ApplyGamma_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(6, 8, NetpbmFormat.PGM_P5);
        var result = img.ApplyGamma(0.5);
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel value tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_AllPixelsInValidRange()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                img.SetPixel(x, y, (x * 50 + y * 10) % 256);
        var result = img.ApplyGamma(2.2);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                Assert.InRange(result.GetPixel(x, y), 0, 255);
    }

    [Fact]
    public void ApplyGamma_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 150);
        var _ = img.ApplyGamma(1.5);
        Assert.Equal(150, img.GetPixel(1, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GammaOne_PixelUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 128);
        var result = img.ApplyGamma(1.0);
        Assert.Equal(128, result.GetPixel(1, 1));
    }

    [Fact]
    public void DogfoodPipeline_FormatDimsChained()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.ApplyGamma(2.2);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(5, result.Width);
        Assert.Equal(3, result.Height);
        Assert.Equal(255, result.MaxValue);
    }
}
