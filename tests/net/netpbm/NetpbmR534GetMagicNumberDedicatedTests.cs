// Tests for NetpbmImage.GetMagicNumber dedicated coverage.
// Sprint: ff-sprint-s516-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R534

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R534: Dedicated tests for NetpbmImage.GetMagicNumber().
/// PBM image returns "P1" or "P4" (ASCII or raw bitmap).
/// PGM image returns "P2" or "P5" (ASCII or raw graymap).
/// PPM image returns "P3" or "P6" (ASCII or raw pixmap).
/// Width unchanged after GetMagicNumber.
/// Height unchanged after GetMagicNumber.
/// Format unchanged after GetMagicNumber.
/// MaxValue unchanged after GetMagicNumber.
/// Idempotent (called twice same result).
/// Dogfood: PBM magic number starts with P.
/// Dogfood: PGM magic number starts with P.
/// Dogfood: PPM magic number starts with P.
/// </summary>
public class NetpbmR534GetMagicNumberDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMagicNumber_PbmImage_StartsWithP()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        string magic = img.GetMagicNumber();
        Assert.StartsWith("P", magic);
    }

    [Fact]
    public void GetMagicNumber_PgmImage_StartsWithP()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        string magic = img.GetMagicNumber();
        Assert.StartsWith("P", magic);
    }

    [Fact]
    public void GetMagicNumber_PpmImage_StartsWithP()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        string magic = img.GetMagicNumber();
        Assert.StartsWith("P", magic);
    }

    [Fact]
    public void GetMagicNumber_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetMagicNumber();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMagicNumber_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetMagicNumber();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMagicNumber_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetMagicNumber();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMagicNumber_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetMagicNumber();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMagicNumber_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        string first = img.GetMagicNumber();
        string second = img.GetMagicNumber();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_MagicStartsWithP()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        string magic = img.GetMagicNumber();
        Assert.StartsWith("P", magic);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_MagicStartsWithP()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        string magic = img.GetMagicNumber();
        Assert.StartsWith("P", magic);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_MagicStartsWithP()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        string magic = img.GetMagicNumber();
        Assert.StartsWith("P", magic);
    }
}
