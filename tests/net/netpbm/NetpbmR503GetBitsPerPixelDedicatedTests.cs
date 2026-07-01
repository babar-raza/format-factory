// Tests for NetpbmImage.GetBitsPerPixel dedicated coverage.
// Sprint: ff-sprint-s485-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R503

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R503: Dedicated tests for NetpbmImage.GetBitsPerPixel().
/// PBM image returns 1 (one bit per pixel).
/// PGM image with maxval 255 returns 8 (8 bits per pixel).
/// PPM image with maxval 255 returns 24 (8 bits x 3 channels).
/// Width unchanged after GetBitsPerPixel.
/// Height unchanged after GetBitsPerPixel.
/// Format unchanged after GetBitsPerPixel.
/// MaxValue unchanged after GetBitsPerPixel.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline returns 1.
/// Dogfood: PGM pipeline returns 8.
/// Dogfood: PPM pipeline returns 24.
/// </summary>
public class NetpbmR503GetBitsPerPixelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBitsPerPixel_PbmImage_ReturnsOne()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.Equal(1, img.GetBitsPerPixel());
    }

    [Fact]
    public void GetBitsPerPixel_PgmImage_ReturnsEight()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.Equal(8, img.GetBitsPerPixel());
    }

    [Fact]
    public void GetBitsPerPixel_PpmImage_ReturnsTwentyFour()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.Equal(24, img.GetBitsPerPixel());
    }

    [Fact]
    public void GetBitsPerPixel_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetBitsPerPixel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetBitsPerPixel_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetBitsPerPixel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetBitsPerPixel_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetBitsPerPixel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetBitsPerPixel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetBitsPerPixel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetBitsPerPixel_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetBitsPerPixel();
        int second = img.GetBitsPerPixel();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ReturnsOne()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        int result = img.GetBitsPerPixel();
        Assert.Equal(1, result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ReturnsEight()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int result = img.GetBitsPerPixel();
        Assert.Equal(8, result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ReturnsTwentyFour()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        int result = img.GetBitsPerPixel();
        Assert.Equal(24, result);
    }
}
