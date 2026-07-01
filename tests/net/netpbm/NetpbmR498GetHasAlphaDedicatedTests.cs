// Tests for NetpbmImage.GetHasAlpha dedicated coverage.
// Sprint: ff-sprint-s480-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R498

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R498: Dedicated tests for NetpbmImage.GetHasAlpha().
/// PBM image returns false (no alpha channel).
/// PGM image returns false (no alpha channel).
/// PPM image returns false (no alpha channel).
/// Width unchanged after GetHasAlpha.
/// Height unchanged after GetHasAlpha.
/// Format unchanged after GetHasAlpha.
/// MaxValue unchanged after GetHasAlpha.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline returns false.
/// Dogfood: PGM pipeline returns false.
/// Dogfood: PPM pipeline returns false.
/// </summary>
public class NetpbmR498GetHasAlphaDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHasAlpha_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.False(img.GetHasAlpha());
    }

    [Fact]
    public void GetHasAlpha_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.False(img.GetHasAlpha());
    }

    [Fact]
    public void GetHasAlpha_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.False(img.GetHasAlpha());
    }

    [Fact]
    public void GetHasAlpha_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(6, 3, 255);
        int before = img.Width;
        _ = img.GetHasAlpha();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHasAlpha_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(6, 3, 255);
        int before = img.Height;
        _ = img.GetHasAlpha();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHasAlpha_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePpm(2, 2, 255);
        string before = img.Format;
        _ = img.GetHasAlpha();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHasAlpha_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetHasAlpha();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHasAlpha_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetHasAlpha();
        bool second = img.GetHasAlpha();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetHasAlpha();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetHasAlpha();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetHasAlpha();
        Assert.False(result);
    }
}
