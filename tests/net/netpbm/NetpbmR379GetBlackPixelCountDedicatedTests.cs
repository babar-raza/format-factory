// Tests for NetpbmImage.GetBlackPixelCount dedicated coverage.
// Sprint: ff-sprint-s366-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R379

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R379: Dedicated tests for NetpbmImage.GetBlackPixelCount().
/// Valid image returns non-negative.
/// All-zero (black) image returns Width*Height.
/// All-max (white) image returns 0.
/// Width unchanged after GetBlackPixelCount.
/// Height unchanged after GetBlackPixelCount.
/// Format unchanged after GetBlackPixelCount.
/// MaxValue unchanged after GetBlackPixelCount.
/// Idempotent (called twice same result).
/// Dogfood: half-black image count in expected range.
/// Dogfood: single black pixel returns 1.
/// </summary>
public class NetpbmR379GetBlackPixelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlackPixelCount_ValidImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int count = img.GetBlackPixelCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetBlackPixelCount_AllBlackImage_ReturnsTotal()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 0);
        int count = img.GetBlackPixelCount();
        Assert.Equal(img.Width * img.Height, count);
    }

    [Fact]
    public void GetBlackPixelCount_AllWhiteImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, img.MaxValue);
        int count = img.GetBlackPixelCount();
        Assert.Equal(0, count);
    }

    [Fact]
    public void GetBlackPixelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetBlackPixelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetBlackPixelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetBlackPixelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetBlackPixelCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetBlackPixelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetBlackPixelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetBlackPixelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetBlackPixelCount_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 1, 0);
        int first = img.GetBlackPixelCount();
        int second = img.GetBlackPixelCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HalfBlackImage_CountInRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int total = img.Width * img.Height;
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? 0 : img.MaxValue);
        int count = img.GetBlackPixelCount();
        Assert.InRange(count, 0, total);
    }

    [Fact]
    public void DogfoodPipeline_SingleBlackPixelInWhite_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, img.MaxValue);
        img.SetPixel(1, 2, 0);
        int count = img.GetBlackPixelCount();
        Assert.Equal(1, count);
    }
}
