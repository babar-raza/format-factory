// Tests for NetpbmImage.GetIsBitmap dedicated coverage.
// Sprint: ff-sprint-s482-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R500

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R500: Dedicated tests for NetpbmImage.GetIsBitmap().
/// PBM image returns true (bitmap format).
/// PGM image returns false (grayscale, not bitmap).
/// PPM image returns false (color, not bitmap).
/// Width unchanged after GetIsBitmap.
/// Height unchanged after GetIsBitmap.
/// Format unchanged after GetIsBitmap.
/// MaxValue unchanged after GetIsBitmap.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline returns true.
/// Dogfood: PGM pipeline returns false.
/// Dogfood: PPM pipeline returns false.
/// </summary>
public class NetpbmR500GetIsBitmapDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsBitmap_PbmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetIsBitmap());
    }

    [Fact]
    public void GetIsBitmap_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.False(img.GetIsBitmap());
    }

    [Fact]
    public void GetIsBitmap_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.False(img.GetIsBitmap());
    }

    [Fact]
    public void GetIsBitmap_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePbm(6, 3);
        int before = img.Width;
        _ = img.GetIsBitmap();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsBitmap_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePbm(6, 3);
        int before = img.Height;
        _ = img.GetIsBitmap();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsBitmap_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePpm(2, 2, 255);
        string before = img.Format;
        _ = img.GetIsBitmap();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsBitmap_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetIsBitmap();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsBitmap_Idempotent()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        bool first = img.GetIsBitmap();
        bool second = img.GetIsBitmap();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetIsBitmap();
        Assert.True(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetIsBitmap();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetIsBitmap();
        Assert.False(result);
    }
}
