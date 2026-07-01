// Tests for NetpbmImage.GetHistogramBinCount dedicated coverage.
// Sprint: ff-sprint-s422-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R440

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R440: Dedicated tests for NetpbmImage.GetHistogramBinCount().
/// Returns positive value.
/// Width unchanged after GetHistogramBinCount.
/// Height unchanged after GetHistogramBinCount.
/// Format unchanged after GetHistogramBinCount.
/// MaxValue unchanged after GetHistogramBinCount.
/// Idempotent (called twice same result).
/// PBM histogram bin count positive.
/// PGM histogram bin count positive.
/// PPM histogram bin count positive.
/// Dogfood: 4x4 PGM histogram bin count positive.
/// Dogfood: 4x4 PPM histogram bin count positive.
/// </summary>
public class NetpbmR440GetHistogramBinCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogramBinCount_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int bins = img.GetHistogramBinCount();
        Assert.True(bins > 0);
    }

    [Fact]
    public void GetHistogramBinCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetHistogramBinCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHistogramBinCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetHistogramBinCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHistogramBinCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetHistogramBinCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHistogramBinCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetHistogramBinCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHistogramBinCount_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetHistogramBinCount();
        int second = img.GetHistogramBinCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetHistogramBinCount_PBM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetHistogramBinCount() > 0);
    }

    [Fact]
    public void GetHistogramBinCount_PGM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetHistogramBinCount() > 0);
    }

    [Fact]
    public void GetHistogramBinCount_PPM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetHistogramBinCount() > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_BinCountPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetHistogramBinCount() > 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_BinCountPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetHistogramBinCount() > 0);
    }
}
