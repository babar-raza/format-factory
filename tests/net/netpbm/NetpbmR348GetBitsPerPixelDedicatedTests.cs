// Tests for NetpbmImage.GetBitsPerPixel dedicated coverage.
// Sprint: ff-sprint-s335-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R348

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R348: Dedicated tests for NetpbmImage.GetBitsPerPixel().
/// Valid image ok.
/// Returns positive value.
/// Width unchanged after GetBitsPerPixel.
/// Height unchanged after GetBitsPerPixel.
/// Format unchanged after GetBitsPerPixel.
/// MaxValue unchanged after GetBitsPerPixel.
/// PBM image returns 1 bit per pixel.
/// PGM image with MaxValue 255 returns 8 bits per pixel.
/// Idempotent (called twice same result).
/// Dogfood: PPM image returns at least 8 bits per pixel.
/// </summary>
public class NetpbmR348GetBitsPerPixelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBitsPerPixel_ValidImage_Ok()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        var ex = Record.Exception(() => img.GetBitsPerPixel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBitsPerPixel_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int bpp = img.GetBitsPerPixel();
        Assert.True(bpp > 0);
    }

    [Fact]
    public void GetBitsPerPixel_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Width;
        _ = img.GetBitsPerPixel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetBitsPerPixel_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Height;
        _ = img.GetBitsPerPixel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetBitsPerPixel_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        string before = img.Format;
        _ = img.GetBitsPerPixel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetBitsPerPixel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.MaxValue;
        _ = img.GetBitsPerPixel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetBitsPerPixel_PbmImage_ReturnsOne()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        int bpp = img.GetBitsPerPixel();
        Assert.Equal(1, bpp);
    }

    [Fact]
    public void GetBitsPerPixel_PgmMaxValue255_ReturnsEight()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int bpp = img.GetBitsPerPixel();
        Assert.Equal(8, bpp);
    }

    [Fact]
    public void GetBitsPerPixel_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreatePgm(6, 6, 255);
        int first = img.GetBitsPerPixel();
        int second = img.GetBitsPerPixel();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PpmImage_AtLeastEight()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        int bpp = img.GetBitsPerPixel();
        Assert.True(bpp >= 8);
    }
}
