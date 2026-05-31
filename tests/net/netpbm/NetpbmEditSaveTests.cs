// FormatFactory.Netpbm.Tests -- Edit + Save + Roundtrip Tests
// R85 Train K: Third commercial .NET product first slice
// commercial_product_ready: false

using System;
using System.IO;
using System.Text;
using Xunit;
using FormatFactory.Netpbm;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmEditSaveTests
{
    // -------------------------------------------------------------------------
    // Edit pixel values (PBM)
    // -------------------------------------------------------------------------

    [Fact]
    public void SetPixel_Pbm_UpdatesValue()
    {
        var image = MakePbm(2, 2);
        image.SetPixel(0, 0, 0);
        image.SetPixel(0, 1, 1);
        Assert.Equal(0, image.GetPixel(0, 0));
        Assert.Equal(1, image.GetPixel(0, 1));
    }

    [Fact]
    public void SetPixel_InvalidPbmValue_Throws()
    {
        var image = MakePbm(2, 2);
        Assert.Throws<ArgumentOutOfRangeException>(() => image.SetPixel(0, 0, 2));
    }

    [Fact]
    public void SetPixel_OutOfRange_Throws()
    {
        var image = MakePbm(2, 2);
        Assert.Throws<ArgumentOutOfRangeException>(() => image.SetPixel(5, 0, 0));
    }

    // -------------------------------------------------------------------------
    // Edit pixel values (PGM)
    // -------------------------------------------------------------------------

    [Fact]
    public void SetPixel_Pgm_UpdatesValue()
    {
        var image = MakePgm(3, 3);
        image.SetPixel(1, 1, 128);
        Assert.Equal(128, image.GetPixel(1, 1));
    }

    [Fact]
    public void SetPixelColor_Ppm_UpdatesChannels()
    {
        var image = MakePpm(2, 2);
        image.SetPixelColor(0, 0, 255, 0, 128);
        var (r, g, b) = image.GetPixelColor(0, 0);
        Assert.Equal(255, r);
        Assert.Equal(0, g);
        Assert.Equal(128, b);
    }

    // -------------------------------------------------------------------------
    // Stats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStats_Pgm_ReturnsCorrectMinMaxMean()
    {
        const string pgm = "P2\n2 2\n255\n0 100\n200 255\n";
        var image = ParseString(pgm);
        var (mean, min, max) = image.GetStats();
        Assert.Equal(0, min);
        Assert.Equal(255, max);
        Assert.Equal(138.75, mean, 1);
    }

    // -------------------------------------------------------------------------
    // Writer roundtrip (PBM → ASCII → parse back)
    // -------------------------------------------------------------------------

    [Fact]
    public void WritePbm_RoundTrip_PixelsPreserved()
    {
        const string original = "P1\n3 2\n0 1 0\n1 0 1\n";
        var image = ParseString(original);
        string written = NetpbmWriter.ToAsciiString(image);
        var reparsed = ParseString(written);

        Assert.Equal(image.Width, reparsed.Width);
        Assert.Equal(image.Height, reparsed.Height);
        for (int i = 0; i < image.Pixels.Length; i++)
            Assert.Equal(image.Pixels[i], reparsed.Pixels[i]);
    }

    [Fact]
    public void WritePgm_RoundTrip_PixelsPreserved()
    {
        const string original = "P2\n2 2\n255\n10 200\n50 100\n";
        var image = ParseString(original);
        string written = NetpbmWriter.ToAsciiString(image);
        var reparsed = ParseString(written);

        Assert.Equal(image.Width, reparsed.Width);
        Assert.Equal(image.Height, reparsed.Height);
        Assert.Equal(image.MaxValue, reparsed.MaxValue);
        for (int i = 0; i < image.Pixels.Length; i++)
            Assert.Equal(image.Pixels[i], reparsed.Pixels[i]);
    }

    [Fact]
    public void WritePpm_RoundTrip_ChannelsPreserved()
    {
        const string original = "P3\n2 1\n255\n255 0 128 0 200 64\n";
        var image = ParseString(original);
        string written = NetpbmWriter.ToAsciiString(image);
        var reparsed = ParseString(written);

        Assert.Equal(image.Width, reparsed.Width);
        var (r0, g0, b0) = reparsed.GetPixelColor(0, 0);
        Assert.Equal(255, r0); Assert.Equal(0, g0); Assert.Equal(128, b0);
    }

    [Fact]
    public void WriteToFile_PbmImage_FileCreated()
    {
        var image = MakePbm(2, 2, new byte[] { 0, 1, 1, 0 });
        string tmpPath = Path.GetTempFileName() + ".pbm";
        try
        {
            NetpbmWriter.Write(image, tmpPath);
            Assert.True(File.Exists(tmpPath));
            string content = File.ReadAllText(tmpPath);
            Assert.StartsWith("P1", content);
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }

    // -------------------------------------------------------------------------
    // Edit-save-reload cycle
    // -------------------------------------------------------------------------

    [Fact]
    public void EditSaveReload_PbmImage_EditSurvives()
    {
        // Create a 3x3 PBM, edit pixel (1,1), save, reload, verify
        const string original = "P1\n3 3\n0 0 0\n0 0 0\n0 0 0\n";
        var image = ParseString(original);

        // Edit: set center pixel to 1
        image.SetPixel(1, 1, 1);
        Assert.Equal(1, image.GetPixel(1, 1));

        // Save to string
        string saved = NetpbmWriter.ToAsciiString(image);

        // Reload
        var reloaded = ParseString(saved);
        Assert.Equal(1, reloaded.GetPixel(1, 1));
        Assert.Equal(0, reloaded.GetPixel(0, 0));
        Assert.Equal(0, reloaded.GetPixel(2, 2));
    }

    [Fact]
    public void EditSaveReload_PgmImage_MultipleEdits_Survive()
    {
        const string original = "P2\n3 3\n255\n0 0 0\n0 0 0\n0 0 0\n";
        var image = ParseString(original);

        image.SetPixel(0, 0, 100);
        image.SetPixel(1, 1, 200);
        image.SetPixel(2, 2, 50);

        var reloaded = ParseString(NetpbmWriter.ToAsciiString(image));
        Assert.Equal(100, reloaded.GetPixel(0, 0));
        Assert.Equal(200, reloaded.GetPixel(1, 1));
        Assert.Equal(50, reloaded.GetPixel(2, 2));
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private static NetpbmImage ParseString(string content)
    {
        using var ms = new MemoryStream(Encoding.ASCII.GetBytes(content));
        return NetpbmParser.ParseStream(ms);
    }

    private static NetpbmImage MakePbm(int w, int h, byte[]? pixels = null)
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = w,
            Height = h,
            MaxValue = 1,
            Pixels = pixels ?? new byte[w * h]
        };
        return img;
    }

    private static NetpbmImage MakePgm(int w, int h)
    {
        return new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = w,
            Height = h,
            MaxValue = 255,
            Pixels = new byte[w * h]
        };
    }

    private static NetpbmImage MakePpm(int w, int h)
    {
        long count = (long)w * h;
        return new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = w,
            Height = h,
            MaxValue = 255,
            RedChannel = new byte[count],
            GreenChannel = new byte[count],
            BlueChannel = new byte[count]
        };
    }
}
