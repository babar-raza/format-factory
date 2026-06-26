// Tests for NetpbmImage.GetChannelCount dedicated coverage.
// Sprint: ff-sprint-s227-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R234

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R234: Dedicated tests for NetpbmImage.GetChannelCount().
/// PGM image has 1 channel.
/// PPM image has 3 channels.
/// Returns positive value.
/// Format preserved after call.
/// MaxValue preserved after call.
/// Dimensions preserved after call.
/// Called twice: same result.
/// PGM_P2 has 1 channel.
/// PPM_P3 has 3 channels.
/// Dogfood: create both formats, verify channel counts differ.
/// </summary>
public class NetpbmR234GetChannelCountTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelCount_PgmP5_HasOneChannel()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.Equal(1, img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_PpmP6_HasThreeChannels()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6, maxValue: 255);
        Assert.Equal(3, img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_ReturnsPositive()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.True(img.GetChannelCount() > 0);
    }

    [Fact]
    public void GetChannelCount_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.GetChannelCount();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void GetChannelCount_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 127);
        img.GetChannelCount();
        Assert.Equal(127, img.MaxValue);
    }

    [Fact]
    public void GetChannelCount_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(5, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        img.GetChannelCount();
        Assert.Equal(5, img.Width);
        Assert.Equal(6, img.Height);
    }

    [Fact]
    public void GetChannelCount_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6, maxValue: 255);
        Assert.Equal(img.GetChannelCount(), img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_PgmP2_HasOneChannel()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P2, maxValue: 255);
        Assert.Equal(1, img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_PpmP3_HasThreeChannels()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P3, maxValue: 255);
        Assert.Equal(3, img.GetChannelCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_BothFormats_ChannelCountsDiffer()
    {
        var pgm = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var ppm = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6, maxValue: 255);
        Assert.NotEqual(pgm.GetChannelCount(), ppm.GetChannelCount());
        Assert.True(ppm.GetChannelCount() > pgm.GetChannelCount());
    }
}
