// R103 Train C: Netpbm .NET ExtractChannel tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R103-GOVERNED-DOTNET-NETPBM-EXTRACTCHANNEL-001

using System;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR103ExtractChannelTests
{
    private static NetpbmImage MakePpm(int w, int h, byte r, byte g, byte b)
    {
        int len = w * h;
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = w, Height = h,
            MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[len],
            GreenChannel = new byte[len],
            BlueChannel = new byte[len],
        };
        Array.Fill(img.RedChannel, r);
        Array.Fill(img.GreenChannel, g);
        Array.Fill(img.BlueChannel, b);
        return img;
    }

    [Fact]
    public void ExtractChannel_Red_ReturnsPGM()
    {
        var img = MakePpm(3, 2, 200, 100, 50);
        var result = img.ExtractChannel(0);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(3, result.Width);
        Assert.Equal(2, result.Height);
    }

    [Fact]
    public void ExtractChannel_Red_CorrectValues()
    {
        var img = MakePpm(2, 1, 200, 100, 50);
        var result = img.ExtractChannel(0);
        Assert.Equal(200, result.Pixels[0]);
        Assert.Equal(200, result.Pixels[1]);
    }

    [Fact]
    public void ExtractChannel_Green_CorrectValues()
    {
        var img = MakePpm(2, 1, 200, 100, 50);
        var result = img.ExtractChannel(1);
        Assert.Equal(100, result.Pixels[0]);
    }

    [Fact]
    public void ExtractChannel_Blue_CorrectValues()
    {
        var img = MakePpm(2, 1, 200, 100, 50);
        var result = img.ExtractChannel(2);
        Assert.Equal(50, result.Pixels[0]);
    }

    [Fact]
    public void ExtractChannel_PGM_Throws()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 1, Height = 1,
            MaxValue = 255,
            Pixels = new byte[] { 128 }
        };
        Assert.Throws<InvalidOperationException>(() => img.ExtractChannel(0));
    }

    [Fact]
    public void ExtractChannel_InvalidChannel_Throws()
    {
        var img = MakePpm(1, 1, 100, 100, 100);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.ExtractChannel(3));
        Assert.Throws<ArgumentOutOfRangeException>(() => img.ExtractChannel(-1));
    }

    [Fact]
    public void ExtractChannel_PreservesMaxValue()
    {
        var img = MakePpm(1, 1, 100, 100, 100);
        var result = img.ExtractChannel(0);
        Assert.Equal(255, result.MaxValue);
    }

    [Fact]
    public void ExtractChannel_IndependentCopy()
    {
        var img = MakePpm(2, 1, 200, 100, 50);
        var result = img.ExtractChannel(0);
        result.Pixels[0] = 0;
        Assert.Equal(200, img.RedChannel![0]); // original unchanged
    }
}
