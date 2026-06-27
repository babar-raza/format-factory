// Tests for NetpbmImage.GetColorChannelCount dedicated coverage.
// Sprint: ff-sprint-s385-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R398

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R398: Dedicated tests for NetpbmImage.GetColorChannelCount().
/// PBM returns 1.
/// PGM returns 1.
/// PPM returns 3.
/// Width unchanged after GetColorChannelCount.
/// Height unchanged after GetColorChannelCount.
/// Format unchanged after GetColorChannelCount.
/// MaxValue unchanged after GetColorChannelCount.
/// Idempotent (called twice same result).
/// Dogfood: 2x2 PBM returns 1.
/// Dogfood: 4x4 PPM returns 3.
/// </summary>
public class NetpbmR398GetColorChannelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorChannelCount_PBM_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        int count = img.GetColorChannelCount();
        Assert.Equal(1, count);
    }

    [Fact]
    public void GetColorChannelCount_PGM_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int count = img.GetColorChannelCount();
        Assert.Equal(1, count);
    }

    [Fact]
    public void GetColorChannelCount_PPM_ReturnsThree()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int count = img.GetColorChannelCount();
        Assert.Equal(3, count);
    }

    [Fact]
    public void GetColorChannelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetColorChannelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetColorChannelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PPM);
        int before = img.Height;
        _ = img.GetColorChannelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetColorChannelCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetColorChannelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetColorChannelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetColorChannelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetColorChannelCount_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetColorChannelCount();
        int second = img.GetColorChannelCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoByTwoPBM_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(2, 2, NetpbmFormat.PBM);
        int count = img.GetColorChannelCount();
        Assert.Equal(1, count);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_ReturnsThree()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int count = img.GetColorChannelCount();
        Assert.Equal(3, count);
    }
}
