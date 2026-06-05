// R107 Wave 2: Netpbm ConvertFormat tests
// Ledger: R107-NETPBM-CONVERTFORMAT

using System;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR107ConvertFormatTests
{
    private static NetpbmImage MakeGray(int w, int h, byte val)
    {
        var px = new byte[w * h];
        for (int i = 0; i < px.Length; i++) px[i] = val;
        return new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = w, Height = h, MaxValue = 255, Pixels = px };
    }

    [Fact]
    public void ConvertFormat_PGM_P2_To_P5()
    {
        var img = MakeGray(4, 4, 128);
        var result = img.ConvertFormat(NetpbmFormat.PGM_P5);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(img.Pixels[0], result.Pixels[0]);
    }

    [Fact]
    public void ConvertFormat_PGM_P5_To_P2()
    {
        var img = MakeGray(4, 4, 200);
        img.Format = NetpbmFormat.PGM_P5;
        var result = img.ConvertFormat(NetpbmFormat.PGM_P2);
        Assert.Equal(NetpbmFormat.PGM_P2, result.Format);
    }

    [Fact]
    public void ConvertFormat_PBM_P1_To_P4()
    {
        var px = new byte[] { 0, 1, 1, 0 };
        var img = new NetpbmImage { Format = NetpbmFormat.PBM_P1, Width = 2, Height = 2, MaxValue = 1, Pixels = px };
        var result = img.ConvertFormat(NetpbmFormat.PBM_P4);
        Assert.Equal(NetpbmFormat.PBM_P4, result.Format);
        Assert.Equal(px, result.Pixels);
    }

    [Fact]
    public void ConvertFormat_PPM_P3_To_P6()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 2, Height = 2, MaxValue = 255,
            Pixels = new byte[0],
            RedChannel = new byte[] { 255, 0, 128, 64 },
            GreenChannel = new byte[] { 0, 255, 128, 64 },
            BlueChannel = new byte[] { 0, 0, 128, 64 },
        };
        var result = img.ConvertFormat(NetpbmFormat.PPM_P6);
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
        Assert.Equal(255, result.RedChannel![0]);
    }

    [Fact]
    public void ConvertFormat_CrossType_Throws()
    {
        var img = MakeGray(4, 4, 128);
        Assert.Throws<InvalidOperationException>(() => img.ConvertFormat(NetpbmFormat.PPM_P3));
    }

    [Fact]
    public void ConvertFormat_PBM_To_PGM_Throws()
    {
        var px = new byte[] { 0, 1 };
        var img = new NetpbmImage { Format = NetpbmFormat.PBM_P1, Width = 2, Height = 1, MaxValue = 1, Pixels = px };
        Assert.Throws<InvalidOperationException>(() => img.ConvertFormat(NetpbmFormat.PGM_P2));
    }

    [Fact]
    public void ConvertFormat_DoesNotMutateOriginal()
    {
        var img = MakeGray(4, 4, 128);
        var result = img.ConvertFormat(NetpbmFormat.PGM_P5);
        Assert.Equal(NetpbmFormat.PGM_P2, img.Format);
    }

    [Fact]
    public void ConvertFormat_SameFormat_ReturnsCopy()
    {
        var img = MakeGray(4, 4, 128);
        var result = img.ConvertFormat(NetpbmFormat.PGM_P2);
        Assert.Equal(NetpbmFormat.PGM_P2, result.Format);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void ConvertFormat_PreservesDimensions()
    {
        var img = MakeGray(10, 5, 100);
        var result = img.ConvertFormat(NetpbmFormat.PGM_P5);
        Assert.Equal(10, result.Width);
        Assert.Equal(5, result.Height);
        Assert.Equal(255, result.MaxValue);
    }

    [Fact]
    public void ConvertFormat_PPM_P6_To_P3()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P6,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[0],
            RedChannel = new byte[] { 42 },
            GreenChannel = new byte[] { 84 },
            BlueChannel = new byte[] { 126 },
        };
        var result = img.ConvertFormat(NetpbmFormat.PPM_P3);
        Assert.Equal(NetpbmFormat.PPM_P3, result.Format);
        Assert.Equal(42, result.RedChannel![0]);
    }
}
