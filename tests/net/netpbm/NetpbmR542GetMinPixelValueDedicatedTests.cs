// Tests for NetpbmImage.GetMinPixelValue dedicated coverage.
// Sprint: ff-sprint-s524-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R542

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R542: Dedicated tests for NetpbmImage.GetMinPixelValue().
/// PBM image returns 0 (minimum pixel value is 0).
/// PGM image returns 0 (minimum pixel value is 0).
/// PPM image returns 0 (minimum pixel value is 0).
/// Width unchanged after GetMinPixelValue.
/// Height unchanged after GetMinPixelValue.
/// Format unchanged after GetMinPixelValue.
/// MaxValue unchanged after GetMinPixelValue.
/// Idempotent (called twice same result).
/// Dogfood: PBM min value is 0.
/// Dogfood: PGM min value is 0.
/// Dogfood: PPM min value is 0.
/// </summary>
public class NetpbmR542GetMinPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMinPixelValue_PbmImage_Returns0()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.Equal(0, img.GetMinPixelValue());
    }

    [Fact]
    public void GetMinPixelValue_PgmImage_Returns0()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.Equal(0, img.GetMinPixelValue());
    }

    [Fact]
    public void GetMinPixelValue_PpmImage_Returns0()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.Equal(0, img.GetMinPixelValue());
    }

    [Fact]
    public void GetMinPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMinPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMinPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMinPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMinPixelValue_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetMinPixelValue();
        int second = img.GetMinPixelValue();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_MinIs0()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        Assert.Equal(0, img.GetMinPixelValue());
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_MinIs0()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        Assert.Equal(0, img.GetMinPixelValue());
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_MinIs0()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        Assert.Equal(0, img.GetMinPixelValue());
    }
}
