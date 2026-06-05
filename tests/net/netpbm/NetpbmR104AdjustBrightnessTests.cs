// R104 Wave 1: Netpbm .NET AdjustBrightness tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R104-GOVERNED-DOTNET-NETPBM-ADJUSTBRIGHTNESS-001

using System;
using System.IO;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR104AdjustBrightnessTests
{
    private static NetpbmImage MakePgm(int w, int h, byte[] pixels) => new()
    {
        Format = NetpbmFormat.PGM_P5,
        Width = w, Height = h, MaxValue = 255,
        Pixels = pixels,
    };

    private static NetpbmImage MakePpm(int w, int h, byte[] r, byte[] g, byte[] b) => new()
    {
        Format = NetpbmFormat.PPM_P6,
        Width = w, Height = h, MaxValue = 255,
        RedChannel = r, GreenChannel = g, BlueChannel = b,
        Pixels = Array.Empty<byte>(),
    };

    [Fact]
    public void AdjustBrightness_PGM_PositiveDelta()
    {
        var img = MakePgm(2, 2, new byte[] { 100, 150, 200, 250 });
        var result = img.AdjustBrightness(50);
        Assert.Equal(150, result.Pixels[0]);
        Assert.Equal(200, result.Pixels[1]);
        Assert.Equal(250, result.Pixels[2]);
        Assert.Equal(255, result.Pixels[3]); // clamped
    }

    [Fact]
    public void AdjustBrightness_PGM_NegativeDelta()
    {
        var img = MakePgm(2, 2, new byte[] { 100, 50, 20, 0 });
        var result = img.AdjustBrightness(-30);
        Assert.Equal(70, result.Pixels[0]);
        Assert.Equal(20, result.Pixels[1]);
        Assert.Equal(0, result.Pixels[2]); // clamped
        Assert.Equal(0, result.Pixels[3]); // clamped
    }

    [Fact]
    public void AdjustBrightness_ZeroDelta_NoChange()
    {
        var pixels = new byte[] { 10, 20, 30, 40 };
        var img = MakePgm(2, 2, pixels);
        var result = img.AdjustBrightness(0);
        Assert.Equal(pixels, result.Pixels);
    }

    [Fact]
    public void AdjustBrightness_PPM_AppliesAllChannels()
    {
        var img = MakePpm(1, 1,
            new byte[] { 100 }, new byte[] { 150 }, new byte[] { 200 });
        var result = img.AdjustBrightness(50);
        Assert.Equal(150, result.RedChannel![0]);
        Assert.Equal(200, result.GreenChannel![0]);
        Assert.Equal(250, result.BlueChannel![0]);
    }

    [Fact]
    public void AdjustBrightness_PPM_ClampsAllChannels()
    {
        var img = MakePpm(1, 1,
            new byte[] { 250 }, new byte[] { 10 }, new byte[] { 240 });
        var result = img.AdjustBrightness(20);
        Assert.Equal(255, result.RedChannel![0]);
        Assert.Equal(30, result.GreenChannel![0]);
        Assert.Equal(255, result.BlueChannel![0]);
    }

    [Fact]
    public void AdjustBrightness_PBM_NoOp()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P4, Width = 2, Height = 2, MaxValue = 1,
            Pixels = new byte[] { 0, 1, 1, 0 }
        };
        var result = img.AdjustBrightness(100);
        Assert.Equal(new byte[] { 0, 1, 1, 0 }, result.Pixels);
    }

    [Fact]
    public void AdjustBrightness_PreservesFormat()
    {
        var img = MakePgm(2, 2, new byte[] { 1, 2, 3, 4 });
        var result = img.AdjustBrightness(10);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(255, result.MaxValue);
    }

    [Fact]
    public void AdjustBrightness_DoesNotMutateOriginal()
    {
        var pixels = new byte[] { 100, 200 };
        var img = MakePgm(2, 1, (byte[])pixels.Clone());
        img.AdjustBrightness(50);
        Assert.Equal(100, img.Pixels[0]);
        Assert.Equal(200, img.Pixels[1]);
    }

    [Fact]
    public void AdjustBrightness_SaveToFile_Roundtrip()
    {
        var img = MakePgm(2, 2, new byte[] { 50, 100, 150, 200 });
        var result = img.AdjustBrightness(30);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            result.SaveToFile(tmp);
            Assert.True(File.Exists(tmp));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
