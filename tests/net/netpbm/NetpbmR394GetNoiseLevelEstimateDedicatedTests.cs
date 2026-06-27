// Tests for NetpbmImage.GetNoiseLevelEstimate dedicated coverage.
// Sprint: ff-sprint-s381-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R394

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R394: Dedicated tests for NetpbmImage.GetNoiseLevelEstimate().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetNoiseLevelEstimate.
/// Height unchanged after GetNoiseLevelEstimate.
/// Format unchanged after GetNoiseLevelEstimate.
/// MaxValue unchanged after GetNoiseLevelEstimate.
/// Uniform image returns 0.0 (no noise).
/// Idempotent (called twice same result).
/// Dogfood: checkerboard image returns positive noise estimate.
/// Dogfood: gradient image returns non-negative.
/// </summary>
public class NetpbmR394GetNoiseLevelEstimateDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNoiseLevelEstimate_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double noise = img.GetNoiseLevelEstimate();
        Assert.True(noise >= 0.0);
    }

    [Fact]
    public void GetNoiseLevelEstimate_ResultIsNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PPM);
        double noise = img.GetNoiseLevelEstimate();
        Assert.True(noise >= 0.0);
    }

    [Fact]
    public void GetNoiseLevelEstimate_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetNoiseLevelEstimate();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetNoiseLevelEstimate_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetNoiseLevelEstimate();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetNoiseLevelEstimate_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetNoiseLevelEstimate();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetNoiseLevelEstimate_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetNoiseLevelEstimate();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetNoiseLevelEstimate_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 100);
        double noise = img.GetNoiseLevelEstimate();
        Assert.Equal(0.0, noise, 6);
    }

    [Fact]
    public void GetNoiseLevelEstimate_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 0);
        img.SetPixel(0, 1, 255);
        double first = img.GetNoiseLevelEstimate();
        double second = img.GetNoiseLevelEstimate();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CheckerboardImage_ReturnsPositiveNoise()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? 0 : 255);
        double noise = img.GetNoiseLevelEstimate();
        Assert.True(noise > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_GradientImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 1, NetpbmFormat.PGM);
        for (int c = 0; c < img.Width; c++)
            img.SetPixel(0, c, c * 32);
        double noise = img.GetNoiseLevelEstimate();
        Assert.True(noise >= 0.0);
    }
}
