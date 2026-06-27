// Tests for NetpbmImage.GetPixelCount dedicated coverage.
// Sprint: ff-sprint-s384-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R397

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R397: Dedicated tests for NetpbmImage.GetPixelCount().
/// Valid image returns Width*Height.
/// Width unchanged after GetPixelCount.
/// Height unchanged after GetPixelCount.
/// Format unchanged after GetPixelCount.
/// MaxValue unchanged after GetPixelCount.
/// 1x1 image returns 1.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 returns 16.
/// Dogfood: 3x7 returns 21.
/// Dogfood: result matches Width*Height.
/// </summary>
public class NetpbmR397GetPixelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelCount_ValidImage_ReturnsWidthTimesHeight()
    {
        var img = NetpbmImage.CreateNew(4, 6, NetpbmFormat.PGM);
        int count = img.GetPixelCount();
        Assert.Equal(img.Width * img.Height, count);
    }

    [Fact]
    public void GetPixelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelCount_OneByOneImage_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(1, 1, NetpbmFormat.PGM);
        int count = img.GetPixelCount();
        Assert.Equal(1, count);
    }

    [Fact]
    public void GetPixelCount_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int first = img.GetPixelCount();
        int second = img.GetPixelCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFour_Returns16()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int count = img.GetPixelCount();
        Assert.Equal(16, count);
    }

    [Fact]
    public void DogfoodPipeline_ThreeBySevenReturns21()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int count = img.GetPixelCount();
        Assert.Equal(21, count);
    }

    [Fact]
    public void DogfoodPipeline_MatchesWidthTimesHeight()
    {
        var img = NetpbmImage.CreateNew(11, 7, NetpbmFormat.PBM);
        int count = img.GetPixelCount();
        Assert.Equal(img.Width * img.Height, count);
    }
}
