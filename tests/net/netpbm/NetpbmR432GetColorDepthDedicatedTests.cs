// Tests for NetpbmImage.GetColorDepth dedicated coverage.
// Sprint: ff-sprint-s414-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R432

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R432: Dedicated tests for NetpbmImage.GetColorDepth().
/// Returns positive value.
/// PBM color depth positive.
/// PGM color depth positive.
/// PPM color depth positive.
/// Width unchanged after GetColorDepth.
/// Height unchanged after GetColorDepth.
/// Format unchanged after GetColorDepth.
/// MaxValue unchanged after GetColorDepth.
/// Idempotent (called twice same result).
/// PPM color depth >= PGM color depth.
/// Dogfood: 4x4 PGM color depth positive.
/// </summary>
public class NetpbmR432GetColorDepthDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorDepth_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int depth = img.GetColorDepth();
        Assert.True(depth > 0);
    }

    [Fact]
    public void GetColorDepth_PBM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetColorDepth() > 0);
    }

    [Fact]
    public void GetColorDepth_PGM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetColorDepth() > 0);
    }

    [Fact]
    public void GetColorDepth_PPM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetColorDepth() > 0);
    }

    [Fact]
    public void GetColorDepth_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetColorDepth();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetColorDepth_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetColorDepth();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetColorDepth_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetColorDepth();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetColorDepth_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetColorDepth();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetColorDepth_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetColorDepth();
        int second = img.GetColorDepth();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColorDepth_PPM_AtLeastPGM()
    {
        var pgm = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        var ppm = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(ppm.GetColorDepth() >= pgm.GetColorDepth());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ColorDepthPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int depth = img.GetColorDepth();
        Assert.True(depth > 0);
    }
}
