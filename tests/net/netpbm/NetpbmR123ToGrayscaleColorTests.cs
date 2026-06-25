// Tests for NetpbmImage.ToGrayscale() and NetpbmImage.ToColor() conversion.
// Sprint: FORMAT-FACTORY-NETPBM-GRAYSCALE-COLOR-20260626
// Ledger: R123-GOVERNED-DOTNET-NETPBM-GRAYSCALE-COLOR-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R123: ToGrayscale() converts a PPM (color) image to PGM (grayscale).
///       ToColor() converts a PGM (grayscale) image to PPM (color).
/// Tests verify format transitions, pixel count preservation, and type flags.
/// </summary>
public class NetpbmR123ToGrayscaleColorTests
{
    private static NetpbmDocument LoadPgm(string content)
    {
        var bytes = Encoding.ASCII.GetBytes(content);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    private static NetpbmDocument LoadPpm(string content)
    {
        var bytes = Encoding.ASCII.GetBytes(content);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    // ---- ToGrayscale: PPM → PGM ----

    [Fact]
    public void ToGrayscale_Ppm_ResultIsGrayscale()
    {
        const string ppm = "P3\n2 2\n255\n100 150 200  100 150 200\n100 150 200  100 150 200\n";
        var doc = LoadPpm(ppm);
        Assert.True(doc.IsColor);

        var gray = doc.Image.ToGrayscale();
        var grayDoc = NetpbmDocument.FromImage(gray);

        Assert.True(grayDoc.IsGrayscale);
        Assert.False(grayDoc.IsColor);
    }

    [Fact]
    public void ToGrayscale_Ppm_DimensionsPreserved()
    {
        const string ppm = "P3\n3 2\n255\n0 0 0  128 128 128  255 255 255\n0 0 0  64 64 64  192 192 192\n";
        var doc = LoadPpm(ppm);
        var gray = doc.Image.ToGrayscale();

        Assert.Equal(doc.Width, gray.Width);
        Assert.Equal(doc.Height, gray.Height);
    }

    [Fact]
    public void ToGrayscale_Ppm_PixelCountPreserved()
    {
        const string ppm = "P3\n4 3\n255\n0 0 0  0 0 0  0 0 0  0 0 0\n0 0 0  0 0 0  0 0 0  0 0 0\n0 0 0  0 0 0  0 0 0  0 0 0\n";
        var doc = LoadPpm(ppm);
        var gray = doc.Image.ToGrayscale();

        Assert.Equal(doc.PixelCount, gray.Width * gray.Height);
    }

    [Fact]
    public void ToGrayscale_WhitePixel_RemainsWhite()
    {
        // Pure white PPM: R=255, G=255, B=255 → grayscale = 255
        const string ppm = "P3\n1 1\n255\n255 255 255\n";
        var doc = LoadPpm(ppm);
        var gray = doc.Image.ToGrayscale();
        var grayDoc = NetpbmDocument.FromImage(gray);

        // White stays white
        Assert.Equal(255, grayDoc.GetPixel(0, 0));
    }

    [Fact]
    public void ToGrayscale_BlackPixel_RemainsBlack()
    {
        // Pure black PPM: R=0, G=0, B=0 → grayscale = 0
        const string ppm = "P3\n1 1\n255\n0 0 0\n";
        var doc = LoadPpm(ppm);
        var gray = doc.Image.ToGrayscale();
        var grayDoc = NetpbmDocument.FromImage(gray);

        Assert.Equal(0, grayDoc.GetPixel(0, 0));
    }

    // ---- ToGrayscale on already-grayscale: identity-like ----

    [Fact]
    public void ToGrayscale_AlreadyGrayscale_StillGrayscale()
    {
        const string pgm = "P2\n2 2\n255\n100 200\n50 150\n";
        var doc = LoadPgm(pgm);
        var gray2 = doc.Image.ToGrayscale();
        var grayDoc = NetpbmDocument.FromImage(gray2);

        Assert.True(grayDoc.IsGrayscale);
        Assert.Equal(doc.Width, gray2.Width);
        Assert.Equal(doc.Height, gray2.Height);
    }

    // ---- ToColor: PGM → PPM ----

    [Fact]
    public void ToColor_Pgm_ResultIsColor()
    {
        const string pgm = "P2\n2 2\n255\n100 200\n50 150\n";
        var doc = LoadPgm(pgm);
        Assert.True(doc.IsGrayscale);

        var color = doc.Image.ToColor();
        var colorDoc = NetpbmDocument.FromImage(color);

        Assert.True(colorDoc.IsColor);
        Assert.False(colorDoc.IsGrayscale);
    }

    [Fact]
    public void ToColor_Pgm_DimensionsPreserved()
    {
        const string pgm = "P2\n3 2\n255\n0 128 255\n64 192 32\n";
        var doc = LoadPgm(pgm);
        var color = doc.Image.ToColor();

        Assert.Equal(doc.Width, color.Width);
        Assert.Equal(doc.Height, color.Height);
    }

    [Fact]
    public void ToColor_Pgm_GrayPixelExpandsToEqualRgb()
    {
        // A grayscale value of 100 → (100, 100, 100) in RGB
        const string pgm = "P2\n1 1\n255\n100\n";
        var doc = LoadPgm(pgm);
        var color = doc.Image.ToColor();
        var colorDoc = NetpbmDocument.FromImage(color);

        var (r, g, b) = colorDoc.GetPixelColor(0, 0);
        Assert.Equal(r, g);
        Assert.Equal(g, b);
    }

    // ---- Dogfood: PPM → ToGrayscale → ToColor → PixelCount invariant ----

    [Fact]
    public void DogfoodPipeline_PpmToGrayscaleToColor_PixelCountInvariant()
    {
        const string ppm = "P3\n4 4\n255\n" +
            "255 0 0  0 255 0  0 0 255  128 128 128\n" +
            "255 0 0  0 255 0  0 0 255  128 128 128\n" +
            "255 0 0  0 255 0  0 0 255  128 128 128\n" +
            "255 0 0  0 255 0  0 0 255  128 128 128\n";

        var doc = LoadPpm(ppm);
        var gray = doc.Image.ToGrayscale();
        var color2 = gray.ToColor();

        // Pixel count must survive both conversions
        Assert.Equal(doc.PixelCount, color2.Width * color2.Height);
        Assert.Equal(doc.Width, color2.Width);
        Assert.Equal(doc.Height, color2.Height);

        var finalDoc = NetpbmDocument.FromImage(color2);
        Assert.True(finalDoc.IsColor);
    }
}
