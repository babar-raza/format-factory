// R96 Train N: Netpbm .NET GetBrightness Tests
// Governed skill: /add-dotnet-api
// Ledger: R96-GOVERNED-DOTNET-NETPBM-GETBRIGHTNESS-001
// Sprint: FORMAT-FACTORY-R96-AUTONOMOUS-CONTINUATION-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

using System;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR96GetBrightnessTests
{
    [Fact]
    public void GetBrightness_WhitePgm_ReturnsOne()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 2, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 255, 255, 255, 255 },
        };
        Assert.Equal(1.0, img.GetBrightness(), 2);
    }

    [Fact]
    public void GetBrightness_BlackPgm_ReturnsZero()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 2, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 0, 0, 0, 0 },
        };
        Assert.Equal(0.0, img.GetBrightness(), 2);
    }

    [Fact]
    public void GetBrightness_MidGray_ReturnsHalf()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 128 },
        };
        var brightness = img.GetBrightness();
        Assert.InRange(brightness, 0.4, 0.6);
    }

    [Fact]
    public void GetBrightness_PpmWhite_ReturnsOne()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 255 },
            GreenChannel = new byte[] { 255 },
            BlueChannel = new byte[] { 255 },
        };
        Assert.Equal(1.0, img.GetBrightness(), 2);
    }

    [Fact]
    public void GetBrightness_PpmBlack_ReturnsZero()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 0 },
            GreenChannel = new byte[] { 0 },
            BlueChannel = new byte[] { 0 },
        };
        Assert.Equal(0.0, img.GetBrightness(), 2);
    }

    [Fact]
    public void GetBrightness_InRange()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 3, Height = 3, MaxValue = 255,
            Pixels = new byte[] { 10, 50, 100, 150, 200, 250, 30, 60, 90 },
        };
        var brightness = img.GetBrightness();
        Assert.InRange(brightness, 0.0, 1.0);
    }

    [Fact]
    public void GetBrightness_PbmBlack_ReturnsOne()
    {
        // PBM: 1 = black, MaxValue = 1
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 2, Height = 2, MaxValue = 1,
            Pixels = new byte[] { 1, 1, 1, 1 },
        };
        Assert.Equal(1.0, img.GetBrightness(), 2);
    }

    [Fact]
    public void GetBrightness_PbmWhite_ReturnsZero()
    {
        // PBM: 0 = white
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 2, Height = 2, MaxValue = 1,
            Pixels = new byte[] { 0, 0, 0, 0 },
        };
        Assert.Equal(0.0, img.GetBrightness(), 2);
    }
}
