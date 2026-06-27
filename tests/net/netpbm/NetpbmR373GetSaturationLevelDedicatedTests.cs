// Tests for NetpbmImage.GetSaturationLevel dedicated coverage.
// Sprint: ff-sprint-s360-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R373

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R373: Dedicated tests for NetpbmImage.GetSaturationLevel().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetSaturationLevel.
/// Height unchanged after GetSaturationLevel.
/// Format unchanged after GetSaturationLevel.
/// MaxValue unchanged after GetSaturationLevel.
/// Uniform image returns 0.0.
/// Idempotent (called twice same result).
/// Dogfood: color PPM image returns non-negative.
/// Dogfood: grayscale PGM returns non-negative.
/// </summary>
public class NetpbmR373GetSaturationLevelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSaturationLevel_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double level = img.GetSaturationLevel();
        Assert.True(level >= 0.0);
    }

    [Fact]
    public void GetSaturationLevel_ResultIsNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM);
        double level = img.GetSaturationLevel();
        Assert.True(level >= 0.0);
    }

    [Fact]
    public void GetSaturationLevel_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetSaturationLevel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetSaturationLevel_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PPM);
        int before = img.Height;
        _ = img.GetSaturationLevel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetSaturationLevel_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetSaturationLevel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetSaturationLevel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetSaturationLevel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetSaturationLevel_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 100);
        double level = img.GetSaturationLevel();
        Assert.Equal(0.0, level, 6);
    }

    [Fact]
    public void GetSaturationLevel_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        img.SetPixel(0, 0, 200);
        img.SetPixel(0, 1, 50);
        double first = img.GetSaturationLevel();
        double second = img.GetSaturationLevel();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ColorPpmImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r * 64 + c * 16) % 256);
        double level = img.GetSaturationLevel();
        Assert.True(level >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_GrayscalePgmImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, r * 40 + c * 20);
        double level = img.GetSaturationLevel();
        Assert.True(level >= 0.0);
    }
}
