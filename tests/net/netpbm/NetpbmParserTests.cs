// FormatFactory.Netpbm.Tests -- Parser Tests
// R85 Train K: Third commercial .NET product first slice
// commercial_product_ready: false

using System;
using System.IO;
using System.Text;
using Xunit;
using FormatFactory.Netpbm;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmParserTests
{
    // -------------------------------------------------------------------------
    // PBM P1 (ASCII bitmap)
    // -------------------------------------------------------------------------

    [Fact]
    public void ParsePbmP1_SimpleImage_ReturnsCorrectDimensions()
    {
        const string pbm = "P1\n2 3\n0 1\n1 0\n0 0\n";
        var image = ParseString(pbm);
        Assert.Equal(NetpbmFormat.PBM_P1, image.Format);
        Assert.Equal(2, image.Width);
        Assert.Equal(3, image.Height);
        Assert.Equal(1, image.MaxValue);
    }

    [Fact]
    public void ParsePbmP1_PixelValues_AreCorrect()
    {
        const string pbm = "P1\n2 2\n0 1\n1 0\n";
        var image = ParseString(pbm);
        Assert.Equal(0, image.Pixels[0]); // row0, col0
        Assert.Equal(1, image.Pixels[1]); // row0, col1
        Assert.Equal(1, image.Pixels[2]); // row1, col0
        Assert.Equal(0, image.Pixels[3]); // row1, col1
    }

    [Fact]
    public void ParsePbmP1_WithComments_CommentsPreserved()
    {
        const string pbm = "P1\n# test comment\n2 2\n0 1\n0 0\n";
        var image = ParseString(pbm);
        Assert.Single(image.Comments);
        Assert.Contains("test comment", image.Comments[0]);
    }

    [Fact]
    public void ParsePbmP1_SinglePixel_Works()
    {
        const string pbm = "P1\n1 1\n1\n";
        var image = ParseString(pbm);
        Assert.Equal(1, image.Width);
        Assert.Equal(1, image.Height);
        Assert.Equal(1, image.Pixels[0]);
    }

    // -------------------------------------------------------------------------
    // PGM P2 (ASCII grayscale)
    // -------------------------------------------------------------------------

    [Fact]
    public void ParsePgmP2_SimpleImage_ReturnsCorrectData()
    {
        const string pgm = "P2\n3 2\n255\n0 128 255\n64 192 32\n";
        var image = ParseString(pgm);
        Assert.Equal(NetpbmFormat.PGM_P2, image.Format);
        Assert.Equal(3, image.Width);
        Assert.Equal(2, image.Height);
        Assert.Equal(255, image.MaxValue);
    }

    [Fact]
    public void ParsePgmP2_PixelValues_AreCorrect()
    {
        const string pgm = "P2\n2 2\n255\n10 20\n30 40\n";
        var image = ParseString(pgm);
        Assert.Equal(10, image.Pixels[0]);
        Assert.Equal(20, image.Pixels[1]);
        Assert.Equal(30, image.Pixels[2]);
        Assert.Equal(40, image.Pixels[3]);
    }

    [Fact]
    public void ParsePgmP2_MaxValue16_Works()
    {
        const string pgm = "P2\n2 1\n16\n0 16\n";
        var image = ParseString(pgm);
        Assert.Equal(16, image.MaxValue);
    }

    // -------------------------------------------------------------------------
    // PPM P3 (ASCII color)
    // -------------------------------------------------------------------------

    [Fact]
    public void ParsePpmP3_SimpleImage_ReturnsChannels()
    {
        const string ppm = "P3\n2 1\n255\n255 0 0 0 255 0\n";
        var image = ParseString(ppm);
        Assert.Equal(NetpbmFormat.PPM_P3, image.Format);
        Assert.Equal(2, image.Width);
        Assert.Equal(1, image.Height);
        Assert.NotNull(image.RedChannel);
        Assert.NotNull(image.GreenChannel);
        Assert.NotNull(image.BlueChannel);
    }

    [Fact]
    public void ParsePpmP3_PixelColors_AreCorrect()
    {
        const string ppm = "P3\n2 1\n255\n255 0 0 0 128 255\n";
        var image = ParseString(ppm);
        var (r0, g0, b0) = image.GetPixelColor(0, 0);
        var (r1, g1, b1) = image.GetPixelColor(0, 1);
        Assert.Equal(255, r0); Assert.Equal(0, g0); Assert.Equal(0, b0);
        Assert.Equal(0, r1); Assert.Equal(128, g1); Assert.Equal(255, b1);
    }

    // -------------------------------------------------------------------------
    // PBM P4 (binary bitmap)
    // -------------------------------------------------------------------------

    [Fact]
    public void ParsePbmP4_BinaryFormat_Works()
    {
        // P4 binary: 4x1 image, pixels: 1 0 1 0 → byte 0b10100000 = 0xA0
        var header = Encoding.ASCII.GetBytes("P4\n4 1\n");
        var pixels = new byte[] { 0xA0 }; // 1010 0000 (padded to byte)
        var data = Combine(header, new byte[] { 0x0A }, pixels); // 0x0A = '\n' (whitespace separator)
        // Actually P4 header ends after height, then ONE whitespace byte, then binary data
        // Let's construct correctly: "P4\n4 1\n" + 0xA0
        var correctData = Encoding.ASCII.GetBytes("P4\n4 1\n");
        var fullData = new byte[correctData.Length + 1];
        Array.Copy(correctData, fullData, correctData.Length);
        fullData[correctData.Length] = 0xA0;

        var image = ParseBytes(fullData);
        Assert.Equal(NetpbmFormat.PBM_P4, image.Format);
        Assert.Equal(4, image.Width);
        Assert.Equal(1, image.Height);
        // bits of 0xA0 = 1010 0000
        Assert.Equal(1, image.Pixels[0]);
        Assert.Equal(0, image.Pixels[1]);
        Assert.Equal(1, image.Pixels[2]);
        Assert.Equal(0, image.Pixels[3]);
    }

    // -------------------------------------------------------------------------
    // Error cases
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseInvalidMagic_ThrowsNetpbmFormatException()
    {
        const string bad = "P7\n1 1\n255\n0\n";
        Assert.Throws<NetpbmFormatException>(() => ParseString(bad));
    }

    [Fact]
    public void ParseEmptyFile_ThrowsNetpbmException()
    {
        Assert.Throws<NetpbmException>(() => ParseBytes(Array.Empty<byte>()));
    }

    [Fact]
    public void ParseOversizedImage_ThrowsNetpbmSizeException()
    {
        // width = 70000 > DefaultMaxDimension 65536
        const string pgm = "P2\n70000 1\n255\n0\n";
        Assert.Throws<NetpbmSizeException>(() => ParseString(pgm));
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private static NetpbmImage ParseString(string content)
    {
        var bytes = Encoding.ASCII.GetBytes(content);
        return ParseBytes(bytes);
    }

    private static NetpbmImage ParseBytes(byte[] bytes)
    {
        using var ms = new MemoryStream(bytes);
        return NetpbmParser.ParseStream(ms);
    }

    private static byte[] Combine(params byte[][] arrays)
    {
        int total = 0;
        foreach (var a in arrays) total += a.Length;
        var result = new byte[total];
        int offset = 0;
        foreach (var a in arrays)
        {
            Array.Copy(a, 0, result, offset, a.Length);
            offset += a.Length;
        }
        return result;
    }
}
