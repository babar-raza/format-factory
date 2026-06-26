// Tests for NetpbmImage.GetPixelCount dedicated coverage.
// Sprint: ff-sprint-s230-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R237

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R237: Dedicated tests for NetpbmImage.GetPixelCount().
/// Returns positive value.
/// Equals width * height.
/// Format preserved after call.
/// MaxValue preserved after call.
/// Dimensions preserved after call.
/// 1x1 image: count is 1.
/// 4x4 image: count is 16.
/// Called twice: same result.
/// Different dimensions: different counts.
/// Dogfood: create image, verify count matches w*h.
/// </summary>
public class NetpbmR237GetPixelCountTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelCount_ReturnsPositive()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.True(img.GetPixelCount() > 0);
    }

    [Fact]
    public void GetPixelCount_EqualsWidthTimesHeight()
    {
        var img = NetpbmImage.Create(5, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.Equal(5 * 6, img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.GetPixelCount();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void GetPixelCount_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 150);
        img.GetPixelCount();
        Assert.Equal(150, img.MaxValue);
    }

    [Fact]
    public void GetPixelCount_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(3, 7, NetpbmFormat.PGM_P5, maxValue: 255);
        img.GetPixelCount();
        Assert.Equal(3, img.Width);
        Assert.Equal(7, img.Height);
    }

    [Fact]
    public void GetPixelCount_1x1Image_IsOne()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.Equal(1, img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_4x4Image_Is16()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.Equal(16, img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(5, 7, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.Equal(img.GetPixelCount(), img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_DifferentDimensions_DifferentCounts()
    {
        var img1 = NetpbmImage.Create(2, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        var img2 = NetpbmImage.Create(4, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.NotEqual(img1.GetPixelCount(), img2.GetPixelCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_VariousImages_CountMatchesWidthTimesHeight()
    {
        int[] widths = { 1, 3, 8, 10 };
        int[] heights = { 1, 4, 6, 12 };
        for (int i = 0; i < widths.Length; i++)
        {
            var img = NetpbmImage.Create(widths[i], heights[i], NetpbmFormat.PGM_P5, maxValue: 255);
            Assert.Equal(widths[i] * heights[i], img.GetPixelCount());
        }
    }
}
