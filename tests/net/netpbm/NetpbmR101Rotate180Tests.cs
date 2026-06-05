// R101 Train D: Netpbm .NET Rotate180 deep product lane tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R101-GOVERNED-DOTNET-NETPBM-ROTATE180-001

using System;
using System.IO;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR101Rotate180Tests
{
    private static NetpbmImage MakePgm(int w, int h, byte[] pixels) => new()
    {
        Format = NetpbmFormat.PGM_P5,
        Width = w, Height = h, MaxValue = 255,
        Pixels = pixels,
    };

    private static NetpbmImage MakePpm(int w, int h, byte[] r, byte[] g, byte[] b) => new()
    {
        Format = NetpbmFormat.PPM_P6,
        Width = w, Height = h, MaxValue = 255,
        RedChannel = r, GreenChannel = g, BlueChannel = b,
        Pixels = Array.Empty<byte>(),
    };

    [Fact]
    public void Rotate180_PGM_DimensionsUnchanged()
    {
        var img = MakePgm(3, 2, new byte[] { 1, 2, 3, 4, 5, 6 });
        var rotated = img.Rotate180();
        Assert.Equal(3, rotated.Width);
        Assert.Equal(2, rotated.Height);
    }

    [Fact]
    public void Rotate180_PGM_PixelsReversed()
    {
        var img = MakePgm(3, 2, new byte[] { 1, 2, 3, 4, 5, 6 });
        var rotated = img.Rotate180();
        Assert.Equal(new byte[] { 6, 5, 4, 3, 2, 1 }, rotated.Pixels);
    }

    [Fact]
    public void Rotate180_Twice_ReturnsOriginal()
    {
        var pixels = new byte[] { 10, 20, 30, 40 };
        var img = MakePgm(2, 2, pixels);
        var rotated = img.Rotate180().Rotate180();
        Assert.Equal(pixels, rotated.Pixels);
    }

    [Fact]
    public void Rotate180_PPM_DimensionsUnchanged()
    {
        var img = MakePpm(2, 2,
            new byte[] { 1, 2, 3, 4 },
            new byte[] { 5, 6, 7, 8 },
            new byte[] { 9, 10, 11, 12 });
        var rotated = img.Rotate180();
        Assert.Equal(2, rotated.Width);
        Assert.Equal(2, rotated.Height);
    }

    [Fact]
    public void Rotate180_PPM_ChannelsReversed()
    {
        var img = MakePpm(2, 2,
            new byte[] { 1, 2, 3, 4 },
            new byte[] { 5, 6, 7, 8 },
            new byte[] { 9, 10, 11, 12 });
        var rotated = img.Rotate180();
        Assert.Equal(new byte[] { 4, 3, 2, 1 }, rotated.RedChannel);
        Assert.Equal(new byte[] { 8, 7, 6, 5 }, rotated.GreenChannel);
        Assert.Equal(new byte[] { 12, 11, 10, 9 }, rotated.BlueChannel);
    }

    [Fact]
    public void Rotate180_PPM_Twice_ReturnsOriginal()
    {
        var r = new byte[] { 1, 2, 3, 4 };
        var g = new byte[] { 5, 6, 7, 8 };
        var b = new byte[] { 9, 10, 11, 12 };
        var img = MakePpm(2, 2, r, g, b);
        var rotated = img.Rotate180().Rotate180();
        Assert.Equal(r, rotated.RedChannel);
        Assert.Equal(g, rotated.GreenChannel);
        Assert.Equal(b, rotated.BlueChannel);
    }

    [Fact]
    public void Rotate180_PBM_PixelsReversed()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P4,
            Width = 2, Height = 2, MaxValue = 1,
            Pixels = new byte[] { 0, 1, 1, 0 },
        };
        var rotated = img.Rotate180();
        Assert.Equal(new byte[] { 0, 1, 1, 0 }, rotated.Pixels);
    }

    [Fact]
    public void Rotate180_PreservesFormat()
    {
        var img = MakePgm(2, 2, new byte[] { 1, 2, 3, 4 });
        var rotated = img.Rotate180();
        Assert.Equal(NetpbmFormat.PGM_P5, rotated.Format);
        Assert.Equal(255, rotated.MaxValue);
    }

    [Fact]
    public void Rotate180_SaveToFile_WritesValidPgm()
    {
        var img = MakePgm(3, 2, new byte[] { 10, 20, 30, 40, 50, 60 });
        var rotated = img.Rotate180();
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            rotated.SaveToFile(tmp);
            Assert.True(File.Exists(tmp));
            var content = File.ReadAllText(tmp);
            Assert.StartsWith("P5", content);
            Assert.Contains("3 2", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Rotate180_EquivalentToTwoRotate90()
    {
        var img = MakePgm(3, 2, new byte[] { 1, 2, 3, 4, 5, 6 });
        var via180 = img.Rotate180();
        var via90x2 = img.Rotate90Cw().Rotate90Cw();
        Assert.Equal(via180.Width, via90x2.Width);
        Assert.Equal(via180.Height, via90x2.Height);
        Assert.Equal(via180.Pixels, via90x2.Pixels);
    }
}
