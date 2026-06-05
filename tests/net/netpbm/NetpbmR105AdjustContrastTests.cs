// R105 Wave 2: Netpbm .NET AdjustContrast tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R105-GOVERNED-DOTNET-NETPBM-ADJUSTCONTRAST-001

using System;
using System.IO;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR105AdjustContrastTests
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
    public void AdjustContrast_Factor1_NoChange()
    {
        var pixels = new byte[] { 50, 100, 150, 200 };
        var img = MakePgm(2, 2, (byte[])pixels.Clone());
        var result = img.AdjustContrast(1.0);
        Assert.Equal(pixels, result.Pixels);
    }

    [Fact]
    public void AdjustContrast_Factor0_AllMidpoint()
    {
        var img = MakePgm(2, 2, new byte[] { 0, 50, 200, 255 });
        var result = img.AdjustContrast(0.0);
        // All values should converge to midpoint (127 or 128)
        foreach (var px in result.Pixels)
            Assert.InRange(px, 127, 128);
    }

    [Fact]
    public void AdjustContrast_HighFactor_ExpandsRange()
    {
        var img = MakePgm(2, 1, new byte[] { 100, 200 });
        var result = img.AdjustContrast(2.0);
        // 100 is below midpoint, should decrease; 200 is above, should increase
        Assert.True(result.Pixels[0] < 100);
        Assert.True(result.Pixels[1] > 200);
    }

    [Fact]
    public void AdjustContrast_ClampsToRange()
    {
        var img = MakePgm(2, 1, new byte[] { 0, 255 });
        var result = img.AdjustContrast(3.0);
        Assert.Equal(0, result.Pixels[0]);
        Assert.Equal(255, result.Pixels[1]);
    }

    [Fact]
    public void AdjustContrast_PPM_AppliesAllChannels()
    {
        var img = MakePpm(1, 1,
            new byte[] { 100 }, new byte[] { 200 }, new byte[] { 50 });
        var result = img.AdjustContrast(2.0);
        Assert.True(result.RedChannel![0] < 100);
        Assert.True(result.GreenChannel![0] > 200);
        Assert.True(result.BlueChannel![0] < 50);
    }

    [Fact]
    public void AdjustContrast_PBM_NoOp()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P4, Width = 2, Height = 2, MaxValue = 1,
            Pixels = new byte[] { 0, 1, 1, 0 }
        };
        var result = img.AdjustContrast(2.0);
        Assert.Equal(new byte[] { 0, 1, 1, 0 }, result.Pixels);
    }

    [Fact]
    public void AdjustContrast_NegativeFactor_Throws()
    {
        var img = MakePgm(1, 1, new byte[] { 128 });
        Assert.Throws<ArgumentOutOfRangeException>(() => img.AdjustContrast(-1.0));
    }

    [Fact]
    public void AdjustContrast_PreservesFormat()
    {
        var img = MakePgm(2, 2, new byte[] { 1, 2, 3, 4 });
        var result = img.AdjustContrast(1.5);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(255, result.MaxValue);
    }

    [Fact]
    public void AdjustContrast_DoesNotMutateOriginal()
    {
        var pixels = new byte[] { 100, 200 };
        var img = MakePgm(2, 1, (byte[])pixels.Clone());
        img.AdjustContrast(2.0);
        Assert.Equal(100, img.Pixels[0]);
        Assert.Equal(200, img.Pixels[1]);
    }

    [Fact]
    public void AdjustContrast_SaveToFile()
    {
        var img = MakePgm(2, 2, new byte[] { 50, 100, 150, 200 });
        var result = img.AdjustContrast(1.5);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            result.SaveToFile(tmp);
            Assert.True(File.Exists(tmp));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
