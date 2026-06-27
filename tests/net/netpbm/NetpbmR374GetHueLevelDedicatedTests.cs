// Tests for NetpbmImage.GetHueLevel dedicated coverage.
// Sprint: ff-sprint-s361-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R374

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R374: Dedicated tests for NetpbmImage.GetHueLevel().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetHueLevel.
/// Height unchanged after GetHueLevel.
/// Format unchanged after GetHueLevel.
/// MaxValue unchanged after GetHueLevel.
/// Idempotent (called twice same result).
/// Uniform image result is non-negative.
/// Dogfood: PPM image returns non-negative.
/// Dogfood: PGM image returns non-negative.
/// </summary>
public class NetpbmR374GetHueLevelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHueLevel_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double level = img.GetHueLevel();
        Assert.True(level >= 0.0);
    }

    [Fact]
    public void GetHueLevel_ResultIsNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM);
        double level = img.GetHueLevel();
        Assert.True(level >= 0.0);
    }

    [Fact]
    public void GetHueLevel_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetHueLevel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHueLevel_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PPM);
        int before = img.Height;
        _ = img.GetHueLevel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHueLevel_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetHueLevel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHueLevel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetHueLevel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHueLevel_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        img.SetPixel(0, 0, 180);
        img.SetPixel(1, 1, 90);
        double first = img.GetHueLevel();
        double second = img.GetHueLevel();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetHueLevel_UniformImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 75);
        double level = img.GetHueLevel();
        Assert.True(level >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PpmImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r * 50 + c * 30) % 256);
        double level = img.GetHueLevel();
        Assert.True(level >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, r * 40 + c * 25);
        double level = img.GetHueLevel();
        Assert.True(level >= 0.0);
    }
}
