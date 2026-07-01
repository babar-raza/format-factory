// Tests for NetpbmImage.GetMagicNumber dedicated coverage.
// Sprint: ff-sprint-s457-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R475

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R475: Dedicated tests for NetpbmImage.GetMagicNumber().
/// PBM returns "P4" (binary PBM magic number).
/// PGM returns "P5" (binary PGM magic number).
/// PPM returns "P6" (binary PPM magic number).
/// Width unchanged after GetMagicNumber.
/// Height unchanged after GetMagicNumber.
/// Format unchanged after GetMagicNumber.
/// MaxValue unchanged after GetMagicNumber.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM magic is "P5".
/// Dogfood: 4x4 PPM magic is "P6".
/// Dogfood: PBM magic starts with P.
/// </summary>
public class NetpbmR475GetMagicNumberDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMagicNumber_PBM_ReturnsP4()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.Equal("P4", img.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_PGM_ReturnsP5()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.Equal("P5", img.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_PPM_ReturnsP6()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.Equal("P6", img.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetMagicNumber();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMagicNumber_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetMagicNumber();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMagicNumber_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetMagicNumber();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMagicNumber_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetMagicNumber();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMagicNumber_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetMagicNumber();
        string second = img.GetMagicNumber();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_MagicIsP5()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.Equal("P5", img.GetMagicNumber());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_MagicIsP6()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.Equal("P6", img.GetMagicNumber());
    }

    [Fact]
    public void DogfoodPipeline_PBM_MagicStartsWithP()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.StartsWith("P", img.GetMagicNumber());
    }
}
