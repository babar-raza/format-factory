// Tests for NetpbmImage.GetMaxPixelValue dedicated coverage.
// Sprint: ff-sprint-s525-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R543

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R543: Dedicated tests for NetpbmImage.GetMaxPixelValue().
/// PBM image returns 1 (max pixel value for bitmap).
/// PGM image returns 255 (max pixel value for standard graymap).
/// PPM image returns 255 (max pixel value per channel).
/// Width unchanged after GetMaxPixelValue.
/// Height unchanged after GetMaxPixelValue.
/// Format unchanged after GetMaxPixelValue.
/// MaxValue unchanged after GetMaxPixelValue.
/// Idempotent (called twice same result).
/// Dogfood: PBM max pixel value is 1.
/// Dogfood: PGM max pixel value is 255.
/// Dogfood: PPM max pixel value is 255.
/// </summary>
public class NetpbmR543GetMaxPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMaxPixelValue_PbmImage_Returns1()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.Equal(1, img.GetMaxPixelValue());
    }

    [Fact]
    public void GetMaxPixelValue_PgmImage_Returns255()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.Equal(255, img.GetMaxPixelValue());
    }

    [Fact]
    public void GetMaxPixelValue_PpmImage_Returns255()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.Equal(255, img.GetMaxPixelValue());
    }

    [Fact]
    public void GetMaxPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMaxPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMaxPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMaxPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMaxPixelValue_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetMaxPixelValue();
        int second = img.GetMaxPixelValue();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_MaxIs1()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        Assert.Equal(1, img.GetMaxPixelValue());
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_MaxIs255()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        Assert.Equal(255, img.GetMaxPixelValue());
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_MaxIs255()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        Assert.Equal(255, img.GetMaxPixelValue());
    }
}
