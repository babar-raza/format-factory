// Tests for NetpbmImage.GetBytesPerPixel dedicated coverage.
// Sprint: ff-sprint-s529-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R547

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R547: Dedicated tests for NetpbmImage.GetBytesPerPixel().
/// PBM image returns 1 (1 byte per pixel for bitmap storage).
/// PGM image returns 1 (1 byte per pixel for grayscale).
/// PPM image returns 3 (3 bytes per pixel for RGB).
/// Width unchanged after GetBytesPerPixel.
/// Height unchanged after GetBytesPerPixel.
/// Format unchanged after GetBytesPerPixel.
/// MaxValue unchanged after GetBytesPerPixel.
/// Idempotent (called twice same result).
/// Dogfood: PBM bytes per pixel is 1.
/// Dogfood: PGM bytes per pixel is 1.
/// Dogfood: PPM bytes per pixel is 3.
/// </summary>
public class NetpbmR547GetBytesPerPixelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBytesPerPixel_PbmImage_Returns1()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.Equal(1, img.GetBytesPerPixel());
    }

    [Fact]
    public void GetBytesPerPixel_PgmImage_Returns1()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.Equal(1, img.GetBytesPerPixel());
    }

    [Fact]
    public void GetBytesPerPixel_PpmImage_Returns3()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.Equal(3, img.GetBytesPerPixel());
    }

    [Fact]
    public void GetBytesPerPixel_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetBytesPerPixel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetBytesPerPixel_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetBytesPerPixel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetBytesPerPixel_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetBytesPerPixel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetBytesPerPixel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetBytesPerPixel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetBytesPerPixel_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetBytesPerPixel();
        int second = img.GetBytesPerPixel();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_BytesPerPixelIs1()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        Assert.Equal(1, img.GetBytesPerPixel());
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_BytesPerPixelIs1()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        Assert.Equal(1, img.GetBytesPerPixel());
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_BytesPerPixelIs3()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        Assert.Equal(3, img.GetBytesPerPixel());
    }
}
