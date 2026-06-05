// R99 Train D: Netpbm .NET ToColor (PGM->PPM) Dogfood Conversion Tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R99-GOVERNED-DOTNET-NETPBM-TOCOLOR-001
// New API: ToColor() — converts PGM grayscale to PPM color

using System;
using System.IO;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR99ToColorTests
{
    [Fact]
    public void ToColor_PgmTosPpm()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 2, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 0, 128, 64, 255 },
        };
        var color = img.ToColor();
        Assert.Equal(NetpbmFormat.PPM_P6, color.Format);
        Assert.Equal(2, color.Width);
        Assert.Equal(2, color.Height);
        Assert.Equal(255, color.MaxValue);
    }

    [Fact]
    public void ToColor_PixelsReplicatedAcrossChannels()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 100 },
        };
        var color = img.ToColor();
        Assert.Equal(100, color.RedChannel![0]);
        Assert.Equal(100, color.GreenChannel![0]);
        Assert.Equal(100, color.BlueChannel![0]);
    }

    [Fact]
    public void ToColor_PreservesAllPixelValues()
    {
        var pixels = new byte[] { 0, 50, 100, 150, 200, 255 };
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 2, MaxValue = 255,
            Pixels = (byte[])pixels.Clone(),
        };
        var color = img.ToColor();
        for (int i = 0; i < pixels.Length; i++)
        {
            Assert.Equal(pixels[i], color.RedChannel![i]);
            Assert.Equal(pixels[i], color.GreenChannel![i]);
            Assert.Equal(pixels[i], color.BlueChannel![i]);
        }
    }

    [Fact]
    public void ToColor_ThenToGrayscale_RoundTrip()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 3, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 10, 50, 100, 150, 200, 250 },
        };
        var color = img.ToColor();
        var gray = color.ToGrayscale();
        Assert.Equal(NetpbmFormat.PGM_P5, gray.Format);
        for (int i = 0; i < img.Pixels.Length; i++)
            Assert.Equal(img.Pixels[i], gray.Pixels[i]);
    }

    [Fact]
    public void ToColor_ThrowsForPpm()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 0 },
            GreenChannel = new byte[] { 0 },
            BlueChannel = new byte[] { 0 },
        };
        Assert.Throws<InvalidOperationException>(() => img.ToColor());
    }

    [Fact]
    public void ToColor_ThrowsForPbm()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 1, Height = 1, MaxValue = 1,
            Pixels = new byte[] { 0 },
        };
        Assert.Throws<InvalidOperationException>(() => img.ToColor());
    }

    [Fact]
    public void ToColor_SaveToFile_Roundtrip()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 2, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 42, 128, 200, 0 },
        };
        var color = img.ToColor();
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            color.SaveToFile(tmp);
            Assert.True(File.Exists(tmp));
            var bytes = File.ReadAllBytes(tmp);
            // P6 binary format starts with "P6"
            Assert.Equal((byte)'P', bytes[0]);
            Assert.Equal((byte)'6', bytes[1]);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ToColor_PreservesMaxValue()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 1, Height = 1, MaxValue = 100,
            Pixels = new byte[] { 50 },
        };
        var color = img.ToColor();
        Assert.Equal(100, color.MaxValue);
    }

    [Fact]
    public void ToColor_GetPixelColor_MatchesGrayValue()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 2, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 77, 200 },
        };
        var color = img.ToColor();
        var (r, g, b) = color.GetPixelColor(0, 0);
        Assert.Equal(77, r);
        Assert.Equal(77, g);
        Assert.Equal(77, b);
        var (r2, g2, b2) = color.GetPixelColor(0, 1);
        Assert.Equal(200, r2);
    }

    [Fact]
    public void ToColor_BinaryPgm_ProducesBinaryPpm()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 128 },
        };
        var color = img.ToColor();
        Assert.Equal(NetpbmFormat.PPM_P6, color.Format);
    }
}
