// Tests for NetpbmImage.GetAspectRatio dedicated coverage.
// Sprint: ff-sprint-s492-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R510

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R510: Dedicated tests for NetpbmImage.GetAspectRatio().
/// PBM square image returns 1.0 aspect ratio.
/// PGM square image returns 1.0 aspect ratio.
/// PPM square image returns 1.0 aspect ratio.
/// Width unchanged after GetAspectRatio.
/// Height unchanged after GetAspectRatio.
/// Format unchanged after GetAspectRatio.
/// MaxValue unchanged after GetAspectRatio.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline aspect ratio is positive.
/// Dogfood: PGM pipeline aspect ratio is positive.
/// Dogfood: PPM pipeline aspect ratio is positive.
/// </summary>
public class NetpbmR510GetAspectRatioDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAspectRatio_PbmSquareImage_ReturnsOne()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.Equal(1.0, img.GetAspectRatio(), precision: 5);
    }

    [Fact]
    public void GetAspectRatio_PgmSquareImage_ReturnsOne()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.Equal(1.0, img.GetAspectRatio(), precision: 5);
    }

    [Fact]
    public void GetAspectRatio_PpmSquareImage_ReturnsOne()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.Equal(1.0, img.GetAspectRatio(), precision: 5);
    }

    [Fact]
    public void GetAspectRatio_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetAspectRatio_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetAspectRatio_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetAspectRatio_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetAspectRatio_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        double first = img.GetAspectRatio();
        double second = img.GetAspectRatio();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_AspectRatioIsPositive()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        double result = img.GetAspectRatio();
        Assert.True(result > 0);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_AspectRatioIsPositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        double result = img.GetAspectRatio();
        Assert.True(result > 0);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_AspectRatioIsPositive()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        double result = img.GetAspectRatio();
        Assert.True(result > 0);
    }
}
