using Xunit;
using System;
using System.IO;
using FormatFactory.Netpbm;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR113CropSaveDepthTests
{
    private NetpbmImage CreateTestImage(int w, int h)
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
    public void Crop_SaveReload_PreservesDimensions()
    {
        var img = CreateTestImage(10, 10);
        var cropped = img.Crop(2, 2, 5, 5);
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
    public void Crop_ThenTile_SaveRoundtrip()
    {
        var img = CreateTestImage(8, 8);
        var cropped = img.Crop(0, 0, 4, 4);
        var tiled = cropped.Tile(2, 2);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            tiled.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(8, reloaded.Width);
            Assert.Equal(8, reloaded.Height);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void FlipHorizontal_SaveRoundtrip()
    {
        var img = CreateTestImage(4, 4);
        img.FlipHorizontal();
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            img.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(4, reloaded.Width);
            Assert.Equal(4, reloaded.Height);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Rotate90_SaveRoundtrip()
    {
        var img = CreateTestImage(3, 5);
        var rotated = img.Rotate90Cw();
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            rotated.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(5, reloaded.Width);
            Assert.Equal(3, reloaded.Height);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void AdjustBrightness_SaveRoundtrip()
    {
        var img = CreateTestImage(4, 4);
        var bright = img.AdjustBrightness(50);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            bright.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(4, reloaded.Width);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Invert_SaveRoundtrip()
    {
        var img = CreateTestImage(4, 4);
        byte original = img.Pixels[0];
        img.Invert();
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            img.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal((byte)(255 - original), reloaded.Pixels[0]);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
