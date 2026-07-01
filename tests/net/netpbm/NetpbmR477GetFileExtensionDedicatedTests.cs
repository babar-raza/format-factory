// Tests for NetpbmImage.GetFileExtension dedicated coverage.
// Sprint: ff-sprint-s459-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R477

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R477: Dedicated tests for NetpbmImage.GetFileExtension().
/// PBM returns "pbm".
/// PGM returns "pgm".
/// PPM returns "ppm".
/// Width unchanged after GetFileExtension.
/// Height unchanged after GetFileExtension.
/// Format unchanged after GetFileExtension.
/// MaxValue unchanged after GetFileExtension.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM extension is "pgm".
/// Dogfood: 4x4 PPM extension is "ppm".
/// Dogfood: PBM extension is "pbm".
/// </summary>
public class NetpbmR477GetFileExtensionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFileExtension_PBM_ReturnsPbm()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.Equal("pbm", img.GetFileExtension());
    }

    [Fact]
    public void GetFileExtension_PGM_ReturnsPgm()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.Equal("pgm", img.GetFileExtension());
    }

    [Fact]
    public void GetFileExtension_PPM_ReturnsPpm()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.Equal("ppm", img.GetFileExtension());
    }

    [Fact]
    public void GetFileExtension_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetFileExtension();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetFileExtension_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetFileExtension();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetFileExtension_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetFileExtension();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetFileExtension_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetFileExtension();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetFileExtension_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetFileExtension();
        string second = img.GetFileExtension();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ExtensionIsPgm()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.Equal("pgm", img.GetFileExtension());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_ExtensionIsPpm()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.Equal("ppm", img.GetFileExtension());
    }

    [Fact]
    public void DogfoodPipeline_PBM_ExtensionIsPbm()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.Equal("pbm", img.GetFileExtension());
    }
}
