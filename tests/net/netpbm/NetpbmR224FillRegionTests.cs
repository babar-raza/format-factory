// Tests for NetpbmImage.FillRegion dedicated coverage.
// Sprint: ff-sprint-s218-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R224

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R224: Dedicated tests for NetpbmImage.FillRegion(int x, int y, int width, int height, int pixelValue).
/// OOB x → throws exception.
/// OOB y → throws exception.
/// Zero width → throws exception.
/// Zero height → throws exception.
/// Valid call: no exception.
/// Region pixels have specified value.
/// Pixels outside region unchanged.
/// Format preserved.
/// MaxValue preserved.
/// Dogfood: fill entire image, all pixels same value.
/// </summary>
public class NetpbmR224FillRegionTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FillRegion_XOutOfBounds_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.FillRegion(10, 0, 2, 2, 100));
    }

    [Fact]
    public void FillRegion_YOutOfBounds_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.FillRegion(0, 10, 2, 2, 100));
    }

    [Fact]
    public void FillRegion_ZeroWidth_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.FillRegion(0, 0, 0, 2, 100));
    }

    [Fact]
    public void FillRegion_ZeroHeight_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.FillRegion(0, 0, 2, 0, 100));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FillRegion_Valid_NoException()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        var ex = Record.Exception(() => img.FillRegion(1, 1, 3, 3, 128));
        Assert.Null(ex);
    }

    [Fact]
    public void FillRegion_RegionPixelsHaveSpecifiedValue()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        img.FillRegion(1, 1, 3, 3, 200);
        for (int y = 1; y < 4; y++)
            for (int x = 1; x < 4; x++)
                Assert.Equal(200, img.GetPixel(x, y));
    }

    [Fact]
    public void FillRegion_PixelsOutsideRegionUnchanged()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        img.FillRegion(2, 2, 2, 2, 200);
        Assert.Equal(50, img.GetPixel(0, 0));
    }

    [Fact]
    public void FillRegion_FormatPreserved()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        img.FillRegion(0, 0, 3, 3, 100);
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void FillRegion_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5, maxValue: 200);
        img.FillRegion(0, 0, 3, 3, 100);
        Assert.Equal(200, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FillEntireImage_AllSameValue()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        img.FillRegion(0, 0, 5, 5, 150);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                Assert.Equal(150, img.GetPixel(x, y));
    }

    [Fact]
    public void DogfoodPipeline_OverlappingFills_LatestValueWins()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        img.FillRegion(0, 0, 4, 4, 100);
        img.FillRegion(2, 2, 4, 4, 200);
        Assert.Equal(200, img.GetPixel(2, 2));
        Assert.Equal(100, img.GetPixel(0, 0));
    }
}
