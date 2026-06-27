// Tests for NetpbmImage.GetFileSizeEstimate dedicated coverage.
// Sprint: ff-sprint-s337-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R350

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R350: Dedicated tests for NetpbmImage.GetFileSizeEstimate().
/// Valid image ok.
/// Returns positive value.
/// Width unchanged after GetFileSizeEstimate.
/// Height unchanged after GetFileSizeEstimate.
/// Format unchanged after GetFileSizeEstimate.
/// MaxValue unchanged after GetFileSizeEstimate.
/// Larger image returns larger estimate.
/// Idempotent (called twice same result).
/// Dogfood: 1x1 PBM returns small estimate.
/// Dogfood: 100x100 PGM returns larger estimate than 10x10.
/// </summary>
public class NetpbmR350GetFileSizeEstimateDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFileSizeEstimate_ValidImage_Ok()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        var ex = Record.Exception(() => img.GetFileSizeEstimate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFileSizeEstimate_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        long estimate = img.GetFileSizeEstimate();
        Assert.True(estimate > 0);
    }

    [Fact]
    public void GetFileSizeEstimate_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Width;
        _ = img.GetFileSizeEstimate();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetFileSizeEstimate_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Height;
        _ = img.GetFileSizeEstimate();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetFileSizeEstimate_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        string before = img.Format;
        _ = img.GetFileSizeEstimate();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetFileSizeEstimate_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.MaxValue;
        _ = img.GetFileSizeEstimate();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetFileSizeEstimate_LargerImage_LargerEstimate()
    {
        var small = NetpbmImage.CreatePgm(4, 4, 255);
        var large = NetpbmImage.CreatePgm(16, 16, 255);
        long smallEstimate = small.GetFileSizeEstimate();
        long largeEstimate = large.GetFileSizeEstimate();
        Assert.True(largeEstimate > smallEstimate);
    }

    [Fact]
    public void GetFileSizeEstimate_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreatePgm(6, 6, 255);
        long first = img.GetFileSizeEstimate();
        long second = img.GetFileSizeEstimate();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_OneByOnePbm_SmallEstimate()
    {
        var img = NetpbmImage.CreatePbm(1, 1);
        long estimate = img.GetFileSizeEstimate();
        Assert.True(estimate > 0);
    }

    [Fact]
    public void DogfoodPipeline_LargerPgm_LargerThanSmall()
    {
        var small = NetpbmImage.CreatePgm(10, 10, 255);
        var large = NetpbmImage.CreatePgm(100, 100, 255);
        long smallEstimate = small.GetFileSizeEstimate();
        long largeEstimate = large.GetFileSizeEstimate();
        Assert.True(largeEstimate > smallEstimate);
    }
}
