// R97 Train N: Netpbm .NET Clone Tests
// Governed skill: /add-dotnet-api
// Ledger: R97-GOVERNED-DOTNET-NETPBM-CLONE-001

using System;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR97CloneTests
{
    [Fact]
    public void Clone_PgmPreservesDimensions()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 3, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 10, 20, 30, 40, 50, 60 },
        };
        var clone = img.Clone();
        Assert.Equal(3, clone.Width);
        Assert.Equal(2, clone.Height);
        Assert.Equal(255, clone.MaxValue);
    }

    [Fact]
    public void Clone_PgmCopiesPixels()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 2, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 100, 200 },
        };
        var clone = img.Clone();
        Assert.Equal(img.Pixels[0], clone.Pixels[0]);
        Assert.Equal(img.Pixels[1], clone.Pixels[1]);
    }

    [Fact]
    public void Clone_IsDeepCopy()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 42 },
        };
        var clone = img.Clone();
        clone.Pixels[0] = 99;
        Assert.Equal(42, img.Pixels[0]);
    }

    [Fact]
    public void Clone_PpmPreservesChannels()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 255 },
            GreenChannel = new byte[] { 128 },
            BlueChannel = new byte[] { 64 },
        };
        var clone = img.Clone();
        Assert.Equal(255, clone.RedChannel![0]);
        Assert.Equal(128, clone.GreenChannel![0]);
        Assert.Equal(64, clone.BlueChannel![0]);
    }

    [Fact]
    public void Clone_PpmIsDeepCopy()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 100 },
            GreenChannel = new byte[] { 100 },
            BlueChannel = new byte[] { 100 },
        };
        var clone = img.Clone();
        clone.RedChannel![0] = 0;
        Assert.Equal(100, img.RedChannel[0]);
    }

    [Fact]
    public void Clone_PreservesFormat()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P4,
            Width = 2, Height = 2, MaxValue = 1,
            Pixels = new byte[] { 0, 1, 1, 0 },
        };
        var clone = img.Clone();
        Assert.Equal(NetpbmFormat.PBM_P4, clone.Format);
    }

    [Fact]
    public void Clone_PreservesMaxValue()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 1, Height = 1, MaxValue = 100,
            Pixels = new byte[] { 50 },
        };
        Assert.Equal(100, img.Clone().MaxValue);
    }

    [Fact]
    public void Clone_ReturnsNewInstance()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 0 },
        };
        var clone = img.Clone();
        Assert.NotSame(img, clone);
    }
}
