// Tests for NetpbmImage.GetFileExtension dedicated coverage.
// Sprint: ff-sprint-s517-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R535

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R535: Dedicated tests for NetpbmImage.GetFileExtension().
/// PBM image returns "pbm".
/// PGM image returns "pgm".
/// PPM image returns "ppm".
/// Width unchanged after GetFileExtension.
/// Height unchanged after GetFileExtension.
/// Format unchanged after GetFileExtension.
/// MaxValue unchanged after GetFileExtension.
/// Idempotent (called twice same result).
/// Dogfood: PBM extension is pbm.
/// Dogfood: PGM extension is pgm.
/// Dogfood: PPM extension is ppm.
/// </summary>
public class NetpbmR535GetFileExtensionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFileExtension_PbmImage_ReturnsPbm()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.Equal("pbm", img.GetFileExtension());
    }

    [Fact]
    public void GetFileExtension_PgmImage_ReturnsPgm()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.Equal("pgm", img.GetFileExtension());
    }

    [Fact]
    public void GetFileExtension_PpmImage_ReturnsPpm()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.Equal("ppm", img.GetFileExtension());
    }

    [Fact]
    public void GetFileExtension_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetFileExtension();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetFileExtension_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetFileExtension();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetFileExtension_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetFileExtension();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetFileExtension_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetFileExtension();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetFileExtension_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        string first = img.GetFileExtension();
        string second = img.GetFileExtension();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ExtensionIsPbm()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        Assert.Equal("pbm", img.GetFileExtension());
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ExtensionIsPgm()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        Assert.Equal("pgm", img.GetFileExtension());
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ExtensionIsPpm()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        Assert.Equal("ppm", img.GetFileExtension());
    }
}
