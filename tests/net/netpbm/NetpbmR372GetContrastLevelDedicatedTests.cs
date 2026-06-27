// Tests for NetpbmImage.GetContrastLevel dedicated coverage.
// Sprint: ff-sprint-s359-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R372

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R372: Dedicated tests for NetpbmImage.GetContrastLevel().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetContrastLevel.
/// Height unchanged after GetContrastLevel.
/// Format unchanged after GetContrastLevel.
/// MaxValue unchanged after GetContrastLevel.
/// Uniform image returns 0.0.
/// Idempotent (called twice same result).
/// Dogfood: high-contrast image returns positive value.
/// Dogfood: gradient image returns positive value.
/// </summary>
public class NetpbmR372GetContrastLevelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContrastLevel_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double level = img.GetContrastLevel();
        Assert.True(level >= 0.0);
    }

    [Fact]
    public void GetContrastLevel_ResultIsNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PPM);
        double level = img.GetContrastLevel();
        Assert.True(level >= 0.0);
    }

    [Fact]
    public void GetContrastLevel_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetContrastLevel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetContrastLevel_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetContrastLevel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetContrastLevel_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetContrastLevel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetContrastLevel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetContrastLevel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetContrastLevel_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 128);
        double level = img.GetContrastLevel();
        Assert.Equal(0.0, level, 6);
    }

    [Fact]
    public void GetContrastLevel_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 0);
        img.SetPixel(0, 1, 255);
        double first = img.GetContrastLevel();
        double second = img.GetContrastLevel();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HighContrastImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? 0 : 255);
        double level = img.GetContrastLevel();
        Assert.True(level > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_GradientImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(8, 1, NetpbmFormat.PGM);
        for (int c = 0; c < img.Width; c++)
            img.SetPixel(0, c, c * 32);
        double level = img.GetContrastLevel();
        Assert.True(level > 0.0);
    }
}
