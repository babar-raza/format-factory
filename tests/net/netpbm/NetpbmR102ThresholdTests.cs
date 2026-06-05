// R102 Train C: Netpbm .NET Threshold tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R102-GOVERNED-DOTNET-NETPBM-THRESHOLD-001

using System;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR102ThresholdTests
{
    [Fact]
    public void Threshold_PGM_ReturnsPBM()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 1,
            MaxValue = 255,
            Pixels = new byte[] { 50, 128, 200 }
        };
        var result = img.Threshold(128);
        Assert.Equal(NetpbmFormat.PBM_P1, result.Format);
        Assert.Equal(1, result.MaxValue);
    }

    [Fact]
    public void Threshold_CorrectBinarization()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 4, Height = 1,
            MaxValue = 255,
            Pixels = new byte[] { 0, 100, 200, 255 }
        };
        var result = img.Threshold(150);
        Assert.Equal((byte)0, result.Pixels[0]); // 0 < 150
        Assert.Equal((byte)0, result.Pixels[1]); // 100 < 150
        Assert.Equal((byte)1, result.Pixels[2]); // 200 >= 150
        Assert.Equal((byte)1, result.Pixels[3]); // 255 >= 150
    }

    [Fact]
    public void Threshold_PPM_UsesLuminance()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 2, Height = 1,
            MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[] { 255, 0 },
            GreenChannel = new byte[] { 255, 0 },
            BlueChannel = new byte[] { 255, 0 },
        };
        var result = img.Threshold(128);
        Assert.Equal((byte)1, result.Pixels[0]); // white >= 128
        Assert.Equal((byte)0, result.Pixels[1]); // black < 128
    }

    [Fact]
    public void Threshold_PBM_Throws()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 2, Height = 1,
            MaxValue = 1,
            Pixels = new byte[] { 0, 1 }
        };
        Assert.Throws<InvalidOperationException>(() => img.Threshold(1));
    }

    [Fact]
    public void Threshold_NegativeValue_Throws()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 1, Height = 1,
            MaxValue = 255,
            Pixels = new byte[] { 128 }
        };
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Threshold(-1));
    }

    [Fact]
    public void Threshold_AboveMax_Throws()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 1, Height = 1,
            MaxValue = 255,
            Pixels = new byte[] { 128 }
        };
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Threshold(256));
    }

    [Fact]
    public void Threshold_Zero_AllBlack()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 1,
            MaxValue = 255,
            Pixels = new byte[] { 0, 100, 255 }
        };
        var result = img.Threshold(0);
        // All pixels >= 0, so all become 1 (black)
        Assert.Equal((byte)1, result.Pixels[0]);
        Assert.Equal((byte)1, result.Pixels[1]);
        Assert.Equal((byte)1, result.Pixels[2]);
    }

    [Fact]
    public void Threshold_PreservesDimensions()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 5, Height = 3,
            MaxValue = 255,
            Pixels = new byte[15]
        };
        var result = img.Threshold(128);
        Assert.Equal(5, result.Width);
        Assert.Equal(3, result.Height);
        Assert.Equal(15, result.Pixels.Length);
    }
}
