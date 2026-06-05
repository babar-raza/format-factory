using Xunit;
using System;
using System.IO;
using FormatFactory.Netpbm;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R112 depth: Netpbm Sepia save-reload roundtrip.
/// Proves Sepia→SaveToFile→Load roundtrip preserves image data.
/// </summary>
public class NetpbmR112SepiaSaveRoundtripTests
{
    private static NetpbmImage CreatePpm(int w, int h, byte r, byte g, byte b)
    {
        var img = new NetpbmImage
        {
            Width = w, Height = h,
            Format = NetpbmFormat.PPM_P3,
            MaxValue = 255,
            RedChannel = new byte[w * h],
            GreenChannel = new byte[w * h],
            BlueChannel = new byte[w * h]
        };
        Array.Fill(img.RedChannel, r);
        Array.Fill(img.GreenChannel, g);
        Array.Fill(img.BlueChannel, b);
        return img;
    }

    [Fact]
    public void Sepia_SaveReload_DimensionsPreserved()
    {
        var img = CreatePpm(4, 4, 100, 150, 200);
        var sepia = img.Sepia();
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            sepia.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(sepia.Width, reloaded.Width);
            Assert.Equal(sepia.Height, reloaded.Height);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Sepia_SaveReload_PixelsPreserved()
    {
        var img = CreatePpm(4, 4, 100, 150, 200);
        var sepia = img.Sepia();
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            sepia.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(sepia.RedChannel![0], reloaded.RedChannel![0]);
            Assert.Equal(sepia.GreenChannel![0], reloaded.GreenChannel![0]);
            Assert.Equal(sepia.BlueChannel![0], reloaded.BlueChannel![0]);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Sepia_HasWarmTones()
    {
        var img = CreatePpm(4, 4, 100, 100, 100);
        var sepia = img.Sepia();
        // Sepia should make red >= green >= blue
        Assert.True(sepia.RedChannel![0] >= sepia.GreenChannel![0]);
        Assert.True(sepia.GreenChannel![0] >= sepia.BlueChannel![0]);
    }

    [Fact]
    public void Sepia_ThenSharpen_SaveReload()
    {
        var img = CreatePpm(8, 8, 100, 150, 200);
        var processed = img.Sepia().Sharpen();
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            processed.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(8, reloaded.Width);
            Assert.Equal(8, reloaded.Height);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Sepia_ThenBlur_SaveReload()
    {
        var img = CreatePpm(8, 8, 100, 150, 200);
        var processed = img.Sepia().BlurBox(1);
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            processed.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(processed.RedChannel![0], reloaded.RedChannel![0]);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Sepia_DoesNotMutateOriginal()
    {
        var img = CreatePpm(4, 4, 100, 150, 200);
        byte origR = img.RedChannel![0];
        var sepia = img.Sepia();
        Assert.Equal(origR, img.RedChannel![0]);
    }

    [Fact]
    public void Equalize_SaveReload_Roundtrip()
    {
        var img = CreatePpm(4, 4, 50, 100, 200);
        img.RedChannel![0] = 0;
        img.RedChannel![1] = 255;
        var eq = img.Equalize();
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            eq.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(eq.Width, reloaded.Width);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ConvertFormat_PgmToPpm_SaveReload()
    {
        var pgm = new NetpbmImage
        {
            Width = 4, Height = 4,
            Format = NetpbmFormat.PGM_P2,
            MaxValue = 255,
            Pixels = new byte[16]
        };
        Array.Fill(pgm.Pixels, (byte)128);
        var ppm = pgm.ToColor();
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            ppm.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(4, reloaded.Width);
            Assert.NotNull(reloaded.RedChannel);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
