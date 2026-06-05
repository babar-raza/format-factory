// R110 Wave 4: Netpbm Solarize tests
// Ledger: R110-GOVERNED-DOTNET-NETPBM-SOLARIZE-001

using System;
using System.IO;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR110SolarizeTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/netpbm"));

    [Fact]
    public void Solarize_PGM_InvertsAboveThreshold()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3,
            Height = 1,
            MaxValue = 255,
            Pixels = new byte[] { 50, 128, 200 }
        };
        var result = img.Solarize(100);
        Assert.Equal(50, result.Pixels[0]);    // below threshold → unchanged
        Assert.Equal(255 - 128, result.Pixels[1]); // above threshold → inverted
        Assert.Equal(255 - 200, result.Pixels[2]); // above threshold → inverted
    }

    [Fact]
    public void Solarize_PGM_ThresholdZero_InvertsAll()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 2,
            Height = 1,
            MaxValue = 255,
            Pixels = new byte[] { 100, 200 }
        };
        var result = img.Solarize(0);
        Assert.Equal(155, result.Pixels[0]);
        Assert.Equal(55, result.Pixels[1]);
    }

    [Fact]
    public void Solarize_PGM_ThresholdMax_InvertsNothing()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 2,
            Height = 1,
            MaxValue = 255,
            Pixels = new byte[] { 100, 200 }
        };
        var result = img.Solarize(255);
        Assert.Equal(100, result.Pixels[0]);
        Assert.Equal(200, result.Pixels[1]);
    }

    [Fact]
    public void Solarize_PPM_InvertsChannelsAboveThreshold()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1,
            Height = 1,
            MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[] { 200 },
            GreenChannel = new byte[] { 50 },
            BlueChannel = new byte[] { 150 }
        };
        var result = img.Solarize(100);
        Assert.Equal(55, result.RedChannel![0]);   // 200 > 100 → 255 - 200
        Assert.Equal(50, result.GreenChannel![0]);  // 50 <= 100 → unchanged
        Assert.Equal(105, result.BlueChannel![0]);  // 150 > 100 → 255 - 150
    }

    [Fact]
    public void Solarize_PBM_ReturnsClone()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 2,
            Height = 1,
            MaxValue = 1,
            Pixels = new byte[] { 0, 1 }
        };
        var result = img.Solarize(0);
        Assert.Equal(img.Pixels[0], result.Pixels[0]);
        Assert.Equal(img.Pixels[1], result.Pixels[1]);
    }

    [Fact]
    public void Solarize_DoesNotMutateOriginal()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 2,
            Height = 1,
            MaxValue = 255,
            Pixels = new byte[] { 200, 100 }
        };
        var result = img.Solarize(50);
        Assert.Equal(200, img.Pixels[0]); // original unchanged
        Assert.Equal(100, img.Pixels[1]);
    }

    [Fact]
    public void Solarize_FormatPreserved()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 1,
            Height = 1,
            MaxValue = 255,
            Pixels = new byte[] { 128 }
        };
        var result = img.Solarize(50);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    [Fact]
    public void Solarize_DimensionsPreserved()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 4,
            Height = 3,
            MaxValue = 255,
            Pixels = new byte[12]
        };
        var result = img.Solarize(128);
        Assert.Equal(4, result.Width);
        Assert.Equal(3, result.Height);
        Assert.Equal(12, result.Pixels.Length);
    }
}
