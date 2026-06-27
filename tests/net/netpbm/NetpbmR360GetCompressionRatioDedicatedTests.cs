// Tests for NetpbmImage.GetCompressionRatio dedicated coverage.
// Sprint: ff-sprint-s347-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R360

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R360: Dedicated tests for NetpbmImage.GetCompressionRatio().
/// Valid image returns ok.
/// Result is positive.
/// Width unchanged after GetCompressionRatio.
/// Height unchanged after GetCompressionRatio.
/// Format unchanged after GetCompressionRatio.
/// MaxValue unchanged after GetCompressionRatio.
/// Larger image same format same ratio category.
/// Idempotent (called twice same result).
/// Dogfood: PBM image returns valid ratio.
/// Dogfood: PPM image returns valid ratio.
/// </summary>
public class NetpbmR360GetCompressionRatioDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionRatio_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        double ratio = img.GetCompressionRatio();
        Assert.True(ratio > 0.0);
    }

    [Fact]
    public void GetCompressionRatio_ResultIsPositive()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM, 255);
        double ratio = img.GetCompressionRatio();
        Assert.True(ratio > 0.0);
    }

    [Fact]
    public void GetCompressionRatio_WidthUnchanged()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetCompressionRatio();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetCompressionRatio_HeightUnchanged()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetCompressionRatio();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetCompressionRatio_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM, 255);
        var before = img.Format;
        _ = img.GetCompressionRatio();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetCompressionRatio_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 200);
        int before = img.MaxValue;
        _ = img.GetCompressionRatio();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetCompressionRatio_Idempotent()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM, 255);
        double first = img.GetCompressionRatio();
        double second = img.GetCompressionRatio();
        Assert.Equal(first, second, precision: 10);
    }

    [Fact]
    public void GetCompressionRatio_SmallAndLargeSameFormat_BothPositive()
    {
        var small = NetpbmImage.Create(2, 2, NetpbmFormat.PGM, 255);
        var large = NetpbmImage.Create(20, 20, NetpbmFormat.PGM, 255);
        double smallRatio = small.GetCompressionRatio();
        double largeRatio = large.GetCompressionRatio();
        Assert.True(smallRatio > 0.0);
        Assert.True(largeRatio > 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ReturnsValidRatio()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PBM, 1);
        img.FillWithValue(0);
        double ratio = img.GetCompressionRatio();
        Assert.True(ratio > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ReturnsValidRatio()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM, 255);
        img.FillWithValue(128);
        double ratio = img.GetCompressionRatio();
        Assert.True(ratio > 0.0);
    }
}
