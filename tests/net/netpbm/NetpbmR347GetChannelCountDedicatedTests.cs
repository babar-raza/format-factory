// Tests for NetpbmImage.GetChannelCount dedicated coverage.
// Sprint: ff-sprint-s334-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R347

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R347: Dedicated tests for NetpbmImage.GetChannelCount().
/// Valid image ok.
/// Returns positive value.
/// Width unchanged after GetChannelCount.
/// Height unchanged after GetChannelCount.
/// Format unchanged after GetChannelCount.
/// MaxValue unchanged after GetChannelCount.
/// PGM image returns 1 channel.
/// PPM image returns 3 channels.
/// Idempotent (called twice same result).
/// Dogfood: PBM image returns 1 channel.
/// </summary>
public class NetpbmR347GetChannelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelCount_ValidImage_Ok()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        var ex = Record.Exception(() => img.GetChannelCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChannelCount_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int count = img.GetChannelCount();
        Assert.True(count > 0);
    }

    [Fact]
    public void GetChannelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Width;
        _ = img.GetChannelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetChannelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Height;
        _ = img.GetChannelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetChannelCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        string before = img.Format;
        _ = img.GetChannelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetChannelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.MaxValue;
        _ = img.GetChannelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetChannelCount_PgmImage_ReturnsOne()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int count = img.GetChannelCount();
        Assert.Equal(1, count);
    }

    [Fact]
    public void GetChannelCount_PpmImage_ReturnsThree()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        int count = img.GetChannelCount();
        Assert.Equal(3, count);
    }

    [Fact]
    public void GetChannelCount_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreatePgm(6, 6, 255);
        int first = img.GetChannelCount();
        int second = img.GetChannelCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ReturnsOne()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        int count = img.GetChannelCount();
        Assert.Equal(1, count);
    }
}
