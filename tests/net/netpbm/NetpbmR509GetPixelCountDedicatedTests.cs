// Tests for NetpbmImage.GetPixelCount dedicated coverage.
// Sprint: ff-sprint-s491-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R509

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R509: Dedicated tests for NetpbmImage.GetPixelCount().
/// PBM 4x4 image returns 16 pixels.
/// PGM 4x4 image returns 16 pixels.
/// PPM 4x4 image returns 16 pixels.
/// Width unchanged after GetPixelCount.
/// Height unchanged after GetPixelCount.
/// Format unchanged after GetPixelCount.
/// MaxValue unchanged after GetPixelCount.
/// Idempotent (called twice same result).
/// Dogfood: PBM 8x8 pipeline returns 64.
/// Dogfood: PGM 8x8 pipeline returns 64.
/// Dogfood: PPM 8x8 pipeline returns 64.
/// </summary>
public class NetpbmR509GetPixelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelCount_PbmImage_ReturnsSixteen()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.Equal(16, img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_PgmImage_ReturnsSixteen()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.Equal(16, img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_PpmImage_ReturnsSixteen()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.Equal(16, img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetPixelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelCount_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetPixelCount();
        int second = img.GetPixelCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ReturnsSixtyFour()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        int result = img.GetPixelCount();
        Assert.Equal(64, result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ReturnsSixtyFour()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int result = img.GetPixelCount();
        Assert.Equal(64, result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ReturnsSixtyFour()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        int result = img.GetPixelCount();
        Assert.Equal(64, result);
    }
}
