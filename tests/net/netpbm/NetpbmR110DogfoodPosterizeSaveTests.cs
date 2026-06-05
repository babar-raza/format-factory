// R110 Wave 6: Netpbm Posterize→Save Dogfood Pipeline Tests
// Dogfood: load→posterize→save pipeline

using System;
using System.IO;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR110DogfoodPosterizeSaveTests
{
    [Fact]
    public void Dogfood_PosterizeThenSave_PGM()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 4,
            Height = 4,
            MaxValue = 255,
            Pixels = new byte[16]
        };
        for (int i = 0; i < 16; i++)
            img.Pixels[i] = (byte)(i * 16);

        var posterized = img.Posterize(4);
        var tmpPath = Path.GetTempFileName() + ".pgm";
        try
        {
            posterized.SaveToFile(tmpPath);
            Assert.True(File.Exists(tmpPath));
            Assert.True(new FileInfo(tmpPath).Length > 0);
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }

    [Fact]
    public void Dogfood_SolarizeThenSave_PGM()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 3,
            Height = 3,
            MaxValue = 255,
            Pixels = new byte[] { 50, 100, 150, 200, 250, 30, 60, 90, 120 }
        };
        var solarized = img.Solarize(128);
        var tmpPath = Path.GetTempFileName() + ".pgm";
        try
        {
            solarized.SaveToFile(tmpPath);
            Assert.True(File.Exists(tmpPath));
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }

    [Fact]
    public void Dogfood_SepiaThenSave_PPM()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 2,
            Height = 2,
            MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[] { 255, 0, 128, 64 },
            GreenChannel = new byte[] { 0, 255, 128, 128 },
            BlueChannel = new byte[] { 0, 0, 128, 192 }
        };
        var sepia = img.Sepia();
        var tmpPath = Path.GetTempFileName() + ".ppm";
        try
        {
            sepia.SaveToFile(tmpPath);
            Assert.True(File.Exists(tmpPath));
            Assert.True(new FileInfo(tmpPath).Length > 0);
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }

    [Fact]
    public void Dogfood_FullPipeline_SolarizePosterizeSave()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 4,
            Height = 2,
            MaxValue = 255,
            Pixels = new byte[] { 10, 50, 100, 150, 200, 230, 250, 128 }
        };
        var step1 = img.Solarize(100);
        var step2 = step1.Posterize(4);
        var tmpPath = Path.GetTempFileName() + ".pgm";
        try
        {
            step2.SaveToFile(tmpPath);
            Assert.True(File.Exists(tmpPath));
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }
}
