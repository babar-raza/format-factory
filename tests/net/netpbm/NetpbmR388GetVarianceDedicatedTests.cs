// Tests for NetpbmImage.GetVariance dedicated coverage.
// Sprint: ff-sprint-s375-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R388

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R388: Dedicated tests for NetpbmImage.GetVariance().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetVariance.
/// Height unchanged after GetVariance.
/// Format unchanged after GetVariance.
/// MaxValue unchanged after GetVariance.
/// Uniform image returns 0.0.
/// Idempotent (called twice same result).
/// Dogfood: two-value image returns positive variance.
/// Dogfood: gradient image returns positive variance.
/// </summary>
public class NetpbmR388GetVarianceDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetVariance_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double variance = img.GetVariance();
        Assert.True(variance >= 0.0);
    }

    [Fact]
    public void GetVariance_ResultIsNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PPM);
        double variance = img.GetVariance();
        Assert.True(variance >= 0.0);
    }

    [Fact]
    public void GetVariance_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetVariance();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetVariance_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetVariance();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetVariance_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetVariance();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetVariance_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetVariance();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetVariance_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 128);
        double variance = img.GetVariance();
        Assert.Equal(0.0, variance, 6);
    }

    [Fact]
    public void GetVariance_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 0);
        img.SetPixel(0, 1, 255);
        double first = img.GetVariance();
        double second = img.GetVariance();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoValueImage_ReturnsPositiveVariance()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? 0 : 255);
        double variance = img.GetVariance();
        Assert.True(variance > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_GradientImage_ReturnsPositiveVariance()
    {
        var img = NetpbmImage.CreateNew(8, 1, NetpbmFormat.PGM);
        for (int c = 0; c < img.Width; c++)
            img.SetPixel(0, c, c * 32);
        double variance = img.GetVariance();
        Assert.True(variance > 0.0);
    }
}
