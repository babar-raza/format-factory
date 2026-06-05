// R111 Wave 5: Netpbm BlurBox tests
// Ledger: R111-GOVERNED-DOTNET-NETPBM-BLURBOX-001

using System;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR111BlurBoxTests
{
    private static NetpbmImage CreatePgm(int w, int h, byte fill)
    {
        var pixels = new byte[w * h];
        Array.Fill(pixels, fill);
        return new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = w, Height = h, MaxValue = 255, Pixels = pixels };
    }

    private static NetpbmImage CreatePpm(int w, int h, byte r, byte g, byte b)
    {
        int count = w * h;
        var rc = new byte[count]; Array.Fill(rc, r);
        var gc = new byte[count]; Array.Fill(gc, g);
        var bc = new byte[count]; Array.Fill(bc, b);
        return new NetpbmImage { Format = NetpbmFormat.PPM_P3, Width = w, Height = h, MaxValue = 255,
            Pixels = Array.Empty<byte>(), RedChannel = rc, GreenChannel = gc, BlueChannel = bc };
    }

    [Fact]
    public void BlurBox_Pgm_ReturnsSameSize()
    {
        var img = CreatePgm(5, 5, 128);
        var result = img.BlurBox(1);
        Assert.Equal(5, result.Width);
        Assert.Equal(5, result.Height);
    }

    [Fact]
    public void BlurBox_Pgm_UniformImage_NoChange()
    {
        var img = CreatePgm(5, 5, 100);
        var result = img.BlurBox(1);
        Assert.Equal(100, result.Pixels[2 * 5 + 2]);
    }

    [Fact]
    public void BlurBox_Ppm_ReturnsSameSize()
    {
        var img = CreatePpm(5, 5, 100, 150, 200);
        var result = img.BlurBox(1);
        Assert.Equal(5, result.Width);
        Assert.NotNull(result.RedChannel);
    }

    [Fact]
    public void BlurBox_Ppm_UniformImage_NoChange()
    {
        var img = CreatePpm(5, 5, 100, 150, 200);
        var result = img.BlurBox(1);
        int center = 2 * 5 + 2;
        Assert.Equal(100, result.RedChannel![center]);
        Assert.Equal(150, result.GreenChannel![center]);
        Assert.Equal(200, result.BlueChannel![center]);
    }

    [Fact]
    public void BlurBox_Pbm_ReturnsClone()
    {
        var img = new NetpbmImage { Format = NetpbmFormat.PBM_P1, Width = 3, Height = 3, MaxValue = 1,
            Pixels = new byte[] { 0, 1, 0, 1, 0, 1, 0, 1, 0 } };
        var result = img.BlurBox(1);
        Assert.Equal(img.Pixels, result.Pixels);
    }

    [Fact]
    public void BlurBox_ZeroRadius_Throws()
    {
        var img = CreatePgm(5, 5, 128);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.BlurBox(0));
    }

    [Fact]
    public void BlurBox_LargerRadius_SmoothsMore()
    {
        var img = CreatePgm(7, 7, 0);
        img.Pixels[3 * 7 + 3] = 255; // single bright pixel
        var blur1 = img.BlurBox(1);
        var blur2 = img.BlurBox(2);
        // Larger radius spreads the bright pixel more → center should be lower
        Assert.True(blur2.Pixels[3 * 7 + 3] <= blur1.Pixels[3 * 7 + 3]);
    }

    [Fact]
    public void BlurBox_DoesNotModifyOriginal()
    {
        var img = CreatePgm(5, 5, 128);
        byte original = img.Pixels[0];
        var _ = img.BlurBox(1);
        Assert.Equal(original, img.Pixels[0]);
    }

    [Fact]
    public void BlurBox_Pgm_CornerPixel_AveragesCorrectly()
    {
        var img = CreatePgm(3, 3, 0);
        img.Pixels[0] = 90; // top-left corner
        var result = img.BlurBox(1);
        // Corner (0,0) with radius=1 averages 4 pixels: (0,0),(0,1),(1,0),(1,1) = 90/4 = 22
        Assert.Equal(22, result.Pixels[0]);
    }

    [Fact]
    public void BlurBox_Ppm_SmallImage()
    {
        var img = CreatePpm(3, 3, 255, 0, 0);
        var result = img.BlurBox(1);
        // All red 255, uniform → should stay 255
        Assert.Equal(255, result.RedChannel![4]); // center
    }
}
