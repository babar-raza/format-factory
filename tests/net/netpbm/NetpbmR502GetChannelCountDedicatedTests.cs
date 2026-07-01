// Tests for NetpbmImage.GetChannelCount dedicated coverage.
// Sprint: ff-sprint-s484-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R502

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R502: Dedicated tests for NetpbmImage.GetChannelCount().
/// PBM image returns 1 (single bitmap channel).
/// PGM image returns 1 (single grayscale channel).
/// PPM image returns 3 (red, green, blue channels).
/// Width unchanged after GetChannelCount.
/// Height unchanged after GetChannelCount.
/// Format unchanged after GetChannelCount.
/// MaxValue unchanged after GetChannelCount.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline returns 1.
/// Dogfood: PGM pipeline returns 1.
/// Dogfood: PPM pipeline returns 3.
/// </summary>
public class NetpbmR502GetChannelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelCount_PbmImage_ReturnsOne()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.Equal(1, img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_PgmImage_ReturnsOne()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.Equal(1, img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_PpmImage_ReturnsThree()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.Equal(3, img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetChannelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetChannelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetChannelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetChannelCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetChannelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetChannelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetChannelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetChannelCount_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
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
        var img = NetpbmImage.CreatePbm(8, 8);
        int result = img.GetChannelCount();
        Assert.Equal(1, result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ReturnsOne()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int result = img.GetChannelCount();
        Assert.Equal(1, result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ReturnsThree()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        int result = img.GetChannelCount();
        Assert.Equal(3, result);
    }
}
