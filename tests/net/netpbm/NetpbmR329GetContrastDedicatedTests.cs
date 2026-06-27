// Tests for NetpbmImage.GetContrast dedicated coverage.
// Sprint: ff-sprint-s318-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R329

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R329: Dedicated tests for NetpbmImage.GetContrast().
/// Returns non-negative value.
/// Width unchanged after GetContrast.
/// Height unchanged after GetContrast.
/// Format unchanged after GetContrast.
/// MaxValue unchanged after GetContrast.
/// All-zero image returns non-negative contrast.
/// Idempotent (called twice same result class).
/// Uniform image contrast in expected range.
/// Dogfood: gradient image contrast non-negative.
/// Dogfood: high-contrast alternating image contrast non-negative.
/// </summary>
public class NetpbmR329GetContrastDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContrast_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 30 + y * 15) % 256);
        double contrast = img.GetContrast();
        Assert.True(contrast >= 0.0);
    }

    [Fact]
    public void GetContrast_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetContrast();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetContrast_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetContrast();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetContrast_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetContrast();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetContrast_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetContrast();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetContrast_AllZeroImage_NonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        double contrast = img.GetContrast();
        Assert.True(contrast >= 0.0);
    }

    [Fact]
    public void GetContrast_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) * 16 % 256);
        double first = img.GetContrast();
        double second = img.GetContrast();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetContrast_UniformImage_NonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 128);
        double contrast = img.GetContrast();
        Assert.True(contrast >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GradientImage_ContrastNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, x * 32);
        double contrast = img.GetContrast();
        Assert.True(contrast >= 0.0);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_HighContrastImage_ContrastNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) % 2 == 0 ? 0 : 255);
        double contrast = img.GetContrast();
        Assert.True(contrast >= 0.0);
    }
}
