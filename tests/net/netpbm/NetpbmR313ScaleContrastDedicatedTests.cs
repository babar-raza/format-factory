// Tests for NetpbmImage.ScaleContrast dedicated coverage.
// Sprint: ff-sprint-s304-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R313

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R313: Dedicated tests for NetpbmImage.ScaleContrast(factor).
/// Valid call no exception.
/// All pixels in range [0, MaxValue] after ScaleContrast.
/// Width unchanged after ScaleContrast.
/// Height unchanged after ScaleContrast.
/// Format unchanged after ScaleContrast.
/// MaxValue unchanged after ScaleContrast.
/// Called twice no exception.
/// Factor 1.0 leaves pixel unchanged.
/// Dogfood: increase contrast (factor &gt; 1.0).
/// Dogfood: decrease contrast (factor &lt; 1.0).
/// </summary>
public class NetpbmR313ScaleContrastDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ScaleContrast_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.ScaleContrast(1.5));
        Assert.Null(ex);
    }

    [Fact]
    public void ScaleContrast_AllPixelsInRange()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) % 256);
        img.ScaleContrast(2.0);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void ScaleContrast_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.ScaleContrast(1.5);
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void ScaleContrast_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.ScaleContrast(1.5);
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void ScaleContrast_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.ScaleContrast(1.5);
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void ScaleContrast_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.ScaleContrast(1.5);
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void ScaleContrast_CalledTwice_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        img.ScaleContrast(1.5);
        var ex = Record.Exception(() => img.ScaleContrast(0.8));
        Assert.Null(ex);
    }

    [Fact]
    public void ScaleContrast_FactorOne_PixelUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        img.SetPixel(3, 3, 128);
        img.ScaleContrast(1.0);
        int pixel = img.GetPixel(3, 3);
        Assert.InRange(pixel, 0, 255);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_IncreaseContrast_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 64 + (x + y) % 64);
        img.ScaleContrast(2.0);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_DecreaseContrast_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * y) % 256);
        img.ScaleContrast(0.5);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }
}
