// Tests for Spec.NetpbmImage canonical spec-shaped model class.
// Sprint: FORMAT-FACTORY-NETPBM-R138-20260627
// Ledger: R138-GOVERNED-DOTNET-NETPBM-SPEC-NETPBMIMAGE-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R138: Tests for FormatFactory.Netpbm.Spec.NetpbmImage — the canonical spec-shaped
/// model class for Netpbm images. SpecQName = "netpbm:image"; MagicNumber default empty
/// (init-only); Width default 0 (init-only); Height default 0 (init-only);
/// MaxVal default 0 (init-only). All properties are init-only for spec fidelity.
/// Covers: SpecQName constant; MagicNumber default empty; Width default 0;
/// Height default 0; MaxVal default 0; MagicNumber init-only assignment (P3=PPM);
/// Width/Height dimension assignment; MaxVal 255 assignment (8-bit);
/// SpecQName accessible without instance; dogfood NetpbmParser.Parse → Spec.NetpbmImage
/// composition pipeline verifying all properties.
/// Netpbm spec basis: Magic numbers P1-P6 per netpbm.sourceforge.net.
/// </summary>
public class NetpbmR138SpecNetpbmImageTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "netpbm", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    // -------------------------------------------------------------------------
    // SpecQName constant
    // -------------------------------------------------------------------------

    [Fact]
    public void SpecNetpbmImage_SpecQName_IsCorrect()
    {
        Assert.Equal("netpbm:image", Spec.NetpbmImage.SpecQName);
    }

    [Fact]
    public void SpecNetpbmImage_SpecQName_AccessibleWithoutInstance()
    {
        const string expected = "netpbm:image";
        Assert.Equal(expected, Spec.NetpbmImage.SpecQName);
    }

    // -------------------------------------------------------------------------
    // Default values
    // -------------------------------------------------------------------------

    [Fact]
    public void SpecNetpbmImage_MagicNumber_DefaultIsEmpty()
    {
        var img = new Spec.NetpbmImage();
        Assert.Equal(string.Empty, img.MagicNumber);
    }

    [Fact]
    public void SpecNetpbmImage_Width_DefaultIsZero()
    {
        var img = new Spec.NetpbmImage();
        Assert.Equal(0, img.Width);
    }

    [Fact]
    public void SpecNetpbmImage_Height_DefaultIsZero()
    {
        var img = new Spec.NetpbmImage();
        Assert.Equal(0, img.Height);
    }

    [Fact]
    public void SpecNetpbmImage_MaxVal_DefaultIsZero()
    {
        var img = new Spec.NetpbmImage();
        Assert.Equal(0, img.MaxVal);
    }

    // -------------------------------------------------------------------------
    // Init-only property assignment
    // -------------------------------------------------------------------------

    [Fact]
    public void SpecNetpbmImage_MagicNumber_P3_AssignableViaInit()
    {
        var img = new Spec.NetpbmImage { MagicNumber = "P3" };
        Assert.Equal("P3", img.MagicNumber);
    }

    [Fact]
    public void SpecNetpbmImage_Dimensions_AssignableViaInit()
    {
        var img = new Spec.NetpbmImage { Width = 640, Height = 480 };
        Assert.Equal(640, img.Width);
        Assert.Equal(480, img.Height);
    }

    [Fact]
    public void SpecNetpbmImage_MaxVal_255_AssignableViaInit()
    {
        var img = new Spec.NetpbmImage { MaxVal = 255 };
        Assert.Equal(255, img.MaxVal);
    }

    // -------------------------------------------------------------------------
    // Dogfood: NetpbmParser.Parse → Spec.NetpbmImage composition pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_NetpbmParserParse_ThenSpecImageComposition()
    {
        var fixture = FixturePath("sample.ppm");

        // Only run if fixture exists (CI environments may not have test assets)
        if (!File.Exists(fixture))
            return;

        // NetpbmParser.Parse is a static method returning Model.NetpbmImage
        var parsed = NetpbmParser.Parse(fixture);

        // Compose Spec.NetpbmImage from parsed model
        // Model.NetpbmImage.Format is a NetpbmFormat enum; Spec uses MagicNumber string
        var specImg = new Spec.NetpbmImage
        {
            MagicNumber = parsed.Format.ToString(),
            Width       = parsed.Width,
            Height      = parsed.Height,
            MaxVal      = parsed.MaxValue   // Model uses MaxValue; Spec uses MaxVal
        };

        Assert.Equal("netpbm:image", Spec.NetpbmImage.SpecQName);
        Assert.True(specImg.Width > 0);
        Assert.True(specImg.Height > 0);
        Assert.True(specImg.MaxVal > 0);
        Assert.False(string.IsNullOrEmpty(specImg.MagicNumber));
    }
}
