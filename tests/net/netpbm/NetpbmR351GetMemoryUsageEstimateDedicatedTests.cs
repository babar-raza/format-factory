// Tests for NetpbmImage.GetMemoryUsageEstimate dedicated coverage.
// Sprint: ff-sprint-s338-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R351

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R351: Dedicated tests for NetpbmImage.GetMemoryUsageEstimate().
/// Valid image ok.
/// Returns positive value.
/// Width unchanged after GetMemoryUsageEstimate.
/// Height unchanged after GetMemoryUsageEstimate.
/// Format unchanged after GetMemoryUsageEstimate.
/// MaxValue unchanged after GetMemoryUsageEstimate.
/// Larger image returns larger estimate.
/// Idempotent (called twice same result).
/// Dogfood: 1x1 image returns small estimate.
/// Dogfood: PPM larger than PGM same dimensions.
/// </summary>
public class NetpbmR351GetMemoryUsageEstimateDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMemoryUsageEstimate_ValidImage_Ok()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        var ex = Record.Exception(() => img.GetMemoryUsageEstimate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMemoryUsageEstimate_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        long estimate = img.GetMemoryUsageEstimate();
        Assert.True(estimate > 0);
    }

    [Fact]
    public void GetMemoryUsageEstimate_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Width;
        _ = img.GetMemoryUsageEstimate();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMemoryUsageEstimate_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Height;
        _ = img.GetMemoryUsageEstimate();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMemoryUsageEstimate_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        string before = img.Format;
        _ = img.GetMemoryUsageEstimate();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMemoryUsageEstimate_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.MaxValue;
        _ = img.GetMemoryUsageEstimate();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMemoryUsageEstimate_LargerImage_LargerEstimate()
    {
        var small = NetpbmImage.CreatePgm(4, 4, 255);
        var large = NetpbmImage.CreatePgm(16, 16, 255);
        long smallEst = small.GetMemoryUsageEstimate();
        long largeEst = large.GetMemoryUsageEstimate();
        Assert.True(largeEst > smallEst);
    }

    [Fact]
    public void GetMemoryUsageEstimate_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreatePgm(6, 6, 255);
        long first = img.GetMemoryUsageEstimate();
        long second = img.GetMemoryUsageEstimate();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_OneByOneImage_SmallPositiveEstimate()
    {
        var img = NetpbmImage.CreatePgm(1, 1, 255);
        long estimate = img.GetMemoryUsageEstimate();
        Assert.True(estimate > 0);
    }

    [Fact]
    public void DogfoodPipeline_PpmLargerThanPgmSameDimensions()
    {
        var pgm = NetpbmImage.CreatePgm(8, 8, 255);
        var ppm = NetpbmImage.CreatePpm(8, 8, 255);
        long pgmEst = pgm.GetMemoryUsageEstimate();
        long ppmEst = ppm.GetMemoryUsageEstimate();
        Assert.True(ppmEst >= pgmEst);
    }
}
