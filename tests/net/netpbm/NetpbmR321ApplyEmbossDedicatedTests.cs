// Tests for NetpbmImage.ApplyEmboss dedicated coverage.
// Sprint: ff-sprint-s311-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R321

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R321: Dedicated tests for NetpbmImage.ApplyEmboss().
/// Valid call no exception.
/// All pixels in range [0, MaxValue] after ApplyEmboss.
/// Width unchanged after ApplyEmboss.
/// Height unchanged after ApplyEmboss.
/// Format unchanged after ApplyEmboss.
/// MaxValue unchanged after ApplyEmboss.
/// Called twice no exception.
/// All-zero image pixels in range.
/// Dogfood: mixed image pixels in range.
/// Dogfood: gradient image pixels in range.
/// </summary>
public class NetpbmR321ApplyEmbossDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyEmboss_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.ApplyEmboss());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyEmboss_AllPixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 5 + y * 3) % 256);
        img.ApplyEmboss();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void ApplyEmboss_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 6, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.ApplyEmboss();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void ApplyEmboss_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 6, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.ApplyEmboss();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void ApplyEmboss_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.ApplyEmboss();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void ApplyEmboss_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.ApplyEmboss();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void ApplyEmboss_CalledTwice_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        img.ApplyEmboss();
        var ex = Record.Exception(() => img.ApplyEmboss());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyEmboss_AllZeroImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        img.ApplyEmboss();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, y % 2 == 0 ? 50 : 200);
        img.ApplyEmboss();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_GradientImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 32) % 256);
        img.ApplyEmboss();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }
}
