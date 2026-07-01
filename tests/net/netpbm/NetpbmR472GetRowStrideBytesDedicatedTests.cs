// Tests for NetpbmImage.GetRowStrideBytes dedicated coverage.
// Sprint: ff-sprint-s454-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R472

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R472: Dedicated tests for NetpbmImage.GetRowStrideBytes().
/// Returns positive value.
/// Width unchanged after GetRowStrideBytes.
/// Height unchanged after GetRowStrideBytes.
/// Format unchanged after GetRowStrideBytes.
/// MaxValue unchanged after GetRowStrideBytes.
/// Idempotent (called twice same result).
/// PBM returns positive.
/// PGM returns positive.
/// PPM returns positive.
/// Dogfood: 4x4 PGM stride is positive.
/// Dogfood: 4x4 PPM stride is at least width * 3.
/// </summary>
public class NetpbmR472GetRowStrideBytesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowStrideBytes_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.True(img.GetRowStrideBytes() > 0);
    }

    [Fact]
    public void GetRowStrideBytes_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetRowStrideBytes();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetRowStrideBytes_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetRowStrideBytes();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetRowStrideBytes_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetRowStrideBytes();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetRowStrideBytes_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetRowStrideBytes();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetRowStrideBytes_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int first = img.GetRowStrideBytes();
        int second = img.GetRowStrideBytes();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetRowStrideBytes_PBM_Positive()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.True(img.GetRowStrideBytes() > 0);
    }

    [Fact]
    public void GetRowStrideBytes_PGM_Positive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.True(img.GetRowStrideBytes() > 0);
    }

    [Fact]
    public void GetRowStrideBytes_PPM_Positive()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.True(img.GetRowStrideBytes() > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_StrideIsPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.True(img.GetRowStrideBytes() > 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_StrideAtLeastWidthTimesThree()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.True(img.GetRowStrideBytes() >= img.Width * 3);
    }
}
