// Tests for NetpbmImage.GetStandardDeviation dedicated coverage.
// Sprint: ff-sprint-s374-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R387

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R387: Dedicated tests for NetpbmImage.GetStandardDeviation().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetStandardDeviation.
/// Height unchanged after GetStandardDeviation.
/// Format unchanged after GetStandardDeviation.
/// MaxValue unchanged after GetStandardDeviation.
/// Uniform image returns 0.0.
/// Idempotent (called twice same result).
/// Dogfood: two-value image returns positive stddev.
/// Dogfood: gradient image returns positive stddev.
/// </summary>
public class NetpbmR387GetStandardDeviationDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStandardDeviation_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double sd = img.GetStandardDeviation();
        Assert.True(sd >= 0.0);
    }

    [Fact]
    public void GetStandardDeviation_ResultIsNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PPM);
        double sd = img.GetStandardDeviation();
        Assert.True(sd >= 0.0);
    }

    [Fact]
    public void GetStandardDeviation_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetStandardDeviation_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetStandardDeviation_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetStandardDeviation_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetStandardDeviation_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 100);
        double sd = img.GetStandardDeviation();
        Assert.Equal(0.0, sd, 6);
    }

    [Fact]
    public void GetStandardDeviation_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 0);
        img.SetPixel(0, 1, 255);
        double first = img.GetStandardDeviation();
        double second = img.GetStandardDeviation();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoValueImage_ReturnsPositiveStdDev()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? 0 : 255);
        double sd = img.GetStandardDeviation();
        Assert.True(sd > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_GradientImage_ReturnsPositiveStdDev()
    {
        var img = NetpbmImage.CreateNew(8, 1, NetpbmFormat.PGM);
        for (int c = 0; c < img.Width; c++)
            img.SetPixel(0, c, c * 32);
        double sd = img.GetStandardDeviation();
        Assert.True(sd > 0.0);
    }
}
