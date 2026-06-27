// Tests for NetpbmImage.GetChannelCount dedicated coverage.
// Sprint: ff-sprint-s363-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R376

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R376: Dedicated tests for NetpbmImage.GetChannelCount().
/// PBM image returns 1.
/// PGM image returns 1.
/// PPM image returns 3.
/// Width unchanged after GetChannelCount.
/// Height unchanged after GetChannelCount.
/// Format unchanged after GetChannelCount.
/// MaxValue unchanged after GetChannelCount.
/// Idempotent (called twice same result).
/// Dogfood: 2x2 PBM returns 1.
/// Dogfood: 4x4 PPM returns 3.
/// </summary>
public class NetpbmR376GetChannelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelCount_PbmImage_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        int channels = img.GetChannelCount();
        Assert.Equal(1, channels);
    }

    [Fact]
    public void GetChannelCount_PgmImage_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int channels = img.GetChannelCount();
        Assert.Equal(1, channels);
    }

    [Fact]
    public void GetChannelCount_PpmImage_ReturnsThree()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int channels = img.GetChannelCount();
        Assert.Equal(3, channels);
    }

    [Fact]
    public void GetChannelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetChannelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetChannelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
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

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoByTwoPbm_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(2, 2, NetpbmFormat.PBM);
        img.SetPixel(0, 0, 1);
        img.SetPixel(0, 1, 0);
        img.SetPixel(1, 0, 0);
        img.SetPixel(1, 1, 1);
        Assert.Equal(1, img.GetChannelCount());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPpm_ReturnsThree()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, r * 60 + c * 20);
        Assert.Equal(3, img.GetChannelCount());
    }
}
