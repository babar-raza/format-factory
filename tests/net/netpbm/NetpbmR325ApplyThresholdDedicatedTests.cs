// Tests for NetpbmImage.ApplyThreshold dedicated coverage.
// Sprint: ff-sprint-s314-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R325

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R325: Dedicated tests for NetpbmImage.ApplyThreshold(threshold).
/// Valid call no exception.
/// All pixels in range [0, MaxValue] after ApplyThreshold.
/// Width unchanged after ApplyThreshold.
/// Height unchanged after ApplyThreshold.
/// Format unchanged after ApplyThreshold.
/// MaxValue unchanged after ApplyThreshold.
/// Called twice no exception.
/// All-zero image pixels still in range.
/// Dogfood: mid-threshold on gradient image.
/// Dogfood: high-threshold on gradient image.
/// </summary>
public class NetpbmR325ApplyThresholdDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyThreshold_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.ApplyThreshold(128));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyThreshold_AllPixelsInRange()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 10 + y * 7) % 256);
        img.ApplyThreshold(100);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void ApplyThreshold_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.ApplyThreshold(128);
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void ApplyThreshold_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.ApplyThreshold(128);
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void ApplyThreshold_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.ApplyThreshold(128);
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void ApplyThreshold_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.ApplyThreshold(128);
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void ApplyThreshold_CalledTwice_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        img.ApplyThreshold(128);
        var ex = Record.Exception(() => img.ApplyThreshold(64));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyThreshold_AllZeroImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        img.ApplyThreshold(128);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MidThreshold_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, x * 32);
        img.ApplyThreshold(128);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_HighThreshold_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y * 8) % 256);
        img.ApplyThreshold(200);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }
}
