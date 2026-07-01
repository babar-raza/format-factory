// Tests for NetpbmImage.GetColorSpace dedicated coverage.
// Sprint: ff-sprint-s494-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R512

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R512: Dedicated tests for NetpbmImage.GetColorSpace().
/// PBM image returns "Gray" (monochrome color space).
/// PGM image returns "Gray" (grayscale color space).
/// PPM image returns "RGB" (color space).
/// Width unchanged after GetColorSpace.
/// Height unchanged after GetColorSpace.
/// Format unchanged after GetColorSpace.
/// MaxValue unchanged after GetColorSpace.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline color space is "Gray".
/// Dogfood: PGM pipeline color space is "Gray".
/// Dogfood: PPM pipeline color space is "RGB".
/// </summary>
public class NetpbmR512GetColorSpaceDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorSpace_PbmImage_ReturnsGray()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.Equal("Gray", img.GetColorSpace());
    }

    [Fact]
    public void GetColorSpace_PgmImage_ReturnsGray()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.Equal("Gray", img.GetColorSpace());
    }

    [Fact]
    public void GetColorSpace_PpmImage_ReturnsRgb()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.Equal("RGB", img.GetColorSpace());
    }

    [Fact]
    public void GetColorSpace_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetColorSpace();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetColorSpace_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetColorSpace();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetColorSpace_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetColorSpace();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetColorSpace_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetColorSpace();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetColorSpace_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        string first = img.GetColorSpace();
        string second = img.GetColorSpace();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ColorSpaceIsGray()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        string result = img.GetColorSpace();
        Assert.Equal("Gray", result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ColorSpaceIsGray()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        string result = img.GetColorSpace();
        Assert.Equal("Gray", result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ColorSpaceIsRgb()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        string result = img.GetColorSpace();
        Assert.Equal("RGB", result);
    }
}
