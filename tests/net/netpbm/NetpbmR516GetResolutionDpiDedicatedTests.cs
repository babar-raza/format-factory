// Tests for NetpbmImage.GetResolutionDpi dedicated coverage.
// Sprint: ff-sprint-s498-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R516

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R516: Dedicated tests for NetpbmImage.GetResolutionDpi().
/// PBM image resolution is positive.
/// PGM image resolution is positive.
/// PPM image resolution is positive.
/// Width unchanged after GetResolutionDpi.
/// Height unchanged after GetResolutionDpi.
/// Format unchanged after GetResolutionDpi.
/// MaxValue unchanged after GetResolutionDpi.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline resolution is positive.
/// Dogfood: PGM pipeline resolution is positive.
/// Dogfood: PPM pipeline resolution is positive.
/// </summary>
public class NetpbmR516GetResolutionDpiDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetResolutionDpi_PbmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetResolutionDpi() > 0);
    }

    [Fact]
    public void GetResolutionDpi_PgmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetResolutionDpi() > 0);
    }

    [Fact]
    public void GetResolutionDpi_PpmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetResolutionDpi() > 0);
    }

    [Fact]
    public void GetResolutionDpi_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetResolutionDpi();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetResolutionDpi_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetResolutionDpi();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetResolutionDpi_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetResolutionDpi();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetResolutionDpi_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetResolutionDpi();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetResolutionDpi_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetResolutionDpi();
        int second = img.GetResolutionDpi();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ResolutionIsPositive()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        int result = img.GetResolutionDpi();
        Assert.True(result > 0);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ResolutionIsPositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int result = img.GetResolutionDpi();
        Assert.True(result > 0);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ResolutionIsPositive()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        int result = img.GetResolutionDpi();
        Assert.True(result > 0);
    }
}
