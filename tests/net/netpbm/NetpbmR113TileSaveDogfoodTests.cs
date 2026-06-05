using Xunit;
using System;
using System.IO;
using FormatFactory.Netpbm;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR113TileSaveDogfoodTests
{
    private NetpbmImage CreateTestPgm(int w, int h)
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = w,
            Height = h,
            MaxValue = 255,
            Pixels = new byte[w * h]
        };
        for (int i = 0; i < img.Pixels.Length; i++)
            img.Pixels[i] = (byte)(i % 256);
        return img;
    }

    [Fact]
    public void Tile_Save_Reload_Dogfood()
    {
        var img = CreateTestPgm(4, 4);
        var tiled = img.Tile(3, 2);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            tiled.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(12, reloaded.Width);
            Assert.Equal(8, reloaded.Height);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Crop_Save_Reload_Dogfood()
    {
        var img = CreateTestPgm(10, 10);
        var cropped = img.Crop(1, 1, 5, 5);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            cropped.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(5, reloaded.Width);
            Assert.Equal(5, reloaded.Height);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Invert_Save_Reload_Dogfood()
    {
        var img = CreateTestPgm(4, 4);
        img.Invert();
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            img.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(4, reloaded.Width);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Threshold_Save_Dogfood()
    {
        var img = CreateTestPgm(4, 4);
        var thresholded = img.Threshold(128);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            thresholded.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(4, reloaded.Width);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Clone_Modify_SaveBoth_Dogfood()
    {
        var img = CreateTestPgm(4, 4);
        var clone = img.Clone();
        clone.Invert();
        var tmp1 = Path.GetTempFileName() + ".pgm";
        var tmp2 = Path.GetTempFileName() + ".pgm";
        try
        {
            img.SaveToFile(tmp1);
            clone.SaveToFile(tmp2);
            var r1 = NetpbmParser.Parse(tmp1);
            var r2 = NetpbmParser.Parse(tmp2);
            Assert.Equal(r1.Width, r2.Width);
            Assert.NotEqual(r1.Pixels[0], r2.Pixels[0]);
        }
        finally
        {
            if (File.Exists(tmp1)) File.Delete(tmp1);
            if (File.Exists(tmp2)) File.Delete(tmp2);
        }
    }

    [Fact]
    public void Posterize_Save_Dogfood()
    {
        var img = CreateTestPgm(4, 4);
        var posterized = img.Posterize(4);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            posterized.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(4, reloaded.Width);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
