// Tests for NetpbmImage.GetNoiseLevelEstimate dedicated coverage.
// Sprint: ff-sprint-s344-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R357

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R357: Dedicated tests for NetpbmImage.GetNoiseLevelEstimate().
/// Valid image ok.
/// Returns non-negative value.
/// Width unchanged after GetNoiseLevelEstimate.
/// Height unchanged after GetNoiseLevelEstimate.
/// Format unchanged after GetNoiseLevelEstimate.
/// MaxValue unchanged after GetNoiseLevelEstimate.
/// All-zero image returns 0.0 noise.
/// Uniform image returns 0.0 noise.
/// Idempotent (called twice same result).
/// Dogfood: random-like high-variance image returns positive noise.
/// </summary>
public class NetpbmR357GetNoiseLevelEstimateDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNoiseLevelEstimate_ValidImage_Ok()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        var ex = Record.Exception(() => img.GetNoiseLevelEstimate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetNoiseLevelEstimate_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        double noise = img.GetNoiseLevelEstimate();
        Assert.True(noise >= 0.0);
    }

    [Fact]
    public void GetNoiseLevelEstimate_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Width;
        _ = img.GetNoiseLevelEstimate();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetNoiseLevelEstimate_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Height;
        _ = img.GetNoiseLevelEstimate();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetNoiseLevelEstimate_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        string before = img.Format;
        _ = img.GetNoiseLevelEstimate();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetNoiseLevelEstimate_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.MaxValue;
        _ = img.GetNoiseLevelEstimate();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetNoiseLevelEstimate_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        double noise = img.GetNoiseLevelEstimate();
        Assert.Equal(0.0, noise, precision: 10);
    }

    [Fact]
    public void GetNoiseLevelEstimate_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        img.FillWithValue(128);
        double noise = img.GetNoiseLevelEstimate();
        Assert.Equal(0.0, noise, precision: 10);
    }

    [Fact]
    public void GetNoiseLevelEstimate_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreatePgm(6, 6, 255);
        img.SetPixel(0, 0, 10);
        img.SetPixel(1, 0, 245);
        double first = img.GetNoiseLevelEstimate();
        double second = img.GetNoiseLevelEstimate();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HighVarianceImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        // Alternating extreme values simulates noise
        for (int x = 0; x < 4; x++)
            for (int y = 0; y < 4; y++)
                img.SetPixel(x, y, (x * 4 + y) % 2 == 0 ? 5 : 250);
        double noise = img.GetNoiseLevelEstimate();
        Assert.True(noise > 0.0);
    }
}
