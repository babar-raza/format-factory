// R104 Wave 3: Netpbm .NET dogfood — brightness + merge pipeline
// Ledger: R104-DOGFOOD-NETPBM-PIPELINE-001

using System;
using System.IO;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR104DogfoodPipelineTests
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
    public void Dogfood_BrightnessThenSave()
    {
        var img = MakePgm(4, 4, new byte[] {
            50, 100, 150, 200,
            25, 75, 125, 175,
            10, 60, 110, 160,
            5, 55, 105, 155
        });
        var bright = img.AdjustBrightness(30);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            bright.SaveToFile(tmp);
            Assert.True(File.Exists(tmp));
            Assert.True(new FileInfo(tmp).Length > 0);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_MergeThenSave()
    {
        var left = MakePgm(2, 2, new byte[] { 10, 20, 30, 40 });
        var right = MakePgm(2, 2, new byte[] { 50, 60, 70, 80 });
        var merged = left.MergeHorizontal(right);
        Assert.Equal(4, merged.Width);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            merged.SaveToFile(tmp);
            Assert.True(File.Exists(tmp));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_BrightnessThenMerge()
    {
        var a = MakePgm(2, 2, new byte[] { 100, 100, 100, 100 });
        var b = MakePgm(2, 2, new byte[] { 50, 50, 50, 50 });
        var brightA = a.AdjustBrightness(50);
        var brightB = b.AdjustBrightness(-20);
        var merged = brightA.MergeHorizontal(brightB);
        Assert.Equal(4, merged.Width);
        Assert.Equal(2, merged.Height);
        // brightA pixels: 150,150,150,150; brightB: 30,30,30,30
        Assert.Equal(150, merged.Pixels[0]);
        Assert.Equal(150, merged.Pixels[1]);
        Assert.Equal(30, merged.Pixels[2]);
        Assert.Equal(30, merged.Pixels[3]);
    }

    [Fact]
    public void Dogfood_RotateThenMerge()
    {
        var img = MakePgm(2, 2, new byte[] { 1, 2, 3, 4 });
        var rotated = img.Rotate180();
        var merged = img.MergeHorizontal(rotated);
        Assert.Equal(4, merged.Width);
        // Original: 1,2,3,4 → Rotated180: 4,3,2,1
        // Row0: 1,2,4,3  Row1: 3,4,2,1
        Assert.Equal(new byte[] { 1, 2, 4, 3, 3, 4, 2, 1 }, merged.Pixels);
    }

    [Fact]
    public void Dogfood_PPM_BrightnessPipeline()
    {
        var img = MakePpm(2, 1,
            new byte[] { 100, 200 },
            new byte[] { 50, 150 },
            new byte[] { 25, 75 });
        var bright = img.AdjustBrightness(50);
        Assert.Equal(150, bright.RedChannel![0]);
        Assert.Equal(250, bright.RedChannel![1]);
        Assert.Equal(100, bright.GreenChannel![0]);
        Assert.Equal(200, bright.GreenChannel![1]);
    }

    [Fact]
    public void Dogfood_FullPipeline_CreateMergeBrightenSave()
    {
        var left = MakePgm(3, 2, new byte[] { 10, 20, 30, 40, 50, 60 });
        var right = MakePgm(3, 2, new byte[] { 70, 80, 90, 100, 110, 120 });
        var merged = left.MergeHorizontal(right);
        var final_ = merged.AdjustBrightness(10);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            final_.SaveToFile(tmp);
            Assert.True(File.Exists(tmp));
            Assert.Equal(6, final_.Width);
            Assert.Equal(2, final_.Height);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
