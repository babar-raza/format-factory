// Tests for NetpbmImage.GetChannelCount dedicated coverage.
// Sprint: ff-sprint-s415-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R433

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R433: Dedicated tests for NetpbmImage.GetChannelCount().
/// PBM returns positive channel count.
/// PGM returns positive channel count.
/// PPM returns positive channel count.
/// Width unchanged after GetChannelCount.
/// Height unchanged after GetChannelCount.
/// Format unchanged after GetChannelCount.
/// MaxValue unchanged after GetChannelCount.
/// Idempotent (called twice same result).
/// PPM channel count >= PGM channel count.
/// Dogfood: 4x4 PGM channel count positive.
/// Dogfood: 4x4 PPM channel count positive.
/// </summary>
public class NetpbmR433GetChannelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelCount_PBM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetChannelCount() > 0);
    }

    [Fact]
    public void GetChannelCount_PGM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetChannelCount() > 0);
    }

    [Fact]
    public void GetChannelCount_PPM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetChannelCount() > 0);
    }

    [Fact]
    public void GetChannelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetChannelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetChannelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetChannelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetChannelCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetChannelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetChannelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetChannelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetChannelCount_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetChannelCount();
        int second = img.GetChannelCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetChannelCount_PPM_AtLeastPGM()
    {
        var pgm = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        var ppm = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(ppm.GetChannelCount() >= pgm.GetChannelCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ChannelCountPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetChannelCount() > 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_ChannelCountPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetChannelCount() > 0);
    }
}
