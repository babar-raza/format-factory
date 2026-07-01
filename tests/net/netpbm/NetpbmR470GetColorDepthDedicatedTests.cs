// Tests for NetpbmImage.GetColorDepth dedicated coverage.
// Sprint: ff-sprint-s452-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R470

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R470: Dedicated tests for NetpbmImage.GetColorDepth().
/// PBM returns 1 (binary).
/// PGM returns value based on MaxValue.
/// PPM returns value based on MaxValue.
/// Width unchanged after GetColorDepth.
/// Height unchanged after GetColorDepth.
/// Format unchanged after GetColorDepth.
/// MaxValue unchanged after GetColorDepth.
/// Idempotent (called twice same result).
/// Dogfood: PGM 255 MaxValue depth is 8.
/// Dogfood: PPM 255 MaxValue depth is 8.
/// Dogfood: PGM 65535 MaxValue depth is 16.
/// </summary>
public class NetpbmR470GetColorDepthDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorDepth_PBM_ReturnsOne()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        int depth = img.GetColorDepth();
        Assert.Equal(1, depth);
    }

    [Fact]
    public void GetColorDepth_PGM_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int depth = img.GetColorDepth();
        Assert.True(depth > 0);
    }

    [Fact]
    public void GetColorDepth_PPM_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        int depth = img.GetColorDepth();
        Assert.True(depth > 0);
    }

    [Fact]
    public void GetColorDepth_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetColorDepth();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetColorDepth_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetColorDepth();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetColorDepth_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetColorDepth();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetColorDepth_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetColorDepth();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetColorDepth_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int first = img.GetColorDepth();
        int second = img.GetColorDepth();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PGM255MaxValue_DepthIsEight()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.Equal(8, img.GetColorDepth());
    }

    [Fact]
    public void DogfoodPipeline_PPM255MaxValue_DepthIsEight()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.Equal(8, img.GetColorDepth());
    }

    [Fact]
    public void DogfoodPipeline_PGM65535MaxValue_DepthIsSixteen()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 65535);
        Assert.Equal(16, img.GetColorDepth());
    }
}
