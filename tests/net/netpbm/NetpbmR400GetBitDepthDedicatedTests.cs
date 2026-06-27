// Tests for NetpbmImage.GetBitDepth dedicated coverage.
// Sprint: ff-sprint-s387-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R400

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R400: Dedicated tests for NetpbmImage.GetBitDepth().
/// PBM returns 1.
/// PGM returns positive value.
/// PPM returns positive value.
/// Width unchanged after GetBitDepth.
/// Height unchanged after GetBitDepth.
/// Format unchanged after GetBitDepth.
/// MaxValue unchanged after GetBitDepth.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PBM bit depth = 1.
/// Dogfood: 4x4 PGM bit depth positive.
/// Dogfood: 4x4 PPM bit depth positive.
/// </summary>
public class NetpbmR400GetBitDepthDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBitDepth_PBM_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        int bitDepth = img.GetBitDepth();
        Assert.Equal(1, bitDepth);
    }

    [Fact]
    public void GetBitDepth_PGM_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int bitDepth = img.GetBitDepth();
        Assert.True(bitDepth > 0);
    }

    [Fact]
    public void GetBitDepth_PPM_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int bitDepth = img.GetBitDepth();
        Assert.True(bitDepth > 0);
    }

    [Fact]
    public void GetBitDepth_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetBitDepth();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetBitDepth_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PPM);
        int before = img.Height;
        _ = img.GetBitDepth();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetBitDepth_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetBitDepth();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetBitDepth_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetBitDepth();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetBitDepth_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetBitDepth();
        int second = img.GetBitDepth();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPBM_BitDepthOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        int bitDepth = img.GetBitDepth();
        Assert.Equal(1, bitDepth);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_BitDepthPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int bitDepth = img.GetBitDepth();
        Assert.True(bitDepth > 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_BitDepthPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int bitDepth = img.GetBitDepth();
        Assert.True(bitDepth > 0);
    }
}
