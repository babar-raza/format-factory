// Tests for NetpbmExporter.PbmToPgm() and NetpbmExporter.PbmToPpm() converters.
// Sprint: FORMAT-FACTORY-NETPBM-EXPORTER-PBM-20260626
// Ledger: R128-GOVERNED-DOTNET-NETPBM-EXPORTER-PBM-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R128: NetpbmExporter.PbmToPgm(pbm) — converts a PBM 1-bit bitmap to PGM grayscale.
/// PBM 0 (white) maps to PGM maxValue (255); PBM 1 (black) maps to PGM 0.
/// PbmToPpm(pbm) — converts PBM to PPM color; 0→(255,255,255), 1→(0,0,0).
/// Non-PBM inputs throw ArgumentException.
/// </summary>
public class NetpbmR128ExporterPbmTests
{
    private static NetpbmDocument LoadPbm(string content)
    {
        var bytes = Encoding.ASCII.GetBytes(content);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    private static NetpbmDocument LoadPgm(string content)
    {
        var bytes = Encoding.ASCII.GetBytes(content);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    // ---- PbmToPgm: result is PGM ----

    [Fact]
    public void PbmToPgm_Result_IsPgm()
    {
        const string pbm = "P1\n2 2\n0 1\n1 0\n";
        var doc = LoadPbm(pbm);

        var pgm = NetpbmExporter.PbmToPgm(doc.Image);
        Assert.Equal(NetpbmFormat.PGM_P2, pgm.Format);
    }

    [Fact]
    public void PbmToPgm_Dimensions_Preserved()
    {
        const string pbm = "P1\n3 2\n0 1 0\n1 0 1\n";
        var doc = LoadPbm(pbm);

        var pgm = NetpbmExporter.PbmToPgm(doc.Image);
        Assert.Equal(doc.Width, pgm.Width);
        Assert.Equal(doc.Height, pgm.Height);
    }

    // ---- PbmToPgm: pixel value mapping (0=white→255, 1=black→0) ----

    [Fact]
    public void PbmToPgm_WhitePixel_MapsTo255()
    {
        // PBM 0 = white → PGM 255
        const string pbm = "P1\n1 1\n0\n";
        var doc = LoadPbm(pbm);

        var pgm = NetpbmExporter.PbmToPgm(doc.Image);
        var pgmDoc = NetpbmDocument.FromImage(pgm);
        Assert.Equal(255, pgmDoc.GetPixel(0, 0));
    }

    [Fact]
    public void PbmToPgm_BlackPixel_MapsToZero()
    {
        // PBM 1 = black → PGM 0
        const string pbm = "P1\n1 1\n1\n";
        var doc = LoadPbm(pbm);

        var pgm = NetpbmExporter.PbmToPgm(doc.Image);
        var pgmDoc = NetpbmDocument.FromImage(pgm);
        Assert.Equal(0, pgmDoc.GetPixel(0, 0));
    }

    // ---- PbmToPgm: wrong format throws ----

    [Fact]
    public void PbmToPgm_PgmInput_ThrowsArgumentException()
    {
        const string pgm = "P2\n2 2\n255\n100 200\n50 150\n";
        var doc = LoadPgm(pgm);

        Assert.Throws<ArgumentException>(() => NetpbmExporter.PbmToPgm(doc.Image));
    }

    // ---- PbmToPpm: result is PPM ----

    [Fact]
    public void PbmToPpm_Result_IsPpm()
    {
        const string pbm = "P1\n2 2\n0 1\n1 0\n";
        var doc = LoadPbm(pbm);

        var ppm = NetpbmExporter.PbmToPpm(doc.Image);
        Assert.Equal(NetpbmFormat.PPM_P3, ppm.Format);
    }

    [Fact]
    public void PbmToPpm_Dimensions_Preserved()
    {
        const string pbm = "P1\n4 3\n0 1 0 1\n1 0 1 0\n0 0 1 1\n";
        var doc = LoadPbm(pbm);

        var ppm = NetpbmExporter.PbmToPpm(doc.Image);
        Assert.Equal(doc.Width, ppm.Width);
        Assert.Equal(doc.Height, ppm.Height);
    }

    // ---- PbmToPpm: pixel value mapping ----

    [Fact]
    public void PbmToPpm_WhitePixel_AllChannels255()
    {
        // PBM 0 = white → PPM (255,255,255)
        const string pbm = "P1\n1 1\n0\n";
        var doc = LoadPbm(pbm);

        var ppm = NetpbmExporter.PbmToPpm(doc.Image);
        var ppmDoc = NetpbmDocument.FromImage(ppm);

        var (r, g, b) = ppmDoc.GetPixelColor(0, 0);
        Assert.Equal(255, r);
        Assert.Equal(255, g);
        Assert.Equal(255, b);
    }

    [Fact]
    public void PbmToPpm_BlackPixel_AllChannelsZero()
    {
        // PBM 1 = black → PPM (0,0,0)
        const string pbm = "P1\n1 1\n1\n";
        var doc = LoadPbm(pbm);

        var ppm = NetpbmExporter.PbmToPpm(doc.Image);
        var ppmDoc = NetpbmDocument.FromImage(ppm);

        var (r, g, b) = ppmDoc.GetPixelColor(0, 0);
        Assert.Equal(0, r);
        Assert.Equal(0, g);
        Assert.Equal(0, b);
    }

    // ---- PbmToPpm: wrong format throws ----

    [Fact]
    public void PbmToPpm_PgmInput_ThrowsArgumentException()
    {
        const string pgm = "P2\n2 2\n255\n100 200\n50 150\n";
        var doc = LoadPgm(pgm);

        Assert.Throws<ArgumentException>(() => NetpbmExporter.PbmToPpm(doc.Image));
    }

    // ---- Dogfood: PBM → PbmToPgm and PbmToPpm produce consistent dimensions ----

    [Fact]
    public void DogfoodPipeline_PbmToPgmAndPbmToPpm_SameDimensions()
    {
        const string pbm = "P1\n3 2\n0 1 0\n1 0 1\n";
        var doc = LoadPbm(pbm);

        var pgm = NetpbmExporter.PbmToPgm(doc.Image);
        var ppm = NetpbmExporter.PbmToPpm(doc.Image);

        Assert.Equal(doc.Width, pgm.Width);
        Assert.Equal(doc.Width, ppm.Width);
        Assert.Equal(doc.Height, pgm.Height);
        Assert.Equal(doc.Height, ppm.Height);
        Assert.Equal(NetpbmFormat.PGM_P2, pgm.Format);
        Assert.Equal(NetpbmFormat.PPM_P3, ppm.Format);
    }
}
