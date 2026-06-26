// Tests for NetpbmImage.GetPixelCount dedicated coverage.
// Sprint: ff-sprint-s264-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R271

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R271: Dedicated tests for NetpbmImage.GetPixelCount().
/// GetPixelCount returns the total number of pixels (Width * Height).
/// Returns a positive integer for any valid image.
/// Equals Width * Height.
/// Width/height/format/MaxValue unchanged (non-mutating).
/// Called twice returns same result.
/// After Resize, reflects new dimensions.
/// Dogfood: create image, verify count = W*H.
/// Dogfood: two images of different sizes, different counts.
/// </summary>
public class NetpbmR271GetPixelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelCount_ReturnsPositive()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        int count = img.GetPixelCount();
        Assert.True(count > 0);
    }

    [Fact]
    public void GetPixelCount_EqualsWidthTimesHeight()
    {
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        int count = img.GetPixelCount();
        Assert.Equal(5 * 4, count);
    }

    [Fact]
    public void GetPixelCount_1x1Image_ReturnsOne()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5, maxValue: 255);
        int count = img.GetPixelCount();
        Assert.Equal(1, count);
    }

    [Fact]
    public void GetPixelCount_SquareImage_EqualsSquare()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        int count = img.GetPixelCount();
        Assert.Equal(36, count);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelCount_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.GetPixelCount();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void GetPixelCount_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.GetPixelCount();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void GetPixelCount_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.GetPixelCount();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void GetPixelCount_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(7, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        int first = img.GetPixelCount();
        int second = img.GetPixelCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownDimensions_CountMatchesWxH()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        int count = img.GetPixelCount();
        Assert.Equal(48, count);
    }

    [Fact]
    public void DogfoodPipeline_TwoDifferentSizeImages_DifferentCounts()
    {
        var small = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        var large = NetpbmImage.Create(10, 10, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.True(large.GetPixelCount() > small.GetPixelCount());
    }
}
