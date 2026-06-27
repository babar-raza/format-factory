// Tests for NetpbmImage.GetColorDepth dedicated coverage.
// Sprint: ff-sprint-s362-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R375

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R375: Dedicated tests for NetpbmImage.GetColorDepth().
/// Valid image returns positive value.
/// PBM image returns positive.
/// PGM image returns positive.
/// PPM image returns positive.
/// Width unchanged after GetColorDepth.
/// Height unchanged after GetColorDepth.
/// Format unchanged after GetColorDepth.
/// MaxValue unchanged after GetColorDepth.
/// Idempotent (called twice same result).
/// Dogfood: 1x1 PBM returns positive.
/// </summary>
public class NetpbmR375GetColorDepthDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorDepth_ValidImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int depth = img.GetColorDepth();
        Assert.True(depth > 0);
    }

    [Fact]
    public void GetColorDepth_PbmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        int depth = img.GetColorDepth();
        Assert.True(depth > 0);
    }

    [Fact]
    public void GetColorDepth_PgmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int depth = img.GetColorDepth();
        Assert.True(depth > 0);
    }

    [Fact]
    public void GetColorDepth_PpmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int depth = img.GetColorDepth();
        Assert.True(depth > 0);
    }

    [Fact]
    public void GetColorDepth_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetColorDepth();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetColorDepth_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
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

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_OneByOnePbm_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(1, 1, NetpbmFormat.PBM);
        img.SetPixel(0, 0, 1);
        int depth = img.GetColorDepth();
        Assert.True(depth > 0);
    }
}
