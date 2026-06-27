// Tests for NetpbmImage.GetWhitePixelCount dedicated coverage.
// Sprint: ff-sprint-s365-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R378

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R378: Dedicated tests for NetpbmImage.GetWhitePixelCount().
/// Valid image returns non-negative.
/// All-zero (black) image returns 0.
/// All-max (white) image returns Width*Height.
/// Width unchanged after GetWhitePixelCount.
/// Height unchanged after GetWhitePixelCount.
/// Format unchanged after GetWhitePixelCount.
/// MaxValue unchanged after GetWhitePixelCount.
/// Idempotent (called twice same result).
/// Dogfood: half-white image count in expected range.
/// Dogfood: single white pixel returns 1.
/// </summary>
public class NetpbmR378GetWhitePixelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWhitePixelCount_ValidImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int count = img.GetWhitePixelCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetWhitePixelCount_AllBlackImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 0);
        int count = img.GetWhitePixelCount();
        Assert.Equal(0, count);
    }

    [Fact]
    public void GetWhitePixelCount_AllWhiteImage_ReturnsTotal()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, img.MaxValue);
        int count = img.GetWhitePixelCount();
        Assert.Equal(img.Width * img.Height, count);
    }

    [Fact]
    public void GetWhitePixelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetWhitePixelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetWhitePixelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetWhitePixelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetWhitePixelCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetWhitePixelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetWhitePixelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetWhitePixelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetWhitePixelCount_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 255);
        img.SetPixel(1, 1, 255);
        int first = img.GetWhitePixelCount();
        int second = img.GetWhitePixelCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HalfWhiteImage_CountInRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int total = img.Width * img.Height;
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? img.MaxValue : 0);
        int count = img.GetWhitePixelCount();
        Assert.InRange(count, 0, total);
    }

    [Fact]
    public void DogfoodPipeline_SingleWhitePixel_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 0);
        img.SetPixel(2, 2, img.MaxValue);
        int count = img.GetWhitePixelCount();
        Assert.Equal(1, count);
    }
}
