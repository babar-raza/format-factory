// R87 Train J: Netpbm .NET third commercial product deepening tests
// Sprint: FORMAT-FACTORY-R87-CLEAN-SUPERVISOR-CLOSEOUT-REVIEW-PACKAGE-POC-PRODUCT-FACTORY-DEEPENING-MEGA-TRAIN-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR87ProductDeepening : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR87ProductDeepening()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "netpbm-r87-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // === GetPixelColor API ===

    [Fact]
    public void GetPixelColor_ReturnsCorrectRGB()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 2, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 255, 0 },
            GreenChannel = new byte[] { 0, 128 },
            BlueChannel = new byte[] { 64, 255 }
        };

        var (r, g, b) = img.GetPixelColor(0, 0);
        Assert.Equal(255, r);
        Assert.Equal(0, g);
        Assert.Equal(64, b);

        var (r2, g2, b2) = img.GetPixelColor(0, 1);
        Assert.Equal(0, r2);
        Assert.Equal(128, g2);
        Assert.Equal(255, b2);
    }

    [Fact]
    public void GetPixelColor_OnPGM_Throws()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 128 }
        };
        Assert.Throws<InvalidOperationException>(() => img.GetPixelColor(0, 0));
    }

    // === FlipHorizontal ===

    [Fact]
    public void FlipHorizontal_PGM_MirrorsPixels()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 10, 20, 30 }
        };
        img.FlipHorizontal();
        Assert.Equal(new byte[] { 30, 20, 10 }, img.Pixels);
    }

    [Fact]
    public void FlipHorizontal_PPM_MirrorsChannels()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 2, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 100, 200 },
            GreenChannel = new byte[] { 50, 150 },
            BlueChannel = new byte[] { 25, 75 }
        };
        img.FlipHorizontal();
        Assert.Equal(new byte[] { 200, 100 }, img.RedChannel);
        Assert.Equal(new byte[] { 150, 50 }, img.GreenChannel);
        Assert.Equal(new byte[] { 75, 25 }, img.BlueChannel);
    }

    // === PgmToPpm export ===

    [Fact]
    public void PgmToPpm_ProducesValidPpm()
    {
        var pgm = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 2, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 0, 128, 255, 64 }
        };
        var ppm = NetpbmExporter.PgmToPpm(pgm);
        Assert.Equal(NetpbmFormat.PPM_P3, ppm.Format);
        Assert.Equal(2, ppm.Width);
        Assert.Equal(2, ppm.Height);
        // Gray value should be replicated to all channels
        Assert.Equal((byte)0, ppm.RedChannel![0]);
        Assert.Equal((byte)128, ppm.RedChannel[1]);
        Assert.Equal((byte)128, ppm.GreenChannel![1]);
        Assert.Equal((byte)128, ppm.BlueChannel![1]);
    }

    [Fact]
    public void PgmToPpm_PreservesComments()
    {
        var pgm = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 100 }
        };
        pgm.Comments.Add("original comment");
        var ppm = NetpbmExporter.PgmToPpm(pgm);
        Assert.Contains("original comment", ppm.Comments);
        Assert.Contains("dogfood export", ppm.Comments[^1]);
    }

    [Fact]
    public void PgmToPpm_RoundTrip_WriteRead()
    {
        var pgm = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 10, 20, 30, 40, 50, 60 }
        };
        var ppm = NetpbmExporter.PgmToPpm(pgm);
        var outPath = Path.Combine(_tempDir, "roundtrip.ppm");
        NetpbmWriter.Write(ppm, outPath);
        var loaded = NetpbmParser.Parse(outPath);
        Assert.Equal(3, loaded.Width);
        Assert.Equal(2, loaded.Height);
    }

    // === PpmToPgm grayscale export ===

    [Fact]
    public void PpmToPgm_GrayscaleConversion()
    {
        var ppm = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 255 },
            GreenChannel = new byte[] { 0 },
            BlueChannel = new byte[] { 0 }
        };
        var pgm = NetpbmExporter.PpmToPgm(ppm);
        Assert.Equal(NetpbmFormat.PGM_P2, pgm.Format);
        // 0.299*255 = 76.245 → 76
        Assert.True(pgm.Pixels[0] >= 75 && pgm.Pixels[0] <= 77,
            $"Expected ~76, got {pgm.Pixels[0]}");
    }

    [Fact]
    public void PpmToPgm_WhiteToWhite()
    {
        var ppm = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 255 },
            GreenChannel = new byte[] { 255 },
            BlueChannel = new byte[] { 255 }
        };
        var pgm = NetpbmExporter.PpmToPgm(ppm);
        Assert.Equal(255, pgm.Pixels[0]);
    }

    [Fact]
    public void PpmToPgm_InvalidFormat_Throws()
    {
        var pbm = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 1, Height = 1,
            Pixels = new byte[] { 0 }
        };
        Assert.Throws<ArgumentException>(() => NetpbmExporter.PpmToPgm(pbm));
    }
}
