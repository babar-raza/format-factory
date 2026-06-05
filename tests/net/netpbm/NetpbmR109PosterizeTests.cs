// R109 Lane E: Netpbm Posterize tests
// Ledger: R109-GOVERNED-DOTNET-NETPBM-POSTERIZE-001

using System;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR109PosterizeTests
{
    private static NetpbmImage MakeGray(int w, int h, byte val)
    {
        var px = new byte[w * h];
        for (int i = 0; i < px.Length; i++) px[i] = val;
        return new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = w, Height = h, MaxValue = 255, Pixels = px };
    }

    private static NetpbmImage MakePpm(int w, int h, byte r, byte g, byte b)
    {
        int len = w * h;
        var rc = new byte[len]; var gc = new byte[len]; var bc = new byte[len];
        for (int i = 0; i < len; i++) { rc[i] = r; gc[i] = g; bc[i] = b; }
        return new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3, Width = w, Height = h, MaxValue = 255,
            Pixels = new byte[0], RedChannel = rc, GreenChannel = gc, BlueChannel = bc
        };
    }

    [Fact]
    public void Posterize_TwoLevels_BinarizesGray()
    {
        var img = MakeGray(4, 4, 128);
        var result = img.Posterize(2);
        // 128/255 ≈ 0.502, bucket = round(0.502 * 1) = 1 → value = 255
        Assert.Equal(255, result.Pixels[0]);
    }

    [Fact]
    public void Posterize_TwoLevels_LowValue()
    {
        var img = MakeGray(4, 4, 50);
        var result = img.Posterize(2);
        // 50/255 ≈ 0.196, bucket = round(0.196 * 1) = 0 → value = 0
        Assert.Equal(0, result.Pixels[0]);
    }

    [Fact]
    public void Posterize_256Levels_PreservesValues()
    {
        var img = MakeGray(4, 4, 128);
        var result = img.Posterize(256);
        Assert.Equal(128, result.Pixels[0]);
    }

    [Fact]
    public void Posterize_LessThanTwo_Throws()
    {
        var img = MakeGray(4, 4, 128);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Posterize(1));
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Posterize(0));
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Posterize(-5));
    }

    [Fact]
    public void Posterize_DoesNotMutateOriginal()
    {
        var img = MakeGray(4, 4, 128);
        byte orig = img.Pixels[0];
        _ = img.Posterize(2);
        Assert.Equal(orig, img.Pixels[0]);
    }

    [Fact]
    public void Posterize_PBM_ReturnsCopy()
    {
        var pbm = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1, Width = 2, Height = 2, MaxValue = 1,
            Pixels = new byte[] { 0, 1, 1, 0 }
        };
        var result = pbm.Posterize(4);
        Assert.Equal(pbm.Pixels, result.Pixels);
    }

    [Fact]
    public void Posterize_PPM_AppliesAllChannels()
    {
        var img = MakePpm(2, 2, 200, 100, 50);
        var result = img.Posterize(3);
        // 200/255 ≈ 0.784, bucket = round(0.784*2)=round(1.569)=2 → value=255
        Assert.Equal(255, result.RedChannel![0]);
        // 100/255 ≈ 0.392, bucket = round(0.392*2)=round(0.784)=1 → value=128
        Assert.True(result.GreenChannel![0] >= 127 && result.GreenChannel[0] <= 128);
        // 50/255 ≈ 0.196, bucket = round(0.196*2)=round(0.392)=0 → value=0
        Assert.Equal(0, result.BlueChannel![0]);
    }

    [Fact]
    public void Posterize_FourLevels_QuantizesCorrectly()
    {
        // 4 levels: output values are 0, 85, 170, 255
        var img = MakeGray(1, 4, 0);
        img.Pixels[0] = 0;
        img.Pixels[1] = 64;
        img.Pixels[2] = 170;
        img.Pixels[3] = 255;
        var result = img.Posterize(4);
        Assert.Equal(0, result.Pixels[0]);
        Assert.True(result.Pixels[1] >= 80 && result.Pixels[1] <= 90); // near 85
        Assert.True(result.Pixels[2] >= 165 && result.Pixels[2] <= 175); // near 170
        Assert.Equal(255, result.Pixels[3]);
    }

    [Fact]
    public void Posterize_MaxValue_And_Zero_Preserved()
    {
        var img = MakeGray(1, 2, 0);
        img.Pixels[0] = 0;
        img.Pixels[1] = 255;
        var result = img.Posterize(5);
        Assert.Equal(0, result.Pixels[0]);
        Assert.Equal(255, result.Pixels[1]);
    }

    [Fact]
    public void Posterize_ResultFormat_Matches()
    {
        var img = MakeGray(2, 2, 128);
        var result = img.Posterize(3);
        Assert.Equal(img.Format, result.Format);
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }
}
