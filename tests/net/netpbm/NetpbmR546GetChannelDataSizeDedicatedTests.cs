// Tests for NetpbmImage.GetChannelDataSize dedicated coverage.
// Sprint: ff-sprint-s528-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R546

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R546: Dedicated tests for NetpbmImage.GetChannelDataSize().
/// PBM image returns positive channel data size.
/// PGM image returns positive channel data size.
/// PPM image returns positive channel data size.
/// Width unchanged after GetChannelDataSize.
/// Height unchanged after GetChannelDataSize.
/// Format unchanged after GetChannelDataSize.
/// MaxValue unchanged after GetChannelDataSize.
/// Idempotent (called twice same result).
/// Dogfood: PBM channel data size positive.
/// Dogfood: PGM channel data size positive.
/// Dogfood: PPM channel data size positive.
/// </summary>
public class NetpbmR546GetChannelDataSizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelDataSize_PbmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetChannelDataSize() > 0);
    }

    [Fact]
    public void GetChannelDataSize_PgmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetChannelDataSize() > 0);
    }

    [Fact]
    public void GetChannelDataSize_PpmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetChannelDataSize() > 0);
    }

    [Fact]
    public void GetChannelDataSize_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetChannelDataSize();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetChannelDataSize_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetChannelDataSize();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetChannelDataSize_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetChannelDataSize();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetChannelDataSize_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetChannelDataSize();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetChannelDataSize_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetChannelDataSize();
        int second = img.GetChannelDataSize();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ChannelDataSizePositive()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        Assert.True(img.GetChannelDataSize() > 0);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ChannelDataSizePositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        Assert.True(img.GetChannelDataSize() > 0);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ChannelDataSizePositive()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        Assert.True(img.GetChannelDataSize() > 0);
    }
}
