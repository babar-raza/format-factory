// Tests for NetpbmImage.GetMinPixel dedicated coverage.
// Sprint: ff-sprint-s330-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R342

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R342: Dedicated tests for NetpbmImage.GetMinPixel().
/// Valid call no exception.
/// Width unchanged after GetMinPixel.
/// Height unchanged after GetMinPixel.
/// Format unchanged after GetMinPixel.
/// MaxValue unchanged after GetMinPixel.
/// Returns value in [0, MaxValue].
/// All-zero image returns zero.
/// Idempotent (called twice same result).
/// Uniform image returns pixel value.
/// Dogfood: mixed image min is non-negative.
/// </summary>
public class NetpbmR342GetMinPixelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMinPixel_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 11 + y * 5) % 256);
        var ex = Record.Exception(() => img.GetMinPixel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMinPixel_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetMinPixel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMinPixel_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetMinPixel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMinPixel_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetMinPixel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMinPixel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetMinPixel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMinPixel_ReturnsInValidRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 13 + y * 7) % 256);
        int minPixel = img.GetMinPixel();
        Assert.InRange(minPixel, 0, img.MaxValue);
    }

    [Fact]
    public void GetMinPixel_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int minPixel = img.GetMinPixel();
        Assert.Equal(0, minPixel);
    }

    [Fact]
    public void GetMinPixel_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 3 + y * 5) % 256);
        int first = img.GetMinPixel();
        int second = img.GetMinPixel();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMinPixel_UniformImage_ReturnsPixelValue()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 75);
        int minPixel = img.GetMinPixel();
        Assert.Equal(75, minPixel);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedImage_MinIsNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 19 + y * 7) % 256);
        int minPixel = img.GetMinPixel();
        Assert.True(minPixel >= 0);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }
}
