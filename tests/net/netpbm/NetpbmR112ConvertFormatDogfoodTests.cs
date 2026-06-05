using Xunit;
using System;
using System.IO;
using FormatFactory.Netpbm;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R112 Dogfood: Netpbm ConvertFormat + SaveToFile roundtrip.
/// Uses FF library for conversion and save — no external dependencies.
/// </summary>
public class NetpbmR112ConvertFormatDogfoodTests
{
    private static NetpbmImage CreatePgm(int w, int h, byte fillValue)
    {
        var img = new NetpbmImage
        {
            Width = w, Height = h,
            Format = NetpbmFormat.PGM_P2,
            MaxValue = 255,
            Pixels = new byte[w * h]
        };
        Array.Fill(img.Pixels, fillValue);
        return img;
    }

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
    public void PgmToPpm_ConvertSaveReload()
    {
        var pgm = CreatePgm(4, 4, 128);
        var ppm = pgm.ToColor();
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            ppm.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(4, reloaded.Width);
            Assert.NotNull(reloaded.RedChannel);
            Assert.Equal(128, reloaded.RedChannel![0]);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void PpmToGrayscale_SaveReload()
    {
        var ppm = CreatePpm(4, 4, 100, 150, 200);
        var gray = ppm.ToGrayscale();
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            gray.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(4, reloaded.Width);
            Assert.NotNull(reloaded.Pixels);
            Assert.True(reloaded.Pixels.Length > 0);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void GrayscaleToColor_SaveReload()
    {
        var pgm = CreatePgm(4, 4, 100);
        var ppm = pgm.ToColor();
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            ppm.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.NotNull(reloaded.RedChannel);
            Assert.Equal(100, reloaded.RedChannel![0]);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Sharpen_ThenSave_ThenReload()
    {
        var ppm = CreatePpm(8, 8, 100, 150, 200);
        var sharpened = ppm.Sharpen();
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            sharpened.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(8, reloaded.Width);
            Assert.Equal(8, reloaded.Height);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void BlurBox_ThenSave_ThenReload()
    {
        var ppm = CreatePpm(8, 8, 100, 150, 200);
        var blurred = ppm.BlurBox(1);
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            blurred.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(blurred.RedChannel![0], reloaded.RedChannel![0]);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Pipeline_Equalize_Sharpen_Save()
    {
        var ppm = CreatePpm(8, 8, 50, 100, 200);
        ppm.RedChannel![0] = 0;
        ppm.RedChannel![1] = 255;
        var processed = ppm.Equalize().Sharpen();
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            processed.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(8, reloaded.Width);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Flip_ThenConvert_ThenSave()
    {
        var pgm = CreatePgm(4, 4, 100);
        pgm.Pixels[0] = 200;
        pgm.FlipHorizontal();
        var ppm = pgm.ToColor();
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            ppm.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(4, reloaded.Width);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Crop_ThenSave_Roundtrip()
    {
        var ppm = CreatePpm(8, 8, 100, 150, 200);
        var cropped = ppm.Crop(2, 2, 4, 4);
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            cropped.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(4, reloaded.Width);
            Assert.Equal(4, reloaded.Height);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
