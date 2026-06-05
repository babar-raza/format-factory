// R101 Train C: Netpbm .NET GetHistogram tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R101-GOVERNED-DOTNET-NETPBM-GETHISTOGRAM-001

using System;
using System.Linq;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR101GetHistogramTests
{
    [Fact]
    public void GetHistogram_PBM_ReturnsTwoBins()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 3, Height = 2,
            MaxValue = 1,
            Pixels = new byte[] { 0, 1, 0, 1, 1, 0 }
        };
        var hist = img.GetHistogram();
        Assert.Equal(2, hist.Length);
        Assert.Equal(3, hist[0]); // white
        Assert.Equal(3, hist[1]); // black
    }

    [Fact]
    public void GetHistogram_PGM_CorrectFrequencies()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 4, Height = 1,
            MaxValue = 255,
            Pixels = new byte[] { 0, 100, 100, 255 }
        };
        var hist = img.GetHistogram();
        Assert.Equal(256, hist.Length);
        Assert.Equal(1, hist[0]);
        Assert.Equal(2, hist[100]);
        Assert.Equal(1, hist[255]);
        Assert.Equal(4, hist.Sum());
    }

    [Fact]
    public void GetHistogram_PPM_LuminanceHistogram()
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
        var hist = img.GetHistogram();
        Assert.Equal(256, hist.Length);
        Assert.Equal(1, hist[255]); // white pixel
        Assert.Equal(1, hist[0]);   // black pixel
        Assert.Equal(2, hist.Sum());
    }

    [Fact]
    public void GetHistogram_EmptyImage_ReturnsEmpty()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 0, Height = 0,
            MaxValue = 255,
            Pixels = Array.Empty<byte>()
        };
        var hist = img.GetHistogram();
        Assert.Empty(hist);
    }

    [Fact]
    public void GetHistogram_AllSameValue_SingleBinFull()
    {
        var pixels = new byte[100];
        Array.Fill(pixels, (byte)128);
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 10, Height = 10,
            MaxValue = 255,
            Pixels = pixels
        };
        var hist = img.GetHistogram();
        Assert.Equal(100, hist[128]);
        Assert.Equal(0, hist[0]);
        Assert.Equal(0, hist[255]);
    }

    [Fact]
    public void GetHistogram_SumEqualsPixelCount()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 5, Height = 3,
            MaxValue = 255,
            Pixels = new byte[] { 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150 }
        };
        var hist = img.GetHistogram();
        Assert.Equal(15, hist.Sum());
    }

    [Fact]
    public void GetHistogram_BinaryPGM_SameAsAscii()
    {
        var pixels = new byte[] { 0, 50, 100, 150, 200, 255 };
        var img1 = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 2, MaxValue = 255,
            Pixels = (byte[])pixels.Clone()
        };
        var img2 = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 3, Height = 2, MaxValue = 255,
            Pixels = (byte[])pixels.Clone()
        };
        var hist1 = img1.GetHistogram();
        var hist2 = img2.GetHistogram();
        Assert.Equal(hist1, hist2);
    }

    [Fact]
    public void GetHistogram_PBM_AllBlack()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P4,
            Width = 4, Height = 2,
            MaxValue = 1,
            Pixels = new byte[] { 1, 1, 1, 1, 1, 1, 1, 1 }
        };
        var hist = img.GetHistogram();
        Assert.Equal(0, hist[0]);
        Assert.Equal(8, hist[1]);
    }
}
