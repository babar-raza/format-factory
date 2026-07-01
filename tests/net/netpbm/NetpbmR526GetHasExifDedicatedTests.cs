// Tests for NetpbmImage.GetHasExif dedicated coverage.
// Sprint: ff-sprint-s508-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R526

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R526: Dedicated tests for NetpbmImage.GetHasExif().
/// PBM image returns false (Netpbm has no EXIF support).
/// PGM image returns false (Netpbm has no EXIF support).
/// PPM image returns false (Netpbm has no EXIF support).
/// Width unchanged after GetHasExif.
/// Height unchanged after GetHasExif.
/// Format unchanged after GetHasExif.
/// MaxValue unchanged after GetHasExif.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline has no EXIF.
/// Dogfood: PGM pipeline has no EXIF.
/// Dogfood: PPM pipeline has no EXIF.
/// </summary>
public class NetpbmR526GetHasExifDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHasExif_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.False(img.GetHasExif());
    }

    [Fact]
    public void GetHasExif_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.False(img.GetHasExif());
    }

    [Fact]
    public void GetHasExif_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.False(img.GetHasExif());
    }

    [Fact]
    public void GetHasExif_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetHasExif();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHasExif_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetHasExif();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHasExif_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetHasExif();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHasExif_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetHasExif();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHasExif_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetHasExif();
        bool second = img.GetHasExif();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_HasNoExif()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetHasExif();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_HasNoExif()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetHasExif();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_HasNoExif()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetHasExif();
        Assert.False(result);
    }
}
