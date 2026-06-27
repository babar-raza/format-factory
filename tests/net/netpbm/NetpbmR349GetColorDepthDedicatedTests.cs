// Tests for NetpbmImage.GetColorDepth dedicated coverage.
// Sprint: ff-sprint-s336-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R349

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R349: Dedicated tests for NetpbmImage.GetColorDepth().
/// Valid image ok.
/// Returns positive value.
/// Width unchanged after GetColorDepth.
/// Height unchanged after GetColorDepth.
/// Format unchanged after GetColorDepth.
/// MaxValue unchanged after GetColorDepth.
/// PGM MaxValue 255 returns 256 color depth.
/// PGM MaxValue 15 returns 16 color depth.
/// Idempotent (called twice same result).
/// Dogfood: PPM returns 256 color depth.
/// </summary>
public class NetpbmR349GetColorDepthDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorDepth_ValidImage_Ok()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        var ex = Record.Exception(() => img.GetColorDepth());
        Assert.Null(ex);
    }

    [Fact]
    public void GetColorDepth_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int depth = img.GetColorDepth();
        Assert.True(depth > 0);
    }

    [Fact]
    public void GetColorDepth_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Width;
        _ = img.GetColorDepth();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetColorDepth_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Height;
        _ = img.GetColorDepth();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetColorDepth_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        string before = img.Format;
        _ = img.GetColorDepth();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetColorDepth_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.MaxValue;
        _ = img.GetColorDepth();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetColorDepth_PgmMaxValue255_Returns256()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int depth = img.GetColorDepth();
        Assert.Equal(256, depth);
    }

    [Fact]
    public void GetColorDepth_PgmMaxValue15_Returns16()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 15);
        int depth = img.GetColorDepth();
        Assert.Equal(16, depth);
    }

    [Fact]
    public void GetColorDepth_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreatePgm(6, 6, 255);
        int first = img.GetColorDepth();
        int second = img.GetColorDepth();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PpmMaxValue255_Returns256()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        int depth = img.GetColorDepth();
        Assert.Equal(256, depth);
    }
}
