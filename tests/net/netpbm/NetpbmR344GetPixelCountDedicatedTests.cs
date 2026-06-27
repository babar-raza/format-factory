// Tests for NetpbmImage.GetPixelCount dedicated coverage.
// Sprint: ff-sprint-s332-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R344

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R344: Dedicated tests for NetpbmImage.GetPixelCount().
/// Valid call no exception.
/// Returns width times height.
/// Width unchanged after GetPixelCount.
/// Height unchanged after GetPixelCount.
/// Format unchanged after GetPixelCount.
/// MaxValue unchanged after GetPixelCount.
/// Idempotent (called twice same result).
/// Larger image returns larger count.
/// Dogfood: 1x1 image returns 1.
/// Dogfood: 8x8 image returns 64.
/// </summary>
public class NetpbmR344GetPixelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelCount_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.GetPixelCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPixelCount_ReturnsWidthTimesHeight()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int count = img.GetPixelCount();
        Assert.Equal(50, count);
    }

    [Fact]
    public void GetPixelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelCount_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int first = img.GetPixelCount();
        int second = img.GetPixelCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPixelCount_LargerImage_LargerCount()
    {
        var small = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM, 255);
        var large = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        Assert.True(large.GetPixelCount() > small.GetPixelCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_1x1Image_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(1, 1, NetpbmFormat.PGM, 255);
        int count = img.GetPixelCount();
        Assert.Equal(1, count);
    }

    [Fact]
    public void DogfoodPipeline_8x8Image_Returns64()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int count = img.GetPixelCount();
        Assert.Equal(64, count);
    }
}
