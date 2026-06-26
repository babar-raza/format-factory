// Tests for NetpbmImage.CopyRegion dedicated coverage.
// Sprint: ff-sprint-s238-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R245

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R245: Dedicated tests for NetpbmImage.CopyRegion(x, y, width, height).
/// OOB coordinates → throws exception.
/// Valid call returns non-null.
/// Returns different object (not same reference).
/// Result has specified width.
/// Result has specified height.
/// Format preserved in copy.
/// MaxValue preserved in copy.
/// Pixel values copied correctly.
/// Modify copy does not affect original.
/// Dogfood: copy corner, verify pixels match original corner.
/// </summary>
public class NetpbmR245CopyRegionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CopyRegion_OobCoordinates_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.ThrowsAny<Exception>(() => img.CopyRegion(3, 3, 5, 5));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CopyRegion_ValidCall_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.CopyRegion(0, 0, 4, 4);
        Assert.NotNull(result);
    }

    [Fact]
    public void CopyRegion_ReturnsDifferentObject()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.CopyRegion(0, 0, 4, 4);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void CopyRegion_ResultHasSpecifiedWidth()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.CopyRegion(0, 0, 3, 4);
        Assert.Equal(3, result.Width);
    }

    [Fact]
    public void CopyRegion_ResultHasSpecifiedHeight()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.CopyRegion(0, 0, 3, 5);
        Assert.Equal(5, result.Height);
    }

    [Fact]
    public void CopyRegion_FormatPreserved()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.CopyRegion(0, 0, 4, 4);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void CopyRegion_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 200);
        var result = img.CopyRegion(0, 0, 4, 4);
        Assert.Equal(200, result.MaxValue);
    }

    [Fact]
    public void CopyRegion_PixelValuesCopiedCorrectly()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(2, 2, 150);
        var result = img.CopyRegion(0, 0, 5, 5);
        Assert.Equal(150, result.GetPixel(2, 2));
    }

    [Fact]
    public void CopyRegion_ModifyCopy_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 100);
        var copy = img.CopyRegion(0, 0, 5, 5);
        copy.SetPixel(1, 1, 200);
        Assert.Equal(100, img.GetPixel(1, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CopyCorner_PixelsMatchOriginal()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 0, 100);
        img.SetPixel(0, 1, 150);
        img.SetPixel(1, 1, 200);
        var corner = img.CopyRegion(0, 0, 2, 2);
        Assert.Equal(50, corner.GetPixel(0, 0));
        Assert.Equal(100, corner.GetPixel(1, 0));
        Assert.Equal(150, corner.GetPixel(0, 1));
        Assert.Equal(200, corner.GetPixel(1, 1));
    }
}
