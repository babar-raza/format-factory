// Tests for NetpbmImage.GetColorSpace dedicated coverage.
// Sprint: ff-sprint-s441-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R459

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R459: Dedicated tests for NetpbmImage.GetColorSpace().
/// Returns non-null string for PBM/PGM/PPM.
/// PBM returns "Binary"; PGM returns "Grayscale"; PPM returns "RGB".
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM returns "Grayscale"; PPM returns "RGB".
/// </summary>
public class NetpbmR459GetColorSpaceDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorSpace_ReturnsNotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string val = img.GetColorSpace();
        Assert.NotNull(val);
    }

    [Fact]
    public void GetColorSpace_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetColorSpace();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetColorSpace_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetColorSpace();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetColorSpace_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetColorSpace();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetColorSpace_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetColorSpace();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetColorSpace_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetColorSpace();
        string second = img.GetColorSpace();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColorSpace_PBM_ReturnsBinary()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        string val = img.GetColorSpace();
        Assert.Equal("Binary", val);
    }

    [Fact]
    public void GetColorSpace_PGM_ReturnsGrayscale()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string val = img.GetColorSpace();
        Assert.Equal("Grayscale", val);
    }

    [Fact]
    public void GetColorSpace_PPM_ReturnsRGB()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        string val = img.GetColorSpace();
        Assert.Equal("RGB", val);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ReturnsGrayscale()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.Equal("Grayscale", img.GetColorSpace());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_ReturnsRGB()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.Equal("RGB", img.GetColorSpace());
    }
}
