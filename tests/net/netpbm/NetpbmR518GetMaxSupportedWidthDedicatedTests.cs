// Tests for NetpbmImage.GetMaxSupportedWidth dedicated coverage.
// Sprint: ff-sprint-s500-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R518

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R518: Dedicated tests for NetpbmImage.GetMaxSupportedWidth().
/// PBM image max supported width is positive.
/// PGM image max supported width is positive.
/// PPM image max supported width is positive.
/// Width unchanged after GetMaxSupportedWidth.
/// Height unchanged after GetMaxSupportedWidth.
/// Format unchanged after GetMaxSupportedWidth.
/// MaxValue unchanged after GetMaxSupportedWidth.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline max width is at least 1.
/// Dogfood: PGM pipeline max width is at least 1.
/// Dogfood: PPM pipeline max width is at least 1.
/// </summary>
public class NetpbmR518GetMaxSupportedWidthDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMaxSupportedWidth_PbmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetMaxSupportedWidth() > 0);
    }

    [Fact]
    public void GetMaxSupportedWidth_PgmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetMaxSupportedWidth() > 0);
    }

    [Fact]
    public void GetMaxSupportedWidth_PpmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetMaxSupportedWidth() > 0);
    }

    [Fact]
    public void GetMaxSupportedWidth_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetMaxSupportedWidth();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMaxSupportedWidth_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetMaxSupportedWidth();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMaxSupportedWidth_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetMaxSupportedWidth();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMaxSupportedWidth_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetMaxSupportedWidth();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMaxSupportedWidth_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetMaxSupportedWidth();
        int second = img.GetMaxSupportedWidth();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_MaxWidthAtLeastOne()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        int result = img.GetMaxSupportedWidth();
        Assert.True(result >= 1);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_MaxWidthAtLeastOne()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int result = img.GetMaxSupportedWidth();
        Assert.True(result >= 1);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_MaxWidthAtLeastOne()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        int result = img.GetMaxSupportedWidth();
        Assert.True(result >= 1);
    }
}
