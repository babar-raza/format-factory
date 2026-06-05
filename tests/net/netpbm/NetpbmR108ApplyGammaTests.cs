// R108 Lane E: Netpbm ApplyGamma tests
// Ledger: R108-GOVERNED-DOTNET-NETPBM-APPLYGAMMA-001

using System;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR108ApplyGammaTests
{
    private static NetpbmImage MakeGray(int w, int h, byte val)
    {
        var px = new byte[w * h];
        for (int i = 0; i < px.Length; i++) px[i] = val;
        return new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = w, Height = h, MaxValue = 255, Pixels = px };
    }

    [Fact]
    public void ApplyGamma_Identity_PreservesValues()
    {
        var img = MakeGray(4, 4, 128);
        var result = img.ApplyGamma(1.0);
        Assert.Equal(128, result.Pixels[0]);
    }

    [Fact]
    public void ApplyGamma_Brighten_IncreasesValues()
    {
        var img = MakeGray(4, 4, 128);
        var result = img.ApplyGamma(0.5); // gamma < 1 brightens
        Assert.True(result.Pixels[0] > 128);
    }

    [Fact]
    public void ApplyGamma_Darken_DecreasesValues()
    {
        var img = MakeGray(4, 4, 128);
        var result = img.ApplyGamma(2.0); // gamma > 1 darkens
        Assert.True(result.Pixels[0] < 128);
    }

    [Fact]
    public void ApplyGamma_Zero_ClampedCorrectly()
    {
        var img = MakeGray(4, 4, 0);
        var result = img.ApplyGamma(2.0);
        Assert.Equal(0, result.Pixels[0]);
    }

    [Fact]
    public void ApplyGamma_MaxValue_PreservedAtMax()
    {
        var img = MakeGray(4, 4, 255);
        var result = img.ApplyGamma(0.5);
        Assert.Equal(255, result.Pixels[0]);
    }

    [Fact]
    public void ApplyGamma_NegativeGamma_Throws()
    {
        var img = MakeGray(4, 4, 128);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.ApplyGamma(-1.0));
    }

    [Fact]
    public void ApplyGamma_ZeroGamma_Throws()
    {
        var img = MakeGray(4, 4, 128);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.ApplyGamma(0));
    }

    [Fact]
    public void ApplyGamma_DoesNotMutateOriginal()
    {
        var img = MakeGray(4, 4, 128);
        var original = img.Pixels[0];
        var _ = img.ApplyGamma(2.0);
        Assert.Equal(original, img.Pixels[0]);
    }

    [Fact]
    public void ApplyGamma_PBM_ReturnsClone()
    {
        var px = new byte[16];
        for (int i = 0; i < 16; i++) px[i] = (byte)(i % 2);
        var img = new NetpbmImage { Format = NetpbmFormat.PBM_P1, Width = 4, Height = 4, MaxValue = 1, Pixels = px };
        var result = img.ApplyGamma(2.0);
        Assert.Equal(img.Pixels[0], result.Pixels[0]);
    }

    [Fact]
    public void ApplyGamma_PPM_AppliesAllChannels()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3, Width = 2, Height = 2, MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[] { 128, 128, 128, 128 },
            GreenChannel = new byte[] { 128, 128, 128, 128 },
            BlueChannel = new byte[] { 128, 128, 128, 128 }
        };
        var result = img.ApplyGamma(2.0);
        Assert.True(result.RedChannel![0] < 128);
        Assert.True(result.GreenChannel![0] < 128);
        Assert.True(result.BlueChannel![0] < 128);
    }
}
