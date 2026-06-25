// Tests for NetpbmImage.ConvertFormat(targetFormat) — within-family format conversion.
// Sprint: FORMAT-FACTORY-NETPBM-CONVERT-FORMAT-20260626
// Ledger: R124-GOVERNED-DOTNET-NETPBM-CONVERT-FORMAT-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R124: ConvertFormat(targetFormat) converts within the same type family:
///   PBM_P1 ↔ PBM_P4, PGM_P2 ↔ PGM_P5, PPM_P3 ↔ PPM_P6.
/// Cross-family conversions (PGM→PPM) throw InvalidOperationException.
/// Tests verify format changes, dimension preservation, and cross-family guard.
/// </summary>
public class NetpbmR124ConvertFormatTests
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

    // ---- PGM: P2 → P5 ----

    [Fact]
    public void ConvertFormat_PgmP2ToP5_FormatChanges()
    {
        const string pgm = "P2\n2 2\n255\n100 200\n50 150\n";
        var doc = LoadPgm(pgm);
        Assert.Equal(NetpbmFormat.PGM_P2, doc.Format);

        var converted = doc.Image.ConvertFormat(NetpbmFormat.PGM_P5);
        Assert.Equal(NetpbmFormat.PGM_P5, converted.Format);
    }

    [Fact]
    public void ConvertFormat_PgmP2ToP5_DimensionsPreserved()
    {
        const string pgm = "P2\n3 4\n255\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n";
        var doc = LoadPgm(pgm);

        var converted = doc.Image.ConvertFormat(NetpbmFormat.PGM_P5);
        Assert.Equal(doc.Width, converted.Width);
        Assert.Equal(doc.Height, converted.Height);
    }

    [Fact]
    public void ConvertFormat_PgmP2ToP5_PixelsPreserved()
    {
        const string pgm = "P2\n2 2\n255\n100 200\n50 150\n";
        var doc = LoadPgm(pgm);

        var converted = doc.Image.ConvertFormat(NetpbmFormat.PGM_P5);
        var convertedDoc = NetpbmDocument.FromImage(converted);

        Assert.Equal(doc.GetPixel(0, 0), convertedDoc.GetPixel(0, 0));
        Assert.Equal(doc.GetPixel(0, 1), convertedDoc.GetPixel(0, 1));
        Assert.Equal(doc.GetPixel(1, 0), convertedDoc.GetPixel(1, 0));
        Assert.Equal(doc.GetPixel(1, 1), convertedDoc.GetPixel(1, 1));
    }

    // ---- PGM: P5 → P2 ----

    [Fact]
    public void ConvertFormat_PgmP5ToP2_FormatChanges()
    {
        const string pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var doc = LoadPgm(pgm);
        var p5 = doc.Image.ConvertFormat(NetpbmFormat.PGM_P5);
        Assert.Equal(NetpbmFormat.PGM_P5, p5.Format);

        var p2 = p5.ConvertFormat(NetpbmFormat.PGM_P2);
        Assert.Equal(NetpbmFormat.PGM_P2, p2.Format);
    }

    // ---- PPM: P3 → P6 ----

    [Fact]
    public void ConvertFormat_PpmP3ToP6_FormatChanges()
    {
        const string ppm = "P3\n2 2\n255\n100 150 200  100 150 200\n100 150 200  100 150 200\n";
        var doc = LoadPpm(ppm);
        Assert.Equal(NetpbmFormat.PPM_P3, doc.Format);

        var converted = doc.Image.ConvertFormat(NetpbmFormat.PPM_P6);
        Assert.Equal(NetpbmFormat.PPM_P6, converted.Format);
    }

    [Fact]
    public void ConvertFormat_PpmP3ToP6_DimensionsPreserved()
    {
        const string ppm = "P3\n3 2\n255\n0 0 0  0 0 0  0 0 0\n0 0 0  0 0 0  0 0 0\n";
        var doc = LoadPpm(ppm);

        var converted = doc.Image.ConvertFormat(NetpbmFormat.PPM_P6);
        Assert.Equal(doc.Width, converted.Width);
        Assert.Equal(doc.Height, converted.Height);
    }

    // ---- Same-format is identity (no exception) ----

    [Fact]
    public void ConvertFormat_SameFormat_DoesNotThrow()
    {
        const string pgm = "P2\n2 2\n255\n10 20\n30 40\n";
        var doc = LoadPgm(pgm);

        var ex = Record.Exception(() => doc.Image.ConvertFormat(NetpbmFormat.PGM_P2));
        Assert.Null(ex);
    }

    // ---- Cross-family throws ----

    [Fact]
    public void ConvertFormat_PgmToPpm_ThrowsInvalidOperation()
    {
        const string pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var doc = LoadPgm(pgm);

        Assert.Throws<InvalidOperationException>(() =>
            doc.Image.ConvertFormat(NetpbmFormat.PPM_P3));
    }

    [Fact]
    public void ConvertFormat_PpmToPgm_ThrowsInvalidOperation()
    {
        const string ppm = "P3\n2 2\n255\n0 0 0  0 0 0\n0 0 0  0 0 0\n";
        var doc = LoadPpm(ppm);

        Assert.Throws<InvalidOperationException>(() =>
            doc.Image.ConvertFormat(NetpbmFormat.PGM_P2));
    }

    // ---- Dogfood: P2→P5→P2 round-trip preserves pixels ----

    [Fact]
    public void DogfoodPipeline_P2ToP5ToP2_PixelsInvariant()
    {
        const string pgm = "P2\n3 3\n255\n10 20 30\n40 50 60\n70 80 90\n";
        var doc = LoadPgm(pgm);

        var p5 = doc.Image.ConvertFormat(NetpbmFormat.PGM_P5);
        var p2Again = p5.ConvertFormat(NetpbmFormat.PGM_P2);
        var finalDoc = NetpbmDocument.FromImage(p2Again);

        for (int row = 0; row < 3; row++)
            for (int col = 0; col < 3; col++)
                Assert.Equal(doc.GetPixel(row, col), finalDoc.GetPixel(row, col));
    }
}
