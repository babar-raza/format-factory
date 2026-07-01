// Tests for NetpbmImage.GetColorPrecision dedicated coverage.
// Sprint: ff-sprint-s523-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R541

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R541: Dedicated tests for NetpbmImage.GetColorPrecision().
/// PBM image returns 1 (1-bit precision).
/// PGM image returns 8 (8-bit precision).
/// PPM image returns 8 (8 bits per channel).
/// Width unchanged after GetColorPrecision.
/// Height unchanged after GetColorPrecision.
/// Format unchanged after GetColorPrecision.
/// MaxValue unchanged after GetColorPrecision.
/// Idempotent (called twice same result).
/// Dogfood: PBM precision is 1.
/// Dogfood: PGM precision is 8.
/// Dogfood: PPM precision is 8.
/// </summary>
public class NetpbmR541GetColorPrecisionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorPrecision_PbmImage_Returns1()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.Equal(1, img.GetColorPrecision());
    }

    [Fact]
    public void GetColorPrecision_PgmImage_Returns8()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.Equal(8, img.GetColorPrecision());
    }

    [Fact]
    public void GetColorPrecision_PpmImage_Returns8()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.Equal(8, img.GetColorPrecision());
    }

    [Fact]
    public void GetColorPrecision_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetColorPrecision();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetColorPrecision_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetColorPrecision();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetColorPrecision_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetColorPrecision();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetColorPrecision_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetColorPrecision();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetColorPrecision_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetColorPrecision();
        int second = img.GetColorPrecision();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_PrecisionIs1()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        Assert.Equal(1, img.GetColorPrecision());
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_PrecisionIs8()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        Assert.Equal(8, img.GetColorPrecision());
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_PrecisionIs8()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        Assert.Equal(8, img.GetColorPrecision());
    }
}
