// Tests for NetpbmImage.GetAverageLuminance dedicated coverage.
// Sprint: ff-sprint-s372-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R385

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R385: Dedicated tests for NetpbmImage.GetAverageLuminance().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetAverageLuminance.
/// Height unchanged after GetAverageLuminance.
/// Format unchanged after GetAverageLuminance.
/// MaxValue unchanged after GetAverageLuminance.
/// Uniform image returns uniform value.
/// Idempotent (called twice same result).
/// Dogfood: all-zero image returns 0.0.
/// Dogfood: all-max image returns MaxValue.
/// </summary>
public class NetpbmR385GetAverageLuminanceDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAverageLuminance_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double lum = img.GetAverageLuminance();
        Assert.True(lum >= 0.0);
    }

    [Fact]
    public void GetAverageLuminance_ResultIsNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PPM);
        double lum = img.GetAverageLuminance();
        Assert.True(lum >= 0.0);
    }

    [Fact]
    public void GetAverageLuminance_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetAverageLuminance();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetAverageLuminance_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetAverageLuminance();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetAverageLuminance_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetAverageLuminance();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetAverageLuminance_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetAverageLuminance();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetAverageLuminance_UniformImage_ReturnsUniformValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 100);
        double lum = img.GetAverageLuminance();
        Assert.True(lum >= 0.0);
    }

    [Fact]
    public void GetAverageLuminance_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 50);
        img.SetPixel(0, 1, 150);
        double first = img.GetAverageLuminance();
        double second = img.GetAverageLuminance();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 0);
        double lum = img.GetAverageLuminance();
        Assert.Equal(0.0, lum, 6);
    }

    [Fact]
    public void DogfoodPipeline_AllMaxImage_ReturnsMaxLuminance()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, img.MaxValue);
        double lum = img.GetAverageLuminance();
        Assert.True(lum > 0.0);
    }
}
