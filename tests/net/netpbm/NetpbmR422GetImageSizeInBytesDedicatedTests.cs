// Tests for NetpbmImage.GetImageSizeInBytes dedicated coverage.
// Sprint: ff-sprint-s404-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R422

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R422: Dedicated tests for NetpbmImage.GetImageSizeInBytes().
/// Returns positive value.
/// Width unchanged after GetImageSizeInBytes.
/// Height unchanged after GetImageSizeInBytes.
/// Format unchanged after GetImageSizeInBytes.
/// MaxValue unchanged after GetImageSizeInBytes.
/// Idempotent (called twice same result).
/// PBM size positive.
/// PGM size positive.
/// PPM size positive.
/// Dogfood: 4x4 PGM size positive.
/// Dogfood: 4x4 PPM size positive.
/// </summary>
public class NetpbmR422GetImageSizeInBytesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImageSizeInBytes_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        long size = img.GetImageSizeInBytes();
        Assert.True(size > 0);
    }

    [Fact]
    public void GetImageSizeInBytes_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetImageSizeInBytes();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetImageSizeInBytes_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetImageSizeInBytes();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetImageSizeInBytes_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetImageSizeInBytes();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetImageSizeInBytes_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetImageSizeInBytes();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetImageSizeInBytes_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        long first = img.GetImageSizeInBytes();
        long second = img.GetImageSizeInBytes();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetImageSizeInBytes_PBM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetImageSizeInBytes() > 0);
    }

    [Fact]
    public void GetImageSizeInBytes_PGM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetImageSizeInBytes() > 0);
    }

    [Fact]
    public void GetImageSizeInBytes_PPM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetImageSizeInBytes() > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_SizePositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetImageSizeInBytes() > 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_SizePositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetImageSizeInBytes() > 0);
    }
}
