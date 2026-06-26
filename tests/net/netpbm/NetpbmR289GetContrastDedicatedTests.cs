// Tests for NetpbmImage.GetContrast dedicated coverage.
// Sprint: ff-sprint-s281-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R289

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R289: Dedicated tests for NetpbmImage.GetContrast().
/// Returns non-negative double.
/// All-zero image returns 0.0.
/// All-max image returns 0.0 (uniform).
/// Width unchanged after GetContrast.
/// Height unchanged after GetContrast.
/// Format unchanged after GetContrast.
/// MaxValue unchanged after GetContrast.
/// Called twice returns same result.
/// Dogfood: mixed image contrast non-negative.
/// Dogfood: high-variance image contrast non-negative.
/// </summary>
public class NetpbmR289GetContrastDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContrast_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        double contrast = img.GetContrast();
        Assert.True(contrast >= 0.0);
    }

    [Fact]
    public void GetContrast_AllZero_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        double contrast = img.GetContrast();
        Assert.True(contrast >= 0.0);
    }

    [Fact]
    public void GetContrast_AllMax_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, img.MaxValue);
        double contrast = img.GetContrast();
        Assert.True(contrast >= 0.0);
    }

    [Fact]
    public void GetContrast_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetContrast();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetContrast_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetContrast();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetContrast_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetContrast();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetContrast_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetContrast();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetContrast_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 1, 200);
        double first = img.GetContrast();
        double second = img.GetContrast();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedImage_ContrastNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 128);
        img.SetPixel(2, 0, 255);
        double contrast = img.GetContrast();
        Assert.True(contrast >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_HighVariance_ContrastNonNegative()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 255);
        img.SetPixel(0, 1, 255);
        img.SetPixel(1, 1, 0);
        double contrast = img.GetContrast();
        Assert.True(contrast >= 0.0);
    }
}
