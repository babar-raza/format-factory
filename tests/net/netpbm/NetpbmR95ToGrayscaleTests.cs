// R95 Train N: Netpbm .NET ToGrayscale Tests
// Governed skill: /add-dotnet-api
// Ledger: R95-GOVERNED-DOTNET-NETPBM-TOGRAYSCALE-001
// Sprint: FORMAT-FACTORY-R95-PARALLEL-SPRINT-INTELLIGENCE-CONTEXT-PACK-ACCELERATION-POC-MEGA-TRAIN-001

using System;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR95ToGrayscaleTests
{
    private static NetpbmImage CreatePpmImage(int width, int height, byte r, byte g, byte b)
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = width,
            Height = height,
            MaxValue = 255,
            RedChannel = new byte[width * height],
            GreenChannel = new byte[width * height],
            BlueChannel = new byte[width * height],
        };
        for (int i = 0; i < width * height; i++)
        {
            img.RedChannel[i] = r;
            img.GreenChannel[i] = g;
            img.BlueChannel[i] = b;
        }
        return img;
    }

    [Fact]
    public void ToGrayscale_ReturnsPgmFormat()
    {
        var ppm = CreatePpmImage(2, 2, 100, 150, 200);
        var pgm = ppm.ToGrayscale();
        Assert.Equal(NetpbmFormat.PGM_P5, pgm.Format);
    }

    [Fact]
    public void ToGrayscale_PreservesDimensions()
    {
        var ppm = CreatePpmImage(4, 3, 50, 50, 50);
        var pgm = ppm.ToGrayscale();
        Assert.Equal(4, pgm.Width);
        Assert.Equal(3, pgm.Height);
    }

    [Fact]
    public void ToGrayscale_WhiteProducesMax()
    {
        var ppm = CreatePpmImage(1, 1, 255, 255, 255);
        var pgm = ppm.ToGrayscale();
        Assert.True(pgm.Pixels[0] >= 254, $"White should produce ~255, got {pgm.Pixels[0]}");
    }

    [Fact]
    public void ToGrayscale_BlackProducesZero()
    {
        var ppm = CreatePpmImage(1, 1, 0, 0, 0);
        var pgm = ppm.ToGrayscale();
        Assert.Equal(0, pgm.Pixels[0]);
    }

    [Fact]
    public void ToGrayscale_GreenHasHigherLuminanceThanRed()
    {
        var red = CreatePpmImage(1, 1, 255, 0, 0).ToGrayscale().Pixels[0];
        var green = CreatePpmImage(1, 1, 0, 255, 0).ToGrayscale().Pixels[0];
        Assert.True(green > red, $"Green ({green}) should have higher luminance than red ({red})");
    }

    [Fact]
    public void ToGrayscale_NonPpmThrows()
    {
        var pgm = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 2, Height = 2, MaxValue = 255,
            Pixels = new byte[4],
        };
        Assert.Throws<InvalidOperationException>(() => pgm.ToGrayscale());
    }

    [Fact]
    public void ToGrayscale_PreservesMaxValue()
    {
        var ppm = CreatePpmImage(2, 2, 100, 100, 100);
        var pgm = ppm.ToGrayscale();
        Assert.Equal(255, pgm.MaxValue);
    }

    [Fact]
    public void ToGrayscale_AllPixelsInRange()
    {
        var ppm = CreatePpmImage(3, 3, 128, 64, 200);
        var pgm = ppm.ToGrayscale();
        foreach (var pixel in pgm.Pixels)
        {
            Assert.InRange(pixel, (byte)0, (byte)255);
        }
    }
}
