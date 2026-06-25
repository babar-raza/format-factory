// Tests for NetpbmExporter.PgmToPpm() and NetpbmExporter.PpmToPgm() cross-family converters.
// Sprint: FORMAT-FACTORY-NETPBM-EXPORTER-PGMPPM-20260626
// Ledger: R127-GOVERNED-DOTNET-NETPBM-EXPORTER-PGMPPM-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R127: NetpbmExporter.PgmToPpm(pgm) — converts a grayscale PGM image to PPM by
/// expanding each pixel to equal R=G=B channels. PpmToPgm(ppm) — converts PPM to PGM
/// using BT.601 luminance weights (0.299R + 0.587G + 0.114B).
/// These are exporter-layer cross-family conversions, distinct from Image.ToGrayscale/ToColor.
/// </summary>
public class NetpbmR127ExporterPgmPpmTests
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

    // ---- PgmToPpm: result is PPM ----

    [Fact]
    public void PgmToPpm_Result_IsPpm()
    {
        const string pgm = "P2\n2 2\n255\n100 200\n50 150\n";
        var doc = LoadPgm(pgm);

        var ppm = NetpbmExporter.PgmToPpm(doc.Image);
        Assert.Equal(NetpbmFormat.PPM_P3, ppm.Format);
    }

    [Fact]
    public void PgmToPpm_Dimensions_Preserved()
    {
        const string pgm = "P2\n3 2\n255\n0 0 0\n0 0 0\n";
        var doc = LoadPgm(pgm);

        var ppm = NetpbmExporter.PgmToPpm(doc.Image);
        Assert.Equal(doc.Width, ppm.Width);
        Assert.Equal(doc.Height, ppm.Height);
    }

    [Fact]
    public void PgmToPpm_GrayPixel_ExpandsToEqualChannels()
    {
        // Pixel 100 should become R=100, G=100, B=100
        const string pgm = "P2\n1 1\n255\n100\n";
        var doc = LoadPgm(pgm);

        var ppm = NetpbmExporter.PgmToPpm(doc.Image);
        var ppmDoc = NetpbmDocument.FromImage(ppm);

        var (r, g, b) = ppmDoc.GetPixelColor(0, 0);
        Assert.Equal(100, r);
        Assert.Equal(100, g);
        Assert.Equal(100, b);
    }

    [Fact]
    public void PgmToPpm_BlackPixel_AllChannelsZero()
    {
        const string pgm = "P2\n1 1\n255\n0\n";
        var doc = LoadPgm(pgm);

        var ppm = NetpbmExporter.PgmToPpm(doc.Image);
        var ppmDoc = NetpbmDocument.FromImage(ppm);

        var (r, g, b) = ppmDoc.GetPixelColor(0, 0);
        Assert.Equal(0, r);
        Assert.Equal(0, g);
        Assert.Equal(0, b);
    }

    [Fact]
    public void PgmToPpm_WhitePixel_AllChannels255()
    {
        const string pgm = "P2\n1 1\n255\n255\n";
        var doc = LoadPgm(pgm);

        var ppm = NetpbmExporter.PgmToPpm(doc.Image);
        var ppmDoc = NetpbmDocument.FromImage(ppm);

        var (r, g, b) = ppmDoc.GetPixelColor(0, 0);
        Assert.Equal(255, r);
        Assert.Equal(255, g);
        Assert.Equal(255, b);
    }

    // ---- PgmToPpm: wrong format throws ----

    [Fact]
    public void PgmToPpm_PpmInput_ThrowsArgumentException()
    {
        const string ppm = "P3\n2 2\n255\n0 0 0  0 0 0\n0 0 0  0 0 0\n";
        var doc = LoadPpm(ppm);

        Assert.Throws<ArgumentException>(() => NetpbmExporter.PgmToPpm(doc.Image));
    }

    // ---- PpmToPgm: result is PGM ----

    [Fact]
    public void PpmToPgm_Result_IsPgm()
    {
        const string ppm = "P3\n2 2\n255\n100 100 100  200 200 200\n50 50 50  150 150 150\n";
        var doc = LoadPpm(ppm);

        var pgm = NetpbmExporter.PpmToPgm(doc.Image);
        Assert.Equal(NetpbmFormat.PGM_P2, pgm.Format);
    }

    [Fact]
    public void PpmToPgm_Dimensions_Preserved()
    {
        const string ppm = "P3\n3 2\n255\n0 0 0  0 0 0  0 0 0\n0 0 0  0 0 0  0 0 0\n";
        var doc = LoadPpm(ppm);

        var pgm = NetpbmExporter.PpmToPgm(doc.Image);
        Assert.Equal(doc.Width, pgm.Width);
        Assert.Equal(doc.Height, pgm.Height);
    }

    [Fact]
    public void PpmToPgm_GrayRgb_SameLuminanceAsGray()
    {
        // Pure gray R=G=B=128 should produce gray=128
        const string ppm = "P3\n1 1\n255\n128 128 128\n";
        var doc = LoadPpm(ppm);

        var pgm = NetpbmExporter.PpmToPgm(doc.Image);
        var pgmDoc = NetpbmDocument.FromImage(pgm);

        // Luminance of equal channels ≈ value itself
        var pixel = pgmDoc.GetPixel(0, 0);
        Assert.True(pixel >= 125 && pixel <= 131,
            $"Expected gray ~128 for equal-channel input, got {pixel}");
    }

    // ---- PpmToPgm: wrong format throws ----

    [Fact]
    public void PpmToPgm_PgmInput_ThrowsArgumentException()
    {
        const string pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var doc = LoadPgm(pgm);

        Assert.Throws<ArgumentException>(() => NetpbmExporter.PpmToPgm(doc.Image));
    }

    // ---- Dogfood: PGM → PgmToPpm → PpmToPgm round-trip dimensions invariant ----

    [Fact]
    public void DogfoodPipeline_PgmToPpmToPgm_DimensionsInvariant()
    {
        const string pgm = "P2\n4 3\n255\n50 100 150 200\n25 75 125 175\n10 60 110 160\n";
        var doc = LoadPgm(pgm);

        var ppm = NetpbmExporter.PgmToPpm(doc.Image);
        var pgm2 = NetpbmExporter.PpmToPgm(ppm);

        Assert.Equal(doc.Width, pgm2.Width);
        Assert.Equal(doc.Height, pgm2.Height);
        Assert.Equal(NetpbmFormat.PGM_P2, pgm2.Format);
    }
}
