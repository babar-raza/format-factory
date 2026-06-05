// R110 Wave 4: Netpbm Sepia tests
// Ledger: R110-GOVERNED-DOTNET-NETPBM-SEPIA-001

using System;
using System.IO;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR110SepiaTests
{
    [Fact]
    public void Sepia_PPM_AppliesSepiaTransform()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1,
            Height = 1,
            MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[] { 255 },
            GreenChannel = new byte[] { 0 },
            BlueChannel = new byte[] { 0 }
        };
        var result = img.Sepia();
        // Pure red: lum = 0.299*255 + 0.587*0 + 0.114*0 = 76.245
        // R = round(76.245 * 1.0) = 76
        // G = round(76.245 * 0.8) = 61
        // B = round(76.245 * 0.6) = 46
        Assert.Equal(76, result.RedChannel![0]);
        Assert.Equal(61, result.GreenChannel![0]);
        Assert.Equal(46, result.BlueChannel![0]);
    }

    [Fact]
    public void Sepia_PPM_WhitePixel()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P6,
            Width = 1,
            Height = 1,
            MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[] { 255 },
            GreenChannel = new byte[] { 255 },
            BlueChannel = new byte[] { 255 }
        };
        var result = img.Sepia();
        // lum = 0.299*255 + 0.587*255 + 0.114*255 = 255
        Assert.Equal(255, result.RedChannel![0]);   // 255 * 1.0 clamped to 255
        Assert.Equal(204, result.GreenChannel![0]);  // 255 * 0.8
        Assert.Equal(153, result.BlueChannel![0]);   // 255 * 0.6
    }

    [Fact]
    public void Sepia_PPM_BlackPixel()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1,
            Height = 1,
            MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[] { 0 },
            GreenChannel = new byte[] { 0 },
            BlueChannel = new byte[] { 0 }
        };
        var result = img.Sepia();
        Assert.Equal(0, result.RedChannel![0]);
        Assert.Equal(0, result.GreenChannel![0]);
        Assert.Equal(0, result.BlueChannel![0]);
    }

    [Fact]
    public void Sepia_PBM_ReturnsClone()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 2,
            Height = 1,
            MaxValue = 1,
            Pixels = new byte[] { 0, 1 }
        };
        var result = img.Sepia();
        Assert.Equal(0, result.Pixels[0]);
        Assert.Equal(1, result.Pixels[1]);
    }

    [Fact]
    public void Sepia_PGM_ReturnsClone()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 2,
            Height = 1,
            MaxValue = 255,
            Pixels = new byte[] { 100, 200 }
        };
        var result = img.Sepia();
        Assert.Equal(100, result.Pixels[0]);
        Assert.Equal(200, result.Pixels[1]);
    }

    [Fact]
    public void Sepia_DoesNotMutateOriginal()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1,
            Height = 1,
            MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[] { 100 },
            GreenChannel = new byte[] { 150 },
            BlueChannel = new byte[] { 200 }
        };
        var result = img.Sepia();
        Assert.Equal(100, img.RedChannel![0]);
        Assert.Equal(150, img.GreenChannel![0]);
        Assert.Equal(200, img.BlueChannel![0]);
    }

    [Fact]
    public void Sepia_FormatPreserved()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P6,
            Width = 1,
            Height = 1,
            MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[] { 128 },
            GreenChannel = new byte[] { 128 },
            BlueChannel = new byte[] { 128 }
        };
        var result = img.Sepia();
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void Sepia_DimensionsPreserved()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 3,
            Height = 2,
            MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[6],
            GreenChannel = new byte[6],
            BlueChannel = new byte[6]
        };
        var result = img.Sepia();
        Assert.Equal(3, result.Width);
        Assert.Equal(2, result.Height);
        Assert.Equal(6, result.RedChannel!.Length);
    }

    [Fact]
    public void Sepia_GreenChannel_LessThanRed()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1,
            Height = 1,
            MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[] { 128 },
            GreenChannel = new byte[] { 128 },
            BlueChannel = new byte[] { 128 }
        };
        var result = img.Sepia();
        // Sepia: R >= G >= B always
        Assert.True(result.RedChannel![0] >= result.GreenChannel![0]);
        Assert.True(result.GreenChannel[0] >= result.BlueChannel![0]);
    }

    [Fact]
    public void Sepia_MultiPixel_AllTransformed()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 2,
            Height = 1,
            MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[] { 255, 0 },
            GreenChannel = new byte[] { 0, 255 },
            BlueChannel = new byte[] { 0, 0 }
        };
        var result = img.Sepia();
        // Pixel 0: pure red → sepia of luminance 76
        // Pixel 1: pure green → sepia of luminance 150
        Assert.True(result.RedChannel![0] > 0);
        Assert.True(result.RedChannel[1] > 0);
    }
}
