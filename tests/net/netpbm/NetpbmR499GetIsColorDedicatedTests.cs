// Tests for NetpbmImage.GetIsColor dedicated coverage.
// Sprint: ff-sprint-s481-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R499

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R499: Dedicated tests for NetpbmImage.GetIsColor().
/// PBM image returns false (bitmap, no color).
/// PGM image returns false (grayscale, no color).
/// PPM image returns true (full color).
/// Width unchanged after GetIsColor.
/// Height unchanged after GetIsColor.
/// Format unchanged after GetIsColor.
/// MaxValue unchanged after GetIsColor.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline returns false.
/// Dogfood: PGM pipeline returns false.
/// Dogfood: PPM pipeline returns true.
/// </summary>
public class NetpbmR499GetIsColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsColor_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.False(img.GetIsColor());
    }

    [Fact]
    public void GetIsColor_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.False(img.GetIsColor());
    }

    [Fact]
    public void GetIsColor_PpmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetIsColor());
    }

    [Fact]
    public void GetIsColor_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetIsColor();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsColor_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetIsColor();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsColor_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetIsColor();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsColor_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePpm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetIsColor();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsColor_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetIsColor();
        bool second = img.GetIsColor();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetIsColor();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetIsColor();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetIsColor();
        Assert.True(result);
    }
}
