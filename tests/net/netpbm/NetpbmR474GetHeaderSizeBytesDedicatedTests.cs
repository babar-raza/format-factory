// Tests for NetpbmImage.GetHeaderSizeBytes dedicated coverage.
// Sprint: ff-sprint-s456-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R474

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R474: Dedicated tests for NetpbmImage.GetHeaderSizeBytes().
/// Returns positive value.
/// Width unchanged after GetHeaderSizeBytes.
/// Height unchanged after GetHeaderSizeBytes.
/// Format unchanged after GetHeaderSizeBytes.
/// MaxValue unchanged after GetHeaderSizeBytes.
/// Idempotent (called twice same result).
/// PBM returns positive.
/// PGM returns positive.
/// PPM returns positive.
/// Dogfood: 4x4 PGM header size is positive.
/// Dogfood: 4x4 PPM header size is positive.
/// </summary>
public class NetpbmR474GetHeaderSizeBytesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaderSizeBytes_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.True(img.GetHeaderSizeBytes() > 0);
    }

    [Fact]
    public void GetHeaderSizeBytes_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetHeaderSizeBytes();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHeaderSizeBytes_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetHeaderSizeBytes();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHeaderSizeBytes_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetHeaderSizeBytes();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHeaderSizeBytes_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetHeaderSizeBytes();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHeaderSizeBytes_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int first = img.GetHeaderSizeBytes();
        int second = img.GetHeaderSizeBytes();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetHeaderSizeBytes_PBM_Positive()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.True(img.GetHeaderSizeBytes() > 0);
    }

    [Fact]
    public void GetHeaderSizeBytes_PGM_Positive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.True(img.GetHeaderSizeBytes() > 0);
    }

    [Fact]
    public void GetHeaderSizeBytes_PPM_Positive()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.True(img.GetHeaderSizeBytes() > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_HeaderSizeIsPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.True(img.GetHeaderSizeBytes() > 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_HeaderSizeIsPositive()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.True(img.GetHeaderSizeBytes() > 0);
    }
}
