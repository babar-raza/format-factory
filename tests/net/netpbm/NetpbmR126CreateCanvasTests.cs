// Tests for NetpbmImage.Create(width, height, format, fill) — blank canvas factory.
// Sprint: FORMAT-FACTORY-NETPBM-CREATE-CANVAS-20260626
// Ledger: R126-GOVERNED-DOTNET-NETPBM-CREATE-CANVAS-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R126: NetpbmImage.Create(width, height, format, fill) creates a blank canvas
/// with all pixels set to fill (default 0). PPM channels are all set to fill.
/// Tests verify dimensions, format, pixel values, fill value, and guard conditions.
/// </summary>
public class NetpbmR126CreateCanvasTests
{
    // ---- Basic: creates PGM canvas with default fill=0 ----

    [Fact]
    public void Create_Pgm_DimensionsCorrect()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P2);
        Assert.Equal(4, img.Width);
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void Create_Pgm_FormatCorrect()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2);
        Assert.Equal(NetpbmFormat.PGM_P2, img.Format);
    }

    [Fact]
    public void Create_Pgm_DefaultFill_AllPixelsZero()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P2);
        var doc = NetpbmDocument.FromImage(img);
        for (int row = 0; row < 3; row++)
            for (int col = 0; col < 3; col++)
                Assert.Equal(0, doc.GetPixel(row, col));
    }

    // ---- Custom fill value ----

    [Fact]
    public void Create_Pgm_CustomFill_AllPixelsFilled()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P2, fill: 128);
        var doc = NetpbmDocument.FromImage(img);
        for (int row = 0; row < 3; row++)
            for (int col = 0; col < 3; col++)
                Assert.Equal(128, doc.GetPixel(row, col));
    }

    [Fact]
    public void Create_Pgm_FillMax255_AllPixels255()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2, fill: 255);
        var doc = NetpbmDocument.FromImage(img);
        Assert.Equal(255, doc.GetPixel(0, 0));
        Assert.Equal(255, doc.GetPixel(1, 1));
    }

    // ---- PPM canvas: all channels filled ----

    [Fact]
    public void Create_Ppm_FormatCorrect()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PPM_P3, fill: 100);
        Assert.Equal(NetpbmFormat.PPM_P3, img.Format);
    }

    [Fact]
    public void Create_Ppm_CustomFill_AllChannelsFilled()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PPM_P3, fill: 150);
        var doc = NetpbmDocument.FromImage(img);
        var (r, g, b) = doc.GetPixelColor(0, 0);
        Assert.Equal(150, r);
        Assert.Equal(150, g);
        Assert.Equal(150, b);
    }

    // ---- Guards: zero/negative dimensions throw ----

    [Fact]
    public void Create_ZeroWidth_ThrowsArgumentOutOfRangeException()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            NetpbmImage.Create(0, 2, NetpbmFormat.PGM_P2));
    }

    [Fact]
    public void Create_ZeroHeight_ThrowsArgumentOutOfRangeException()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            NetpbmImage.Create(2, 0, NetpbmFormat.PGM_P2));
    }

    [Fact]
    public void Create_NegativeWidth_ThrowsArgumentOutOfRangeException()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            NetpbmImage.Create(-1, 2, NetpbmFormat.PGM_P2));
    }

    // ---- Dogfood: Create canvas, edit pixels, serialize, reload ----

    [Fact]
    public void DogfoodPipeline_CreateCanvas_EditPixel_Serialize_Reload()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P2, fill: 50);
        var doc = NetpbmDocument.FromImage(img);

        // Edit center pixels
        doc.Image.SetPixel(1, 1, 200);
        doc.Image.SetPixel(2, 2, 200);

        // Serialize and reload
        var ascii = doc.ToAsciiString();
        var bytes = Encoding.ASCII.GetBytes(ascii);
        using var ms = new MemoryStream(bytes);
        var doc2 = NetpbmDocument.LoadStream(ms);

        Assert.Equal(200, doc2.GetPixel(1, 1));
        Assert.Equal(200, doc2.GetPixel(2, 2));
        // Untouched pixels remain 50
        Assert.Equal(50, doc2.GetPixel(0, 0));
        Assert.Equal(50, doc2.GetPixel(3, 3));
    }
}
