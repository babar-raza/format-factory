// Tests for NetpbmDocument image editing via Image property: SetPixel, SetPixelColor, FillRegion.
// Sprint: FORMAT-FACTORY-NETPBM-IMAGE-EDIT-20260626
// Ledger: R121-GOVERNED-DOTNET-NETPBM-IMAGE-EDIT-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R121: Image editing APIs accessed via NetpbmDocument.Image —
/// SetPixel (PGM), SetPixelColor (PPM), FillRegion. Tests verify
/// pixel mutations are reflected by GetPixel/GetPixelColor and survive serialization.
/// </summary>
public class NetpbmR121ImageEditingTests
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

    // ---- SetPixel: basic mutation ----

    [Fact]
    public void SetPixel_PgmChangesValue_GetPixelReflects()
    {
        const string pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var doc = LoadPgm(pgm);
        doc.Image.SetPixel(0, 0, 128);
        Assert.Equal(128, doc.GetPixel(0, 0));
    }

    [Fact]
    public void SetPixel_PgmTargetCell_OthersUnchanged()
    {
        const string pgm = "P2\n3 1\n255\n10\n20\n30\n";
        var doc = LoadPgm(pgm);
        doc.Image.SetPixel(1, 0, 200);

        Assert.Equal(10, doc.GetPixel(0, 0));
        Assert.Equal(200, doc.GetPixel(1, 0));
        Assert.Equal(30, doc.GetPixel(2, 0));
    }

    [Fact]
    public void SetPixel_PgmWhite_ReturnsMax()
    {
        const string pgm = "P2\n1 1\n255\n0\n";
        var doc = LoadPgm(pgm);
        doc.Image.SetPixel(0, 0, 255);
        Assert.Equal(255, doc.GetPixel(0, 0));
    }

    // ---- SetPixelColor: basic mutation for PPM ----

    [Fact]
    public void SetPixelColor_PpmChangesRGB_GetPixelColorReflects()
    {
        const string ppm = "P3\n2 2\n255\n0 0 0  0 0 0\n0 0 0  0 0 0\n";
        var doc = LoadPpm(ppm);
        doc.Image.SetPixelColor(0, 1, 100, 150, 200);
        var (r, g, b) = doc.GetPixelColor(0, 1);
        Assert.Equal(100, r);
        Assert.Equal(150, g);
        Assert.Equal(200, b);
    }

    [Fact]
    public void SetPixelColor_PpmTargetCell_OthersUnchanged()
    {
        const string ppm = "P3\n1 2\n255\n255 0 0  0 255 0\n";
        var doc = LoadPpm(ppm);
        doc.Image.SetPixelColor(0, 0, 128, 64, 32);

        var (r0, g0, b0) = doc.GetPixelColor(0, 0);
        Assert.Equal(128, r0); Assert.Equal(64, g0); Assert.Equal(32, b0);

        var (r1, g1, b1) = doc.GetPixelColor(0, 1);
        Assert.Equal(0, r1); Assert.Equal(255, g1); Assert.Equal(0, b1); // unchanged
    }

    // ---- FillRegion: PGM ----

    [Fact]
    public void FillRegion_Pgm_AllCellsInRegionFilled()
    {
        const string pgm = "P2\n4 4\n255\n0 0 0 0\n0 0 0 0\n0 0 0 0\n0 0 0 0\n";
        var doc = LoadPgm(pgm);
        doc.Image.FillRegion(1, 1, 2, 2, value: 100);

        // Inside region
        Assert.Equal(100, doc.GetPixel(1, 1));
        Assert.Equal(100, doc.GetPixel(1, 2));
        Assert.Equal(100, doc.GetPixel(2, 1));
        Assert.Equal(100, doc.GetPixel(2, 2));

        // Outside region — unchanged
        Assert.Equal(0, doc.GetPixel(0, 0));
        Assert.Equal(0, doc.GetPixel(3, 3));
    }

    [Fact]
    public void FillRegion_Pgm_FullImage_AllPixelsSet()
    {
        const string pgm = "P2\n3 3\n255\n0 0 0\n0 0 0\n0 0 0\n";
        var doc = LoadPgm(pgm);
        doc.Image.FillRegion(0, 0, 3, 3, value: 200);

        for (int row = 0; row < 3; row++)
            for (int col = 0; col < 3; col++)
                Assert.Equal(200, doc.GetPixel(row, col));
    }

    // ---- FillRegion: out-of-bounds throws ----

    [Fact]
    public void FillRegion_ExceedsBounds_Throws()
    {
        const string pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var doc = LoadPgm(pgm);
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.Image.FillRegion(1, 1, 2, 2, value: 50)); // would go out of bounds
    }

    // ---- Dogfood pipeline: edit + serialize + verify ----

    [Fact]
    public void DogfoodPipeline_EditPixels_Serialize_Reload_VerifyMutation()
    {
        // Load PGM, set a pixel, serialize, reload, verify pixel persists
        const string pgm = "P2\n3 3\n255\n0 0 0\n0 0 0\n0 0 0\n";
        var doc = LoadPgm(pgm);
        doc.Image.SetPixel(1, 1, 99);

        // Serialize to ASCII
        var ascii = doc.ToAsciiString();
        var bytes = Encoding.ASCII.GetBytes(ascii);
        using var ms = new MemoryStream(bytes);
        var doc2 = NetpbmDocument.LoadStream(ms);

        Assert.Equal(99, doc2.GetPixel(1, 1));
        // Surrounding pixels should still be 0
        Assert.Equal(0, doc2.GetPixel(0, 0));
        Assert.Equal(0, doc2.GetPixel(2, 2));
    }
}
