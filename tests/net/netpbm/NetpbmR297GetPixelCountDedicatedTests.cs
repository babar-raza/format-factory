// Tests for NetpbmImage.GetPixelCount dedicated coverage.
// Sprint: ff-sprint-s289-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R297

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R297: Dedicated tests for NetpbmImage.GetPixelCount().
/// Returns positive int.
/// Equals Width * Height.
/// Width unchanged after GetPixelCount.
/// Height unchanged after GetPixelCount.
/// Format unchanged after GetPixelCount.
/// MaxValue unchanged after GetPixelCount.
/// Called twice returns same result.
/// 4x4 image returns 16.
/// 1x1 image returns 1.
/// Dogfood: arbitrary-size pixel count matches W*H.
/// </summary>
public class NetpbmR297GetPixelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelCount_ReturnsPositive()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int count = img.GetPixelCount();
        Assert.True(count > 0);
    }

    [Fact]
    public void GetPixelCount_EqualsWidthTimesHeight()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int count = img.GetPixelCount();
        Assert.Equal(img.Width * img.Height, count);
    }

    [Fact]
    public void GetPixelCount_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelCount_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelCount_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelCount_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int first = img.GetPixelCount();
        int second = img.GetPixelCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPixelCount_FourByFour_ReturnsSixteen()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        Assert.Equal(16, img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_OneByOne_ReturnsOne()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM, 255);
        Assert.Equal(1, img.GetPixelCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ArbitrarySize_CountMatchesWidthTimesHeight()
    {
        var img = NetpbmImage.Create(7, 5, NetpbmFormat.PGM, 255);
        int count = img.GetPixelCount();
        Assert.Equal(35, count);
    }
}
