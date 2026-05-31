// FormatFactory.Netpbm.Tests -- Dogfood Export Tests
// R85 Train K: Third commercial .NET product first slice
// commercial_product_ready: false
//
// dogfood_status: IMPLEMENTED — PBM→PGM and PBM→PPM use Format Factory Netpbm model

using System;
using System.IO;
using System.Text;
using Xunit;
using FormatFactory.Netpbm;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmExporterTests
{
    // -------------------------------------------------------------------------
    // PBM → PGM (dogfood export)
    // -------------------------------------------------------------------------

    [Fact]
    public void PbmToPgm_Black_MapsToZero()
    {
        // PBM black pixel (1) → PGM 0
        const string pbm = "P1\n1 1\n1\n";
        var pbmImg = ParseString(pbm);
        var pgmImg = NetpbmExporter.PbmToPgm(pbmImg);

        Assert.Equal(NetpbmFormat.PGM_P2, pgmImg.Format);
        Assert.Equal(0, pgmImg.GetPixel(0, 0));
    }

    [Fact]
    public void PbmToPgm_White_MapsToMaxValue()
    {
        // PBM white pixel (0) → PGM 255
        const string pbm = "P1\n1 1\n0\n";
        var pbmImg = ParseString(pbm);
        var pgmImg = NetpbmExporter.PbmToPgm(pbmImg);

        Assert.Equal(255, pgmImg.GetPixel(0, 0));
    }

    [Fact]
    public void PbmToPgm_DimensionsPreserved()
    {
        const string pbm = "P1\n4 3\n0 1 0 1\n1 0 1 0\n0 0 1 1\n";
        var pbmImg = ParseString(pbm);
        var pgmImg = NetpbmExporter.PbmToPgm(pbmImg);

        Assert.Equal(4, pgmImg.Width);
        Assert.Equal(3, pgmImg.Height);
    }

    [Fact]
    public void PbmToPgm_CustomMaxValue_UsedCorrectly()
    {
        const string pbm = "P1\n2 1\n0 1\n";
        var pbmImg = ParseString(pbm);
        var pgmImg = NetpbmExporter.PbmToPgm(pbmImg, maxValue: 100);

        Assert.Equal(100, pgmImg.MaxValue);
        Assert.Equal(100, pgmImg.GetPixel(0, 0)); // white
        Assert.Equal(0, pgmImg.GetPixel(0, 1));   // black
    }

    [Fact]
    public void PbmToPgm_OutputIsWritable()
    {
        const string pbm = "P1\n3 2\n0 1 0\n1 0 1\n";
        var pbmImg = ParseString(pbm);
        var pgmImg = NetpbmExporter.PbmToPgm(pbmImg);

        // Should be able to write the resulting PGM
        string written = NetpbmWriter.ToAsciiString(pgmImg);
        Assert.StartsWith("P2", written);
        Assert.Contains("255", written);
    }

    [Fact]
    public void PbmToPgm_CommentPropagated()
    {
        const string pbm = "P1\n# source image\n1 1\n0\n";
        var pbmImg = ParseString(pbm);
        var pgmImg = NetpbmExporter.PbmToPgm(pbmImg);

        Assert.Contains("source image", pgmImg.Comments[0]);
        // Also contains dogfood comment
        Assert.Contains("FormatFactory.Netpbm", pgmImg.Comments[^1]);
    }

    [Fact]
    public void PbmToPgm_CheckerPattern_CorrectlyMapped()
    {
        // 2x2 checkerboard: 0 1 / 1 0
        const string pbm = "P1\n2 2\n0 1\n1 0\n";
        var pbmImg = ParseString(pbm);
        var pgmImg = NetpbmExporter.PbmToPgm(pbmImg);

        Assert.Equal(255, pgmImg.GetPixel(0, 0)); // white
        Assert.Equal(0, pgmImg.GetPixel(0, 1));   // black
        Assert.Equal(0, pgmImg.GetPixel(1, 0));   // black
        Assert.Equal(255, pgmImg.GetPixel(1, 1)); // white
    }

    // -------------------------------------------------------------------------
    // PBM → PPM (dogfood export)
    // -------------------------------------------------------------------------

    [Fact]
    public void PbmToPpm_Black_MapsToZeroChannels()
    {
        const string pbm = "P1\n1 1\n1\n";
        var pbmImg = ParseString(pbm);
        var ppmImg = NetpbmExporter.PbmToPpm(pbmImg);

        Assert.Equal(NetpbmFormat.PPM_P3, ppmImg.Format);
        var (r, g, b) = ppmImg.GetPixelColor(0, 0);
        Assert.Equal(0, r); Assert.Equal(0, g); Assert.Equal(0, b);
    }

    [Fact]
    public void PbmToPpm_White_MapsToMaxChannels()
    {
        const string pbm = "P1\n1 1\n0\n";
        var pbmImg = ParseString(pbm);
        var ppmImg = NetpbmExporter.PbmToPpm(pbmImg);

        var (r, g, b) = ppmImg.GetPixelColor(0, 0);
        Assert.Equal(255, r); Assert.Equal(255, g); Assert.Equal(255, b);
    }

    [Fact]
    public void PbmToPpm_OutputIsWritable()
    {
        const string pbm = "P1\n2 2\n0 1\n1 0\n";
        var pbmImg = ParseString(pbm);
        var ppmImg = NetpbmExporter.PbmToPpm(pbmImg);
        string written = NetpbmWriter.ToAsciiString(ppmImg);
        Assert.StartsWith("P3", written);
    }

    // -------------------------------------------------------------------------
    // Error handling
    // -------------------------------------------------------------------------

    [Fact]
    public void PbmToPgm_WithPgmInput_Throws()
    {
        const string pgm = "P2\n2 1\n255\n0 100\n";
        var pgmImg = ParseString(pgm);
        Assert.Throws<ArgumentException>(() => NetpbmExporter.PbmToPgm(pgmImg));
    }

    // -------------------------------------------------------------------------
    // Helper
    // -------------------------------------------------------------------------

    private static NetpbmImage ParseString(string content)
    {
        using var ms = new MemoryStream(Encoding.ASCII.GetBytes(content));
        return NetpbmParser.ParseStream(ms);
    }
}
