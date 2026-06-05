// R100 Train D: Netpbm .NET Rotate270Cw deep product lane tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R100-GOVERNED-DOTNET-NETPBM-ROTATE270-001

using System;
using System.IO;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR100Rotate270Tests
{
    private static NetpbmImage MakePgm(int w, int h)
    {
        var pixels = new byte[w * h];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)(i % 256);
        return new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2, Width = w, Height = h,
            MaxValue = 255, Pixels = pixels
        };
    }

    private static NetpbmImage MakePpm(int w, int h)
    {
        int len = w * h;
        var r = new byte[len]; var g = new byte[len]; var b = new byte[len];
        for (int i = 0; i < len; i++) { r[i] = (byte)(i % 256); g[i] = (byte)((i * 2) % 256); b[i] = (byte)((i * 3) % 256); }
        return new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3, Width = w, Height = h,
            MaxValue = 255, Pixels = Array.Empty<byte>(),
            RedChannel = r, GreenChannel = g, BlueChannel = b
        };
    }

    [Fact]
    public void Rotate270_SwapsDimensions()
    {
        var img = MakePgm(4, 3);
        var rotated = img.Rotate270Cw();
        Assert.Equal(3, rotated.Width);  // Height becomes Width
        Assert.Equal(4, rotated.Height); // Width becomes Height
    }

    [Fact]
    public void Rotate270_PreservesFormat()
    {
        var img = MakePgm(3, 2);
        Assert.Equal(NetpbmFormat.PGM_P2, img.Rotate270Cw().Format);
    }

    [Fact]
    public void Rotate270_PreservesMaxValue()
    {
        var img = MakePgm(3, 2);
        Assert.Equal(255, img.Rotate270Cw().MaxValue);
    }

    [Fact]
    public void Rotate270_FourRotations_RestoresOriginal()
    {
        var img = MakePgm(4, 3);
        var r4 = img.Rotate270Cw().Rotate270Cw().Rotate270Cw().Rotate270Cw();
        Assert.Equal(img.Width, r4.Width);
        Assert.Equal(img.Height, r4.Height);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                Assert.Equal(img.GetPixel(r, c), r4.GetPixel(r, c));
    }

    [Fact]
    public void Rotate270_EqualsThreeRotate90()
    {
        var img = MakePgm(4, 3);
        var via270 = img.Rotate270Cw();
        var via90x3 = img.Rotate90Cw().Rotate90Cw().Rotate90Cw();
        Assert.Equal(via270.Width, via90x3.Width);
        Assert.Equal(via270.Height, via90x3.Height);
        for (int r = 0; r < via270.Height; r++)
            for (int c = 0; c < via270.Width; c++)
                Assert.Equal(via270.GetPixel(r, c), via90x3.GetPixel(r, c));
    }

    [Fact]
    public void Rotate270_PPM_PreservesColors()
    {
        var img = MakePpm(3, 2);
        var rotated = img.Rotate270Cw();
        // Verify dimensions swapped
        Assert.Equal(2, rotated.Width);
        Assert.Equal(3, rotated.Height);
        // Pixel at (0,0) in original maps to (Width-1, 0) in 270 rotation
        var orig = img.GetPixelColor(0, 0);
        var rot = rotated.GetPixelColor(img.Width - 1, 0);
        Assert.Equal(orig.R, rot.R);
        Assert.Equal(orig.G, rot.G);
        Assert.Equal(orig.B, rot.B);
    }

    [Fact]
    public void Rotate270_SaveToFile_Roundtrip()
    {
        var img = MakePgm(4, 3);
        var rotated = img.Rotate270Cw();
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            rotated.SaveToFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.StartsWith("P2", content);
            Assert.Contains("3 4", content); // Width=3(was Height), Height=4(was Width)
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Rotate270_PBM_Works()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1, Width = 3, Height = 2,
            MaxValue = 1, Pixels = new byte[] { 0, 1, 0, 1, 0, 1 }
        };
        var rotated = img.Rotate270Cw();
        Assert.Equal(2, rotated.Width);
        Assert.Equal(3, rotated.Height);
    }

    [Fact]
    public void Rotate90_Then270_RestoresOriginal()
    {
        var img = MakePgm(4, 3);
        var result = img.Rotate90Cw().Rotate270Cw();
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                Assert.Equal(img.GetPixel(r, c), result.GetPixel(r, c));
    }

    [Fact]
    public void Rotate270_PPM_FourRotations_RestoresOriginal()
    {
        var img = MakePpm(3, 2);
        var r4 = img.Rotate270Cw().Rotate270Cw().Rotate270Cw().Rotate270Cw();
        Assert.Equal(img.Width, r4.Width);
        Assert.Equal(img.Height, r4.Height);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
            {
                var o = img.GetPixelColor(r, c);
                var f = r4.GetPixelColor(r, c);
                Assert.Equal(o.R, f.R);
                Assert.Equal(o.G, f.G);
                Assert.Equal(o.B, f.B);
            }
    }
}
