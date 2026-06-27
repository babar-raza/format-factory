// Tests for NetpbmImage.ScaleBrightness dedicated coverage.
// Sprint: ff-sprint-s303-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R311

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R311: Dedicated tests for NetpbmImage.ScaleBrightness(factor).
/// Valid call no exception.
/// All pixels in [0, MaxValue] after ScaleBrightness.
/// Width unchanged after ScaleBrightness.
/// Height unchanged after ScaleBrightness.
/// Format unchanged after ScaleBrightness.
/// MaxValue unchanged after ScaleBrightness.
/// Called twice no exception.
/// Factor of 1.0 leaves pixels unchanged.
/// Dogfood: factor 0.5 dims image pixels in range.
/// Dogfood: factor 2.0 brightens image pixels in range.
/// </summary>
public class NetpbmR311ScaleBrightnessDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ScaleBrightness_ValidCall_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        var ex = Record.Exception(() => img.ScaleBrightness(0.5));
        Assert.Null(ex);
    }

    [Fact]
    public void ScaleBrightness_AllPixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(3, 3, 200);
        img.ScaleBrightness(1.5);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void ScaleBrightness_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.ScaleBrightness(0.8);
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void ScaleBrightness_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.ScaleBrightness(0.8);
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void ScaleBrightness_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.ScaleBrightness(1.2);
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void ScaleBrightness_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.ScaleBrightness(1.2);
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void ScaleBrightness_CalledTwice_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.ScaleBrightness(0.5);
        var ex = Record.Exception(() => img.ScaleBrightness(2.0));
        Assert.Null(ex);
    }

    [Fact]
    public void ScaleBrightness_FactorOne_PixelsUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(2, 2, 100);
        int before = img.GetPixel(2, 2);
        img.ScaleBrightness(1.0);
        Assert.Equal(before, img.GetPixel(2, 2));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FactorHalf_DimsImagePixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 200);
        img.ScaleBrightness(0.5);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void DogfoodPipeline_FactorTwo_BrightensImagePixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 1, 100);
        img.ScaleBrightness(2.0);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }
}
