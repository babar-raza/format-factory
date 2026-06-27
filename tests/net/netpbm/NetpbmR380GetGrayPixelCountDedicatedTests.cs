// Tests for NetpbmImage.GetGrayPixelCount dedicated coverage.
// Sprint: ff-sprint-s367-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R380

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R380: Dedicated tests for NetpbmImage.GetGrayPixelCount().
/// Valid image returns non-negative.
/// All-black image returns 0.
/// All-white image returns 0.
/// Width unchanged after GetGrayPixelCount.
/// Height unchanged after GetGrayPixelCount.
/// Format unchanged after GetGrayPixelCount.
/// MaxValue unchanged after GetGrayPixelCount.
/// Idempotent (called twice same result).
/// Dogfood: mid-gray pixels returns positive.
/// Dogfood: mixed image returns non-negative.
/// </summary>
public class NetpbmR380GetGrayPixelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGrayPixelCount_ValidImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int count = img.GetGrayPixelCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetGrayPixelCount_AllBlackImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 0);
        int count = img.GetGrayPixelCount();
        Assert.Equal(0, count);
    }

    [Fact]
    public void GetGrayPixelCount_AllWhiteImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, img.MaxValue);
        int count = img.GetGrayPixelCount();
        Assert.Equal(0, count);
    }

    [Fact]
    public void GetGrayPixelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetGrayPixelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetGrayPixelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetGrayPixelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetGrayPixelCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        NetpbmFormat before = img.Format;
        _ = img.GetGrayPixelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetGrayPixelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetGrayPixelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetGrayPixelCount_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 128);
        int first = img.GetGrayPixelCount();
        int second = img.GetGrayPixelCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MidGrayPixels_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 128);
        int count = img.GetGrayPixelCount();
        Assert.True(count > 0);
    }

    [Fact]
    public void DogfoodPipeline_MixedImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r * 64 + c * 32) % 256);
        int count = img.GetGrayPixelCount();
        Assert.True(count >= 0);
    }
}
