// Tests for NetpbmImage.GetMaxSupportedHeight dedicated coverage.
// Sprint: ff-sprint-s501-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R519

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R519: Dedicated tests for NetpbmImage.GetMaxSupportedHeight().
/// PBM image max supported height is positive.
/// PGM image max supported height is positive.
/// PPM image max supported height is positive.
/// Width unchanged after GetMaxSupportedHeight.
/// Height unchanged after GetMaxSupportedHeight.
/// Format unchanged after GetMaxSupportedHeight.
/// MaxValue unchanged after GetMaxSupportedHeight.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline max height is at least 1.
/// Dogfood: PGM pipeline max height is at least 1.
/// Dogfood: PPM pipeline max height is at least 1.
/// </summary>
public class NetpbmR519GetMaxSupportedHeightDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMaxSupportedHeight_PbmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetMaxSupportedHeight() > 0);
    }

    [Fact]
    public void GetMaxSupportedHeight_PgmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetMaxSupportedHeight() > 0);
    }

    [Fact]
    public void GetMaxSupportedHeight_PpmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetMaxSupportedHeight() > 0);
    }

    [Fact]
    public void GetMaxSupportedHeight_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetMaxSupportedHeight();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMaxSupportedHeight_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetMaxSupportedHeight();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMaxSupportedHeight_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetMaxSupportedHeight();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMaxSupportedHeight_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetMaxSupportedHeight();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMaxSupportedHeight_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetMaxSupportedHeight();
        int second = img.GetMaxSupportedHeight();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_MaxHeightAtLeastOne()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        int result = img.GetMaxSupportedHeight();
        Assert.True(result >= 1);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_MaxHeightAtLeastOne()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int result = img.GetMaxSupportedHeight();
        Assert.True(result >= 1);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_MaxHeightAtLeastOne()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        int result = img.GetMaxSupportedHeight();
        Assert.True(result >= 1);
    }
}
