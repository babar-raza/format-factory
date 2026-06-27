// Tests for NetpbmImage.ApplyBlur dedicated coverage.
// Sprint: ff-sprint-s312-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R323

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R323: Dedicated tests for NetpbmImage.ApplyBlur().
/// Valid call no exception.
/// All pixels in range [0, MaxValue] after ApplyBlur.
/// Width unchanged after ApplyBlur.
/// Height unchanged after ApplyBlur.
/// Format unchanged after ApplyBlur.
/// MaxValue unchanged after ApplyBlur.
/// Called twice no exception.
/// All-zero image pixels still in range.
/// Dogfood: checkerboard image pixels in range.
/// Dogfood: uniform image pixels unchanged range.
/// </summary>
public class NetpbmR323ApplyBlurDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyBlur_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.ApplyBlur());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyBlur_AllPixelsInRange()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y * 3) % 256);
        img.ApplyBlur();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void ApplyBlur_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.ApplyBlur();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void ApplyBlur_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.ApplyBlur();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void ApplyBlur_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.ApplyBlur();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void ApplyBlur_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.ApplyBlur();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void ApplyBlur_CalledTwice_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        img.ApplyBlur();
        var ex = Record.Exception(() => img.ApplyBlur());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyBlur_AllZeroImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        img.ApplyBlur();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CheckerboardImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) % 2 == 0 ? 0 : 255);
        img.ApplyBlur();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_UniformImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 128);
        img.ApplyBlur();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }
}
