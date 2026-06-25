// Tests for NetpbmDocument sealed class (GAP-PROD-INV-NETPBM-001)
// Sprint: FORMAT-FACTORY-NETPBM-DOCUMENT-20260624
// commercial_product_ready: false

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR117DocumentTests
{
    // ---- Helpers ----

    private static NetpbmImage MakePbmImage(int w, int h)
    {
        var img = new NetpbmImage { Format = NetpbmFormat.PBM_P1, Width = w, Height = h, MaxValue = 1 };
        img.Pixels = new byte[w * h];
        return img;
    }

    private static NetpbmImage MakePgmImage(int w, int h)
    {
        var img = new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = w, Height = h, MaxValue = 255 };
        img.Pixels = new byte[w * h];
        return img;
    }

    private static NetpbmImage MakePpmImage(int w, int h)
    {
        var img = new NetpbmImage { Format = NetpbmFormat.PPM_P3, Width = w, Height = h, MaxValue = 255 };
        img.RedChannel = new byte[w * h];
        img.GreenChannel = new byte[w * h];
        img.BlueChannel = new byte[w * h];
        return img;
    }

    // ---- FromImage / properties ----

    [Fact]
    public void FromImage_ReturnsDocumentWithCorrectDimensions()
    {
        var img = MakePbmImage(4, 3);
        var doc = NetpbmDocument.FromImage(img);
        Assert.Equal(4, doc.Width);
        Assert.Equal(3, doc.Height);
    }

    [Fact]
    public void PixelCount_IsWidthTimesHeight()
    {
        var img = MakePgmImage(5, 7);
        var doc = NetpbmDocument.FromImage(img);
        Assert.Equal(35, doc.PixelCount);
    }

    [Fact]
    public void Format_ReflectsUnderlyingImage()
    {
        var pbm = NetpbmDocument.FromImage(MakePbmImage(2, 2));
        var pgm = NetpbmDocument.FromImage(MakePgmImage(2, 2));
        var ppm = NetpbmDocument.FromImage(MakePpmImage(2, 2));
        Assert.Equal(NetpbmFormat.PBM_P1, pbm.Format);
        Assert.Equal(NetpbmFormat.PGM_P2, pgm.Format);
        Assert.Equal(NetpbmFormat.PPM_P3, ppm.Format);
    }

    [Fact]
    public void MaxValue_ReflectsImage()
    {
        var img = MakePgmImage(2, 2);
        img.MaxValue = 63;
        var doc = NetpbmDocument.FromImage(img);
        Assert.Equal(63, doc.MaxValue);
    }

    [Fact]
    public void FromImage_NullThrows()
    {
        Assert.Throws<ArgumentNullException>(() => NetpbmDocument.FromImage(null!));
    }

    // ---- GetPixel / GetPixelColor ----

    [Fact]
    public void GetPixel_PgmReturnsCorrectValue()
    {
        var img = MakePgmImage(3, 3);
        img.SetPixel(1, 2, 128);
        var doc = NetpbmDocument.FromImage(img);
        Assert.Equal(128, doc.GetPixel(1, 2));
    }

    [Fact]
    public void GetPixelColor_PpmReturnsRgb()
    {
        var img = MakePpmImage(2, 2);
        img.SetPixelColor(0, 1, 10, 20, 30);
        var doc = NetpbmDocument.FromImage(img);
        var (r, g, b) = doc.GetPixelColor(0, 1);
        Assert.Equal(10, r);
        Assert.Equal(20, g);
        Assert.Equal(30, b);
    }

    // ---- ToAsciiString / ToBinaryBytes ----

    [Fact]
    public void ToAsciiString_PbmProducesP1Header()
    {
        var img = MakePbmImage(2, 1);
        var doc = NetpbmDocument.FromImage(img);
        var s = doc.ToAsciiString();
        Assert.StartsWith("P1", s);
    }

    [Fact]
    public void ToBinaryBytes_PbmP4ProducesBytes()
    {
        var img = new NetpbmImage { Format = NetpbmFormat.PBM_P4, Width = 8, Height = 1, MaxValue = 1 };
        img.Pixels = new byte[8];
        var doc = NetpbmDocument.FromImage(img);
        var bytes = doc.ToBinaryBytes();
        Assert.NotEmpty(bytes);
    }

    // ---- Load / Save roundtrip ----

    [Fact]
    public void LoadStream_ThenSave_RoundtripPreservesDimensions()
    {
        // Build P2 ASCII PGM in memory
        var img = MakePgmImage(3, 2);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 2, 200);
        var ascii = NetpbmWriter.ToAsciiString(img);
        var bytes = System.Text.Encoding.ASCII.GetBytes(ascii);

        NetpbmDocument doc;
        using (var ms = new MemoryStream(bytes))
            doc = NetpbmDocument.LoadStream(ms);

        Assert.Equal(3, doc.Width);
        Assert.Equal(2, doc.Height);
        Assert.Equal(50, doc.GetPixel(0, 0));
        Assert.Equal(200, doc.GetPixel(1, 2));
    }

    [Fact]
    public void SourcePath_IsNullForStreamLoad()
    {
        var img = MakePbmImage(1, 1);
        var ascii = System.Text.Encoding.ASCII.GetBytes(NetpbmWriter.ToAsciiString(img));
        using var ms = new MemoryStream(ascii);
        var doc = NetpbmDocument.LoadStream(ms);
        Assert.Null(doc.SourcePath);
    }

    [Fact]
    public void FromImage_SourcePathIsNull()
    {
        var doc = NetpbmDocument.FromImage(MakePbmImage(2, 2));
        Assert.Null(doc.SourcePath);
    }
}
