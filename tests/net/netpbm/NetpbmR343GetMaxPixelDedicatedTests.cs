// Tests for NetpbmImage.GetMaxPixel dedicated coverage.
// Sprint: ff-sprint-s331-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R343

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R343: Dedicated tests for NetpbmImage.GetMaxPixel().
/// Valid call no exception.
/// Width unchanged after GetMaxPixel.
/// Height unchanged after GetMaxPixel.
/// Format unchanged after GetMaxPixel.
/// MaxValue unchanged after GetMaxPixel.
/// Returns value in [0, MaxValue].
/// All-zero image returns zero.
/// Idempotent (called twice same result).
/// Uniform image returns pixel value.
/// Dogfood: all-max image returns MaxValue.
/// </summary>
public class NetpbmR343GetMaxPixelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMaxPixel_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 9 + y * 7) % 256);
        var ex = Record.Exception(() => img.GetMaxPixel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMaxPixel_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetMaxPixel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMaxPixel_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetMaxPixel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMaxPixel_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetMaxPixel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMaxPixel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetMaxPixel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMaxPixel_ReturnsInValidRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 5 + y * 11) % 256);
        int maxPixel = img.GetMaxPixel();
        Assert.InRange(maxPixel, 0, img.MaxValue);
    }

    [Fact]
    public void GetMaxPixel_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int maxPixel = img.GetMaxPixel();
        Assert.Equal(0, maxPixel);
    }

    [Fact]
    public void GetMaxPixel_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 7 + y * 3) % 256);
        int first = img.GetMaxPixel();
        int second = img.GetMaxPixel();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMaxPixel_UniformImage_ReturnsPixelValue()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 200);
        int maxPixel = img.GetMaxPixel();
        Assert.Equal(200, maxPixel);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AllMaxImage_ReturnsMaxValue()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 255);
        int maxPixel = img.GetMaxPixel();
        Assert.Equal(255, maxPixel);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }
}
