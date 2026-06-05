// R94 Train O: Netpbm .NET Resize Tests
// Governed skill: /add-dotnet-api
// Ledger: R94-GOVERNED-DOTNET-NETPBM-RESIZE-001
// Sprint: FORMAT-FACTORY-R94-CONTEXT-PACK-SELF-CONTAINED-DECLARATION-REVIEW-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

using System;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR94ResizeTests
{
    private static NetpbmImage CreatePgm(int width, int height, byte fill = 128)
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = width,
            Height = height,
            MaxValue = 255,
            Pixels = new byte[width * height],
        };
        Array.Fill(img.Pixels, fill);
        return img;
    }

    private static NetpbmImage CreatePpm(int width, int height, byte r = 100, byte g = 150, byte b = 200)
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
        Array.Fill(img.RedChannel, r);
        Array.Fill(img.GreenChannel, g);
        Array.Fill(img.BlueChannel, b);
        return img;
    }

    [Fact]
    public void Resize_PGM_Upscale_CorrectDimensions()
    {
        var img = CreatePgm(4, 4);
        var resized = img.Resize(8, 8);
        Assert.Equal(8, resized.Width);
        Assert.Equal(8, resized.Height);
        Assert.Equal(NetpbmFormat.PGM_P2, resized.Format);
    }

    [Fact]
    public void Resize_PGM_Downscale_CorrectDimensions()
    {
        var img = CreatePgm(8, 8);
        var resized = img.Resize(4, 4);
        Assert.Equal(4, resized.Width);
        Assert.Equal(4, resized.Height);
    }

    [Fact]
    public void Resize_PGM_PreservesPixelValues()
    {
        var img = CreatePgm(4, 4, fill: 200);
        var resized = img.Resize(2, 2);
        // Nearest neighbor: all pixels should still be 200
        for (int i = 0; i < resized.Pixels.Length; i++)
            Assert.Equal(200, resized.Pixels[i]);
    }

    [Fact]
    public void Resize_PPM_Upscale_CorrectDimensions()
    {
        var img = CreatePpm(4, 4);
        var resized = img.Resize(8, 8);
        Assert.Equal(8, resized.Width);
        Assert.Equal(8, resized.Height);
        Assert.Equal(NetpbmFormat.PPM_P3, resized.Format);
    }

    [Fact]
    public void Resize_PPM_PreservesChannels()
    {
        var img = CreatePpm(4, 4, r: 10, g: 20, b: 30);
        var resized = img.Resize(2, 2);
        for (int i = 0; i < resized.RedChannel!.Length; i++)
        {
            Assert.Equal(10, resized.RedChannel[i]);
            Assert.Equal(20, resized.GreenChannel![i]);
            Assert.Equal(30, resized.BlueChannel![i]);
        }
    }

    [Fact]
    public void Resize_ZeroWidth_Throws()
    {
        var img = CreatePgm(4, 4);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Resize(0, 4));
    }

    [Fact]
    public void Resize_NegativeHeight_Throws()
    {
        var img = CreatePgm(4, 4);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Resize(4, -1));
    }

    [Fact]
    public void Resize_PreservesMaxValue()
    {
        var img = CreatePgm(4, 4);
        img.MaxValue = 127;
        var resized = img.Resize(8, 8);
        Assert.Equal(127, resized.MaxValue);
    }
}
