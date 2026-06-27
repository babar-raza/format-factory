// Tests for NetpbmImage.Normalize dedicated coverage.
// Sprint: ff-sprint-s313-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R324

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R324: Dedicated tests for NetpbmImage.Normalize().
/// Valid call no exception.
/// All pixels in range [0, MaxValue] after Normalize.
/// Width unchanged after Normalize.
/// Height unchanged after Normalize.
/// Format unchanged after Normalize.
/// MaxValue unchanged after Normalize.
/// Called twice no exception.
/// All-zero image pixels still in range.
/// Dogfood: gradient image pixels in range.
/// Dogfood: alternating image pixels in range after normalize.
/// </summary>
public class NetpbmR324NormalizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Normalize_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.Normalize());
        Assert.Null(ex);
    }

    [Fact]
    public void Normalize_AllPixelsInRange()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 10 + y * 5) % 200);
        img.Normalize();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void Normalize_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.Normalize();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void Normalize_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.Normalize();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void Normalize_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.Normalize();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void Normalize_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.Normalize();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void Normalize_CalledTwice_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        img.Normalize();
        var ex = Record.Exception(() => img.Normalize());
        Assert.Null(ex);
    }

    [Fact]
    public void Normalize_AllZeroImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        img.Normalize();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GradientImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 32) % 256);
        img.Normalize();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_AlternatingImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, y % 2 == 0 ? 50 : 200);
        img.Normalize();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }
}
