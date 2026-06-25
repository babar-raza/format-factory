// Tests for NetpbmDocument.GetPixel() and GetPixelColor() pixel access APIs.
// Sprint: FORMAT-FACTORY-NETPBM-PIXEL-ACCESS-20260626
// Ledger: R120-GOVERNED-DOTNET-NETPBM-PIXEL-ACCESS-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R120: Pixel access APIs — GetPixel(row,col) returns grayscale byte value,
/// GetPixelColor(row,col) returns (R,G,B) tuple. Verified against known ASCII
/// PGM and PPM content loaded via LoadStream.
/// </summary>
public class NetpbmR120PixelAccessTests
{
    // ---- Helper: load PGM/PPM from ASCII string ----

    private static NetpbmDocument LoadPgm(string pgmContent)
    {
        var bytes = Encoding.ASCII.GetBytes(pgmContent);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    private static NetpbmDocument LoadPpm(string ppmContent)
    {
        var bytes = Encoding.ASCII.GetBytes(ppmContent);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    // ---- PGM GetPixel: basic values ----

    [Fact]
    public void GetPixel_PgmBlack_ReturnsZero()
    {
        // 1×1 PGM, pixel value 0 (black)
        const string pgm = "P2\n1 1\n255\n0\n";
        var doc = LoadPgm(pgm);
        Assert.Equal(0, doc.GetPixel(0, 0));
    }

    [Fact]
    public void GetPixel_PgmWhite_Returns255()
    {
        // 1×1 PGM, pixel value 255 (white)
        const string pgm = "P2\n1 1\n255\n255\n";
        var doc = LoadPgm(pgm);
        Assert.Equal(255, doc.GetPixel(0, 0));
    }

    [Fact]
    public void GetPixel_PgmMidGray_Returns128()
    {
        // 1×1 PGM, pixel value 128
        const string pgm = "P2\n1 1\n255\n128\n";
        var doc = LoadPgm(pgm);
        Assert.Equal(128, doc.GetPixel(0, 0));
    }

    [Fact]
    public void GetPixel_PgmTwoByTwo_EachPixelCorrect()
    {
        // 2×2 PGM: row0=[10,20], row1=[30,40]
        const string pgm = "P2\n2 2\n255\n10 20\n30 40\n";
        var doc = LoadPgm(pgm);
        Assert.Equal(10, doc.GetPixel(0, 0));
        Assert.Equal(20, doc.GetPixel(0, 1));
        Assert.Equal(30, doc.GetPixel(1, 0));
        Assert.Equal(40, doc.GetPixel(1, 1));
    }

    // ---- GetPixelColor: PGM (R=G=B=grayscale) ----

    [Fact]
    public void GetPixelColor_Pgm_RGBEqualGrayscale()
    {
        const string pgm = "P2\n1 1\n255\n100\n";
        var doc = LoadPgm(pgm);
        var (r, g, b) = doc.GetPixelColor(0, 0);
        Assert.Equal(100, r);
        Assert.Equal(100, g);
        Assert.Equal(100, b);
    }

    [Fact]
    public void GetPixelColor_PgmBlack_AllZero()
    {
        const string pgm = "P2\n1 1\n255\n0\n";
        var doc = LoadPgm(pgm);
        var (r, g, b) = doc.GetPixelColor(0, 0);
        Assert.Equal(0, r);
        Assert.Equal(0, g);
        Assert.Equal(0, b);
    }

    // ---- GetPixelColor: PPM color ----

    [Fact]
    public void GetPixelColor_Ppm_ReturnsCorrectRGB()
    {
        // 1×1 PPM: red pixel (255, 0, 0)
        const string ppm = "P3\n1 1\n255\n255 0 0\n";
        var doc = LoadPpm(ppm);
        var (r, g, b) = doc.GetPixelColor(0, 0);
        Assert.Equal(255, r);
        Assert.Equal(0, g);
        Assert.Equal(0, b);
    }

    [Fact]
    public void GetPixelColor_Ppm_GreenPixel()
    {
        // 1×1 PPM: green pixel (0, 255, 0)
        const string ppm = "P3\n1 1\n255\n0 255 0\n";
        var doc = LoadPpm(ppm);
        var (r, g, b) = doc.GetPixelColor(0, 0);
        Assert.Equal(0, r);
        Assert.Equal(255, g);
        Assert.Equal(0, b);
    }

    [Fact]
    public void GetPixelColor_Ppm_BluePixel()
    {
        // 1×1 PPM: blue pixel (0, 0, 255)
        const string ppm = "P3\n1 1\n255\n0 0 255\n";
        var doc = LoadPpm(ppm);
        var (r, g, b) = doc.GetPixelColor(0, 0);
        Assert.Equal(0, r);
        Assert.Equal(0, g);
        Assert.Equal(255, b);
    }

    [Fact]
    public void GetPixelColor_Ppm_TwoByTwo_AllPixelsCorrect()
    {
        // 2×2 PPM: 4 different colors
        const string ppm = "P3\n2 2\n255\n255 0 0  0 255 0\n0 0 255  128 128 128\n";
        var doc = LoadPpm(ppm);

        var (r0, g0, b0) = doc.GetPixelColor(0, 0); // red
        Assert.Equal(255, r0); Assert.Equal(0, g0); Assert.Equal(0, b0);

        var (r1, g1, b1) = doc.GetPixelColor(0, 1); // green
        Assert.Equal(0, r1); Assert.Equal(255, g1); Assert.Equal(0, b1);

        var (r2, g2, b2) = doc.GetPixelColor(1, 0); // blue
        Assert.Equal(0, r2); Assert.Equal(0, g2); Assert.Equal(255, b2);

        var (r3, g3, b3) = doc.GetPixelColor(1, 1); // gray
        Assert.Equal(128, r3); Assert.Equal(128, g3); Assert.Equal(128, b3);
    }

    // ---- GetPixel for PPM returns red channel ----

    [Fact]
    public void GetPixel_Ppm_ReturnsRedChannel()
    {
        const string ppm = "P3\n1 1\n255\n200 100 50\n";
        var doc = LoadPpm(ppm);
        // GetPixel for PPM returns the red channel
        Assert.Equal(200, doc.GetPixel(0, 0));
    }

    // ---- Dogfood pipeline ----

    [Fact]
    public void DogfoodPipeline_LoadStream_GetPixels_Serialize_Reload()
    {
        // Load a 2×2 PGM, read pixels, serialize to ASCII, reload, verify pixels match
        const string pgm = "P2\n2 2\n255\n10 20\n30 40\n";
        var doc = LoadPgm(pgm);

        byte p00 = doc.GetPixel(0, 0);
        byte p01 = doc.GetPixel(0, 1);
        byte p10 = doc.GetPixel(1, 0);
        byte p11 = doc.GetPixel(1, 1);

        // Serialize and reload
        var ascii = doc.ToAsciiString();
        var bytes2 = Encoding.ASCII.GetBytes(ascii);
        using var ms2 = new MemoryStream(bytes2);
        var doc2 = NetpbmDocument.LoadStream(ms2);

        Assert.Equal(p00, doc2.GetPixel(0, 0));
        Assert.Equal(p01, doc2.GetPixel(0, 1));
        Assert.Equal(p10, doc2.GetPixel(1, 0));
        Assert.Equal(p11, doc2.GetPixel(1, 1));
    }
}
