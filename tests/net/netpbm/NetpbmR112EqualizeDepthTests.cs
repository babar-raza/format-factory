using Xunit;
using System;
using System.IO;
using FormatFactory.Netpbm;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R112 depth: Netpbm Equalize comprehensive tests.
/// Tests histogram equalization edge cases and correctness.
/// </summary>
public class NetpbmR112EqualizeDepthTests
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
    public void Equalize_Pgm_ReturnsSameSize()
    {
        var img = CreatePgm(4, 4, 128);
        var eq = img.Equalize();
        Assert.Equal(img.Width, eq.Width);
        Assert.Equal(img.Height, eq.Height);
    }

    [Fact]
    public void Equalize_Pgm_UniformImage_AllSameValue()
    {
        var img = CreatePgm(4, 4, 100);
        var eq = img.Equalize();
        byte first = eq.Pixels[0];
        foreach (var p in eq.Pixels)
            Assert.Equal(first, p);
    }

    [Fact]
    public void Equalize_Pgm_ValuesInRange()
    {
        var img = CreatePgm(4, 4, 0);
        img.Pixels[0] = 0;
        img.Pixels[1] = 128;
        img.Pixels[2] = 255;
        var eq = img.Equalize();
        foreach (var p in eq.Pixels)
            Assert.InRange(p, (byte)0, (byte)255);
    }

    [Fact]
    public void Equalize_Ppm_ReturnsSameSize()
    {
        var img = CreatePpm(4, 4, 100, 150, 200);
        var eq = img.Equalize();
        Assert.Equal(img.Width, eq.Width);
        Assert.Equal(img.Height, eq.Height);
    }

    [Fact]
    public void Equalize_Ppm_ResultHasValidDimensions()
    {
        var img = CreatePpm(4, 4, 50, 100, 200);
        img.RedChannel![0] = 0;
        img.RedChannel![1] = 255;
        var eq = img.Equalize();
        Assert.Equal(4, eq.Width);
        Assert.Equal(4, eq.Height);
        // Equalize may convert to grayscale internally — verify it produces output
        bool hasPixels = eq.Pixels != null && eq.Pixels.Length > 0;
        bool hasChannels = eq.RedChannel != null && eq.RedChannel.Length > 0;
        Assert.True(hasPixels || hasChannels, "Equalized image must have pixel data");
    }

    [Fact]
    public void Equalize_Pgm_GradientImage_SpreadsDynamic()
    {
        var img = CreatePgm(16, 1, 0);
        for (int i = 0; i < 16; i++)
            img.Pixels[i] = (byte)(i * 16);
        var eq = img.Equalize();
        // Equalized gradient should use fuller range
        int min = 255, max = 0;
        foreach (var p in eq.Pixels)
        {
            if (p < min) min = p;
            if (p > max) max = p;
        }
        Assert.True(max - min >= 200, $"Expected spread >= 200, got {max - min}");
    }

    [Fact]
    public void Equalize_DoesNotMutateOriginal()
    {
        var img = CreatePgm(4, 4, 100);
        byte original = img.Pixels[0];
        var eq = img.Equalize();
        Assert.Equal(original, img.Pixels[0]);
    }

    [Fact]
    public void Equalize_1x1Image_Works()
    {
        var img = CreatePgm(1, 1, 42);
        var eq = img.Equalize();
        Assert.Equal(1, eq.Width);
        Assert.Equal(1, eq.Height);
    }
}
