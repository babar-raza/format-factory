// R90 TASK-008: PPM-specific P3/P6 load, edit, save, export tests
// Closes GAP-CAP-001: PPM load/parse (P3/P6)
// Sprint: R90 autonomous continuation (iteration 1)

using System;
using System.IO;
using System.Text;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR90PpmParseTests
{
    [Fact]
    public void Parse_P3_Ascii_ReadsCorrectly()
    {
        var content = "P3\n2 2\n255\n255 0 0  0 255 0\n0 0 255  128 128 128\n";
        var path = WriteTempFile(content, ".ppm");
        try
        {
            var img = NetpbmParser.Parse(path);
            Assert.Equal(NetpbmFormat.PPM_P3, img.Format);
            Assert.Equal(2, img.Width);
            Assert.Equal(2, img.Height);
            Assert.Equal(255, img.MaxValue);

            var (r, g, b) = img.GetPixelColor(0, 0);
            Assert.Equal(255, r); Assert.Equal(0, g); Assert.Equal(0, b);

            var (r1, g1, b1) = img.GetPixelColor(0, 1);
            Assert.Equal(0, r1); Assert.Equal(255, g1); Assert.Equal(0, b1);

            var (r2, g2, b2) = img.GetPixelColor(1, 0);
            Assert.Equal(0, r2); Assert.Equal(0, g2); Assert.Equal(255, b2);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void Parse_P3_WithComments_PreservesComments()
    {
        var content = "P3\n# test comment\n1 1\n255\n100 150 200\n";
        var path = WriteTempFile(content, ".ppm");
        try
        {
            var img = NetpbmParser.Parse(path);
            Assert.Contains("test comment", img.Comments);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void Parse_P6_Binary_ReadsCorrectly()
    {
        // P6: header is ASCII, pixels are binary RGB triplets
        var header = "P6\n2 1\n255\n";
        var headerBytes = Encoding.ASCII.GetBytes(header);
        var pixelBytes = new byte[] { 255, 0, 0, 0, 255, 0 }; // red, green
        var allBytes = new byte[headerBytes.Length + pixelBytes.Length];
        Buffer.BlockCopy(headerBytes, 0, allBytes, 0, headerBytes.Length);
        Buffer.BlockCopy(pixelBytes, 0, allBytes, headerBytes.Length, pixelBytes.Length);

        var path = Path.GetTempFileName() + ".ppm";
        File.WriteAllBytes(path, allBytes);
        try
        {
            var img = NetpbmParser.Parse(path);
            Assert.Equal(NetpbmFormat.PPM_P6, img.Format);
            Assert.Equal(2, img.Width);
            Assert.Equal(1, img.Height);

            var (r, g, b) = img.GetPixelColor(0, 0);
            Assert.Equal(255, r); Assert.Equal(0, g); Assert.Equal(0, b);

            var (r1, g1, b1) = img.GetPixelColor(0, 1);
            Assert.Equal(0, r1); Assert.Equal(255, g1); Assert.Equal(0, b1);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void Parse_P6_MaxValue_Preserved()
    {
        var header = "P6\n1 1\n127\n";
        var headerBytes = Encoding.ASCII.GetBytes(header);
        var pixelBytes = new byte[] { 64, 32, 16 };
        var allBytes = new byte[headerBytes.Length + pixelBytes.Length];
        Buffer.BlockCopy(headerBytes, 0, allBytes, 0, headerBytes.Length);
        Buffer.BlockCopy(pixelBytes, 0, allBytes, headerBytes.Length, pixelBytes.Length);

        var path = Path.GetTempFileName() + ".ppm";
        File.WriteAllBytes(path, allBytes);
        try
        {
            var img = NetpbmParser.Parse(path);
            Assert.Equal(127, img.MaxValue);
        }
        finally { File.Delete(path); }
    }

    private static string WriteTempFile(string content, string ext)
    {
        var path = Path.GetTempFileName() + ext;
        File.WriteAllText(path, content);
        return path;
    }
}

public class NetpbmR90PpmEditTests
{
    [Fact]
    public void SetPixelColor_UpdatesChannels()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 2, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 0, 0 },
            GreenChannel = new byte[] { 0, 0 },
            BlueChannel = new byte[] { 0, 0 }
        };

        img.SetPixelColor(0, 1, 100, 150, 200);
        var (r, g, b) = img.GetPixelColor(0, 1);
        Assert.Equal(100, r);
        Assert.Equal(150, g);
        Assert.Equal(200, b);
    }

    [Fact]
    public void GetPixel_ThrowsOnPpm()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 0 },
            GreenChannel = new byte[] { 0 },
            BlueChannel = new byte[] { 0 }
        };

        Assert.Throws<InvalidOperationException>(() => img.GetPixel(0, 0));
    }
}

public class NetpbmR90PpmWriteTests
{
    [Fact]
    public void Write_P3_Roundtrip()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 2, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 255, 0 },
            GreenChannel = new byte[] { 0, 128 },
            BlueChannel = new byte[] { 0, 64 }
        };

        var ascii = NetpbmWriter.ToAsciiString(img);
        Assert.Contains("P3", ascii);
        Assert.Contains("255", ascii);
    }

    [Fact]
    public void Write_P6_Binary_Roundtrip()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P6,
            Width = 2, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 100, 200 },
            GreenChannel = new byte[] { 50, 150 },
            BlueChannel = new byte[] { 25, 75 }
        };

        var path = Path.GetTempFileName() + ".ppm";
        try
        {
            NetpbmWriter.Write(img, path);
            var reloaded = NetpbmParser.Parse(path);

            Assert.Equal(NetpbmFormat.PPM_P6, reloaded.Format);
            Assert.Equal(2, reloaded.Width);

            var (r, g, b) = reloaded.GetPixelColor(0, 0);
            Assert.Equal(100, r);
            Assert.Equal(50, g);
            Assert.Equal(25, b);
        }
        finally { File.Delete(path); }
    }
}

public class NetpbmR90PpmExportTests
{
    [Fact]
    public void PpmToPgm_ProducesGrayscale()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 255 },
            GreenChannel = new byte[] { 255 },
            BlueChannel = new byte[] { 255 }
        };

        var pgm = NetpbmExporter.PpmToPgm(img);
        Assert.Equal(NetpbmFormat.PGM_P2, pgm.Format);
        Assert.Equal(255, pgm.GetPixel(0, 0)); // white → 255 gray
    }

    [Fact]
    public void PgmToPpm_ProducesColor()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 128 }
        };

        var ppm = NetpbmExporter.PgmToPpm(img);
        Assert.Equal(NetpbmFormat.PPM_P3, ppm.Format);
        var (r, g, b) = ppm.GetPixelColor(0, 0);
        Assert.Equal(128, r);
        Assert.Equal(128, g);
        Assert.Equal(128, b);
    }
}
